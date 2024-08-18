import logging

# Create a custom logger
logger = logging.getLogger('custom_logger')

# Set the log level
logger.setLevel(logging.DEBUG)

# Create a stream handler (for console output)
stream_handler = logging.StreamHandler()

# Create a formatter and set it for the stream handler
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)

# Add the stream handler to the logger if it doesn't already have handlers
if not logger.handlers:
    logger.addHandler(stream_handler)

# Optional: prevent the logger from propagating to the root logger
logger.propagate = False
