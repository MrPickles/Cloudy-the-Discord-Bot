import logging
from collections import defaultdict
from textwrap import dedent

from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from openai.error import OpenAIError

from util import db, fixtures, gpt, locks


logger = logging.getLogger(__name__)

class Cloudy(commands.Bot):
    """The base class for Cloud the Discord Bot.
    
    Cloudy's implementation includes standard handlers for messaging and
    server-joining events. Additionally, it will initialize several slash
    commands upon instantiation.

    For details about the specific functionality, please refer to the README.
    """
    def __init__(self, *args, **kwargs):
        super(Cloudy, self).__init__(*args, **kwargs)
        self.history = defaultdict(list)
        self.lock = locks.Lock()
        self._init_slash_commands()
   
    async def on_ready(self):
        """Handler for when the bot has become interactive."""
        logger.info("We have logged in as %s", self.user)
        db.set_last_init()

    async def on_guild_join(self, guild):
        """Handler for when the bot joins a Discord server."""
        logger.info("Joined guild: %d", guild.id)
        for channel in guild.text_channels:
            if channel.name == "general":
                await channel.send(fixtures.introduction)
        db.increment_guild_count()

    async def on_message(self, message):
        """Handler for when the bot receives a message."""
        if message.author == self.user:
            return

        if message.channel.id == 326580881965842433:
            # TODO: for now, skip the general channel
            return

        guild_id = message.guild.id
        mode = db.get_mode(guild_id)
        if mode == fixtures.silence:
            logger.debug("Bot is in silence mode. Skipping interaction in guild %d", guild_id)
            return

        if not self.lock.claim_lock(guild_id):
            logger.info("Guild %d currently holds a lock; ignoring new messages...", guild_id)
            return
        prompt = self._build_prompt(guild_id, message.content)
        config = fixtures.config[mode]
        try:
            response = gpt.complete(prompt, [config["p1"], config["p2"]])
            if mode == fixtures.chat:
                self._update_history(guild_id, message.content, response)
            elif mode == fixtures.react:
                response = f"```{response}```"
            await message.channel.send(response)
        except OpenAIError as e:
            await message.channel.send(str(e))

        self.lock.release_lock(guild_id)

    def _update_history(self, guild_id: int, opener: str, response: str):
        """Updates the AI chat history for a given server.

        For now, the maximum history length is 10. This is to prevent too much
        of a memory overhead per server.
        """
        self.history[guild_id].append((opener, response))
        if len(self.history[guild_id]) > fixtures.max_history_length:
            self.history[guild_id].pop(0)

    def _build_prompt(self, guild_id: int, msg: str) -> str:
        """Constructs a conversational template to feed into GPT-3.

        The actual template itself depends on the bot's interaction mode and
        prior chat history. We need something to work off of in order for GPT-3
        to create a reasonable output.
        """
        mode = db.get_mode(guild_id)
        config = fixtures.config[mode]
        p1 = config["p1"]
        p2 = config["p2"]
        history = []
        if mode == fixtures.react:
            history = fixtures.react_history
        elif mode == fixtures.chat:
            if guild_id not in self.history:
                opener, response = fixtures.initial_chat_exchange
                self._update_history(guild_id, opener, response)
            history = self.history[guild_id]

        prompt = "" if "starter" not in config else config["starter"] + "\n"
        for (opener, response) in history:
            prompt = prompt + dedent(
                f"""
                {p1} {opener}
                {p2} {response}
                """
            ).rstrip()
        return prompt + dedent(
            f"""
            {p1} {msg}
            {p2}
            """
        ).rstrip()

    def _init_slash_commands(self):
        """Initializes all slash commands for this bot."""
        cmd = SlashCommand(self, sync_commands=True)
        # TODO: Remove guild whitelisting.
        guild_ids = [326580881965842433]
       
        @cmd.slash(
            name="help",
            description="Get help and usage details for this bot.",
            guild_ids=guild_ids,
        )
        async def _help(ctx):
            """Displays the help message for this bot."""
            await ctx.send(fixtures.help_message)

        @cmd.slash(
            name="about",
            description="Show general information about this bot.",
            guild_ids=guild_ids,
        )
        async def _about(ctx):
            """Displays the introductory message for this bot."""
            await ctx.send(fixtures.introduction)

        @cmd.slash(
            name="metrics",
            description="Show global statistics about this bot.",
            guild_ids=guild_ids,
        )
        async def _metrics(ctx):
            """Displays global statistics about this bot."""
            await ctx.send(
                dedent(
                    f"""
                    GPT-3 completions generated: {db.get_gpt_completions()}
                    Discord servers joined: {db.get_guild_count()}
                    """
                ).strip()
            )

        @cmd.slash(
            name="status",
            description="Get the general bot status and latency.",
            guild_ids=guild_ids,
        )
        async def _status(ctx):
            """Displays the bot's interaction mode and latency."""
            latency = round(self.latency * 1000, 3)
            mode = db.get_mode(ctx.guild.id)
            await ctx.send(f"I received your ping in {latency} ms. I'm currently in `{mode}` mode.")

        @cmd.slash(
            name="switch",
            description="Change the bot interaction mode.",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="mode",
                    description="How you'd like the bot to act.",
                    option_type=3,
                    required=True,
                    choices=[
                        create_choice(
                            name="Conversation Mode",
                            value=fixtures.chat,
                        ),
                        create_choice(
                            name="React Code Generator",
                            value=fixtures.react,
                        ),
                        create_choice(
                            name="Silence the bot for now",
                            value=fixtures.silence,
                        ),
                    ],
                ),
            ],
        )
        async def _switch(ctx, mode: str):
            """Changes the bot's interaction mode to the user's input choice."""
            db.switch_mode(ctx.guild.id, mode)
            await ctx.send(fixtures.switch_replies[mode])
    
        @cmd.slash(
            name="engines",
            description="List available GPT-3 engines.",
            guild_ids=guild_ids,
        )
        async def _engines(ctx):
            """Lists the available GPT-3 engines.

            This command was intended for developers and will not be helpful or
            interesting to users.
            """
            try:
                engines = gpt.engines()
                msg = "The following GPT-3 engines are available:\n"
                msg += "\n".join(map(lambda engine: f"- `{engine}`", engines))
                await ctx.send(msg)
            except OpenAIError as e:
                await ctx.send(str(e))
    
        @cmd.slash(
            name="complete",
            description="Send raw input into GPT-3 (not recommended).",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="prompt",
                    description="The raw prompt to feed GPT-3. Please wrap it in quotes.",
                    option_type=3,
                    required=True,
                ),
            ],
        )
        async def _complete(ctx, prompt: str):
            """Feeds user-specified raw input into GPT-3.

            This command was intended for developers and will not be helpful or
            interesting to users.
            """
            try:
                res = gpt.complete(prompt, max_tokens=50)
                await ctx.send(f"**{prompt[1:-1]}** {res}")
            except OpenAIError as e:
                await ctx.send(str(e))
    
        @cmd.slash(
            name="amongus",
            guild_ids=guild_ids,
            description="View the maps in Among Us.",
            options=[
                create_option(
                    name="map",
                    description="The name of the map you'd like to view.",
                    option_type=3,
                    required=True,
                    choices=[
                        create_choice(
                            name="The Skeld",
                            value=fixtures.skeld_url,
                        ),
                        create_choice(
                            name="MIRA HQ",
                            value=fixtures.mira_url,
                        ),
                        create_choice(
                            name="Polus",
                            value=fixtures.polus_url,
                        ),
                        create_choice(
                            name="The Airship",
                            value=fixtures.airship_url,
                        ),
                    ],
                ),
            ],
        )
        async def _amongus(ctx, map_url: str):
            """Displays a map from Among Us, depending on user selection."""
            await ctx.send(map_url)
 