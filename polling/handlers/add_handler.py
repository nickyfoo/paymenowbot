from .util.util import *
from telegram.ext import CommandHandler

async def add_cost(update, context):
    price = get_price(context.args[0])
    num_people = len(context.involved_names)
    split_price = get_split_price(price,num_people)
    
    for name in context.involved_names:
        context.cost_per_person[name] += split_price
        
    await context.bot.send_message(chat_id=update.effective_chat.id, text = get_reply_text(context), 
        reply_markup=build_keyboard(context.chat_data.names))
    
add_handler = CommandHandler('add', add_cost)