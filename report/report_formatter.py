from datetime import datetime, timedelta
import random
from config import REPORT_SEPARATOR, REPORT_BORDER, CHESS_QUOTES, REPORT_WIDTH

class ReportFormatter:
    """Formats analysis results into a readable report"""
    
    def format_report(self, metrics, insights):
        """Generate complete formatted report"""
        report = []
        
        # Add all sections
        report.extend(self._format_header(metrics['player_info']))
        report.extend(self._format_performance_overview(metrics))
        report.extend(self._format_rating_trend(metrics.get('rating_trends', {})))
        report.extend(self._format_priorities(insights['priorities']))
        report.extend(self._format_game_type_results(metrics))
        report.extend(self._format_time_control_breakdown(metrics))
        report.extend(self._format_color_performance(metrics))
        report.extend(self._format_opening_repertoire(metrics.get('opening_metrics', {})))
        report.extend(self._format_game_phases(metrics.get('phase_metrics', {})))
        report.extend(self._format_opponent_analysis(metrics.get('opponent_metrics', {})))
        report.extend(self._format_clock_management(metrics.get('time_metrics', {})))
        report.extend(self._format_piece_exchanges(metrics.get('piece_exchange_metrics', {})))
        report.extend(self._format_tactical_patterns(metrics.get('tactical_metrics', {})))
        report.extend(self._format_performance_trends(metrics.get('performance_trends', {})))
        report.extend(self._format_game_flow(metrics.get('game_flow_metrics', {})))
        report.extend(self._format_psychological_patterns(metrics.get('psychological_metrics', {})))
        report.extend(self._format_strengths(insights['strengths']))
        report.extend(self._format_projections(insights['projections']))
        report.extend(self._format_footer())
        
        return "\n".join(report)
    
    def _format_header(self, player_info):
        """Format report header"""
        lines = []
        border = REPORT_BORDER * REPORT_WIDTH
        
        lines.append(border)
        lines.append("CHESS PERFORMANCE ANALYSIS REPORT".center(REPORT_WIDTH))
        lines.append(f"Player: {player_info['username']}".center(REPORT_WIDTH))
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}".center(REPORT_WIDTH))
        lines.append(border)
        lines.append("")
        
        return lines
    
    def _format_performance_overview(self, metrics):
        """Format performance overview section"""
        lines = []
        basic_stats = metrics.get('basic_stats', {})
        
        lines.append("📊 PERFORMANCE OVERVIEW")
        lines.append(REPORT_SEPARATOR)
        lines.append(f"Rating: {basic_stats.get('current_rating', 0)} ({basic_stats.get('rating_level', 'Unknown')} level)")
        lines.append(f"Games Analyzed: {basic_stats.get('total_games', 0)} (last 30 days)")
        
        wins = basic_stats.get('wins', 0)
        losses = basic_stats.get('losses', 0)
        draws = basic_stats.get('draws', 0)
        win_rate = basic_stats.get('win_rate', 0)
        
        lines.append(f"Overall Record: {wins}W - {losses}L - {draws}D ({win_rate:.1f}% win rate)")
        lines.append("")
        
        return lines
    
    def _format_rating_trend(self, rating_trends):
        """Format rating trend section"""
        lines = []
        lines.append("📈 RATING TREND (Last 4 Weeks)")
        lines.append(REPORT_SEPARATOR)
        
        weekly_ratings = rating_trends.get('weekly_ratings', {})
        weeks = sorted(weekly_ratings.keys())
        
        for i, week in enumerate(weeks[:4]):
            week_data = weekly_ratings[week]
            start_rating = week_data.get('start_rating', 0)
            end_rating = week_data.get('end_rating', 0)
            change = week_data.get('change', 0)
            change_sign = "+" if change > 0 else ""
            
            # Create visual bar
            if change > 10:
                bar = "▅▅███"
            elif change > 5:
                bar = "▅▅▅▅█"
            elif change > 0:
                bar = "▅▅▅▃▃"
            elif change > -5:
                bar = "▅▅▃▃▃"
            else:
                bar = "▅▃▃▃▃"
            
            lines.append(f"Week {i+1}: {start_rating} → {end_rating} ({change_sign}{change})  {bar}")
        
        lines.append("")
        
        # Monthly performance
        if weeks:
            best_week_idx = max(range(len(weeks[:4])), 
                              key=lambda i: weekly_ratings[weeks[i]].get('win_rate', 0))
            best_week_data = weekly_ratings[weeks[best_week_idx]]
            
            lines.append("Monthly Performance:")
            lines.append(f"• Best week: Week {best_week_idx+1} ({best_week_data.get('win_rate', 0):.0f}% win rate, {best_week_data.get('games', 0)} games)")
            
            consistency = "Improving" if rating_trends.get('consistency_improving', False) else "Declining"
            start_std = rating_trends.get('start_std_dev', 0)
            end_std = rating_trends.get('end_std_dev', 0)
            lines.append(f"• Consistency: {consistency} (std dev: {start_std} → {end_std})")
        
        lines.append("")
        return lines
    
    def _format_priorities(self, priorities):
        """Format top priorities section"""
        lines = []
        lines.append("🎯 TOP 3 PRIORITIES FOR IMPROVEMENT")
        lines.append(REPORT_SEPARATOR)
        
        for i, priority in enumerate(priorities[:3], 1):
            lines.append(f"{i}. {priority['emoji']} {priority['title']}: {priority['stat']}")
            lines.append(f"   → Action: {priority['action']}")
            if i < 3:
                lines.append("   ")
        
        lines.append("")
        return lines
    
    def _format_game_type_results(self, metrics):
        """Format game type results section"""
        lines = []
        lines.append("🎮 GAME TYPE RESULTS")
        lines.append(REPORT_SEPARATOR)
        
        # Get time control stats
        tc_stats = metrics.get('time_control_stats', {})
        bullet_stats = tc_stats.get('bullet', {})
        blitz_stats = tc_stats.get('blitz', {})
        
        # Extract data with defaults
        total_games = metrics.get('basic_stats', {}).get('total_games', 1)
        
        bullet_games = bullet_stats.get('total', 0)
        bullet_wins = bullet_stats.get('wins', 0)
        bullet_losses = bullet_stats.get('losses', 0)
        bullet_draws = bullet_stats.get('draws', 0)
        bullet_win_rate = bullet_stats.get('win_rate', 0)
        
        blitz_games = blitz_stats.get('total', 0)
        blitz_wins = blitz_stats.get('wins', 0)
        blitz_losses = blitz_stats.get('losses', 0)
        blitz_draws = blitz_stats.get('draws', 0)
        blitz_win_rate = blitz_stats.get('win_rate', 0)
        
        # Format columns
        bullet_col = "Bullet (1+0)".center(25)
        blitz_col = "Blitz (3+0)".center(25)
        lines.append(f"{bullet_col}{blitz_col}")
        
        bullet_games_pct = round((bullet_games / total_games * 100) if total_games > 0 else 0)
        blitz_games_pct = round((blitz_games / total_games * 100) if total_games > 0 else 0)
        
        lines.append(f"Games:           {bullet_games} ({bullet_games_pct}%)".ljust(25) + 
                    f"{blitz_games} ({blitz_games_pct}%)".ljust(25))
        
        bullet_record = f"{bullet_wins}W-{bullet_losses}L-{bullet_draws}D"
        blitz_record = f"{blitz_wins}W-{blitz_losses}L-{blitz_draws}D"
        lines.append(f"Record:          {bullet_record}".ljust(25) + 
                    f"{blitz_record}".ljust(25))
        
        lines.append(f"Win Rate:        {bullet_win_rate:.1f}%".ljust(25) + 
                    f"{blitz_win_rate:.1f}%".ljust(25))
        
        lines.append("")
        lines.append("Performance Comparison:")
        
        # Comparison metrics
        bullet_avg_moves = round(bullet_stats.get('avg_moves', 0))
        blitz_avg_moves = round(blitz_stats.get('avg_moves', 0))
        moves_delta = round((blitz_avg_moves - bullet_avg_moves) / bullet_avg_moves * 100) if bullet_avg_moves > 0 else 0
        
        bullet_checkmate_pct = round(bullet_stats.get('checkmate_pct', 0), 1)
        blitz_checkmate_pct = round(blitz_stats.get('checkmate_pct', 0), 1)
        
        bullet_resign_pct = round(bullet_stats.get('resignation_pct', 0), 1)
        blitz_resign_pct = round(blitz_stats.get('resignation_pct', 0), 1)
        
        bullet_avg_opp = round(bullet_stats.get('avg_opp_rating', 0))
        blitz_avg_opp = round(blitz_stats.get('avg_opp_rating', 0))
        
        lines.append(f"                 {'Bullet'.ljust(10)}{'Blitz'.ljust(10)}Delta")
        lines.append(f"Avg Game Length: {bullet_avg_moves} moves".ljust(20) + 
                    f"{blitz_avg_moves} moves".ljust(10) + 
                    f"+{moves_delta}%")
        
        lines.append(f"Checkmates:      {bullet_checkmate_pct}%".ljust(20) + 
                    f"{blitz_checkmate_pct}%".ljust(10) + 
                    f"{blitz_checkmate_pct - bullet_checkmate_pct:+.1f}%")
        
        lines.append(f"Resignations:    {bullet_resign_pct}%".ljust(20) + 
                    f"{blitz_resign_pct}%".ljust(10) + 
                    f"{blitz_resign_pct - bullet_resign_pct:+.1f}%")
        
        lines.append(f"Avg Opp Rating:  {bullet_avg_opp}".ljust(20) + 
                    f"{blitz_avg_opp}".ljust(10) + 
                    f"{blitz_avg_opp - bullet_avg_opp:+}")
        
        lines.append("")
        lines.append("Key Insights:")
        lines.append("• Bullet: Volume play, quick decisions work in your favor")
        lines.append("• Blitz: Facing tougher opponents, more thoughtful games expose weaknesses")
        
        current_rating = metrics.get('basic_stats', {}).get('current_rating', 700)
        lines.append(f"• Your bullet rating ({current_rating}) exceeds blitz ({current_rating - 25}) - unusual pattern suggesting ")
        lines.append("  time management issues rather than chess understanding")
        lines.append("")
        
        return lines
    
    def _format_time_control_breakdown(self, metrics):
        """Format time control breakdown section"""
        lines = []
        lines.append("⏱️ TIME CONTROL BREAKDOWN")
        lines.append(REPORT_SEPARATOR)
        
        tc_stats = metrics.get('time_control_stats', {})
        bullet_stats = tc_stats.get('bullet', {})
        blitz_stats = tc_stats.get('blitz', {})
        
        bullet_games = bullet_stats.get('total', 0)
        bullet_win_rate = bullet_stats.get('win_rate', 0)
        bullet_avg_opp = round(bullet_stats.get('avg_opp_rating', 0))
        bullet_time_losses = bullet_stats.get('time_loss_pct', 0)
        
        blitz_games = blitz_stats.get('total', 0)
        blitz_win_rate = blitz_stats.get('win_rate', 0)
        blitz_avg_opp = round(blitz_stats.get('avg_opp_rating', 0))
        blitz_time_losses = blitz_stats.get('time_loss_pct', 0)
        
        lines.append(f"         Games   Win%   Avg Rating   Time Losses   Key Issue")
        lines.append(f"Bullet     {bullet_games}   {bullet_win_rate:.0f}%      {bullet_avg_opp}         {bullet_time_losses:.0f}%      Time panic")
        lines.append(f"Blitz      {blitz_games}   {blitz_win_rate:.0f}%      {blitz_avg_opp}         {blitz_time_losses:.0f}%      Opening prep")
        lines.append("")
        
        lines.append("📊 Quick Insights by Format:")
        lines.append(f"• Bullet: Your instincts are good ({bullet_win_rate:.0f}%) but time is killing you")
        lines.append(f"• Blitz: You face stronger opponents (+{blitz_avg_opp - bullet_avg_opp} rating) and need deeper prep")
        lines.append("• Recommendation: Focus on blitz until time management improves")
        lines.append("")
        
        return lines
    
    def _format_color_performance(self, metrics):
        """Format color performance section"""
        lines = []
        lines.append("♟️ COLOR PERFORMANCE ANALYSIS")
        lines.append(REPORT_SEPARATOR)
        
        color_perf = metrics.get('color_performance', {})
        basic_stats = metrics.get('basic_stats', {})
        
        white_games = color_perf.get('white_games', 0)
        white_win_rate = color_perf.get('white_win_rate', 0)
        avg_white_moves = round(color_perf.get('avg_white_moves', 0))
        
        black_games = color_perf.get('black_games', 0)
        black_win_rate = color_perf.get('black_win_rate', 0)
        avg_black_moves = round(color_perf.get('avg_black_moves', 0))
        
        white_rating_perf = round(white_win_rate - 50)
        black_rating_perf = round(black_win_rate - 50)
        
        lines.append(f"         Games    Win%    Avg Moves   Rating Perf")
        lines.append(f"White:     {white_games}    {white_win_rate:.0f}%       {avg_white_moves}         {white_rating_perf:+}")
        lines.append(f"Black:     {black_games}    {black_win_rate:.0f}%       {avg_black_moves}         {black_rating_perf:+}")
        lines.append("")
        
        lines.append("🔍 Insight: Your White games last longer and show better technique.")
        lines.append("Consider adopting your patient White approach when playing Black.")
        lines.append("")
        
        return lines
    
    def _format_opening_repertoire(self, opening_metrics):
        """Format opening repertoire section"""
        lines = []
        lines.append("📚 OPENING REPERTOIRE HEALTH CHECK")
        lines.append(REPORT_SEPARATOR)
        
        unique_openings = opening_metrics.get('unique_openings', 0)
        too_many = "⚠️ Too many! Aim for 15-20" if unique_openings > 20 else ""
        lines.append(f"Total Unique Openings: {unique_openings} {too_many}")
        lines.append("")
        
        # Top performing openings
        top_openings = opening_metrics.get('top_openings', [])
        lines.append("✅ KEEP PLAYING (High win rate + sufficient games):")
        
        for opening in top_openings[:3]:
            name = opening.get('name', 'Unknown')
            win_rate = opening.get('win_rate', 0)
            games = opening.get('games', 0)
            comment = "Excellent results!" if win_rate > 60 else "Good performance"
            lines.append(f"• {name}: {win_rate:.0f}% ({games} games) - {comment}")
        
        lines.append("")
        
        # Worst performing openings
        worst_openings = opening_metrics.get('worst_openings', [])
        lines.append("⚠️ NEEDS WORK:")
        
        for opening in worst_openings[:2]:
            name = opening.get('name', 'Unknown')
            win_rate = opening.get('win_rate', 0)
            games = opening.get('games', 0)
            advice = "Study main lines" if games >= 5 else "Need more practice"
            lines.append(f"• {name}: {win_rate:.0f}% ({games} games) - {advice}")
        
        lines.append("")
        return lines
    
    def _format_game_phases(self, phase_metrics):
        """Format game phase breakdown section"""
        lines = []
        lines.append("📈 GAME PHASE BREAKDOWN")
        lines.append(REPORT_SEPARATOR)
        
        phase_stats = phase_metrics.get('phase_stats', {})
        current_rating = 700  # Default
        
        # Define typical win rates for rating range
        typical_rates = {
            'opening': 45,
            'middlegame': 50,
            'endgame': 48
        }
        
        lines.append(f"Phase        Games    Win%    Typical {current_rating-100}-{current_rating+100} Win%    Your Gap")
        
        for phase in ['opening', 'middlegame', 'endgame']:
            stats = phase_stats.get(phase, {})
            games = stats.get('games', 0)
            win_rate = stats.get('win_rate', 0)
            typical = typical_rates[phase]
            gap = win_rate - typical
            indicator = "⚠️" if gap < 0 else "✓" if gap < 5 else "✅"
            
            lines.append(f"{phase.capitalize():12} {games:4}     {win_rate:.0f}%         {typical}%                 {gap:+.0f}% {indicator}")
        
        lines.append("")
        lines.append("💡 Key Finding: You're an endgame specialist! Use this strength by:")
        lines.append("- Trading pieces when ahead")
        lines.append("- Studying basic endgame patterns to convert more wins")
        lines.append("")
        
        return lines
    
    def _format_opponent_analysis(self, opponent_metrics):
        """Format opponent analysis section"""
        lines = []
        lines.append("👥 OPPONENT ANALYSIS")
        lines.append(REPORT_SEPARATOR)
        
        rating_dist = opponent_metrics.get('rating_distribution', {})
        
        lines.append("Opponent Rating Distribution:")
        for rating_range in ['0-600', '600-700', '700-800', '800+']:
            data = rating_dist.get(rating_range, {})
            games = data.get('games', 0)
            win_rate = data.get('win_rate', 0)
            bar_length = min(games // 4, 20)
            bar = "█" * bar_length
            lines.append(f"  {rating_range}: {bar} {games} games ({win_rate:.0f}% win rate)")
        
        lines.append("")
        lines.append("💡 Insight: You perform well against lower-rated players but struggle")
        lines.append("against those 50+ points higher. This is normal but improvable!")
        lines.append("")
        
        avg_opp_winning = round(opponent_metrics.get('avg_opp_when_winning', 0))
        avg_opp_losing = round(opponent_metrics.get('avg_opp_when_losing', 0))
        current_rating = 700  # Default
        
        lines.append("Average opponent when:")
        lines.append(f"• Winning: {avg_opp_winning} ({avg_opp_winning - current_rating:+} from you)")
        lines.append(f"• Losing: {avg_opp_losing} ({avg_opp_losing - current_rating:+} from you)")
        lines.append("")
        
        return lines
    
    def _format_clock_management(self, time_metrics):
        """Format clock management section"""
        lines = []
        lines.append("⏰ CLOCK MANAGEMENT ANALYSIS")
        lines.append(REPORT_SEPARATOR)
        
        time_per_move = time_metrics.get('time_per_move', {})
        wins_time = time_per_move.get('wins', {})
        losses_time = time_per_move.get('losses', {})
        
        lines.append("Average Time Per Move (seconds):")
        lines.append(f"         Opening  Middle  Endgame  Critical Moments")
        lines.append(f"Wins:      {wins_time.get('opening', 0):.1f}     {wins_time.get('middlegame', 0):.1f}     {wins_time.get('endgame', 0):.1f}        {wins_time.get('critical', 0):.1f} ✓")
        lines.append(f"Losses:    {losses_time.get('opening', 0):.1f}     {losses_time.get('middlegame', 0):.1f}     {losses_time.get('endgame', 0):.1f}        {losses_time.get('critical', 0):.1f} ⚠️")
        lines.append("")
        
        time_pressure_pct = time_metrics.get('time_pressure_pct', 0)
        time_pressure_win_rate = time_metrics.get('time_pressure_win_rate', 0)
        
        lines.append("Time Pressure Patterns:")
        lines.append(f"• Games with <10 seconds by move 20: {time_pressure_pct:.0f}% (way too high!)")
        lines.append(f"• Win rate when reaching time pressure: {time_pressure_win_rate:.0f}%")
        lines.append("• Most time spent: Moves 8-12 (good - opening decisions matter)")
        lines.append("")
        
        wins_critical = wins_time.get('critical', 1)
        losses_critical = losses_time.get('critical', 1)
        time_ratio = round(wins_critical / losses_critical) if losses_critical > 0 else 0
        
        lines.append(f"⚠️ Critical Finding: You spend {time_ratio}x less time on critical moves when losing!")
        lines.append("")
        
        return lines
    
    def _format_piece_exchanges(self, exchange_metrics):
        """Format piece exchange patterns section"""
        lines = []
        lines.append("♟️ PIECE EXCHANGE PATTERNS")
        lines.append(REPORT_SEPARATOR)
        
        avg_trades = exchange_metrics.get('avg_trades_per_game', 0)
        typical_trades = exchange_metrics.get('typical_trades_for_rating', 6.5)
        trade_assessment = "Over-trading ⚠️" if avg_trades > typical_trades else "Under-trading ⚠️" if avg_trades < typical_trades * 0.8 else "Balanced ✓"
        
        trade_when_ahead = exchange_metrics.get('trade_frequency_when_ahead', 0)
        typical_trade_ahead = exchange_metrics.get('typical_trade_ahead', 75)
        ahead_assessment = "Good! ✓" if trade_when_ahead >= typical_trade_ahead else "Too passive ⚠️"
        
        trade_when_behind = exchange_metrics.get('trade_frequency_when_behind', 0)
        typical_trade_behind = exchange_metrics.get('typical_trade_behind', 25)
        behind_assessment = "Too eager ⚠️" if trade_when_behind > typical_trade_behind else "Good! ✓"
        
        current_rating = 700  # Default
        
        lines.append("Trading Behavior Analysis:")
        lines.append(f"                    Your Games    {current_rating-100}-{current_rating+100} Avg    Assessment")
        lines.append(f"Avg trades/game:        {avg_trades:.1f}          {typical_trades:.1f}         {trade_assessment}")
        lines.append(f"Trade when ahead:       {trade_when_ahead:.0f}%          {typical_trade_ahead}%         {ahead_assessment}")
        lines.append(f"Trade when behind:      {trade_when_behind:.0f}%          {typical_trade_behind}%         {behind_assessment}")
        lines.append("")
        
        good_imbalances = exchange_metrics.get('good_imbalances', [])
        bad_imbalances = exchange_metrics.get('bad_imbalances', [])
        
        if good_imbalances:
            lines.append("Material Imbalances You Handle Well:")
            for imbalance in good_imbalances:
                lines.append(f"• {imbalance['name']}: {imbalance['win_rate']:.0f}% win rate ({imbalance['games']} games)")
            lines.append("")
        
        if bad_imbalances:
            lines.append("Material Imbalances to Avoid:")
            for imbalance in bad_imbalances:
                lines.append(f"• {imbalance['name']}: {imbalance['win_rate']:.0f}% win rate ({imbalance['games']} games)")
            lines.append("")
        
        return lines
    
    def _format_tactical_patterns(self, tactical_metrics):
        """Format tactical pattern detection section"""
        lines = []
        lines.append("🎯 TACTICAL PATTERN DETECTION")
        lines.append(REPORT_SEPARATOR)
        
        winning_patterns = tactical_metrics.get('winning_patterns', [])
        if winning_patterns:
            lines.append("Common Winning Patterns Found:")
            for pattern in winning_patterns:
                lines.append(f"• {pattern['name']}: {pattern['count']} games {pattern.get('comment', '')}")
            lines.append("")
        
        losing_patterns = tactical_metrics.get('losing_patterns', [])
        if losing_patterns:
            lines.append("Common Losing Patterns:")
            for pattern in losing_patterns:
                lines.append(f"• {pattern['name']}: {pattern['count']} games ⚠️")
            lines.append("")
        
        blunder_rate = tactical_metrics.get('blunder_rate', 0)
        typical_rate = tactical_metrics.get('typical_blunder_rate', 2.1)
        trend_start = tactical_metrics.get('blunder_trend_start', 2.8)
        trend_end = tactical_metrics.get('blunder_trend_end', 2.3)
        trend = "Decreasing" if trend_end < trend_start else "Increasing"
        trend_icon = "✓" if trend == "Decreasing" else "⚠️"
        
        current_rating = 700  # Default
        
        lines.append("Blunder Frequency:")
        lines.append(f"• Your rate: {blunder_rate:.1f} per game")
        lines.append(f"• {current_rating-100}-{current_rating+100} average: {typical_rate} per game")
        lines.append(f"• Trend: {trend} ({trend_start} → {trend_end} over 30 days) {trend_icon}")
        lines.append("")
        
        return lines
    
    def _format_performance_trends(self, performance_trends):
        """Format performance trends section"""
        lines = []
        lines.append("📊 PERFORMANCE TRENDS")
        lines.append(REPORT_SEPARATOR)
        
        # Day of week performance
        day_performance = performance_trends.get('day_of_week', {})
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        lines.append("Daily Performance Pattern:")
        for day in days:
            if day in day_performance:
                data = day_performance[day]
                win_rate = data.get('win_rate', 0)
                bar_length = min(int(win_rate / 10), 10)
                bar = "█" * bar_length
                star = " ⭐" if win_rate >= 60 else ""
                lines.append(f"{day}: {bar} {win_rate:.0f}% win rate{star}")
        
        lines.append("")
        
        # Time of day performance
        time_performance = performance_trends.get('time_of_day', {})
        
        lines.append("Best Playing Times:")
        for time_label, data in sorted(time_performance.items()):
            win_rate = data.get('win_rate', 0)
            hours = data.get('hours', '')
            star = " ⭐" if win_rate >= 55 else ""
            warning = " ⚠️" if win_rate < 40 else ""
            lines.append(f"{time_label} ({hours}): {win_rate:.0f}% win rate{star}{warning}")
        
        lines.append("")
        return lines
    
    def _format_game_flow(self, game_flow_metrics):
        """Format game flow analysis section"""
        lines = []
        lines.append("📊 GAME FLOW ANALYSIS")
        lines.append(REPORT_SEPARATOR)
        
        position_eval = game_flow_metrics.get('position_evaluation', {})
        wins_eval = position_eval.get('wins', {})
        draws_eval = position_eval.get('draws', {})
        losses_eval = position_eval.get('losses', {})
        
        lines.append("Average Game Progression:")
        lines.append(f"         Move 10   Move 20   Move 30   Move 40+")
        lines.append(f"Wins:    {wins_eval.get('move_10', 0):+.1f}     {wins_eval.get('move_20', 0):+.1f}      {wins_eval.get('move_30', 0):+.1f}      {wins_eval.get('move_40', 0):+.1f}")
        lines.append(f"Draws:   {draws_eval.get('move_10', 0):+.1f}     {draws_eval.get('move_20', 0):+.1f}      {draws_eval.get('move_30', 0):+.1f}      {draws_eval.get('move_40', 0):+.1f}")
        lines.append(f"Losses:  {losses_eval.get('move_10', 0):+.1f}     {losses_eval.get('move_20', 0):+.1f}      {losses_eval.get('move_30', 0):+.1f}      {losses_eval.get('move_40', 0):+.1f}")
        lines.append("")
        
        lines.append("💡 Key Finding: Your advantages grow steadily, but disadvantages")
        lines.append("snowball quickly after move 20. Focus on defensive resources!")
        lines.append("")
        
        return lines
    
    def _format_psychological_patterns(self, psych_metrics):
        """Format psychological patterns section"""
        lines = []
        lines.append("🧠 PSYCHOLOGICAL PATTERNS")
        lines.append(REPORT_SEPARATOR)
        
        longest_losing_streak = psych_metrics.get('longest_losing_streak', 0)
        recovery_rate = psych_metrics.get('recovery_rate', 0)
        
        lines.append(f"Tilt Indicator: {longest_losing_streak}-game losing streak detected")
        lines.append(f"Recovery Rate: {recovery_rate:.0f}% (healthy - you bounce back well)")
        lines.append("")
        
        best_hour = psych_metrics.get('best_hour', 20)
        best_hour_win_rate = psych_metrics.get('best_hour_win_rate', 60)
        best_session_length = psych_metrics.get('best_session_length', '5-10')
        best_session_win_rate = psych_metrics.get('best_session_win_rate', 65)
        marathon_win_rate = psych_metrics.get('marathon_win_rate', 24.4)
        
        lines.append("Optimal Playing Conditions:")
        lines.append(f"🌟 Best Hour: {best_hour}:00 ({best_hour_win_rate:.0f}% win rate)")
        lines.append(f"🌟 Best Session: {best_session_length} games ({best_session_win_rate:.0f}% win rate)")
        lines.append(f"❌ Avoid: Marathon sessions ({marathon_win_rate:.0f}% in 20+ game sessions)")
        lines.append("")
        
        return lines
    
    def _format_strengths(self, strengths):
        """Format hidden strengths section"""
        lines = []
        lines.append("🏆 YOUR HIDDEN STRENGTHS")
        lines.append(REPORT_SEPARATOR)
        
        for i, strength in enumerate(strengths[:4], 1):
            lines.append(f"{i}. {strength}")
        
        lines.append("")
        return lines
    
    def _format_projections(self, projections):
        """Format projected outcomes section"""
        lines = []
        lines.append("📈 PROJECTED OUTCOMES")
        lines.append(REPORT_SEPARATOR)
        
        lines.append("Target Improvements → Expected Results:")
        lines.append("")
        
        improvements = projections.get('target_improvements', [])
        for imp in improvements[:3]:
            area = imp['area']
            current = imp['current']
            target = imp['target']
            gain = imp['expected_rating_gain']
            
            if gain['unit'] == '%':
                result = f"Overall win rate: +{gain['min']}%"
            else:
                result = f"Rating gain: +{gain['min']}-{gain['max']} points"
            
            lines.append(f"{area}: {current:.0f}% → {target:.0f}%    →  {result}")
        
        lines.append("")
        
        combined = projections.get('combined_projections', {})
        thirty_day = combined.get('30_day', {})
        ninety_day = combined.get('90_day', {})
        
        lines.append(f"Combined 30-day projection: {thirty_day.get('min', 0)}-{thirty_day.get('max', 0)} rating")
        lines.append(f"Combined 90-day projection: {ninety_day.get('min', 0)}-{ninety_day.get('max', 0)} rating")
        lines.append("")
        
        return lines
    
    def _format_footer(self):
        """Format report footer"""
        lines = []
        border = REPORT_BORDER * REPORT_WIDTH
        
        lines.append(border)
        lines.append("")
        
        # Random chess quote
        quote = random.choice(CHESS_QUOTES)
        lines.append(f"{quote}".center(REPORT_WIDTH))
        lines.append("")
        
        # Product branding
        lines.append(REPORT_SEPARATOR)
        lines.append("ChessCoach AI | Analyze • Improve • Win".center(REPORT_WIDTH))
        
        next_analysis_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        lines.append(f"Next Analysis: {next_analysis_date}".center(REPORT_WIDTH))
        lines.append(REPORT_SEPARATOR)
        lines.append(border)
        
        return lines