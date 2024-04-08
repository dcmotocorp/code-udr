import logging
from logging.handlers import TimedRotatingFileHandler
import os

class UdrLogger:
    def __init__(self):
        self.log_file_name = 'udr_log.log'

        log_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')
        
        os.makedirs(log_folder, exist_ok=True)
        
        self.log_file_path = os.path.join(log_folder, self.log_file_name)

        # Set up logging
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # Create a TimedRotatingFileHandler that writes log messages to a rotating file
        self.handler = TimedRotatingFileHandler(
            self.log_file_path,
            when='midnight',
            interval=1,
            backupCount=30  # Keep logs for the last 30 days
        )

        # Create a formatter and set it on the handler
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(self.handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_error(self, message):
        self.logger.error(message)

