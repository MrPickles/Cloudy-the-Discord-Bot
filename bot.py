import logging
from collections import defaultdict
from textwrap import dedent

from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from openai.error import OpenAIError

import db
import gpt
import locks


logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super(DiscordBot, self).__init__(*args, **kwargs)
        self.config = {
            "chat": {
                "p1": "Human:",
                "p2": "AI:",
                "starter": "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.",
            },
            "react": {
                "p1": "description:",
                "p2": "code:",
            },
        }
        self.history = defaultdict(list)
        self.lock = locks.Lock()
        self._init_slash_commands()
   
    async def on_ready(self):
        logger.info("We have logged in as %s", self.user)
        db.set_last_init()

    async def on_guild_join(self, guild):
        logger.info("Joined guild: %d", guild.id)
        for channel in guild.text_channels:
            # TODO: make sure this works properly
            if channel.name == "debug":
                await channel.send("Hello! I just joined.")
        db.increment_guild_count()

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.id != 705667675292172288:
            # TODO: for now, only use the debug channel
            return

        guild_id = message.guild.id
        mode = db.get_mode(guild_id)
        if mode == "silence":
            logger.debug("Bot is in silence mode. Skipping interaction in guild %d", guild_id)
            return

        prompt = self._build_prompt(guild_id, message.content)
        config = self.config[mode]
        try:
            if not self.lock.claim_lock(guild_id):
                return
            response = gpt.complete(prompt, [config["p1"], config["p2"]])
            self.lock.release_lock(guild_id)
            if mode == "chat":
                self._update_history(guild_id, message.content, response)
            elif mode == "react":
                response = f"```{response}```"
            await message.channel.send(response)
        except OpenAIError as e:
            await message.channel.send(str(e))
            self.lock.release_lock(guild_id)

        # https://discordpy.readthedocs.io/en/stable/faq.html#why-does-on-message-make-my-commands-stop-working
        await self.process_commands(message)

    def _update_history(self, guild_id: int, opener: str, response: str):
        self.history[guild_id].append((opener, response))
        if len(self.history[guild_id]) > 10:
            self.history[guild_id].pop(0)

    def _build_prompt(self, guild_id: int, msg: str) -> str:
        mode = db.get_mode(guild_id)
        config = self.config[mode]
        p1 = config["p1"]
        p2 = config["p2"]
        history = []
        if mode == "react":
            history = [
                (
                    "a red button that says stop",
                    "<button style={{color: 'white', backgroundColor: 'red'}}>Stop</button>",
                ),
                (
                    "a blue box that contains 3 yellow circles with red borders",
                    "<div style={{backgroundColor: 'blue', padding: 20}}><div style={{backgroundColor: 'yellow', border: '5px solid red', borderRadius: '50%', padding: 20, width: 100, height: 100}}></div><div style={{backgroundColor: 'yellow', borderWidth: 1, border: '5px solid red', borderRadius: '50%', padding: 20, width: 100, height: 100}}></div><div style={{backgroundColor: 'yellow', borderWidth: 1, border: '5px solid red', borderRadius: '50%', padding: 20, width: 100, height: 100}}></div></div>",
                ),
            ]
        elif mode == "chat":
            if guild_id not in self.history:
                self._update_history(
                    guild_id,
                    "Hello, who are you?",
                    "I am an AI created by OpenAI. How can I help you today?",
                )
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
        cmd = SlashCommand(self, sync_commands=True)
        guild_ids = [326580881965842433]
       
        @cmd.slash(
            name="help",
            description="Get help and usage details for this bot.",
            guild_ids=guild_ids,
        )
        async def _help(ctx):
            await ctx.send(
                dedent(
                    f"""
                    Hello! :wave: I'm Big Bob, your virtual friend powered by GPT-3! To get started, send a message in this server and see how I respond.

                    I also support several commands that you can invoke:

                    :robot: `/about`: Displays general information about me.
                    :question: `/help`: Displays this message.
                    :traffic_light: `/status`: Checks my latency and interaction mode.
                    :bar_chart: `/metrics`: Lists global statistics about me.
                    :currency_exchange: `/switch`: Changes my interaction mode. I can have a conversation, generate React code, or stay silent.
                    :steam_locomotive: `/engines`: Lists available GPT-3 engines. (Not recommended.)
                    :tickets: `/complete`: Sends raw input to GPT-3 for completion. (Not recommended.)
                    :knife: `/amongus`: Displays the selected map for the game _Among Us_. This has nothing to do with AI, but it's still useful...
                    """
                ).strip()
            )

        @cmd.slash(
            name="about",
            description="Show general information about this bot.",
            guild_ids=guild_ids,
        )
        async def _about(ctx):
            await ctx.send(
                # TODO: Add links and whatnot
                dedent(
                    f"""
                    Hello! :wave: I'm Big Bob, your virtual friend powered by GPT-3! To get started, send a message in this server and see how I respond.
                    """
                ).strip()
            )

        @cmd.slash(
            name="metrics",
            description="Show global statistics about this bot.",
            guild_ids=guild_ids,
        )
        async def _metrics(ctx):
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
                            value="chat",
                        ),
                        create_choice(
                            name="React Code Generator",
                            value="react",
                        ),
                        create_choice(
                            name="Silence the bot for now",
                            value="silence",
                        ),
                    ],
                ),
            ],
        )
        async def _switch(ctx, mode: str):
            db.switch_mode(ctx.guild.id, mode)
            replies = {
                "chat": "I'm in chat mode. Say something and we can have an AI-powered conversation.",
                "react": "I will now generate code. Describe a UI you'd like to see, and I'll generate the React code!",
                "silence": "I'm in silent mode now. I won't answer messages on this server unless otherwise configured.",
            }
            await ctx.send(replies[mode])
    
        @cmd.slash(
            name="engines",
            description="List available GPT-3 engines.",
            guild_ids=guild_ids,
        )
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
                            value="https://media.discordapp.net/attachments/757358510911520879/757415061663907870/skeldmapguidev2.png",
                        ),
                        create_choice(
                            name="MIRA HQ",
                            value="https://i.redd.it/8i1kd1mp9ij51.png",
                        ),
                        create_choice(
                            name="Polus",
                            value="https://cdn.discordapp.com/attachments/757358510911520879/792121876192690176/polus.jpg",
                        ),
                        create_choice(
                            name="The Airship",
                            value="https://imgur.com/4gQUZn8",
                        ),
                    ],
                ),
            ],
        )
        async def _amongus(ctx, map_url: str):
            await ctx.send(map_url)
 