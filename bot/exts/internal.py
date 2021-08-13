import contextlib
import inspect
import logging
import re
import textwrap
import traceback
from io import StringIO
from typing import Optional

import discord
from discord.ext.commands import Cog, Context, group, has_any_role

from bot import Bot
from bot.constants import admin_role

log = logging.getLogger(__name__)


class Internal(Cog):
    """Administrator and Core Developer commands."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.env = {}
        self.stdout = StringIO()

    @group(name='internal', aliases=('int',))
    @has_any_role(admin_role)
    async def internal_group(self, ctx: Context) -> None:
        """Internal commands. Top secret!"""
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    async def _eval(self, ctx: Context, code: str) -> Optional[discord.Message]:
        """Eval the input code string & send an embed to the invoking context."""

        env = {
            "message": ctx.message,
            "author": ctx.message.author,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "ctx": ctx,
            "self": self,
            "bot": self.bot,
            "inspect": inspect,
            "discord": discord,
            "contextlib": contextlib
        }

        self.env.update(env)

        # Ignore this code, it works
        code_ = """
async def func():  # (None,) -> Any
    try:
        with contextlib.redirect_stdout(self.stdout):
{0}
        if '_' in locals():
            if inspect.isawaitable(_):
                _ = await _
            return _
    finally:
        self.env.update(locals())
""".format(textwrap.indent(code, '            '))

        try:
            exec(code_, self.env)  # noqa: B102,S102
            func = self.env['func']
            res = await func()

        except Exception:
            res = traceback.format_exc()

        self.stdout.seek(0)
        text = self.stdout.read()
        self.stdout.close()
        self.stdout = StringIO()

        if text:
            res += (text + "\n")

        out = res.rstrip("\n")  # Strip empty lines from output

        if len(out) <= 2000:
            return await ctx.send(out)
        else:
            for i in range(len(out) // 2000 + 1):
                start = 2000 * i
                content = out[start: start + 2000]

                if len(content) > 0:
                    return await ctx.send(content)

    @internal_group.command(name='eval', aliases=('e',))
    @has_any_role(admin_role)
    async def eval(self, ctx: Context, *, code: str) -> None:
        """Run eval in a REPL-like format."""
        code = code.strip("`")
        if re.match('py(thon)?\n', code):
            code = "\n".join(code.split("\n")[1:])

        if not re.search(  # Check if it's an expression
                r"^(return|import|for|while|def|class|"
                r"from|exit|[a-zA-Z0-9]+\s*=)", code, re.M) and len(
                    code.split("\n")) == 1:
            code = "_ = " + code

        await self._eval(ctx, code)


def setup(bot: Bot) -> None:
    """Load the Internal cog."""
    bot.add_cog(Internal(bot))
