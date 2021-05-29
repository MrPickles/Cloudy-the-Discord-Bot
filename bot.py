import logging

from discord.ext import commands
from discord_slash import SlashCommand

logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super(DiscordBot, self).__init__(*args, **kwargs)
        _set_commands(self)

    async def on_ready(self):
        logger.info("We have logged in as %s", self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

        # https://discordpy.readthedocs.io/en/stable/faq.html#why-does-on-message-make-my-commands-stop-working
        await self.process_commands(message)


def _set_commands(bot):
    slash = SlashCommand(bot, sync_commands=True)

    @bot.command()
    async def add(ctx, left: int, right: int):
        """Adds two numbers together."""
        await ctx.send(left + right)

    guild_ids = [326580881965842433]

    @slash.slash(name="ping", description="Just checks the latency. That's all.", guild_ids=guild_ids)
    async def _ping(ctx):
        await ctx.send(f"Pong! ({bot.latency*1000}ms)")
