import logging
import sys
from config import Config

class UnicodeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            # Fallback to ASCII-only output
            msg = record.getMessage().encode('ascii', 'ignore').decode('ascii')
            stream.write(msg + self.terminator)
            self.flush()

def configure_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(Config.LOG_LEVEL)
    
    handler = UnicodeStreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

# Create and configure the logger
logger = configure_logger()