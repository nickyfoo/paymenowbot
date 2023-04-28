import requests
from .util.util import edit_message_with_keyboard, SELECT_ALL, CLEAR_ALL
from .util.context import context, token

def answer_callback(callback_id):
  url = f'https://api.telegram.org/bot{token}/answerCallbackQuery'
  payload = {'callback_query_id': callback_id}
  resp = requests.post(url, json=payload)


def handle_callback(callback):
  callback_query = callback['callback_query']
  callback_data = callback_query['data']
  callback_id = callback_query['id']
  chat_id = callback_query['message']['chat']['id']
  message_id = callback_query['message']['message_id']

  execute_callback(chat_id, callback_data)
  answer_callback(callback_id)
  edit_message_with_keyboard(chat_id, message_id)


def execute_callback(chat_id, name):
  involved_names = context.chat_data[chat_id].involved_names
  names = context.chat_data[chat_id].names
  if name == SELECT_ALL:
    if len(involved_names) != len(names):
      involved_names.update(names)
  elif name == CLEAR_ALL:
    if len(involved_names) != 0:
      involved_names.clear()
  elif name in involved_names:
    involved_names.remove(name)
  else:
    involved_names.add(name)
  print(involved_names)