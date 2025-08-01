import os
from datetime import datetime
from analyzer.chess_analyzer import ChessAnalyzer
from report.report_formatter import ReportFormatter
from config import DEFAULT_NUM_GAMES, DEFAULT_ANALYSIS_DAYS

def main():
    """Main entry point"""
    print("Chess.com Performance Analyzer")
    print("=" * 40)
    
    # Get user input
    username = input("Enter Chess.com username: ").strip()
    if not username:
        print("Username required!")
        return
    
    try:
        num_games = int(input(f"Number of games to analyze (default {DEFAULT_NUM_GAMES}): ").strip() or DEFAULT_NUM_GAMES)
    except ValueError:
        num_games = DEFAULT_NUM_GAMES
    
    # Run analysis
    analyzer = ChessAnalyzer(username)
    metrics, insights = analyzer.analyze(num_games, DEFAULT_ANALYSIS_DAYS)
    
    if not metrics or not insights:
        print("Analysis failed - no data available")
        return
    
    # Generate report
    print("\nGenerating report...")
    formatter = ReportFormatter()
    report = formatter.format_report(metrics, insights)
    
    # Save report
    os.makedirs('output', exist_ok=True)
    filename = f"output/{username}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✓ Analysis complete! Report saved to: {filename}")
    print("\nReport Preview:")
    print("-" * 40)
    print(report[:500] + "...")
    print("-" * 40)

if __name__ == "__main__":
    main()