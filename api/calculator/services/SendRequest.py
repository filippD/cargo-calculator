import requests


class SendRequest:
  def __init__(self, params):
    token = "5871171868:AAETw8Q8jpl-V2odBjP32lH9BBbtgGRKHf0"
    self.apiURL = f'https://api.telegram.org/bot{token}/sendMessage'
    self.params = params

  def call(self):
    

    try:
        response = requests.post(
          self.apiURL,
          json={'chat_id': '199003199', 'text': self.request_info()}
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
