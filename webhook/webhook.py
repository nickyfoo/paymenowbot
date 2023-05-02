from flask import Flask
from flask import request, Response

app = Flask(__name__)

from handlers.util.context import token
from handlers.callback_handler import handle_callback
from handlers.command_handler import handle_command

@app.route(f'/{token}', methods=['POST', 'GET'])
def index():
  if request.method == 'POST':
    msg = request.get_json()
    print(msg)
    if 'callback_query' in msg:
      handle_callback(msg)
    else:
      try:
        handle_command(msg)
      except KeyError:
        pass
    return Response('ok', status=200)
  else:
    return Response('ok', status=200)


if __name__ == '__main__':
  app.run(host='0.0.0.0')
