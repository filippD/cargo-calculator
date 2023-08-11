import requests
import environ

class ModifyPaymentEmailRequest:
  def __init__(self, user_email, communication_email):
    env = environ.Env()
    environ.Env.read_env()
    self.chatId = env('TG_CHAT_ID')
    token = env('BOT_TOKEN')
    self.apiURL = f'https://api.telegram.org/bot{token}/sendMessage'
    self.user_email = user_email
    self.communication_email = communication_email

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
Requested new email for payment communication

user email: {self.user_email}
requested communication email: {self.communication_email}
'''
