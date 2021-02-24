import asyncio

import aiohttp

from .util import request_manager
from .util import utils as util
from .util.classes.config import BackConfig, population_back_config, Config
from .util.name_system import api_timing, namemc_timing

import os.path


class Sniper:
    def __init__(self,
                 colorer,
                 logger):
        self.color = colorer
        self.log = logger
        self.session = request_manager.RequestManager(
            aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=300),
                headers={}
            )
        )

        self.target = str()  # target username
        self.offset = int()  # Time offset (e.g., 400 = snipe the name 400ms early)

        self.config = None  # util.classes.config.BackConfig
        self.user_config = None  # util.classes.config.Config

        self.data = None

    @property
    def initialized(self):
        return self.config.init_path != ""

    def init(self):
        # if self.initilized:
        #     self.log.debug("Already initialized")
        # else:
        #     self.log.debug("Not initialized")

        population_back_config()

    async def run(self, target=None, offset=None):

        self.config = BackConfig()
        self.log.debug(f"Using sniping path of {self.config.init_path}")

        self.user_config = Config(self.config.init_path)

        if target is None:
            self.log.debug('No username detected')
            self.target = self.log.input("Target Username:")
        else:
            self.log.info(f"Sniping username: {target}")

        if offset is None:
            self.log.debug('no offset detected')
            self.offset = self.log.input("Time Offset:")
        else:
            self.log.info(f"Delay (ms): {offset}")

        self.log.debug("Loading accounts from file.")

        accounts = util.parse_accs(os.path.join(self.config.init_path, "accounts.txt"))
        if len(accounts) == 0:
            self.log.error("No accounts were loaded from file. Please check accounts.txt and try again.")
            sys.exit(0)

        self.log.info(f"{len(accounts)} account(s) have been loaded from file.")

        droptime = await api_timing(target, self.session)

        if droptime is None:
            self.log.error("Failed to get droptime.")
            sys.exit(0)

        auth_delay = int(config.get("auth_delay"))
        drop_time_datetime = datetime.datetime.fromtimestamp(droptime)
        rd = relativedelta(datetime.datetime.now(), drop_time_datetime)

        for acc in accounts:
            await acc.fully_authenticate()
            await asyncio.sleep(auth_delay / 1000)

        while datetime.datetime.now().timestamp() < droptime:
            time.sleep(1)

        self.on_shutdown()

    def on_shutdown(self):
        asyncio.get_event_loop().run_until_complete(self.session.session.close())
