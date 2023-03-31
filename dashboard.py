from quart import Quart, render_template, request
import logging
import os
import datetime
from discord.utils import setup_logging
from quart.logging import default_handler
from replit import db

from logger import logger


class dashboard:
    logging.getLogger('hypercorn').removeHandler(default_handler)
    logging.getLogger('quart.app').setLevel(logging.FATAL)
    logging.getLogger('quart').setLevel(logging.FATAL)
    logging.getLogger('hypercorn').setLevel(logging.FATAL)
    logging.getLogger('hypercorn.error').setLevel(logging.FATAL)
    logging.getLogger('hypercorn.access').setLevel(logging.FATAL)
    logging.getLogger('aiohttp').setLevel(logging.FATAL)
    logging.getLogger('quart').handlers.clear()
    logging.getLogger('quart.serving').removeHandler(default_handler)
    logging.getLogger('werkzeug').setLevel(logging.FATAL)
    setup_logging(root=True)
    app = Quart('Dashboard')
    online = False

    def __init__(self):
        print('hi')

    @app.route("/",methods=["GET", "POST"])
    async def home():
        # a = datetime.datetime.now()
        log_file_name = 'log/' + str(datetime.datetime.now().year) + '/' + str(
            datetime.datetime.now().month).zfill(2) + '/' + str(
                datetime.datetime.now().date()) + '.log'
        bot_name = db['bot_name']
        log_messages = []
        with open(log_file_name, 'r') as f:
            log_messages = f.readlines()[-20:]
        tokens = db['token'][1]
        online = os.path.exists('running.lock')
        price = f'{(tokens * 0.002 / 1000):.5f}'
        # if request.method == "POST":
        #     # os.system('kill 1')
        #     print(await request.form.get("password"))
        return await render_template('index.html',
                                     online=online,
                                     bot_name=bot_name,
                                     log_messages=log_messages,
                                     price=price)

    # lo = logging.getLogger('quart.serving')
    # lo.handlers.clear()

    # logger = logger('dashboard')
    # lo.addHandler(logger.get_handler())
