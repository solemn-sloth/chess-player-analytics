import requests
from datetime import datetime, timedelta
from config import USER_AGENT

class DataFetcher:
    """Handles all Chess.com API interactions"""
    
    def __init__(self):
        self.headers = {'User-Agent': USER_AGENT}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_games(self, username, num_games=100, days=30, progress_callback=None):
        """Fetch games from Chess.com API with option to limit by time period"""
        # Get archives
        archives = self._get_archives(username)
        if not archives:
            return []
        
        games = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Fetch games from recent archives
        for archive_url in reversed(archives):
            if len(games) >= num_games:
                break
            
            month_games = self._fetch_month_games(archive_url)
            
            # Filter by date if needed
            if days > 0 and month_games:
                filtered_games = []
                for game in month_games:
                    game_date = datetime.fromtimestamp(game.get('end_time', 0))
                    if game_date >= cutoff_date:
                        filtered_games.append(game)
                month_games = filtered_games
            
            games.extend(month_games)
            
            # Update progress if callback provided
            if progress_callback and num_games > 0:
                progress = min(len(games), num_games)
                progress_callback(progress, num_games)
        
        return games[:num_games]
    
    def fetch_player_stats(self, username):
        """Fetch player statistics from Chess.com API"""
        
        response = self.session.get(f"https://api.chess.com/pub/player/{username}/stats")
        if response.status_code != 200:
            print(f"Error: Could not fetch player stats (Status: {response.status_code})")
            return {}
        
        stats = response.json()
        
        # Extract current rating
        rating = 0
        if 'chess_rapid' in stats:
            rating = stats['chess_rapid'].get('last', {}).get('rating', 0)
        elif 'chess_blitz' in stats:
            rating = stats['chess_blitz'].get('last', {}).get('rating', 0)
        elif 'chess_bullet' in stats:
            rating = stats['chess_bullet'].get('last', {}).get('rating', 0)
        
        return {
            'rating': rating,
            'stats': stats
        }
    
    def _get_archives(self, username):
        """Get list of game archives for a player"""
        response = self.session.get(f"https://api.chess.com/pub/player/{username}/games/archives")
        if response.status_code != 200:
            print(f"Error: Could not fetch game archives (Status: {response.status_code})")
            return []
        
        return response.json().get('archives', [])
    
    def _fetch_month_games(self, archive_url):
        """Fetch games from a specific month archive"""
        response = self.session.get(archive_url)
        if response.status_code == 200:
            return response.json().get('games', [])
        return []