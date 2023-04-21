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
New request

company: {self.params["company"]}
message: {self.params["message"]}
name: {self.params["name"]}
phone: {self.params["phone"]}

Segments:
{self.request_info_segments()}
'''

  def request_info_segments(self):
    segmentsString = ""
    for segment in self.params["segments"]:
      segmentsString += f'''------------
ARR: {segment["ARR"]}
Aircraft: {segment["Aircraft"]}
DEP: {segment["DEP"]}
Number of Flights: {segment["Number of Flights"]}
Total Flight Time: {segment["Total Flight Time"]}
Total Price: {segment["Total Price"]}
'''
    return segmentsString
