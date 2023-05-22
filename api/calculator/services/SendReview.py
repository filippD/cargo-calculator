import requests
import environ

class SendReview:
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
New review was left

name: {self.params["name"]}
company: {self.params.get("company")}
review: {self.params.get("review")}
rating: {self.params["rating"]}
'''
