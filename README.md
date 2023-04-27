# paymebot
paymebot is a telegram bot that provides a convenient way to split the costs of your meal and be able to account for additional charges.

## Implementation overview

`paymebot.py` is the polling version of the bot, which regularly polls the Telegram API looking for any updates. It was implemented with the python-telegram-bot library, which helps to abstract a lot of the lower level details away.

`webhook.py` is the webhook version of the bot, which receives a POST request from Telegram whenever there's an update for the bot. This was implemented with Flask. Requests to the Telegram API were done with the requests library, and state was managed using an in-memory dict mapping each chat id to its respective state.

## Hosting
Since the heroku free tier died, hosting has been tough :(

Initially I was hosting the polling version of the bot on pythonanywhere's bash console. But whenever the pythonanywhere servers are restarted, that bot will be shut down and not restarted. 

As such, I refactored it to the webhook version, which would be able to be hosted as a web app on pythonanywhere. Unfortunately there were [consistent problems](https://www.pythonanywhere.com/forums/topic/31919/) with getting updates from Telegram

Finally settled on what I think is quite an interesting combination: repl.it with uptimerobot.com.
We host the web app on repl.it, and keep it alive with regular (5 min) pings from uptimerobot.com.

## Learnings
It was fun finally getting to write a Telegram bot. It gave me some insight into how Telegram works.

Webhooks and general http interactions
API and how to communicate with the Telegram servers
Telegram specific features like InlineKeyboards 
Debugging deployments

## Future work
Additional features like a breakdown of the items, only problem being I'm not sure how to implement an undo/remove item feature nicely, since it would depend on something like unique item names.

The current solution wouldn't be scalable, but for a pet project like this I wouldn't expect a lot of traffic anyway
I think it would be good to regularly purge the in-memory dict, or even extend to a db.

I'm not actually sure how well the bot works with simultaneous users - one thing to consider would be using [Python coroutines with async await](https://realpython.com/async-io-python/)

Some error handling and forced reply prompts - currently we're assuming a very nice user. E.g. since we store people involved in a payment in a set, we get some undesired behaviour from non-distinct names being input.

Consider making a docker image to host on fly.io's free tier

