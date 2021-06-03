# Cloudy - The Hacker's Assistant

Cloudy is a friendly Discord bot, designed to help a Discord server full of hackers of all interests.
Cloudy has various talents depending on the situation:

* AI-powered chat if you're lonely or need someone to bounce ideas off of.
* Generates react code from your description to help with coding
* Shows you the map in Among Us when you're feeling social and want to have some recreation.

Invite him to your server with [this link][1].

_Imagine a demo video link here_

* also link to GH
* link to REPLIT
* link to my twitter or something

## User Guide & Features

Below are some features of what Cloudy can do.

### AI chat

* it'll use GPT-3 to be a chat bot
* use `/switch` to use chat mode; though this is the default
* there is some semblance of memory here
* it can chat with you or answer questions; the world's your oyster

### Code Generator

* also uses GPT-3
* just `/switch` to change it to code mode
* describe the UI you want and it'll spit out react code

### Among Us Maps

* this is a slash command `/amongus`
* you can pick from 4 maps
* that's about it, but it's remarkably helpful

### ...and more!

* use `/about` and `/help` when in doubt
* `/metrics` for global stats
* `/switch` to change modes or silence the bot
* other fun easter eggs

## Developer Guide

### having a local running bot

* fork this repl
* make a discord app and discord bot account
* and set the account permissions and whatnot
* get the token and set it as your env
* get an openAI API key (optional)
* run the bot

## how to operate GPT-3 under the hood

* create a "warmup" history to "train" the bot
* if you have memory, append to the history
* for slash commands, we use an extension library


[1]: https://discord.com/oauth2/authorize?client_id=847843661973684224&permissions=18496&scope=bot%20applications.commands