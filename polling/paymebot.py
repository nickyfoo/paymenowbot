from collections import defaultdict
import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    ContextTypes,
    ExtBot,
)
from handlers.help_handler import start_handler, help_handler
from handlers.group_handler import group_handler
from handlers.add_handler import add_handler
from handlers.addtax_handler import addtax_handler
from handlers.callback_handler import callback_handler


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class ChatData:
    """Custom class for chat_data. Here we store data per message."""
    def __init__(self):
        self.cost_per_person = defaultdict(float)
        self.names = []
        self.involved_names = set()


# The [ExtBot, dict, ChatData, dict] is for type checkers like mypy
class CustomContext(CallbackContext[ExtBot, dict, ChatData, dict]):
    """Custom class for context."""

    def __init__(self, application, chat_id = None, user_id = None):
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self._message_id = None

    @property
    def names(self):
        return self.chat_data.names

    @property
    def involved_names(self):
        return self.chat_data.involved_names
    
    @property
    def cost_per_person(self):
        return self.chat_data.cost_per_person

    @classmethod
    def from_update(cls, update, application):
        """Override from_update to set _message_id."""
        # Make sure to call super()
        context = super().from_update(update, application)

        if context.chat_data and isinstance(update, Update) and update.effective_message:
            context._message_id = update.effective_message.message_id

        # Remember to return the object
        return context


if __name__ == '__main__':
    context_types = ContextTypes(context=CustomContext, chat_data=ChatData)
    application = ApplicationBuilder().token(os.environ['TOKEN']).context_types(context_types).build()
     
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(group_handler)
    application.add_handler(add_handler)
    application.add_handler(addtax_handler)
    application.add_handler(callback_handler)
    
    application.run_polling()

