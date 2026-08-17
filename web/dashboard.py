import logging
import os
from pathlib import Path

from discord.utils import setup_logging
from quart import Quart, jsonify, render_template, request
from quart.logging import default_handler

from repositories import BotRepository


class Dashboard:
    def __init__(self, repository: BotRepository):
        self.repository = repository
        self.root = Path(__file__).resolve().parents[1]
        self._configure_logging()
        self.app = Quart(
            "Dashboard",
            template_folder=str(self.root / "templates"),
            static_folder=str(self.root / "static"),
        )
        self.app.add_url_rule("/", "home", self.home, methods=["GET", "POST"])
        self.app.add_url_rule("/online_status", "online_status", self.online_status)

    @staticmethod
    def _configure_logging() -> None:
        for name in (
            "quart.app",
            "quart",
            "hypercorn",
            "hypercorn.error",
            "hypercorn.access",
            "aiohttp",
            "werkzeug",
        ):
            logging.getLogger(name).setLevel(logging.FATAL)
        logging.getLogger("quart").handlers.clear()
        for name in ("hypercorn", "quart.serving"):
            target = logging.getLogger(name)
            if default_handler in target.handlers:
                target.removeHandler(default_handler)
        setup_logging(root=True)

    def _latest_log(self) -> list[str]:
        log_root = self.root / "log"
        candidates = sorted(log_root.glob("*/*/*.log"), reverse=True)
        if not candidates:
            return []
        return candidates[0].read_text(encoding="utf-8").splitlines()

    async def home(self):
        dashboard_logger = logging.getLogger("dashboard")
        if request.method == "POST":
            form = await request.get_json()
            command = form["command"]
            if command == "kill 1":
                dashboard_logger.info("command: kill 1")
                os.system("kill 1")
            elif command.startswith("set verbose "):
                level = command.split()[2]
                if level.isnumeric() and 0 <= int(level) <= 7:
                    dashboard_logger.info("command: " + command)
                    self.repository.set_verbose_level(level)
                else:
                    dashboard_logger.error("command error: verbose level should be 0-7")
            else:
                dashboard_logger.error("wrong command: " + command)

        online = (self.root / "running.lock").exists()
        tokens = self.repository.get_token_usage()
        return await render_template(
            "index.html",
            online=online,
            bot_name=self.repository.get_bot_name(),
            log_messages=[line.split() for line in self._latest_log()],
            price=f"{(tokens * 0.002 / 1000):.5f}",
            online_text="Online" if online else "Offline",
            online_class="is-success" if online else "is-danger",
        )

    async def online_status(self):
        return jsonify({"online": (self.root / "running.lock").exists()})
