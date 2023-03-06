import logging
import datetime
from pytz import timezone


class logger:
    tz = datetime.timezone(datetime.timedelta(hours=+8))

    def timetz(*args):
        return datetime.datetime.now(timezone('Asia/Taipei')).timetuple()

    # tz = timezone('Asia/Shanghai')
    logging.Formatter.converter = timetz
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO,
                        filename='log/' + str(datetime.datetime.now(tz).year) +
                        '/' + str(datetime.datetime.now(tz).month).zfill(2) +
                        '/' + str(datetime.datetime.now(tz).date()) + '.log',
                        filemode='a',
                        format=FORMAT)

    def info(msg):
        logging.info(msg)
        print('[INFO] ' + msg)

    def warn(msg):
        logging.warning(msg)
        print('[WARNING] ' + msg)

    def err(msg):
        logging.error(msg)
        print('[ERROR]' + msg)
