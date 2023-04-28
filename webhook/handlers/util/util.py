from .context import context, token
import requests
import json
import math


def get_involved_names_output(chat_id):
  involved_names = context.chat_data[chat_id].involved_names
  if involved_names:
    return ', '.join(involved_names)
  else:
    return "no one"


SELECT_ALL = "SELECT ALL"
CLEAR_ALL = "CLEAR ALL"

def get_ceil_price(price: float):
  return math.ceil(price * 100) / 100

def get_cost_output(chat_id):
  costs = context.chat_data[chat_id].cost_per_person
  return '\n'.join(
    [f'{key}: {get_ceil_price(val)}' for key, val in costs.items()])


def get_button(name):
  return [{'text': name, 'callback_data': name}]

def build_keyboard(chat_id):
  """Helper function to build the next inline keyboard."""
  names = context.chat_data[chat_id].names + [SELECT_ALL, CLEAR_ALL]

  return [get_button(name) for name in names]

def get_reply_markup(chat_id):
  return json.dumps({'inline_keyboard': build_keyboard(chat_id)})

def get_reply_text(chat_id):
  return f'Current costs are:\n{get_cost_output(chat_id)}\n\nSo far you\'ve selected {get_involved_names_output(chat_id)}. Select (or deselect) the next person:'


def send_message(chat_id, text):
  url = f'https://api.telegram.org/bot{token}/sendMessage'
  payload = {'chat_id': chat_id, 'text': text}
  resp = requests.post(url, json=payload)
  return resp

def send_message_with_keyboard(chat_id):
  url = f'https://api.telegram.org/bot{token}/sendMessage'
  payload = {
    'chat_id': chat_id,
    'text': get_reply_text(chat_id),
    'reply_markup': get_reply_markup(chat_id)
  }
  resp = requests.post(url, json=payload)
  return resp

def edit_message_with_keyboard(chat_id, message_id):
  url = f'https://api.telegram.org/bot{token}/editMessageText'
  payload = {
    'chat_id': chat_id,
    'message_id': message_id,
    'text': get_reply_text(chat_id),
    'reply_markup': get_reply_markup(chat_id)
  }
  resp = requests.post(url, json=payload)
  return resp

