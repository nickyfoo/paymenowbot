from .util.context import context
from .util.util import send_message_with_keyboard

#give the percentage of tax to be added in percent
def addtax_handler(chat_id, toks):
  if len(toks) == 0: return
  try:
    tax = float(toks[0])
    cost_per_person = context.chat_data[chat_id].cost_per_person
    for key, val in cost_per_person.items():
      cost_per_person[key] = val * (100 + tax) / 100

    send_message_with_keyboard(chat_id)
  except ValueError:
    return
