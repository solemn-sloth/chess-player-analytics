import re
from datetime import datetime
from collections import defaultdict
from config import (OPENING_PHASE_END, MIDDLEGAME_PHASE_END, TIME_PRESSURE_SECONDS,
                   CRITICAL_TIME_THRESHOLD, TIME_CATEGORIES)

class GameParser:
    """Parses chess games and extracts relevant data"""
    
    def parse_game(self, game_json, username):
        """Parse a single game and extract all relevant information"""
        parsed = {}
        
        # Basic info
        parsed['url'] = game_json['url']
        parsed['time_control'] = game_json.get('time_class', 'unknown')
        parsed['rated'] = game_json.get('rated', False)
        parsed['date'] = datetime.fromtimestamp(game_json.get('end_time', 0))
        
        # Player color and result
        color_data = self._determine_player_color(game_json, username)
        parsed.update(color_data)
        
        # Parse moves
        moves = self._parse_pgn_moves(game_json['pgn'])
        parsed['moves'] = moves
        parsed['total_moves'] = len(moves) // 2
        
        # Game phase analysis
        parsed['end_phase'] = self._analyze_game_phases(parsed['total_moves'])
        
        # Opening info
        parsed['opening'] = self._extract_opening(game_json)
        parsed['opening_moves'] = ' '.join(moves[:10]) if len(moves) >= 10 else ' '.join(moves)
        
        # Termination analysis
        parsed['termination'] = self._analyze_termination(game_json['pgn'], parsed['result'])
        
        # Time analysis
        parsed['day_of_week'] = parsed['date'].strftime('%a')
        parsed['hour_of_day'] = parsed['date'].hour
        parsed['time_of_day'] = self._get_time_of_day(parsed['hour_of_day'])
        
        # Time management
        time_data = self._extract_time_data(game_json['pgn'], parsed['color'])
        parsed.update(time_data)
        
        # Piece activity
        parsed['piece_activity'] = self._analyze_piece_activity(moves)
        parsed['captures_made'] = sum(1 for m in moves if 'x' in m)
        
        # Trades and exchanges
        trade_data = self._analyze_trades(moves, parsed['color'])
        parsed.update(trade_data)
        
        # Tactical patterns
        parsed['tactics'] = self._detect_tactical_patterns(moves)
        
        return parsed
    
    def _parse_pgn_moves(self, pgn):
        """Extract moves from PGN string"""
        # Remove comments and variations
        pgn_clean = re.sub(r'\{[^}]*\}', '', pgn)
        pgn_clean = re.sub(r'\([^)]*\)', '', pgn_clean)
        
        # Find all moves
        moves = re.findall(r'\d+\.\s*([^\s]+)\s*(?:\{[^}]*\})?\s*([^\s]+)?', pgn_clean)
        
        flat_moves = []
        for white_move, black_move in moves:
            if white_move and not white_move.startswith('['):
                flat_moves.append(white_move)
            if black_move and not black_move.startswith('['):
                flat_moves.append(black_move)
        
        return flat_moves
    
    def _determine_player_color(self, game_json, username):
        """Determine player color and extract ratings"""
        if game_json['white']['username'].lower() == username.lower():
            return {
                'color': 'white',
                'result': game_json['white']['result'],
                'opponent': game_json['black']['username'],
                'player_rating': game_json['white']['rating'],
                'opponent_rating': game_json['black']['rating'],
                'result_type': self._simplify_result(game_json['white']['result'])
            }
        else:
            return {
                'color': 'black',
                'result': game_json['black']['result'],
                'opponent': game_json['white']['username'],
                'player_rating': game_json['black']['rating'],
                'opponent_rating': game_json['white']['rating'],
                'result_type': self._simplify_result(game_json['black']['result'])
            }
    
    def _simplify_result(self, result):
        """Convert result to win/loss/draw"""
        if result == 'win':
            return 'win'
        elif result in ['checkmated', 'resigned', 'timeout', 'abandoned']:
            return 'loss'
        else:
            return 'draw'
    
    def _analyze_game_phases(self, total_moves):
        """Determine which phase the game ended in"""
        if total_moves <= OPENING_PHASE_END:
            return 'opening'
        elif total_moves <= MIDDLEGAME_PHASE_END:
            return 'middlegame'
        else:
            return 'endgame'
    
    def _extract_opening(self, game_json):
        """Extract opening name from game data"""
        if 'eco' in game_json:
            eco_url = game_json['eco']
            return eco_url.split('/')[-1].replace('-', ' ')
        return 'Unknown'
    
    def _analyze_termination(self, pgn, result):
        """Determine how the game ended"""
        pgn_lower = pgn.lower()
        if 'checkmate' in pgn_lower:
            return 'checkmate'
        elif 'resignation' in pgn_lower or 'resigned' in result:
            return 'resignation'
        elif 'time' in pgn_lower or 'timeout' in result:
            return 'time'
        elif 'stalemate' in pgn_lower:
            return 'stalemate'
        elif 'draw' in result:
            return 'draw'
        else:
            return 'other'
    
    def _get_time_of_day(self, hour):
        """Categorize hour into time of day"""
        for category, (start_hour, end_hour) in TIME_CATEGORIES.items():
            if start_hour <= hour < end_hour:
                return category
        return 'Unknown'
    
    def _extract_time_data(self, pgn, color):
        """Extract time management data from PGN"""
        clock_times = re.findall(r'\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]', pgn)
        if not clock_times:
            return {}
        
        time_data = []
        for hours, minutes, seconds in clock_times:
            total_seconds = int(hours)*3600 + int(minutes)*60 + float(seconds)
            time_data.append(total_seconds)
        
        # Extract player's times based on color
        if color == 'white':
            player_times = [time_data[i] for i in range(0, len(time_data), 2) if i < len(time_data)]
        else:
            player_times = [time_data[i] for i in range(1, len(time_data), 2) if i < len(time_data)]
        
        if not player_times:
            return {}
        
        result = {
            'time_data': time_data,
            'final_time': player_times[-1],
            'time_pressure_moves': sum(1 for t in player_times if t < TIME_PRESSURE_SECONDS)
        }
        
        # Time per phase
        move_numbers = list(range(1, len(player_times) + 1))
        opening_times = [t for i, t in enumerate(player_times) if move_numbers[i] <= OPENING_PHASE_END]
        middle_times = [t for i, t in enumerate(player_times) if OPENING_PHASE_END < move_numbers[i] <= MIDDLEGAME_PHASE_END]
        endgame_times = [t for i, t in enumerate(player_times) if move_numbers[i] > MIDDLEGAME_PHASE_END]
        
        result['avg_time_per_phase'] = {
            'opening': sum(opening_times) / len(opening_times) if opening_times else 0,
            'middlegame': sum(middle_times) / len(middle_times) if middle_times else 0,
            'endgame': sum(endgame_times) / len(endgame_times) if endgame_times else 0
        }
        
        # Critical moves
        if len(player_times) > 1:
            time_diffs = [player_times[i] - player_times[i+1] for i in range(len(player_times)-1)]
            avg_time_per_move = sum(time_diffs) / len(time_diffs) if time_diffs else 0
            
            critical_moves = []
            for i, diff in enumerate(time_diffs):
                if diff > 3 * avg_time_per_move or (diff < avg_time_per_move / 3 and player_times[i+1] < CRITICAL_TIME_THRESHOLD):
                    critical_moves.append((move_numbers[i], diff, player_times[i]))
            
            result['critical_moves'] = critical_moves[:5]
            result['avg_time_per_move'] = avg_time_per_move
        
        return result
    
    def _analyze_piece_activity(self, moves):
        """Count piece moves by type"""
        piece_moves = defaultdict(int)
        for move in moves:
            if move[0] in 'NBRQK':
                piece_moves[move[0]] += 1
            elif move[0] in 'abcdefgh' and 'x' not in move:
                piece_moves['P'] += 1
        return dict(piece_moves)
    
    def _analyze_trades(self, moves, color):
        """Analyze piece trades and exchanges"""
        trades_initiated = 0
        piece_trades = defaultdict(int)
        queen_trade = False
        
        for i, move in enumerate(moves):
            if 'x' in move:
                # Check if player initiated the capture
                if (i % 2 == 0 and color == 'white') or (i % 2 == 1 and color == 'black'):
                    trades_initiated += 1
                    
                    # Determine captured piece type (simplified)
                    if move[0] in 'NBRQK':
                        captured_piece = move.split('x')[1][0] if len(move.split('x')[1]) > 0 and move.split('x')[1][0] in 'NBRQKpnbrqk' else 'P'
                        piece_trades[captured_piece] += 1
                        
                        if captured_piece == 'Q':
                            queen_trade = True
        
        return {
            'trades_initiated': trades_initiated,
            'piece_trades': dict(piece_trades),
            'queen_trade': queen_trade
        }
    
    def _detect_tactical_patterns(self, moves):
        """Detect tactical patterns in the game"""
        tactics = {}
        move_text = ' '.join(moves)
        
        # Forks
        fork_patterns = [r'\+.*x', r'x.*\+']
        for pattern in fork_patterns:
            if re.search(pattern, move_text):
                tactics['forks'] = True
                break
        
        # Discovered attacks
        if re.search(r'[NBRQ][a-h]\d.*\+', move_text):
            tactics['discovered'] = True
        
        # Back rank patterns
        if re.search(r'[RQ].*[18]\+', move_text):
            tactics['back_rank'] = True
        
        return tactics