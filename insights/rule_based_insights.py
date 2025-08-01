from .insight_generator import InsightGenerator

class RuleBasedInsights(InsightGenerator):
    """Rule-based insight generator using hardcoded logic"""
    
    def generate_priorities(self, metrics):
        """Generate top 3 priorities based on metrics"""
        priorities = []
        
        # Check black vs white performance gap
        color_perf = metrics.get('color_performance', {})
        white_win_rate = color_perf.get('white_win_rate', 0)
        black_win_rate = color_perf.get('black_win_rate', 0)
        black_white_gap = white_win_rate - black_win_rate
        
        if black_white_gap >= 15:
            priorities.append({
                'emoji': '⚫',
                'title': 'BLACK REPERTOIRE CRISIS',
                'stat': f"{black_win_rate:.0f}% win rate ({black_white_gap:.0f}% below White)",
                'action': "Study the French Defense or Caro-Kann for solid Black play"
            })
        
        # Check time management issues
        time_metrics = metrics.get('time_metrics', {})
        time_loss_rate = time_metrics.get('time_loss_percentage', 0)
        
        if time_loss_rate >= 25:
            priorities.append({
                'emoji': '⏱️',
                'title': 'TIME MANAGEMENT',
                'stat': f"{time_loss_rate:.0f}% of losses on time (2x typical rate)",
                'action': "Practice 10+0 time control before returning to bullet"
            })
        
        # Check opening preparation
        phase_metrics = metrics.get('phase_metrics', {})
        opening_stats = phase_metrics.get('phase_stats', {}).get('opening', {})
        opening_loss_rate = opening_stats.get('loss_rate', 0)
        
        if opening_loss_rate >= 50:
            priorities.append({
                'emoji': '📖',
                'title': 'OPENING PREPARATION',
                'stat': f"{opening_loss_rate:.0f}% loss rate in opening phase",
                'action': "Learn 5-10 moves deep in your main openings"
            })
        
        # Check middlegame tactics
        tactical_metrics = metrics.get('tactical_metrics', {})
        tactical_loss_rate = tactical_metrics.get('tactical_loss_rate', 0)
        
        if tactical_loss_rate >= 40 and len(priorities) < 3:
            priorities.append({
                'emoji': '🎯',
                'title': 'TACTICAL AWARENESS',
                'stat': f"{tactical_loss_rate:.0f}% of losses due to tactical errors",
                'action': "Do 15 minutes of tactical puzzles daily"
            })
        
        # Check endgame technique
        endgame_stats = phase_metrics.get('phase_stats', {}).get('endgame', {})
        endgame_win_rate = endgame_stats.get('win_rate', 0)
        
        if endgame_win_rate <= 60 and len(priorities) < 3:
            priorities.append({
                'emoji': '🏁',
                'title': 'ENDGAME TECHNIQUE',
                'stat': f"Only {endgame_win_rate:.0f}% winning position conversion",
                'action': "Study basic king and pawn endgames"
            })
        
        # Ensure we have exactly 3 priorities
        while len(priorities) < 3:
            current_rating = metrics.get('player_info', {}).get('current_rating', 700)
            priorities.append({
                'emoji': '🧩',
                'title': 'GENERAL IMPROVEMENT',
                'stat': f"{current_rating} current rating (room to grow)",
                'action': "Focus on basic principles and avoid blunders"
            })
        
        return priorities[:3]
    
    def generate_strengths(self, metrics):
        """Identify player strengths from metrics"""
        strengths = []
        
        # Check endgame strength
        phase_metrics = metrics.get('phase_metrics', {})
        endgame_stats = phase_metrics.get('phase_stats', {}).get('endgame', {})
        endgame_win_rate = endgame_stats.get('win_rate', 0)
        
        basic_stats = metrics.get('basic_stats', {})
        overall_win_rate = basic_stats.get('win_rate', 0)
        
        if endgame_win_rate > overall_win_rate + 10:
            strengths.append("Endgame Technique: Significantly above your rating level")
        
        # Check psychological resilience
        psych_metrics = metrics.get('psychological_metrics', {})
        recovery_rate = psych_metrics.get('recovery_rate', 0)
        
        if recovery_rate > 60:
            strengths.append("Psychological Resilience: Excellent recovery from losses")
        
        # Check tactical patterns
        tactical_metrics = metrics.get('tactical_metrics', {})
        winning_patterns = tactical_metrics.get('winning_patterns', [])
        
        if winning_patterns:
            top_pattern = winning_patterns[0]['name']
            strengths.append(f"{top_pattern}: You spot these well!")
        
        # Check trading skill
        exchange_metrics = metrics.get('piece_exchange_metrics', {})
        trade_when_ahead = exchange_metrics.get('trade_frequency_when_ahead', 0)
        
        if trade_when_ahead >= 75:
            strengths.append("Trading When Ahead: Excellent simplification instincts")
        
        # Ensure we have at least 4 strengths
        default_strengths = [
            "Consistent play across time controls",
            "Patience in complex positions",
            "Quick pattern recognition",
            "Solid opening knowledge"
        ]
        
        while len(strengths) < 4:
            if default_strengths:
                strengths.append(default_strengths.pop(0))
        
        return strengths[:4]
    
    def generate_recommendations(self, metrics):
        """Generate personalized recommendations"""
        recommendations = []
        
        # Based on priorities
        priorities = self.generate_priorities(metrics)
        for priority in priorities:
            recommendations.append(priority['action'])
        
        # Additional recommendations based on patterns
        psych_metrics = metrics.get('psychological_metrics', {})
        if psych_metrics.get('max_loss_streak', 0) >= 5:
            recommendations.append("Take breaks after 2 consecutive losses to avoid tilt")
        
        time_metrics = metrics.get('time_metrics', {})
        if time_metrics.get('time_pressure_pct', 0) > 50:
            recommendations.append("Pre-move in obvious positions to save time")
        
        return recommendations
    
    def generate_patterns(self, metrics):
        """Identify various patterns in play"""
        patterns = {}
        
        # Win/loss patterns
        pattern_metrics = metrics.get('pattern_metrics', {})
        win_patterns = pattern_metrics.get('win_patterns', {})
        loss_patterns = pattern_metrics.get('loss_patterns', {})
        
        patterns['winning_conditions'] = {
            'most_common_termination': self._get_most_common(win_patterns.get('termination', {})),
            'avg_game_length': sum(win_patterns.get('game_length', [])) / len(win_patterns.get('game_length', [])) if win_patterns.get('game_length') else 0
        }
        
        patterns['losing_conditions'] = {
            'most_common_termination': self._get_most_common(loss_patterns.get('termination', {})),
            'avg_game_length': sum(loss_patterns.get('game_length', [])) / len(loss_patterns.get('game_length', [])) if loss_patterns.get('game_length') else 0
        }
        
        return patterns
    
    def generate_projections(self, metrics):
        """Project future performance improvements"""
        current_rating = metrics.get('player_info', {}).get('current_rating', 700)
        
        # Calculate potential improvements
        improvements = []
        
        # Black repertoire improvement
        color_perf = metrics.get('color_performance', {})
        black_win_rate = color_perf.get('black_win_rate', 0)
        if black_win_rate < 45:
            improvements.append({
                'area': 'Black win rate',
                'current': black_win_rate,
                'target': 45,
                'expected_rating_gain': {'min': 3.5, 'max': 3.5, 'unit': '%'}
            })
        
        # Time management improvement
        time_metrics = metrics.get('time_metrics', {})
        time_loss_rate = time_metrics.get('time_loss_percentage', 0)
        if time_loss_rate > 30:
            improvements.append({
                'area': 'Time losses',
                'current': time_loss_rate,
                'target': 30,
                'expected_rating_gain': {'min': 30, 'max': 40, 'unit': 'points'}
            })
        
        # Opening improvement
        phase_metrics = metrics.get('phase_metrics', {})
        opening_loss_rate = phase_metrics.get('phase_stats', {}).get('opening', {}).get('loss_rate', 0)
        if opening_loss_rate > 45:
            improvements.append({
                'area': 'Opening losses',
                'current': opening_loss_rate,
                'target': 45,
                'expected_rating_gain': {'min': 20, 'max': 25, 'unit': 'points'}
            })
        
        # Calculate projections
        total_gain_min = sum(imp['expected_rating_gain']['min'] for imp in improvements if imp['expected_rating_gain']['unit'] == 'points')
        total_gain_max = sum(imp['expected_rating_gain']['max'] for imp in improvements if imp['expected_rating_gain']['unit'] == 'points')
        
        return {
            'target_improvements': improvements[:3],
            'combined_projections': {
                '30_day': {'min': current_rating + total_gain_min // 2, 'max': current_rating + total_gain_max // 2},
                '90_day': {'min': current_rating + total_gain_min, 'max': current_rating + total_gain_max}
            }
        }
    
    def _get_most_common(self, count_dict):
        """Get most common item from a count dictionary"""
        if not count_dict:
            return 'none'
        return max(count_dict.items(), key=lambda x: x[1])[0]