import logging
import datetime

class logger:
    tz = datetime.timezone(datetime.timedelta(hours=+8))
    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.INFO, filename='log/'+str(datetime.datetime.now(tz).date())+'.log', filemode='a', format=FORMAT)
    def info(msg):
        logging.info(msg)
        print('[INFO] ' + msg)
    def warn(msg):
        logging.warning(msg)
        print('[WARNING] '+msg)
    def err(msg):
        logging.error(msg)
        print('[ERROR]'+msg)