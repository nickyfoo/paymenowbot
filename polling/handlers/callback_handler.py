from .util.util import *
from telegram.ext import CallbackQueryHandler

async def person_button(update, context):
    query = update.callback_query
    await query.answer()
    name = query.data
    if name==SELECT_ALL:
        context.involved_names.update(context.names)
    elif name==CLEAR_ALL:
        context.involved_names.clear()
    elif name in context.involved_names:
        context.involved_names.remove(name)
    else:
        context.involved_names.add(query.data)
    print(context.involved_names)

    await query.edit_message_text(
        text=get_reply_text(context),
        reply_markup=build_keyboard(context.chat_data.names),
    )

callback_handler = CallbackQueryHandler(person_button)