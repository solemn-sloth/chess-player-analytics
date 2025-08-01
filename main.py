import json
import re
from collections import defaultdict, Counter
from datetime import datetime
import requests
import os
from config import *

class ChessAnalyzer:
    def __init__(self, username):
        self.username = username
        self.headers = {'User-Agent': USER_AGENT}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.games = []
        self.analyzed_games = []
        
    def fetch_games(self, num_games=DEFAULT_NUM_GAMES):
        """Fetch games from Chess.com API"""
        print(f"Fetching {num_games} games for {self.username}...")
        
        # Get archives
        response = self.session.get(f"https://api.chess.com/pub/player/{self.username}/games/archives")
        if response.status_code != 200:
            print(f"Error: Could not fetch game archives (Status: {response.status_code})")
            return []
        
        archives = response.json()['archives']
        games = []
        
        # Fetch games from recent archives
        for archive_url in reversed(archives):
            if len(games) >= num_games:
                break
                
            response = self.session.get(archive_url)
            if response.status_code == 200:
                month_games = response.json()['games']
                games.extend(month_games)
                print(f"Fetched {len(games)} games so far...")
        
        self.games = games[:num_games]
        print(f"Successfully fetched {len(self.games)} games")
        return self.games
    
    def parse_pgn_moves(self, pgn):
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
    
    def analyze_single_game(self, game):
        """Deep analysis of a single game"""
        analysis = {}
        
        # Basic info
        analysis['url'] = game['url']
        analysis['time_control'] = game.get('time_class', 'unknown')
        analysis['rated'] = game.get('rated', False)
        analysis['date'] = datetime.fromtimestamp(game.get('end_time', 0))
        
        # Determine player color and result
        if game['white']['username'].lower() == self.username.lower():
            analysis['color'] = 'white'
            analysis['result'] = game['white']['result']
            analysis['opponent'] = game['black']['username']
            analysis['player_rating'] = game['white']['rating']
            analysis['opponent_rating'] = game['black']['rating']
        else:
            analysis['color'] = 'black'
            analysis['result'] = game['black']['result']
            analysis['opponent'] = game['white']['username']
            analysis['player_rating'] = game['black']['rating']
            analysis['opponent_rating'] = game['white']['rating']
        
        # Simplified result
        if analysis['result'] == 'win':
            analysis['result_type'] = 'win'
        elif analysis['result'] in ['checkmated', 'resigned', 'timeout', 'abandoned']:
            analysis['result_type'] = 'loss'
        else:
            analysis['result_type'] = 'draw'
        
        # Rating difference
        analysis['rating_diff'] = analysis['opponent_rating'] - analysis['player_rating']
        
        # Parse moves and game length
        moves = self.parse_pgn_moves(game['pgn'])
        analysis['moves'] = moves
        analysis['total_moves'] = len(moves) // 2
        
        # Game phase when it ended
        if analysis['total_moves'] <= OPENING_PHASE_END:
            analysis['end_phase'] = 'opening'
        elif analysis['total_moves'] <= MIDDLEGAME_PHASE_END:
            analysis['end_phase'] = 'middlegame'
        else:
            analysis['end_phase'] = 'endgame'
        
        # Opening info
        if 'eco' in game:
            eco_url = game['eco']
            analysis['opening'] = eco_url.split('/')[-1].replace('-', ' ')
        else:
            analysis['opening'] = 'Unknown'
        
        # First few moves for pattern analysis
        analysis['opening_moves'] = ' '.join(moves[:10]) if len(moves) >= 10 else ' '.join(moves)
        
        # Game termination
        pgn = game['pgn']
        if 'checkmate' in pgn.lower():
            analysis['termination'] = 'checkmate'
        elif 'resignation' in pgn.lower() or 'resigned' in analysis['result']:
            analysis['termination'] = 'resignation'
        elif 'time' in pgn.lower() or 'timeout' in analysis['result']:
            analysis['termination'] = 'time'
        elif 'stalemate' in pgn.lower():
            analysis['termination'] = 'stalemate'
        elif 'draw' in analysis['result']:
            analysis['termination'] = 'draw'
        else:
            analysis['termination'] = 'other'
        
        # Time management analysis
        clock_times = re.findall(r'\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]', pgn)
        if clock_times:
            analysis['time_data'] = []
            for i in range(len(clock_times)):
                hours, minutes, seconds = clock_times[i]
                total_seconds = int(hours)*3600 + int(minutes)*60 + float(seconds)
                analysis['time_data'].append(total_seconds)
            
            # Check for time pressure
            if analysis['color'] == 'white':
                player_times = [analysis['time_data'][i] for i in range(0, len(analysis['time_data']), 2)]
            else:
                player_times = [analysis['time_data'][i] for i in range(1, len(analysis['time_data']), 2)]
            
            if player_times:
                analysis['final_time'] = player_times[-1]
                analysis['time_pressure_moves'] = sum(1 for t in player_times if t < TIME_PRESSURE_SECONDS)
        
        # Piece activity (simplified - count piece moves)
        piece_moves = defaultdict(int)
        for move in moves:
            # Identify piece type from move notation
            if move[0] in 'NBRQK':
                piece_moves[move[0]] += 1
            elif move[0] in 'abcdefgh' and 'x' not in move:  # Pawn move
                piece_moves['P'] += 1
        analysis['piece_activity'] = dict(piece_moves)
        
        # Material tracking (simplified)
        captures = [m for m in moves if 'x' in m]
        analysis['captures_made'] = len(captures)
        
        return analysis
    
    def analyze_all_games(self):
        """Analyze all fetched games"""
        print("\nAnalyzing games...")
        self.analyzed_games = []
        
        for i, game in enumerate(self.games):
            if i % 20 == 0:
                print(f"Analyzed {i}/{len(self.games)} games...")
            
            try:
                analysis = self.analyze_single_game(game)
                self.analyzed_games.append(analysis)
            except Exception as e:
                print(f"Error analyzing game {i}: {e}")
                continue
        
        print(f"Successfully analyzed {len(self.analyzed_games)} games")
        return self.analyzed_games
    
    def generate_insights(self):
        """Generate all insights from analyzed games"""
        insights = {
            'basic_stats': self.calculate_basic_stats(),
            'opening_analysis': self.analyze_openings(),
            'pattern_recognition': self.analyze_patterns(),
            'phase_performance': self.analyze_game_phases(),
            'mistake_patterns': self.analyze_mistakes(),
            'endgame_proficiency': self.analyze_endgames(),
            'momentum_psychology': self.analyze_momentum()
        }
        
        return insights
    
    def calculate_basic_stats(self):
        """Calculate basic statistics"""
        total = len(self.analyzed_games)
        wins = sum(1 for g in self.analyzed_games if g['result_type'] == 'win')
        losses = sum(1 for g in self.analyzed_games if g['result_type'] == 'loss')
        draws = total - wins - losses
        
        # By color
        white_games = [g for g in self.analyzed_games if g['color'] == 'white']
        black_games = [g for g in self.analyzed_games if g['color'] == 'black']
        
        white_wins = sum(1 for g in white_games if g['result_type'] == 'win')
        black_wins = sum(1 for g in black_games if g['result_type'] == 'win')
        
        # By time control
        time_control_stats = defaultdict(lambda: {'total': 0, 'wins': 0})
        for game in self.analyzed_games:
            tc = game['time_control']
            time_control_stats[tc]['total'] += 1
            if game['result_type'] == 'win':
                time_control_stats[tc]['wins'] += 1
        
        # Average ratings
        avg_player_rating = sum(g['player_rating'] for g in self.analyzed_games) / total
        avg_opponent_rating = sum(g['opponent_rating'] for g in self.analyzed_games) / total
        
        return {
            'total_games': total,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'white_games': len(white_games),
            'white_win_rate': (white_wins / len(white_games) * 100) if white_games else 0,
            'black_games': len(black_games),
            'black_win_rate': (black_wins / len(black_games) * 100) if black_games else 0,
            'avg_player_rating': avg_player_rating,
            'avg_opponent_rating': avg_opponent_rating,
            'time_control_stats': dict(time_control_stats)
        }
    
    def analyze_openings(self):
        """Analyze opening repertoire and performance"""
        opening_stats = defaultdict(lambda: {'total': 0, 'wins': 0, 'losses': 0, 'draws': 0})
        
        # By opening name
        for game in self.analyzed_games:
            opening = game['opening']
            result_key = game['result_type'] + 's'  # wins, losses, draws
            opening_stats[opening]['total'] += 1
            
            # Make sure the key exists before incrementing
            if result_key in opening_stats[opening]:
                opening_stats[opening][result_key] += 1
        
        # Convert to list and sort
        opening_list = []
        for opening, stats in opening_stats.items():
            if stats['total'] >= MIN_GAMES_FOR_PATTERN:
                win_rate = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
                opening_list.append({
                    'name': opening,
                    'games': stats['total'],
                    'wins': stats['wins'],
                    'losses': stats['losses'],
                    'draws': stats['draws'],
                    'win_rate': win_rate
                })
        
        opening_list.sort(key=lambda x: x['games'], reverse=True)
        
        # Best and worst openings
        if opening_list:
            best_opening = max(opening_list, key=lambda x: x['win_rate'])
            worst_opening = min(opening_list, key=lambda x: x['win_rate'])
        else:
            best_opening = worst_opening = None
        
        return {
            'repertoire': opening_list[:10],  # Top 10 most played
            'best_opening': best_opening,
            'worst_opening': worst_opening,
            'total_unique_openings': len(opening_stats)
        }
    
    def analyze_patterns(self):
        """Analyze winning and losing patterns"""
        win_patterns = {
            'termination': defaultdict(int),
            'game_length': [],
            'rating_diff': [],
            'piece_activity': defaultdict(list),
            'time_remaining': []
        }
        
        loss_patterns = {
            'termination': defaultdict(int),
            'game_length': [],
            'rating_diff': [],
            'piece_activity': defaultdict(list),
            'time_remaining': []
        }
        
        for game in self.analyzed_games:
            if game['result_type'] == 'win':
                patterns = win_patterns
            elif game['result_type'] == 'loss':
                patterns = loss_patterns
            else:
                continue
            
            patterns['termination'][game['termination']] += 1
            patterns['game_length'].append(game['total_moves'])
            patterns['rating_diff'].append(game['rating_diff'])
            
            # Piece activity
            for piece, count in game.get('piece_activity', {}).items():
                patterns['piece_activity'][piece].append(count)
            
            # Time remaining
            if 'final_time' in game:
                patterns['time_remaining'].append(game['final_time'])
        
        # Initialize insights dictionary
        insights = {}
        
        # Calculate win pattern averages
        if win_patterns['game_length']:
            avg_win_length = sum(win_patterns['game_length']) / len(win_patterns['game_length'])
            avg_win_rating_diff = sum(win_patterns['rating_diff']) / len(win_patterns['rating_diff'])
            
            # Calculate piece activity averages
            win_piece_avg = {}
            for piece, counts in win_patterns['piece_activity'].items():
                win_piece_avg[piece] = sum(counts) / len(counts) if counts else 0
            
            insights['wins'] = {
                'most_common_termination': max(win_patterns['termination'].items(), key=lambda x: x[1])[0] if win_patterns['termination'] else 'none',
                'avg_game_length': avg_win_length,
                'avg_rating_diff': avg_win_rating_diff,
                'termination_breakdown': dict(win_patterns['termination']),
                'avg_piece_activity': win_piece_avg,
                'avg_time_remaining': sum(win_patterns['time_remaining']) / len(win_patterns['time_remaining']) if win_patterns['time_remaining'] else 0
            }
            
        # Calculate loss pattern averages
        if loss_patterns['game_length']:
            avg_loss_length = sum(loss_patterns['game_length']) / len(loss_patterns['game_length'])
            avg_loss_rating_diff = sum(loss_patterns['rating_diff']) / len(loss_patterns['rating_diff'])
            
            # Calculate piece activity averages
            loss_piece_avg = {}
            for piece, counts in loss_patterns['piece_activity'].items():
                loss_piece_avg[piece] = sum(counts) / len(counts) if counts else 0
            
            insights['losses'] = {
                'most_common_termination': max(loss_patterns['termination'].items(), key=lambda x: x[1])[0] if loss_patterns['termination'] else 'none',
                'avg_game_length': avg_loss_length,
                'avg_rating_diff': avg_loss_rating_diff,
                'termination_breakdown': dict(loss_patterns['termination']),
                'avg_piece_activity': loss_piece_avg,
                'avg_time_remaining': sum(loss_patterns['time_remaining']) / len(loss_patterns['time_remaining']) if loss_patterns['time_remaining'] else 0
            }
        
        # Specific winning patterns
        wins = [g for g in self.analyzed_games if g['result_type'] == 'win']
        checkmate_wins = [g for g in wins if g['termination'] == 'checkmate']
        
        insights['checkmate_percentage'] = (len(checkmate_wins) / len(wins) * 100) if wins else 0
        
        return insights
    
    def analyze_game_phases(self):
        """Analyze performance by game phase"""
        phase_stats = {
            'opening': {'games': 0, 'wins': 0, 'losses': 0},
            'middlegame': {'games': 0, 'wins': 0, 'losses': 0},
            'endgame': {'games': 0, 'wins': 0, 'losses': 0}
        }
        
        # Games reaching each phase
        games_reaching_phase = {
            'opening': len(self.analyzed_games),
            'middlegame': 0,
            'endgame': 0
        }
        
        for game in self.analyzed_games:
            # Count games ending in each phase
            phase = game['end_phase']
            phase_stats[phase]['games'] += 1
            
            if game['result_type'] == 'win':
                phase_stats[phase]['wins'] += 1
            elif game['result_type'] == 'loss':
                phase_stats[phase]['losses'] += 1
            
            # Count games reaching each phase
            if game['total_moves'] > OPENING_PHASE_END:
                games_reaching_phase['middlegame'] += 1
            if game['total_moves'] > MIDDLEGAME_PHASE_END:
                games_reaching_phase['endgame'] += 1
        
        # Calculate win rates
        insights = {}
        for phase, stats in phase_stats.items():
            if stats['games'] > 0:
                win_rate = (stats['wins'] / stats['games'] * 100)
                loss_rate = (stats['losses'] / stats['games'] * 100)
            else:
                win_rate = loss_rate = 0
            
            insights[phase] = {
                'games_ended': stats['games'],
                'wins': stats['wins'],
                'losses': stats['losses'],
                'win_rate': win_rate,
                'loss_rate': loss_rate
            }
        
        # Conversion rates
        total = len(self.analyzed_games)
        insights['phase_reach_rates'] = {
            'middlegame': (games_reaching_phase['middlegame'] / total * 100) if total > 0 else 0,
            'endgame': (games_reaching_phase['endgame'] / total * 100) if total > 0 else 0
        }
        
        return insights
    
    def analyze_mistakes(self):
        """Analyze mistake patterns"""
        mistakes = {
            'quick_losses': [],
            'time_losses': [],
            'resignation_patterns': defaultdict(int),
            'blunder_indicators': []
        }
        
        for game in self.analyzed_games:
            if game['result_type'] == 'loss':
                # Quick losses
                if game['total_moves'] < QUICK_LOSS_MOVES:
                    mistakes['quick_losses'].append({
                        'moves': game['total_moves'],
                        'opening': game['opening'],
                        'phase': game['end_phase']
                    })
                
                # Time losses
                if game['termination'] == 'time':
                    mistakes['time_losses'].append({
                        'moves': game['total_moves'],
                        'time_control': game['time_control'],
                        'final_time': game.get('final_time', 0)
                    })
                
                # Resignation patterns
                if game['termination'] == 'resignation':
                    mistakes['resignation_patterns'][game['end_phase']] += 1
                
                # Potential blunders (games with very few moves by losing side)
                if game['total_moves'] < 30 and game.get('captures_made', 0) > 3:
                    mistakes['blunder_indicators'].append({
                        'moves': game['total_moves'],
                        'captures': game['captures_made']
                    })
        
        # Analysis
        total_losses = sum(1 for g in self.analyzed_games if g['result_type'] == 'loss')
        
        insights = {
            'quick_loss_rate': (len(mistakes['quick_losses']) / total_losses * 100) if total_losses > 0 else 0,
            'time_loss_rate': (len(mistakes['time_losses']) / total_losses * 100) if total_losses > 0 else 0,
            'quick_losses': mistakes['quick_losses'][:5],  # Top 5
            'resignation_by_phase': dict(mistakes['resignation_patterns']),
            'potential_blunder_games': len(mistakes['blunder_indicators'])
        }
        
        # Most problematic time control
        if mistakes['time_losses']:
            tc_counts = Counter(g['time_control'] for g in mistakes['time_losses'])
            insights['worst_time_control'] = tc_counts.most_common(1)[0][0]
        
        return insights
    
    def analyze_endgames(self):
        """Analyze endgame performance"""
        endgames = [g for g in self.analyzed_games if g['end_phase'] == 'endgame']
        
        if not endgames:
            return {'no_endgames': True}
        
        # Categorize endgames by piece count (simplified)
        endgame_types = {
            'pawn': [],  # Games with mostly pawns
            'rook': [],  # Games with rooks
            'minor': [],  # Games with knights/bishops
            'queen': []  # Games with queens
        }
        
        # Analyze each endgame
        for game in endgames:
            # Simplified categorization based on moves
            late_moves = ' '.join(game['moves'][-10:]) if len(game['moves']) >= 10 else ' '.join(game['moves'])
            
            if 'Q' in late_moves or 'q' in late_moves:
                endgame_types['queen'].append(game)
            elif 'R' in late_moves or 'r' in late_moves:
                endgame_types['rook'].append(game)
            elif 'N' in late_moves or 'B' in late_moves or 'n' in late_moves or 'b' in late_moves:
                endgame_types['minor'].append(game)
            else:
                endgame_types['pawn'].append(game)
        
        # Calculate performance by endgame type
        insights = {
            'total_endgames': len(endgames),
            'endgame_win_rate': sum(1 for g in endgames if g['result_type'] == 'win') / len(endgames) * 100
        }
        
        for eg_type, games in endgame_types.items():
            if games:
                wins = sum(1 for g in games if g['result_type'] == 'win')
                insights[f'{eg_type}_endgames'] = {
                    'count': len(games),
                    'win_rate': (wins / len(games) * 100) if games else 0
                }
        
        # Conversion rate when ahead
        ahead_endgames = [g for g in endgames if g['rating_diff'] < -50]  # Playing lower rated
        if ahead_endgames:
            conversion_rate = sum(1 for g in ahead_endgames if g['result_type'] == 'win') / len(ahead_endgames) * 100
            insights['conversion_rate_when_ahead'] = conversion_rate
        
        return insights
    
    def analyze_momentum(self):
        """Analyze psychological patterns and momentum"""
        # Sort games by date
        sorted_games = sorted(self.analyzed_games, key=lambda x: x['date'])
        
        # Streak analysis
        current_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        streaks = []
        
        for i, game in enumerate(sorted_games):
            if i == 0:
                current_streak = 1 if game['result_type'] == 'win' else -1
            else:
                prev_result = sorted_games[i-1]['result_type']
                curr_result = game['result_type']
                
                if curr_result == 'win':
                    if prev_result == 'win':
                        current_streak += 1
                    else:
                        streaks.append(current_streak)
                        current_streak = 1
                    max_win_streak = max(max_win_streak, current_streak)
                elif curr_result == 'loss':
                    if prev_result == 'loss':
                        current_streak -= 1
                    else:
                        streaks.append(current_streak)
                        current_streak = -1
                    max_loss_streak = max(max_loss_streak, abs(current_streak))
        
        # Performance after losses (tilt analysis)
        performance_after_loss = []
        for i in range(1, len(sorted_games)):
            if sorted_games[i-1]['result_type'] == 'loss':
                performance_after_loss.append(sorted_games[i]['result_type'])
        
        recovery_rate = (sum(1 for r in performance_after_loss if r == 'win') / len(performance_after_loss) * 100) if performance_after_loss else 0
        
        # Time of day analysis (if we have enough games)
        hour_performance = defaultdict(lambda: {'games': 0, 'wins': 0})
        for game in self.analyzed_games:
            hour = game['date'].hour
            hour_performance[hour]['games'] += 1
            if game['result_type'] == 'win':
                hour_performance[hour]['wins'] += 1
        
        # Find best hours
        best_hours = []
        for hour, stats in hour_performance.items():
            if stats['games'] >= 5:  # Minimum games
                win_rate = (stats['wins'] / stats['games'] * 100)
                best_hours.append((hour, win_rate, stats['games']))
        
        best_hours.sort(key=lambda x: x[1], reverse=True)
        
        # Session length analysis
        daily_games = defaultdict(list)
        for game in sorted_games:
            date_key = game['date'].date()
            daily_games[date_key].append(game)
        
        session_performance = []
        for date, games in daily_games.items():
            if len(games) >= 3:  # Meaningful session
                wins = sum(1 for g in games if g['result_type'] == 'win')
                win_rate = (wins / len(games) * 100)
                session_performance.append({
                    'games': len(games),
                    'win_rate': win_rate
                })
        
        # Optimal session length
        if session_performance:
            # Group by session length
            length_groups = defaultdict(list)
            for session in session_performance:
                if session['games'] <= 5:
                    length_groups['short'].append(session['win_rate'])
                elif session['games'] <= 10:
                    length_groups['medium'].append(session['win_rate'])
                else:
                    length_groups['long'].append(session['win_rate'])
            
            optimal_length = {}
            for length, rates in length_groups.items():
                if rates:
                    optimal_length[length] = sum(rates) / len(rates)
        else:
            optimal_length = {}
        
        return {
            'max_win_streak': max_win_streak,
            'max_loss_streak': max_loss_streak,
            'recovery_rate_after_loss': recovery_rate,
            'best_hours': best_hours[:3],  # Top 3 hours
            'optimal_session_length': optimal_length,
            'total_sessions': len(daily_games)
        }
    
    def generate_report(self, insights):
        """Generate comprehensive text report"""
        report = []
        
        # Header
        report.append("=" * REPORT_WIDTH)
        report.append(f"CHESS PERFORMANCE ANALYSIS REPORT".center(REPORT_WIDTH))
        report.append(f"Player: {self.username}".center(REPORT_WIDTH))
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}".center(REPORT_WIDTH))
        report.append("=" * REPORT_WIDTH)
        report.append("")
        
        # 1. Executive Summary
        basic = insights['basic_stats']
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 40)
        report.append(f"Games Analyzed: {basic['total_games']}")
        report.append(f"Overall Record: {basic['wins']}W - {basic['losses']}L - {basic['draws']}D")
        report.append(f"Win Rate: {basic['win_rate']:.1f}%")
        report.append(f"Average Rating: {basic['avg_player_rating']:.0f}")
        report.append(f"Average Opponent: {basic['avg_opponent_rating']:.0f}")
        report.append("")
        
        # 2. Performance by Color
        report.append("PERFORMANCE BY COLOR")
        report.append("-" * 40)
        report.append(f"As White: {basic['white_games']} games, {basic['white_win_rate']:.1f}% win rate")
        report.append(f"As Black: {basic['black_games']} games, {basic['black_win_rate']:.1f}% win rate")
        
        if abs(basic['white_win_rate'] - basic['black_win_rate']) > 10:
            if basic['white_win_rate'] > basic['black_win_rate']:
                report.append("⚠️  Significantly stronger as White - consider improving Black repertoire")
            else:
                report.append("✓ Strong Black repertoire - unusual and advantageous!")
        report.append("")
        
        # 3. Time Control Performance
        report.append("TIME CONTROL ANALYSIS")
        report.append("-" * 40)
        for tc, stats in basic['time_control_stats'].items():
            win_rate = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
            report.append(f"{tc.title()}: {stats['total']} games, {win_rate:.1f}% win rate")
        report.append("")
        
        # 4. Opening Analysis
        openings = insights['opening_analysis']
        report.append("OPENING REPERTOIRE")
        report.append("-" * 40)
        report.append(f"Unique Openings Played: {openings['total_unique_openings']}")
        report.append("")
        
        if openings['repertoire']:
            report.append("Most Played Openings:")
            for i, opening in enumerate(openings['repertoire'][:5], 1):
                report.append(f"{i}. {opening['name']}")
                report.append(f"   Games: {opening['games']} | Win Rate: {opening['win_rate']:.1f}%")
                report.append(f"   Record: {opening['wins']}W-{opening['losses']}L-{opening['draws']}D")
        
        if openings['best_opening'] and openings['best_opening']['games'] >= MIN_GAMES_FOR_PATTERN:
            report.append("")
            report.append(f"✓ Best Opening: {openings['best_opening']['name']} ({openings['best_opening']['win_rate']:.1f}% in {openings['best_opening']['games']} games)")
        
        if openings['worst_opening'] and openings['worst_opening']['games'] >= MIN_GAMES_FOR_PATTERN:
            report.append(f"✗ Worst Opening: {openings['worst_opening']['name']} ({openings['worst_opening']['win_rate']:.1f}% in {openings['worst_opening']['games']} games)")
        report.append("")
        
        # 5. Pattern Recognition
        patterns = insights['pattern_recognition']
        report.append("WINNING & LOSING PATTERNS")
        report.append("-" * 40)
        
        report.append("When You Win:")
        report.append(f"- Average game length: {patterns['wins']['avg_game_length']:.0f} moves")
        report.append(f"- Most common ending: {patterns['wins']['most_common_termination']}")
        report.append(f"- Average opponent rating difference: {patterns['wins']['avg_rating_diff']:+.0f}")
        report.append(f"- Checkmate percentage: {patterns['checkmate_percentage']:.1f}%")
        
        report.append("")
        report.append("When You Lose:")
        report.append(f"- Average game length: {patterns['losses']['avg_game_length']:.0f} moves")
        report.append(f"- Most common ending: {patterns['losses']['most_common_termination']}")
        report.append(f"- Average opponent rating difference: {patterns['losses']['avg_rating_diff']:+.0f}")
        
        # Piece activity insights
        if patterns['wins']['avg_piece_activity'] and patterns['losses']['avg_piece_activity']:
            report.append("")
            report.append("Piece Activity Patterns:")
            pieces = ['N', 'B', 'R', 'Q']
            for piece in pieces:
                win_activity = patterns['wins']['avg_piece_activity'].get(piece, 0)
                loss_activity = patterns['losses']['avg_piece_activity'].get(piece, 0)
                if win_activity > loss_activity * 1.2:
                    piece_name = {'N': 'Knight', 'B': 'Bishop', 'R': 'Rook', 'Q': 'Queen'}[piece]
                    report.append(f"✓ {piece_name} activity correlates with wins ({win_activity:.1f} vs {loss_activity:.1f} moves)")
        report.append("")
        
        # 6. Game Phase Analysis
        phases = insights['phase_performance']
        report.append("GAME PHASE PERFORMANCE")
        report.append("-" * 40)
        
        for phase in ['opening', 'middlegame', 'endgame']:
            if phase in phases:
                p = phases[phase]
                report.append(f"{phase.title()}:")
                report.append(f"  Games ending here: {p['games_ended']}")
                report.append(f"  Win rate: {p['win_rate']:.1f}%")
                report.append(f"  Loss rate: {p['loss_rate']:.1f}%")
        
        report.append("")
        report.append("Phase Progression:")
        report.append(f"- Reach middlegame: {phases['phase_reach_rates']['middlegame']:.1f}% of games")
        report.append(f"- Reach endgame: {phases['phase_reach_rates']['endgame']:.1f}% of games")
        
        # Identify phase weaknesses
        phase_issues = []
        for phase in ['opening', 'middlegame', 'endgame']:
            if phase in phases and phases[phase]['loss_rate'] > 40:
                phase_issues.append(phase)
        
        if phase_issues:
            report.append("")
            report.append(f"⚠️  High loss rate in: {', '.join(phase_issues)}")
        report.append("")
        
        # 7. Mistake Analysis
        mistakes = insights['mistake_patterns']
        report.append("MISTAKE PATTERNS")
        report.append("-" * 40)
        
        if mistakes['quick_loss_rate'] > 15:
            report.append(f"⚠️  Quick losses: {mistakes['quick_loss_rate']:.1f}% of losses are under {QUICK_LOSS_MOVES} moves")
            if mistakes['quick_losses']:
                report.append("   Recent quick losses:")
                for ql in mistakes['quick_losses'][:3]:
                    report.append(f"   - {ql['moves']} moves in {ql['opening']}")
        
        if mistakes['time_loss_rate'] > 10:
            report.append(f"⚠️  Time management: {mistakes['time_loss_rate']:.1f}% of losses are on time")
            if 'worst_time_control' in mistakes:
                report.append(f"   Worst in: {mistakes['worst_time_control']}")
        
        if mistakes['resignation_by_phase']:
            report.append("")
            report.append("Resignation patterns by phase:")
            for phase, count in mistakes['resignation_by_phase'].items():
                report.append(f"  {phase}: {count} resignations")
        report.append("")
        
        # 8. Endgame Analysis
        endgames = insights['endgame_proficiency']
        if not endgames.get('no_endgames'):
            report.append("ENDGAME PROFICIENCY")
            report.append("-" * 40)
            report.append(f"Total endgames reached: {endgames['total_endgames']}")
            report.append(f"Endgame win rate: {endgames['endgame_win_rate']:.1f}%")
            
            report.append("")
            report.append("Performance by endgame type:")
            for eg_type in ['pawn', 'rook', 'minor', 'queen']:
                key = f'{eg_type}_endgames'
                if key in endgames:
                    eg = endgames[key]
                    report.append(f"  {eg_type.title()}: {eg['count']} games, {eg['win_rate']:.1f}% win rate")
            
            if 'conversion_rate_when_ahead' in endgames:
                report.append("")
                report.append(f"Conversion rate vs lower-rated: {endgames['conversion_rate_when_ahead']:.1f}%")
                if endgames['conversion_rate_when_ahead'] < 70:
                    report.append("⚠️  Consider studying endgame technique")
            report.append("")
        
        # 9. Psychological Patterns
        momentum = insights['momentum_psychology']
        report.append("PSYCHOLOGICAL & MOMENTUM ANALYSIS")
        report.append("-" * 40)
        report.append(f"Maximum win streak: {momentum['max_win_streak']} games")
        report.append(f"Maximum loss streak: {momentum['max_loss_streak']} games")
        report.append(f"Recovery rate after losses: {momentum['recovery_rate_after_loss']:.1f}%")
        
        if momentum['recovery_rate_after_loss'] < 40:
            report.append("⚠️  Tilt tendency detected - take breaks after losses")
        elif momentum['recovery_rate_after_loss'] > 60:
            report.append("✓ Excellent mental resilience!")
        
        if momentum['best_hours']:
            report.append("")
            report.append("Best performance hours:")
            for hour, win_rate, games in momentum['best_hours']:
                report.append(f"  {hour}:00 - {win_rate:.1f}% win rate ({games} games)")
        
        if momentum['optimal_session_length']:
            report.append("")
            report.append("Session length analysis:")
            for length, win_rate in momentum['optimal_session_length'].items():
                report.append(f"  {length} sessions: {win_rate:.1f}% win rate")
        report.append("")
        
        # 10. Key Recommendations
        report.append("=" * REPORT_WIDTH)
        report.append("KEY RECOMMENDATIONS")
        report.append("=" * REPORT_WIDTH)
        
        recommendations = []
        
        # Color imbalance
        if abs(basic['white_win_rate'] - basic['black_win_rate']) > 15:
            weaker_color = 'Black' if basic['white_win_rate'] > basic['black_win_rate'] else 'White'
            recommendations.append(f"1. Focus on {weaker_color} repertoire - significant performance gap")
        
        # Opening issues
        if openings['worst_opening'] and openings['worst_opening']['win_rate'] < 35:
            recommendations.append(f"2. Study or replace {openings['worst_opening']['name']} - poor results")
        
        # Time management
        if mistakes['time_loss_rate'] > 15:
            recommendations.append("3. Practice time management - too many time losses")
        
        # Quick losses
        if mistakes['quick_loss_rate'] > 20:
            recommendations.append("4. Strengthen opening preparation - too many quick losses")
        
        # Endgame conversion
        if not endgames.get('no_endgames') and endgames.get('conversion_rate_when_ahead', 100) < 70:
            recommendations.append("5. Study endgame technique - low conversion rate")
        
        # Phase-specific
        weak_phases = []
        for phase in ['opening', 'middlegame', 'endgame']:
            if phase in phases and phases[phase]['loss_rate'] > 45:
                weak_phases.append(phase)
        if weak_phases:
            recommendations.append(f"6. Focus on {'/'.join(weak_phases)} - high loss rate in these phases")
        
        # Tilt management
        if momentum['recovery_rate_after_loss'] < 40:
            recommendations.append("7. Implement tilt management - performance drops after losses")
        
        # Session length
        if momentum['optimal_session_length']:
            best_length = max(momentum['optimal_session_length'].items(), key=lambda x: x[1])[0]
            recommendations.append(f"8. Prefer {best_length} playing sessions for optimal performance")
        
        for rec in recommendations[:5]:  # Top 5 recommendations
            report.append(rec)
        
        report.append("")
        report.append("=" * REPORT_WIDTH)
        report.append(f"Report based on {basic['total_games']} games".center(REPORT_WIDTH))
        report.append("Good luck in your chess improvement journey!".center(REPORT_WIDTH))
        report.append("=" * REPORT_WIDTH)
        
        return "\n".join(report)

def main():
    """Main entry point"""
    print("Chess.com Performance Analyzer")
    print("=" * 40)
    
    username = input("Enter Chess.com username: ").strip()
    if not username:
        print("Username required!")
        return
    
    try:
        num_games = int(input(f"Number of games to analyze (default {DEFAULT_NUM_GAMES}): ").strip() or DEFAULT_NUM_GAMES)
    except ValueError:
        num_games = DEFAULT_NUM_GAMES
    
    # Create analyzer
    analyzer = ChessAnalyzer(username)
    
    # Fetch games
    games = analyzer.fetch_games(num_games)
    if not games:
        print("No games found!")
        return
    
    # Analyze games
    analyzer.analyze_all_games()
    
    # Generate insights
    print("\nGenerating insights...")
    insights = analyzer.generate_insights()
    
    # Generate report
    print("Creating report...")
    report = analyzer.generate_report(insights)
    
    # Save report
    os.makedirs('output', exist_ok=True)
    filename = f"output/{username}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✓ Analysis complete! Report saved to: {filename}")
    print("\nReport Preview:")
    print("-" * 40)
    print(report[:500] + "...")

if __name__ == "__main__":
    main()

