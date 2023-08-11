from api.calculator.services.Calculate import Calculate
from api.calculator.services.SendRequest import SendRequest
from api.calculator.services.SendReview import SendReview
from api.calculator.services.SendPaymentRequest import SendPaymentRequest
from api.calculator.services.ModifyPaymentEmailRequest import ModifyPaymentEmailRequest

class Client:
    def calculate(params):
        return Calculate(params).call()

    def send_request(params):
        return SendRequest(params).call()

    def send_review(params):
        return SendReview(params).call()

    def send_payment_request(email):
        return SendPaymentRequest(email).call()

    def modify_payment_email_request(user_email, communication_email):
        return ModifyPaymentEmailRequest(user_email, communication_email).call()
