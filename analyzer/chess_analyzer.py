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
    
    def analyze(self, num_games=100, days=30, progress_callbacks=None):
        """Run complete analysis with progress reporting"""
        # Initialize default callbacks if not provided
        if progress_callbacks is None:
            progress_callbacks = {
                'fetch': lambda x, y: None,
                'analyze': lambda x, y: None,
                'insights': lambda x, y: None
            }
        
        # Step 1: Fetch data
        games_json = self.data_fetcher.fetch_games(
            self.username, num_games, days, 
            progress_callbacks.get('fetch')
        )
        stats_data = self.data_fetcher.fetch_player_stats(self.username)
        
        if not games_json:
            return None, None
        
        # Step 2: Parse games and calculate metrics
        parsed_games = []
        total_games = len(games_json)
        
        for i, game in enumerate(games_json):
            try:
                parsed = self.game_parser.parse_game(game, self.username)
                parsed_games.append(parsed)
                
                # Update progress
                if progress_callbacks.get('analyze'):
                    progress_callbacks['analyze'](i + 1, total_games)
                    
            except Exception as e:
                continue
        
        # Step 3: Calculate metrics
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
        
        # Step 4: Generate insights with progress reporting
        insights = {}
        insight_types = ['priorities', 'strengths', 'recommendations', 'patterns', 'projections']
        total_insights = len(insight_types)
        
        for i, insight_type in enumerate(insight_types):
            if insight_type == 'priorities':
                insights['priorities'] = self.insight_generator.generate_priorities(metrics)
            elif insight_type == 'strengths':
                insights['strengths'] = self.insight_generator.generate_strengths(metrics)
            elif insight_type == 'recommendations':
                insights['recommendations'] = self.insight_generator.generate_recommendations(metrics)
            elif insight_type == 'patterns':
                insights['patterns'] = self.insight_generator.generate_patterns(metrics)
            elif insight_type == 'projections':
                insights['projections'] = self.insight_generator.generate_projections(metrics)
                
            # Update progress
            if progress_callbacks.get('insights'):
                progress_callbacks['insights'](i + 1, total_insights)
        
        return metrics, insights
    
    def _get_rating_level(self, rating):
        """Determine rating level based on rating"""
        for threshold, level in sorted(RATING_LEVELS.items()):
            if rating >= threshold:
                rating_level = level
        return rating_level