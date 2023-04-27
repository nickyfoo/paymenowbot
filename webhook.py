import math
import json
from collections import defaultdict
import requests

from flask import Flask
from flask import request, Response
from flask_sslify import SSLify

import os

app = Flask(__name__)
sslify = SSLify(app)

token = os.environ['TOKEN']

help_message = '''
Welcome to paymebot, a convenient way to split the costs of your meal and be able to account for additional charges.

Start off by making a group of people (be careful, this clears all existing data!)
The /group command accepts a space separated list of (unique) people,
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
'''


class Context:

  def __init__(self):
    self.chat_data = defaultdict(ChatContext)


class ChatContext:

  def __init__(self):
    self.names = []
    self.involved_names = set()
    self.cost_per_person = defaultdict(float)


context = Context()


def get_involved_names_output(chat_id):
  involved_names = context.chat_data[chat_id].involved_names
  if involved_names:
    return ', '.join(involved_names)
  else:
    return "no one"


SELECT_ALL = "SELECT ALL"
CLEAR_ALL = "CLEAR ALL"


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


def help_handler(chat_id):
  send_message(chat_id, help_message)


def group_handler(chat_id, names):
  context.chat_data[chat_id].__init__()
  context.chat_data[chat_id].names = names
  print(names)
  send_message_with_keyboard(chat_id)


def parse_message(message):
  chat_id = message['message']['chat']['id']
  txt = message['message']['text']
  return chat_id, txt


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


def get_split_price(price: float, num_people: int):
  if (num_people == 0): return 0
  return price / num_people


def get_ceil_price(price: float):
  return math.ceil(price * 100) / 100


def get_cost_output(chat_id):
  costs = context.chat_data[chat_id].cost_per_person
  return '\n'.join(
    [f'{key}: {get_ceil_price(val)}' for key, val in costs.items()])


def add_cost(chat_id, toks):
  if len(toks) == 0: return
  price = float(toks[0])
  involved_names = context.chat_data[chat_id].involved_names
  num_people = len(involved_names)
  split_price = get_split_price(price, num_people)

  for name in involved_names:
    context.chat_data[chat_id].cost_per_person[name] += split_price

  send_message_with_keyboard(chat_id)


#give the percentage of tax to be added in percent
def add_tax(chat_id, toks):
  if len(toks) == 0: return
  tax = float(toks[0])
  cost_per_person = context.chat_data[chat_id].cost_per_person
  for key, val in cost_per_person.items():
    cost_per_person[key] = val * (100 + tax) / 100

  send_message_with_keyboard(chat_id)


def execute_command(chat_id, command):
  toks = command.split()
  if len(toks) == 0: return
  if toks[0] in ['/start', '/help']:
    help_handler(chat_id)
  elif toks[0] in ['/group']:
    group_handler(chat_id, toks[1:])
  elif toks[0] in ['/add']:
    add_cost(chat_id, toks[1:])
  elif toks[0] in ['/addtax']:
    add_tax(chat_id, toks[1:])


@app.route('/', methods=['POST', 'GET'])
def index():
  if request.method == 'POST':
    msg = request.get_json()
    print(msg)
    if 'callback_query' in msg:
      handle_callback(msg)
    else:
      chat_id, command = parse_message(msg)
      execute_command(chat_id, command)
    return Response('ok', status=200)
  else:
    return Response('ok', status=200)


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
