import logging
import math
from collections import defaultdict
from typing import DefaultDict, Optional, Set
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ExtBot,
    TypeHandler,
)



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

SELECT_ALL = "SELECT ALL"
CLEAR_ALL = "CLEAR ALL"

def build_keyboard(names: list[str]) -> InlineKeyboardMarkup:
    """Helper function to build the next inline keyboard."""
    return InlineKeyboardMarkup.from_column(
        [InlineKeyboardButton(name, callback_data=name) for name in names] + [InlineKeyboardButton(SELECT_ALL, callback_data=SELECT_ALL), InlineKeyboardButton(CLEAR_ALL, callback_data=CLEAR_ALL)]
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='''
    Welcome to paymebot, a convenient way to split the costs of your meal and be able to account for additional charges.

Start off by making a group of people (be careful, this clears all existing data!)
The /group command accepts a space separated list of people,
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
''')

async def set_people(update: Update, context: ContextTypes.DEFAULT_TYPE):
    names = context.args
    context.chat_data.__init__()
    context.chat_data.names = names
    await update.message.reply_text(get_reply_text(context), reply_markup=build_keyboard(names))


def get_price(price_str: str):
    return float(price_str)
        
def get_split_price(price: float, num_people: int):
    if (num_people==0): return 0
    return price/num_people
    
def get_ceil_price(price:float):
    return math.ceil(price*100)/100

def get_cost_output(costs: DefaultDict[str,float]):
    return '\n'.join([f'{key}: {get_ceil_price(val)}' for key, val in costs.items()])

def get_involved_names_output(involved_names: Set[str]) -> str:
    if involved_names:
        return ', '.join(involved_names)
    else:
        return "no one"

def get_reply_text(context: ContextTypes.DEFAULT_TYPE):
    return f'Current costs are:\n{get_cost_output(context.cost_per_person)}\n\nSo far you\'ve selected {get_involved_names_output(context.involved_names)}. Select (or deselect) the next person:'

async def person_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def add_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_price(context.args[0])
    num_people = len(context.involved_names)
    split_price = get_split_price(price,num_people)
    
    for name in context.involved_names:
        context.cost_per_person[name] += split_price
        
    await context.bot.send_message(chat_id=update.effective_chat.id, text = get_reply_text(context), 
        reply_markup=build_keyboard(context.chat_data.names))

#give the percentage of tax to be added in percent
async def add_tax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    tax = float(context.args[0])
    for key, val in context.cost_per_person.items():
        context.cost_per_person[key] = val*(100+tax)/100
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text = get_reply_text(context),
                                   reply_markup=build_keyboard(context.chat_data.names))

class ChatData:
    """Custom class for chat_data. Here we store data per message."""
    def __init__(self) -> None:
        self.cost_per_person: DefaultDict[str, float] = defaultdict(float)
        self.names: list = []
        self.involved_names: Set[str] = set()



# The [ExtBot, dict, ChatData, dict] is for type checkers like mypy
class CustomContext(CallbackContext[ExtBot, dict, ChatData, dict]):
    """Custom class for context."""

    def __init__(self, application: Application, chat_id: int = None, user_id: int = None):
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self._message_id: Optional[int] = None

    @property
    def names(self) -> list[str]:
        return self.chat_data.names

    @property
    def involved_names(self) -> Set[str]:
        return self.chat_data.involved_names
    
    @property
    def cost_per_person(self) -> defaultdict(float):
        return self.chat_data.cost_per_person

    @classmethod
    def from_update(cls, update: object, application: "Application") -> "CustomContext":
        """Override from_update to set _message_id."""
        # Make sure to call super()
        context = super().from_update(update, application)

        if context.chat_data and isinstance(update, Update) and update.effective_message:
            # pylint: disable=protected-access
            context._message_id = update.effective_message.message_id

        # Remember to return the object
        return context


if __name__ == '__main__':
    context_types = ContextTypes(context=CustomContext, chat_data=ChatData)
    application = ApplicationBuilder().token('TOKEN').context_types(context_types).build()
    
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', start)
    set_list_handler = CommandHandler('group', set_people)
    add_cost_handler = CommandHandler('add', add_cost)
    add_tax_handler = CommandHandler('addtax', add_tax)
    
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(set_list_handler)
    application.add_handler(add_cost_handler)
    application.add_handler(add_tax_handler)
    application.add_handler(CallbackQueryHandler(person_button))
    
    application.run_polling()

