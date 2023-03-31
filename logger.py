import logging
import datetime
from pytz import timezone
import sys


class logger:
    def __init__(self, name: str = 'bot'):
        self.logger = logging.getLogger(name)
        self.name = name
        token_file_handler = logging.FileHandler('log/token.log', mode='a')
        self.token_logger = logging.getLogger('OPEN_AI_TOKEN')
        self.token_logger.handlers.clear()
        self.token_logger.addHandler(token_file_handler)

    tz = datetime.timezone(datetime.timedelta(hours=+8))

    def timetz(*args):
        return datetime.datetime.now(timezone('Asia/Taipei')).timetuple()

    logging.Formatter.converter = timetz
    FORMAT = '%(asctime)s %(levelname)6s %(name)15s: %(message)s'
    handlers = [
        logging.FileHandler(
            'log/' + str(datetime.datetime.now(tz).year) + '/' +
            str(datetime.datetime.now(tz).month).zfill(2) + '/' +
            str(datetime.datetime.now(tz).date()) + '.log',
            mode='a'),
        # logging.StreamHandler(sys.stdout)
    ]
    logging.basicConfig(level=logging.INFO, format=FORMAT, handlers=handlers)
    # logging.getLogger('quart.app').handlers.clear()
    # logging.getLogger('quart.app').addHandler(logging.FileHandler(
    #         'log/' + str(datetime.datetime.now(tz).year) + '/' +
    #         str(datetime.datetime.now(tz).month).zfill(2) + '/' +
    #         str(datetime.datetime.now(tz).date()) + '.log',
    #         mode='a'))

    def info(self, msg):
        self.logger.info(msg)
        # print('[INFO] ' + msg)

    def warn(self, msg):
        self.logger.warning(msg)
        # print('[WARNING] ' + msg)

    def err(self, msg):
        self.logger.error(msg)
        # print('[ERROR]' + msg)
    
    def get_handler(self):
        return logging.FileHandler(
            'log/' + str(datetime.datetime.now(self.tz).year) + '/' +
            str(datetime.datetime.now(self.tz).month).zfill(2) + '/' +
            str(datetime.datetime.now(self.tz).date()) + '.log',
            mode='a')
