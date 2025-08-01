# Chess Analytics Configuration

# API Settings
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Analysis Settings
DEFAULT_NUM_GAMES = 100  # Number of games to analyze
MIN_GAMES_FOR_PATTERN = 3  # Minimum games to identify a pattern

# Game Phase Definitions (by move number)
OPENING_PHASE_END = 15
MIDDLEGAME_PHASE_END = 35

# Evaluation Thresholds
BLUNDER_THRESHOLD = 200  # Centipawn loss to be considered a blunder
MISTAKE_THRESHOLD = 100  # Centipawn loss to be considered a mistake
WINNING_ADVANTAGE = 150  # Centipawns advantage to be considered winning

# Time Settings
TIME_PRESSURE_SECONDS = 30  # Seconds remaining to be considered time pressure
QUICK_LOSS_MOVES = 20  # Games ending before this are "quick losses"

# Report Settings
REPORT_WIDTH = 80  # Character width for report formatting