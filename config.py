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
CRITICAL_TIME_THRESHOLD = 10  # Seconds threshold for critical decision time pressure

# Report Settings
REPORT_WIDTH = 80  # Character width for report formatting
REPORT_SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"  # Section separator
REPORT_BORDER = "═"  # Border character for report

# Rating Levels
RATING_LEVELS = {
    0: "Beginner",
    500: "Casual",
    700: "Intermediate",
    1000: "Competent",
    1200: "Skilled",
    1600: "Expert",
    1800: "Advanced",
    2000: "Master",
    2200: "Grandmaster"
}

# Analysis Period
DEFAULT_ANALYSIS_DAYS = 30  # Default period for analysis in days

# Time of Day Categories
TIME_CATEGORIES = {
    "Morning": (6, 12),    # 6 AM to 12 PM
    "Afternoon": (12, 18),  # 12 PM to 6 PM
    "Evening": (18, 24),   # 6 PM to 12 AM
    "Night": (0, 6)       # 12 AM to 6 AM
}

# Chess Quotes
CHESS_QUOTES = [
    "\"In chess, as in life, opportunity strikes but once.\" - David Bronstein",
    "\"Every chess master was once a beginner.\" - Irving Chernev",
    "\"Chess is life in miniature.\" - Garry Kasparov",
    "\"Chess is not only knowledge and logic.\" - Anatoly Karpov",
    "\"Chess is a war over the board.\" - Bobby Fischer",
    "\"Chess is the struggle against error.\" - Johannes Zukertort",
    "\"Chess is 99% tactics.\" - Richard Teichmann",
    "\"Chess makes men wiser and clear-sighted.\" - Vladimir Putin",
    "\"Chess holds its master in its own bonds.\" - Wilhelm Steinitz",
    "\"Chess is beautiful enough to waste your life for.\" - Hans Ree"
]