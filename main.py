import os
import sys
import time
from datetime import datetime
from analyzer.chess_analyzer import ChessAnalyzer
from report.report_formatter import ReportFormatter
from config import DEFAULT_NUM_GAMES, DEFAULT_ANALYSIS_DAYS

def draw_progress_bar(current, total, bar_length=45):
    """Draw a progress bar showing completion status"""
    if total == 0:
        return
    
    progress = min(1.0, current / total)
    block = int(round(bar_length * progress))
    
    bar = '█' * block + '░' * (bar_length - block)
    
    sys.stdout.write(f"\r█{bar}█ {current}/{total} ✓")
    sys.stdout.flush()
    
    if progress >= 1.0:
        # Add an extra newline after completion, except for the last one
        if not hasattr(draw_progress_bar, 'completed_bars'):
            draw_progress_bar.completed_bars = 0
        
        draw_progress_bar.completed_bars += 1
        
        # Add newline plus an extra line unless it's the last progress bar
        if draw_progress_bar.completed_bars < 3:  # We have 3 progress bars total
            sys.stdout.write('\n\n')
        else:
            sys.stdout.write('\n')

def main():
    """Main entry point"""
    # Print header with border
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                Chess.com Performance Analyzer                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Get user input
    username = input("Username: ").strip()
    if not username:
        print("Username required!")
        return
    
    try:
        num_games = int(input(f"Games to analyze: ").strip() or DEFAULT_NUM_GAMES)
    except ValueError:
        num_games = DEFAULT_NUM_GAMES
        
    print()
    
    # Define progress callbacks for each step
    progress_callbacks = {
        'fetch': lambda current, total: update_progress("📥 Fetching games from Chess.com...", current, total),
        'analyze': lambda current, total: update_progress("🔍 Analyzing game data...", current, total),
        'insights': lambda current, total: update_progress("💡 Generating insights...", current, total)
    }
    
    # Run analysis with progress reporting
    analyzer = ChessAnalyzer(username)
    metrics, insights = analyzer.analyze(num_games, DEFAULT_ANALYSIS_DAYS, progress_callbacks)
    
    if not metrics or not insights:
        print("\nAnalysis failed - no data available")
        return
    
    # Generate report (silently)
    formatter = ReportFormatter()
    report = formatter.format_report(metrics, insights)
    
    # Save report
    os.makedirs('output', exist_ok=True)
    filename = f"output/{username}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Print completion message with border
    print("\n═══════════════════════════════════════════════════════════════")
    print("\n✨ Analysis complete!")
    print()
    print("📄 Full report saved to:")
    print(f"   {filename}")
    print()
    print("═══════════════════════════════════════════════════════════════")

def update_progress(message, current, total):
    """Update progress with message and bar"""
    # Use a static variable to track if we've printed a message already
    if not hasattr(update_progress, 'last_message') or update_progress.last_message != message:
        sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear current line
        print(message)
        print()  # Add a line space between message and progress bar
        update_progress.last_message = message
    
    draw_progress_bar(current, total)
    sys.stdout.flush()

if __name__ == "__main__":
    main()