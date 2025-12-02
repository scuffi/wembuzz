import sys
from loguru import logger

# Remove default handler and configure custom format
logger.remove()
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} {file}:{line} {message}",
    colorize=False,
)
