import requests
import environ

class SendPaymentRequest:
  def __init__(self, email):
    env = environ.Env()
    environ.Env.read_env()
    self.chatId = env('TG_CHAT_ID')
    token = env('BOT_TOKEN')
    self.apiURL = f'https://api.telegram.org/bot{token}/sendMessage'
    self.email = email

  def call(self):
    try:
        response = requests.post(
          self.apiURL,
          json={'chat_id': self.chatId, 'text': self.user_info()}
        )
        print(response.text)
    except Exception as e:
        print(e)

  def user_info(self):
    return f'''
New payment request

email: {self.email}
'''
