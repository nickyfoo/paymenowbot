from telegram.ext import CommandHandler

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='''
    Welcome to paymebot, a convenient way to split the costs of your meal and be able to account for additional charges.

Start off by making a group of people (be careful, this clears all existing data!)
The /group command accepts a space separated list of people,
e.g. "/group alice bob charlie"

From the prompt that appears, select the people who are involved in the current transaction you're recording (you can deselect people who aren't involved by tapping their name)
e.g. select bob, charlie

Add the transaction with /add, which accepts the cost of the transaction in dollars (no units, just numbers)
(You can remove a transaction by adding the negative amount for the same group of people)
e.g. "/add 420.69"
This will split the money among all the people who are involved, i.e. bob and charlie.

Finally, add the tax(es) with /addtax, which accepts the tax in percent (no units, just numbers)
e.g. "/addtax 18.8"
This adds a tax of 18.8% to all recorded transactions.

You can then copy and paste the costs to send to your friends :)
''')

start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', start)