import aiohttp
from discord.ext import commands

from bot import log

log.setup()


class Bot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.eval_session = aiohttp.ClientSession()

    async def close(self):
        await super().close()
        await self.eval_session.close()
