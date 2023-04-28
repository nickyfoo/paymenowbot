from collections import defaultdict
import os

class Context:
  def __init__(self):
    self.chat_data = defaultdict(ChatContext)

class ChatContext:
  def __init__(self):
    self.names = []
    self.involved_names = set()
    self.cost_per_person = defaultdict(float)

context = Context()
token = os.environ['TOKEN']
