# twitch-betbot

[![Build Status](https://travis-ci.org/tefa-dev/twitch-betbot.svg?branch=master)](https://travis-ci.org/tefa-dev/twitch-betbot)

`BetBot` is a twitch bot for viewers to bet streamer game results. We support only battleroyale gameplay for now, eg. Fortnite, PUBG, H1Z1... We are looking into LOL/CSGO supports.

This project intends to enhance twitch community experience while live streams, by helping streamers to reward their viewers through an interactive type-in interface deployed by BetBot.

### Requirement

- Python 2.7.x

### Get started

- Clone the project and run `python setup.py install` from its root folder. This compiles source after fetching librairies. This step can be skipped by downloading latest binaries here.
- Edit `config.cfg` with your personal information such as moderator list, oauth key, channel name...
- Start the bot by running `python start.py`

### Battleroyale
Features: 
- Only the first participant to find the right position is a winner. Therefore the game rewards only one viewer per game instance. At least for now!
- Only the last placement inputted by a user is taken accounted for final bet result.

#### Commands

##### Moderators

Only moderators defined within configuration file are allowed to perform theses actions. Beware sending 20 commands that needs an answer from the bot within a 30 seconds period will lock out the bot for 8 hours due to Twitch limiatations.

- `!cmdbet` Lists available moderator commands.
- `!startbet` Enters in lobby mode. Viewers can bet placements using `!top` command.
- `!stopbet` Stops the bets. This is when the streamer starts his battleroyale game.
- `!final <placement>` Notifies final placement in term of streamer's game to the bot. This outputs the winner name if any.
- `!statusbet` Returns current game state. Either 'init', 'lobby' or 'game'.
- `!lastwinner` Outputs last winner name.

##### Viewers

- `!top <placement>` Bets the streamer final placement. 
    This can be only done within 'lobby' state. Moderators can also send this command.

### Language

All bot output is customizable with your language preferences. To do so, edit `language.cfg` by replacing current text fields or adding a new section. Section header is the key passed to bot configuration file for informing which language section to use.

### CLI

- `python start.py` Starts bot.
- `python setup.py install` Installs librairies and builds project.
- `python setup.py clean --all` Cleans all built files.
- `python test.py` Runs tests.

### Contribution

Feel free to contact us if you have any suggestions or feedbacks to share! Pull requests are also welcomed!
