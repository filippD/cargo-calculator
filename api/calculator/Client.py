from api.calculator.services.Calculate import Calculate
from api.calculator.services.SendRequest import SendRequest
from api.calculator.services.SendReview import SendReview

class Client:
    def calculate(params):
        return Calculate(params).call()

    def send_request(params):
        return SendRequest(params).call()

    def send_review(params):
        return SendReview(params).call()
