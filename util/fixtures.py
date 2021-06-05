from textwrap import dedent

# This file contains constant values that are used throughout this REPL.

# URL to add this bot to your Discord server.
auth_url = "https://discord.com/api/oauth2/authorize?client_id=847843661973684224&permissions=18496&scope=bot%20applications.commands"

# Bot modes.
chat = "chat"
react = "react"
silence = "silence"

# Links for the images of maps in Among Us.
skeld_url = "https://media.discordapp.net/attachments/757358510911520879/757415061663907870/skeldmapguidev2.png"
mira_url = "https://i.redd.it/8i1kd1mp9ij51.png"
polus_url = "https://cdn.discordapp.com/attachments/757358510911520879/792121876192690176/polus.jpg"
airship_url = "https://imgur.com/4gQUZn8"

# The maximum amount of "memory" the bot will have for a given server's conversation.
max_history_length = 10

# GPT-3 configuration values depending on bot mode.
config = {
    chat: {
        "p1": "Human:",
        "p2": "AI:",
        "starter": "The following is a conversation with an AI assistant. The assistant's name is Cloudy. The assistant is helpful, creative, clever, and very friendly.",
    },
    react: {
        "p1": "description:",
        "p2": "code:",
    },
}

# Description message when joining servers.
introduction = dedent(
    f"""
    Hello! :wave: I'm Cloudy, your virtual friend powered by GPT-3! To get started, send a message in this server and I'll respond.
    """
).strip()

# Help message from the bot.
help_message = dedent(
    f"""
    Hello! :wave: I'm Cloudy, your virtual friend powered by GPT-3! To get started, send a message in this server and see how I respond.

    I also support several commands that you can invoke:

    :robot: `/about`: Displays general information about me.
    :question: `/help`: Displays this message.
    :traffic_light: `/status`: Checks my latency and interaction mode.
    :bar_chart: `/metrics`: Lists global statistics about me.
    :currency_exchange: `/switch`: Changes my interaction mode. I can have a conversation, generate React code, or stay silent.
    :steam_locomotive: `/engines`: Lists available GPT-3 engines. (Not recommended.)
    :tickets: `/complete`: Sends raw input to GPT-3 for completion. (Not recommended.)
    :knife: `/amongus`: Displays the selected map for the game _Among Us_.
    :coin: `/eth`: Executes various subcommands related to Ethereum.
    """
).strip()

# Response messages when switching to various interaction modes.
switch_replies = {
    chat: "I'm in chat mode. Say something and we can have an AI-powered conversation.",
    react: "I will now generate code. Describe a UI you'd like to see, and I'll generate the React code!",
    silence: "I'm in silent mode now. I won't answer messages on this server unless otherwise configured.",
}

# Default messaging history when doing React code generation.
react_history = [
    (
        "a red button that says stop",
        "<button style={{color: 'white', backgroundColor: 'red'}}>Stop</button>",
    ),
    (
        "a blue box that contains 3 yellow circles with red borders",
        dedent(
            """
            <div style={{backgroundColor: 'blue', padding: 20}}>
                <div style={{backgroundColor: 'yellow', borderWidth: 1, border: '5px solid red', borderRadius: '50%', padding: 20, width: 100, height: 100}}></div>
                <div style={{backgroundColor: 'yellow', borderWidth: 1, border: '5px solid red', borderRadius: '50%', padding: 20, width: 100, height: 100}}></div>
                <div style={{backgroundColor: 'yellow', borderWidth: 1, border: '5px solid red', borderRadius: '50%', padding: 20, width: 100, height: 100}}></div>
            </div>
            """
        ).replace("\n", ""),
    ),
]

# Default messaging history when doing AI-based conversational chat.
initial_chat_exchange = ("Hello, who are you?", "My name is Cloudy. I am an AI created by Andrew Liu. How can I help you today?")

# A generic error message to show during failed commands.
generic_error_message = "Oops! Cloudy ran into an unknown error while handling your command."

# The message show show for if Cloudy is missing an Etherscan API key.
missing_etherscan_api_key_msg = "Sorry! I'm missing an Etherscan API key, so I can't help you right now. Please try again later."

# Hmm, what's this?
definitely_silent = {
    "bitcoin": "https://tenor.com/T1Ro.gif",
    "catan": "https://gfycat.com/flawlessbigheartedcapybara-catan",
    "elon": "https://gph.is/2M7iQRP",
    "trigger": "https://gfycat.com/eagereminentamethystinepython",
    "time": "https://i.imgur.com/CoWZ05t.gif",
}