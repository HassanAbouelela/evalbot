from typing import Callable

import aiohttp
from discord import Message
from discord.ext import commands
from discord.ext.commands import errors

from bot import log

log.setup()


class Bot(commands.Bot):
    """The main bot class."""

    def __init__(self, command_prefix: Callable[["Bot", Message], list[str]], **options):
        super().__init__(command_prefix, **options)
        self.eval_session = aiohttp.ClientSession()

        self.add_check(check_not_bot)
        self.add_check(check_on_guild)

    async def close(self) -> None:
        """The destructor for the bot. Just calls the default discord stuff, then closes our custom eval_session."""
        await super().close()
        await self.eval_session.close()


def check_not_bot(ctx: commands.Context) -> bool:
    """Check if the context is a bot user."""
    return not ctx.author.bot


def check_on_guild(ctx: commands.Context) -> bool:
    """Check if the context is in a guild."""
    if ctx.guild is None:
        raise errors.NoPrivateMessage()
    return True
