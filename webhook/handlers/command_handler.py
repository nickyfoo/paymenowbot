from .help_handler import help_handler
from .group_handler import group_handler
from .add_handler import add_handler
from .addtax_handler import addtax_handler

def parse_message(message):
  chat_id = message['message']['chat']['id']
  txt = message['message']['text']
  return chat_id, txt


def execute_command(chat_id, command):
  toks = command.split()
  if len(toks) == 0: return
  if toks[0] in ['/start', '/help']:
    help_handler(chat_id)
  elif toks[0] in ['/group']:
    group_handler(chat_id, toks[1:])
  elif toks[0] in ['/add']:
    add_handler(chat_id, toks[1:])
  elif toks[0] in ['/addtax']:
    addtax_handler(chat_id, toks[1:])

def handle_command(msg):
    chat_id, command = parse_message(msg)
    execute_command(chat_id, command)

    