import logging
import typing as t

from discord import Color, Embed
from discord.ext.commands import ChannelNotFound, Cog, Context, TextChannelConverter, VoiceChannelConverter, errors
from sentry_sdk import push_scope

from bot import Bot

log = logging.getLogger(__name__)


class ErrorHandler(Cog):
    """Handles errors emitted from commands."""

    def __init__(self, bot: Bot):
        self.bot = bot

    def _get_error_embed(self, title: str, body: str) -> Embed:
        """Return an embed that contains the exception."""
        return Embed(
            title=title,
            colour=Color.red(),
            description=body
        )

    @Cog.listener()
    async def on_command_error(self, ctx: Context, e: errors.CommandError) -> None:
        """
        Provide generic command error handling.

        Error handling is deferred to any local error handler, if present. This is done by
        checking for the presence of a `handled` attribute on the error.

        Error handling emits a single error message in the invoking context `ctx` and a log message,
        prioritised as follows:

        1. If the name fails to match a command:
            * If it matches shh+ or unshh+, the channel is silenced or unsilenced respectively.
              Otherwise if it matches a tag, the tag is invoked
            * If CommandNotFound is raised when invoking the tag (determined by the presence of the
              `invoked_from_error_handler` attribute), this error is treated as being unexpected
              and therefore sends an error message
        2. UserInputError: see `handle_user_input_error`
        3. CheckFailure: see `handle_check_failure`
        4. CommandOnCooldown: send an error message in the invoking context
        5. ResponseCodeError: see `handle_api_error`
        6. Otherwise, if not a DisabledCommand, handling is deferred to `handle_unexpected_error`
        """
        command = ctx.command

        if hasattr(e, "handled"):
            log.debug(f"Command {command} had its error already handled locally; ignoring.")
            return

        if isinstance(e, errors.CommandNotFound):
            await ctx.send("Command not found. Try the help command.")
            return
        elif isinstance(e, errors.UserInputError):
            await self.handle_user_input_error(ctx, e)
        elif isinstance(e, errors.CheckFailure):
            bot_missing_errors = (
                errors.BotMissingPermissions,
                errors.BotMissingRole,
                errors.BotMissingAnyRole
            )

            if isinstance(e, bot_missing_errors):
                await ctx.send("Sorry, it looks like I don't have the permissions or roles I need to do that.")
            else:
                await ctx.send("You don't have permission to do that!")
        elif isinstance(e, errors.CommandOnCooldown):
            await ctx.send(e)
        elif isinstance(e, errors.CommandInvokeError):
            await self.handle_unexpected_error(ctx, e.original)
            return
        elif isinstance(e, errors.ConversionError):
            await self.handle_unexpected_error(ctx, e.original)
            return
        elif not isinstance(e, errors.DisabledCommand):
            # MaxConcurrencyReached, ExtensionError
            await self.handle_unexpected_error(ctx, e)
            return  # Exit early to avoid logging.

        log.debug(
            f"Command {command} invoked by {ctx.message.author} with error "
            f"{e.__class__.__name__}: {e}"
        )

    @staticmethod
    def get_help_command(ctx: Context) -> t.Coroutine:
        """Return a prepared `help` command invocation coroutine."""
        if ctx.command:
            return ctx.send_help(ctx.command)

        return ctx.send_help()

    async def try_silence(self, ctx: Context) -> bool:
        """
        Attempt to invoke the silence or unsilence command if invoke with matches a pattern.

        Respecting the checks if:
        * invoked with `shh+` silence channel for amount of h's*2 with max of 15.
        * invoked with `unshh+` unsilence channel
        Return bool depending on success of command.
        """
        command = ctx.invoked_with.lower()
        args = ctx.message.content.lower().split(" ")
        silence_command = self.bot.get_command("silence")
        ctx.invoked_from_error_handler = True

        try:
            if not await silence_command.can_run(ctx):
                log.debug("Cancelling attempt to invoke silence/unsilence due to failed checks.")
                return False
        except errors.CommandError:
            log.debug("Cancelling attempt to invoke silence/unsilence due to failed checks.")
            return False

        # Parse optional args
        channel = None
        duration = min(command.count("h") * 2, 15)
        kick = False

        if len(args) > 1:
            # Parse channel
            for converter in (TextChannelConverter(), VoiceChannelConverter()):
                try:
                    channel = await converter.convert(ctx, args[1])
                    break
                except ChannelNotFound:
                    continue

        if len(args) > 2 and channel is not None:
            # Parse kick
            kick = args[2].lower() == "true"

        if command.startswith("shh"):
            await ctx.invoke(silence_command, duration_or_channel=channel, duration=duration, kick=kick)
            return True
        elif command.startswith("unshh"):
            await ctx.invoke(self.bot.get_command("unsilence"), channel=channel)
            return True
        return False

    async def handle_user_input_error(self, ctx: Context, e: errors.UserInputError) -> None:
        """
        Send an error message in `ctx` for UserInputError, sometimes invoking the help command too.

        * MissingRequiredArgument: send an error message with arg name and the help command
        * TooManyArguments: send an error message and the help command
        * BadArgument: send an error message and the help command
        * BadUnionArgument: send an error message including the error produced by the last converter
        * ArgumentParsingError: send an error message
        * Other: send an error message and the help command
        """
        if isinstance(e, errors.MissingRequiredArgument):
            embed = self._get_error_embed("Missing required argument", e.param.name)
            await ctx.send(embed=embed)
            await self.get_help_command(ctx)
        elif isinstance(e, errors.TooManyArguments):
            embed = self._get_error_embed("Too many arguments", str(e))
            await ctx.send(embed=embed)
            await self.get_help_command(ctx)
        elif isinstance(e, errors.BadArgument):
            embed = self._get_error_embed("Bad argument", str(e))
            await ctx.send(embed=embed)
            await self.get_help_command(ctx)
        elif isinstance(e, errors.BadUnionArgument):
            embed = self._get_error_embed("Bad argument", f"{e}\n{e.errors[-1]}")
            await ctx.send(embed=embed)
            await self.get_help_command(ctx)
        elif isinstance(e, errors.ArgumentParsingError):
            embed = self._get_error_embed("Argument parsing error", str(e))
            await ctx.send(embed=embed)
            self.get_help_command(ctx).close()
        else:
            embed = self._get_error_embed(
                "Input error",
                "Something about your input seems off. Check the arguments and try again."
            )
            await ctx.send(embed=embed)
            await self.get_help_command(ctx)

    @staticmethod
    async def handle_unexpected_error(ctx: Context, e: errors.CommandError) -> None:
        """Send a generic error message in `ctx` and log the exception as an error with exc_info."""
        await ctx.send(
            f"Sorry, an unexpected error occurred. Please let us know!\n\n"
            f"```{e.__class__.__name__}: {e}```"
        )

        with push_scope() as scope:
            scope.user = {
                "id": ctx.author.id,
                "username": str(ctx.author)
            }

            scope.set_tag("command", ctx.command.qualified_name)
            scope.set_tag("message_id", ctx.message.id)
            scope.set_tag("channel_id", ctx.channel.id)

            scope.set_extra("full_message", ctx.message.content)

            if ctx.guild is not None:
                scope.set_extra(
                    "jump_to",
                    f"https://discordapp.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id}"
                )

            log.error(f"Error executing command invoked by {ctx.message.author}: {ctx.message.content}", exc_info=e)


def setup(bot: Bot) -> None:
    """Load the ErrorHandler cog."""
    bot.add_cog(ErrorHandler(bot))
