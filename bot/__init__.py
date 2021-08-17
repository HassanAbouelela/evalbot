from typing import Callable

import aiohttp
from discord import Message
from discord.ext import commands

from bot import log

log.setup()


class Bot(commands.Bot):
    """The main bot class."""

    def __init__(self, command_prefix: Callable[["Bot", Message], list[str]], **options):
        super().__init__(command_prefix, **options)
        self.eval_session = aiohttp.ClientSession()

    async def close(self) -> None:
        """The destructor for the bot. Just calls the default discord stuff, then closes our custom eval_session."""
        await super().close()
        await self.eval_session.close()
