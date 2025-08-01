from .data_fetcher import DataFetcher
from .game_parser import GameParser
from .metrics_calculator import MetricsCalculator
from insights.rule_based_insights import RuleBasedInsights
from config import RATING_LEVELS

class ChessAnalyzer:
    """Main analyzer that orchestrates the analysis process"""
    
    def __init__(self, username, insight_generator=None):
        self.username = username
        self.data_fetcher = DataFetcher()
        self.game_parser = GameParser()
        self.metrics_calculator = MetricsCalculator()
        
        # Default to rule-based insights
        if insight_generator is None:
            self.insight_generator = RuleBasedInsights()
        else:
            self.insight_generator = insight_generator
    
    def analyze(self, num_games=100, days=30):
        """Run complete analysis"""
        
        # Step 1: Fetch data
        print(f"Fetching games for {self.username}...")
        games_json = self.data_fetcher.fetch_games(self.username, num_games, days)
        stats_data = self.data_fetcher.fetch_player_stats(self.username)
        
        if not games_json:
            print("No games found!")
            return None, None
        
        # Step 2: Parse games
        print("Parsing games...")
        parsed_games = []
        for i, game in enumerate(games_json):
            if i % 20 == 0:
                print(f"Parsed {i}/{len(games_json)} games...")
            
            try:
                parsed = self.game_parser.parse_game(game, self.username)
                parsed_games.append(parsed)
            except Exception as e:
                print(f"Error parsing game: {e}")
                continue
        
        print(f"Successfully parsed {len(parsed_games)} games")
        
        # Step 3: Calculate metrics
        print("Calculating metrics...")
        metrics = self.metrics_calculator.calculate_all_metrics(parsed_games)
        
        # Add player info to metrics
        current_rating = stats_data.get('rating', 0)
        metrics['player_info'] = {
            'username': self.username,
            'current_rating': current_rating,
            'rating_level': self._get_rating_level(current_rating)
        }
        
        # Add username to basic stats for report
        metrics['basic_stats']['username'] = self.username
        metrics['basic_stats']['current_rating'] = current_rating
        metrics['basic_stats']['rating_level'] = self._get_rating_level(current_rating)
        
        # Step 4: Generate insights
        print("Generating insights...")
        insights = {
            'priorities': self.insight_generator.generate_priorities(metrics),
            'strengths': self.insight_generator.generate_strengths(metrics),
            'recommendations': self.insight_generator.generate_recommendations(metrics),
            'patterns': self.insight_generator.generate_patterns(metrics),
            'projections': self.insight_generator.generate_projections(metrics)
        }
        
        return metrics, insights
    
    def _get_rating_level(self, rating):
        """Determine rating level based on rating"""
        for threshold, level in sorted(RATING_LEVELS.items()):
            if rating >= threshold:
                rating_level = level
        return rating_level