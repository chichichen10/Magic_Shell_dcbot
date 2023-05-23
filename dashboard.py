from quart import Quart, render_template, request, jsonify
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

    @app.route("/", methods=["GET", "POST"])
    async def home():
        dashboard_logger = logging.getLogger('dashboard')
        today = datetime.datetime.now()
        today += datetime.timedelta(hours=8)
        log_file_name = 'log/' + str(today.year) + '/' + str(
            today.month).zfill(2) + '/' + str(today.date()) + '.log'
        time_delta = datetime.timedelta(days=1)
        while (not os.path.exists(log_file_name)):
            today = today - time_delta
            log_file_name = 'log/' + str(today.year) + '/' + str(
                today.month).zfill(2) + '/' + str(today.date()) + '.log'
        bot_name = db['bot_name']
        log_messages = []
        with open(log_file_name, 'r') as f:
            log_messages = f.readlines()
        tokens = db['token'][1]
        online = os.path.exists('running.lock')
        price = f'{(tokens * 0.002 / 1000):.5f}'

        split_messages = [i.split() for i in log_messages]
        if request.method == "POST":
            # os.system('kill 1')
            form = await request.get_json()
            if form['command'] == "kill 1":
                dashboard_logger.info('command: kill 1')
                os.system('kill 1')
            elif 'set verbose' in form['command']:
                n = form['command'].split()[2]
                if (n.isnumeric()):
                    if (int(n) <= 7 and int(n) >= 0):
                        dashboard_logger.info('command: ' + form['command'])
                        db['verbose'] = n
                    else:
                        dashboard_logger.error(
                            'command error: verbose level should be 0-7')
                else:
                    dashboard_logger.error('wrong usage ' + form['command'])
            else:
                dashboard_logger.error('wrong command: ' + form['command'])

        online_text = 'Online' if online else 'Offline'
        online_class = 'is-success' if online else 'is-danger'
        return await render_template('index.html',
                                     online=online,
                                     bot_name=bot_name,
                                     log_messages=split_messages,
                                     price=price,
                                     online_text=online_text,
                                     online_class=online_class)

    @app.route('/online_status')
    async def online_status():
        # 返回在线状态信息的 JSON 数据
        online = os.path.exists('running.lock')
        return jsonify({
            'online': online
        })


# lo = logging.getLogger('quart.serving')
# lo.handlers.clear()

# logger = logger('dashboard')
# lo.addHandler(logger.get_handler())
