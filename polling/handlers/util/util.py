import math
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

SELECT_ALL = "SELECT ALL"
CLEAR_ALL = "CLEAR ALL"

def get_price(price_str):
    return float(price_str)
        
def get_split_price(price, num_people):
    if (num_people==0): return 0
    return price/num_people
    
def get_ceil_price(price):
    return math.ceil(price*100)/100

def get_cost_output(costs):
    return '\n'.join([f'{key}: {get_ceil_price(val)}' for key, val in costs.items()])

def get_involved_names_output(involved_names):
    if involved_names:
        return ', '.join(involved_names)
    else:
        return "no one"

def get_reply_text(context):
    return f'Current costs are:\n{get_cost_output(context.cost_per_person)}\n\nSo far you\'ve selected {get_involved_names_output(context.involved_names)}. Select (or deselect) the next person:'

def build_keyboard(names):
    """Helper function to build the next inline keyboard."""
    return InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton(name, callback_data=name) for name in names] + [InlineKeyboardButton(SELECT_ALL, callback_data=SELECT_ALL), InlineKeyboardButton(CLEAR_ALL, callback_data=CLEAR_ALL)]
    )



