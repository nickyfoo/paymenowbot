from .util.context import context
from .util.util import send_message_with_keyboard

def group_handler(chat_id, names):
  context.chat_data[chat_id].__init__()
  context.chat_data[chat_id].names = names
  print(names)
  send_message_with_keyboard(chat_id)

