from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.calculator.Client import Client
from api.Airports import Airports
from api.Authorize import Authorize
import json
import time
import environ
from google.cloud import recaptchaenterprise_v1

class CalculateApiView(APIView):
	def post(self, request, *args, **kwargs):
		params = json.loads(request.body)
		env = environ.Env()
		environ.Env.read_env()
		captcha_assesment = create_assessment(
			project_id=env('GOOGLE_PROJECT_ID'),
			recaptcha_site_key=env('RECAPTCHA_SITE_KEY'),
			token=params.get("recaptchaToken"),
			recaptcha_action="formSearch"
		)
		if captcha_assesment.risk_analysis.score < 0.5:
			return Response(status=status.HTTP_403_FORBIDDEN)

		response = Client.calculate(params)
		time.sleep(1)
		return Response(response, status=status.HTTP_200_OK)

class RequestsApiView(APIView):
	def post(self, request, *args, **kwargs):
		Client.send_request(json.loads(request.body))
		return Response(status=status.HTTP_200_OK)

class AirportsApiView(APIView):
	def post(self, request, *args, **kwargs):
		response = Airports.find(json.loads(request.body))
		return Response(response, status=status.HTTP_200_OK)

class ReviewsApiView(APIView):
	def post(self, request, *args, **kwargs):
		Client.send_review(json.loads(request.body))
		return Response(status=status.HTTP_200_OK)

class AuthorizeApiView(APIView):
	def post(self, request, *args, **kwargs):
		response = Authorize.call(json.loads(request.body))
		print(response)
		return Response(response, status=status.HTTP_200_OK)

class UploadApiView(APIView):
	def post(self, request, *args, **kwargs):
		env = environ.Env()
		environ.Env.read_env()
		if request.headers["Authorization"].split(" ")[1] == env('ADMIN_TOKEN'):
			newFile = request.FILES['file']
			handle_uploaded_file(newFile)
			return Response(status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)

def handle_uploaded_file(file):
	with open("base.csv", "wb+") as destination:
		for chunk in file.chunks():
			destination.write(chunk)


def create_assessment(
    project_id: str, recaptcha_site_key: str, token: str, recaptcha_action: str
):
    client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()

    # Set the properties of the event to be tracked.
    event = recaptchaenterprise_v1.Event()
    event.site_key = recaptcha_site_key
    event.token = token

    assessment = recaptchaenterprise_v1.Assessment()
    assessment.event = event

    project_name = f"projects/{project_id}"

    # Build the assessment request.
    request = recaptchaenterprise_v1.CreateAssessmentRequest()
    request.assessment = assessment
    request.parent = project_name

    response = client.create_assessment(request)

    # Check if the token is valid.
    if not response.token_properties.valid:
        print(
            "The CreateAssessment call failed because the token was "
            + "invalid for for the following reasons: "
            + str(response.token_properties.invalid_reason)
        )
        return

    # Check if the expected action was executed.
    if response.token_properties.action != recaptcha_action:
        print(
            "The action attribute in your reCAPTCHA tag does"
            + "not match the action you are expecting to score"
        )
        return
    else:
        # Get the risk score and the reason(s)
        # For more information on interpreting the assessment,
        # see: https://cloud.google.com/recaptcha-enterprise/docs/interpret-assessment
        for reason in response.risk_analysis.reasons:
            print(reason)
        print(
            "The reCAPTCHA score for this token is: "
            + str(response.risk_analysis.score)
        )
        # Get the assessment name (id). Use this to annotate the assessment.
        assessment_name = client.parse_assessment_path(response.name).get("assessment")
        print(f"Assessment name: {assessment_name}")
    return response
