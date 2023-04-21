from api.calculator.services.Calculate import Calculate
from api.calculator.services.SendRequest import SendRequest

class Client:
    def calculate(params):
        return Calculate(params).call()

    def send_request(params):
        return SendRequest(params).call()
