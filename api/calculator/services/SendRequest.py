import requests
import environ

class SendRequest:
  def __init__(self, params):
    env = environ.Env()
    environ.Env.read_env()
    self.chatId = env('TG_CHAT_ID')
    token = env('BOT_TOKEN')
    self.apiURL = f'https://api.telegram.org/bot{token}/sendMessage'
    self.params = params

  def call(self):
    

    try:
        response = requests.post(
          self.apiURL,
          json={'chat_id': self.chatId, 'text': self.request_info()}
        )
        print(response.text)
    except Exception as e:
        print(e)

  def request_info(self):
    return f'''
New {self.params["type"]} request

name: {self.params["name"]}
email: {self.params["email"]}
company: {self.params.get("company")}
cargo description: {self.params.get("cargo_description")}
additional information: {self.params.get("additional_information")}
departure airport: {self.params.get("departure_airport")}
arrival airport: {self.params.get("arrival_airport")}
departure date: {self.params.get("departure_date")}
payload: {self.params.get("payload")}
'''
