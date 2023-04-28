from .util.util import *
from telegram.ext import CommandHandler

#give the percentage of tax to be added in percent
async def add_tax(update, context):
    tax = float(context.args[0])
    for key, val in context.cost_per_person.items():
        context.cost_per_person[key] = val*(100+tax)/100
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text = get_reply_text(context),
                                   reply_markup=build_keyboard(context.chat_data.names))
    
addtax_handler = CommandHandler('addtax', add_tax)