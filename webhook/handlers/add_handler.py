from .util.context import context
from .util.util import send_message_with_keyboard

def get_split_price(price: float, num_people: int):
  if (num_people == 0): return 0
  return price / num_people

def add_handler(chat_id, toks):
  if len(toks) == 0: return
  try:
    price = float(toks[0])
    involved_names = context.chat_data[chat_id].involved_names
    num_people = len(involved_names)
    split_price = get_split_price(price, num_people)

    for name in involved_names:
      context.chat_data[chat_id].cost_per_person[name] += split_price

    send_message_with_keyboard(chat_id)
  except ValueError:
    return
