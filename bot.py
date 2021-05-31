import logging

from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from openai.error import OpenAIError

import gpt


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

        if message.channel.id == 705667675292172288:
            response = gpt.complete(message.content)
            await message.channel.send(response)

        # https://discordpy.readthedocs.io/en/stable/faq.html#why-does-on-message-make-my-commands-stop-working
        await self.process_commands(message)


def _set_commands(bot):
    cmd = SlashCommand(bot, sync_commands=True)

    @bot.command()
    async def add(ctx, left: int, right: int):
        """Adds two numbers together."""
        await ctx.send(left + right)

    guild_ids = [326580881965842433]

    @cmd.slash(
        name="ping",
        description="Just checks the latency. That's all.",
        guild_ids=guild_ids,
    )
    async def _ping(ctx):
        await ctx.send(f"Pong! ({bot.latency*1000}ms)")

    @cmd.slash(name="engines", guild_ids=guild_ids)
    async def _engines(ctx):
        try:
            engines = gpt.engines()
            msg = "The following GPT-3 engines are available:\n"
            msg += "\n".join(map(lambda engine: f"- `{engine}`", engines))
            await ctx.send(msg)
        except OpenAIError as e:
            await ctx.send(str(e))

    @cmd.slash(
        name="complete",
        guild_ids=guild_ids,
        options=[
            create_option(
                name="prompt",
                description="The prompt to feed GPT-3. Please wrap it in quotes.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _complete(ctx, prompt):
        try:
            res = gpt.complete(prompt)
            await ctx.send(res)
        except OpenAIError as e:
            await ctx.send(str(e))

    @cmd.slash(
        name="amongus",
        guild_ids=guild_ids,
        description="View the maps in Among Us.",
        options=[
            create_option(
                name="map",
                description="The map name. It can be skeld, mira, polus, or airship.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _amongus(ctx, map_name):
        map_urls = {
            "skeld": "https://media.discordapp.net/attachments/757358510911520879/757415061663907870/skeldmapguidev2.png",
            "mira": "https://i.redd.it/8i1kd1mp9ij51.png",
            "polus": "https://cdn.discordapp.com/attachments/757358510911520879/792121876192690176/polus.jpg",
            "airship": "https://imgur.com/4gQUZn8",
        }
        if map_name not in map_urls:
            await ctx.send(f"Invalid map. Please use one of the following map names: `skeld`, `mira`, `polus`, or `airship`.")
        else:
            await ctx.send(map_urls[map_name])