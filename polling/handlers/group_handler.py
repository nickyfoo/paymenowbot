from .util.util import *
from telegram.ext import CommandHandler

async def set_names(update, context):
    names = context.args
    context.chat_data.__init__()
    context.chat_data.names = names
    await update.message.reply_text(get_reply_text(context), reply_markup=build_keyboard(names))

group_handler = CommandHandler('group', set_names)