# Chess Player Analytics

A Python tool to analyze your Chess.com games and generate insights about your chess performance.

## Features

- Fetches games from Chess.com API for any username
- Analyzes your chess performance across various dimensions:
  - Basic statistics (win rate, rating, etc.)
  - Opening repertoire analysis
  - Performance by game phase (opening, middlegame, endgame)
  - Pattern recognition in wins and losses
  - Endgame proficiency
  - Mistake patterns
  - Psychological and momentum insights

## Requirements

- Python 3.6+
- Internet connection to access Chess.com API

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/solemn-sloth/chess-player-analytics.git
   cd chess-player-analytics
   ```

2. Install dependencies:
   ```
   pip install requests
   ```

## Usage

Run the main script:

```
python main.py
```

Follow the prompts:
1. Enter your Chess.com username
2. Specify how many games to analyze (default: 100)

The script will:
1. Fetch your recent games from Chess.com
2. Analyze your games
3. Generate a detailed report
4. Save the report to a text file in the 'output' folder

## Configuration

You can modify settings in `config.py`:
- `DEFAULT_NUM_GAMES`: Default number of games to analyze
- `MIN_GAMES_FOR_PATTERN`: Minimum games needed to identify a pattern
- Game phase definitions (by move number)
- Various thresholds for analysis

## Example Output

The analysis report includes:
- Executive summary of your chess performance
- Performance breakdown by color (white/black)
- Time control analysis
- Opening repertoire assessment
- Winning and losing patterns
- Game phase performance
- Mistake pattern analysis
- Endgame proficiency
- Psychological and momentum insights
- Key recommendations for improvement

## Limitations

- Only works with Chess.com accounts
- Limited to standard chess games
- Analysis is statistical, not engine-based

## License

This project is available as open source under the terms of the MIT License.