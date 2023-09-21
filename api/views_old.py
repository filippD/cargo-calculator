from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.calculator.Client import Client
from api.Airports import Airports
from api.Authorize import Authorize
import json
import environ
from google.cloud import recaptchaenterprise_v1
from django.contrib.auth import authenticate
from .models import User, UserSession
from rest_framework.permissions import IsAuthenticated
from .serializers import CurrentUserSerializer, UserSessionSerializer
from django.forms.models import model_to_dict
from rest_framework_simplejwt.tokens import RefreshToken
import pandas as pd

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

    if request.user.is_authenticated:
      if request.user.is_premium or request.user.searches_left > 0:
        if not request.user.is_premium:
          request.user.searches_left = request.user.searches_left - 1
          request.user.save()
        response = Client.calculate(params)
        return Response({"flights": response, "searches_left": request.user.searches_left}, status=status.HTTP_200_OK)
      else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    else:
      session = UserSession.objects.get(session_id=params.get("session_id"))
      if session and session.searches_left > 0:
        session.searches_left = session.searches_left - 1
        session.save()
        response = Client.calculate(params)
        return Response({"flights": response, "searches_left": session.searches_left}, status=status.HTTP_200_OK)
      else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

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

class CharterCompanyApiView(APIView):
  authentication_classes = []
  permission_classes = []
  def post(self, request, charter_id):
    df = pd.read_csv('base.csv', sep=";")
    charter_company = df[df["reg"] == charter_id]
    # res = charter_company
    df_output = pd.DataFrame()
    df_output["airline"] = charter_company["airline"]
    df_output["email"] = charter_company['email'].fillna('') if not charter_company['email'].empty else charter_company['email']
    df_output["phone"] = charter_company['phone'].fillna('') if not charter_company['phone'].empty else charter_company['phone']
    df_output["link"] = charter_company['link'].fillna('') if not charter_company['link'].empty else charter_company['link']
    df_output["form"] = charter_company['form'].fillna('') if not charter_company['form'].empty else charter_company['form']
    df_output["Operator"] = charter_company['operator'].fillna('') if not charter_company['operator'].empty else charter_company['operator']
    rsp = df_output.to_dict("records")
    # rsp = res.to_dict("records")
    # rsp = json.dumps(charter_company.to_dict("records"), allow_nan=True)

		# Client.send_review(json.loads(request.body))
    return Response(rsp, status=status.HTTP_200_OK)

class RequestPaymentApiView(APIView):
  permission_classes = (IsAuthenticated, )

  def post(self, request, *args, **kwargs):
    Client.send_payment_request(request.user.email)
    return Response(status=status.HTTP_200_OK)

class ModifyPaymentEmailApiView(APIView):
  permission_classes = (IsAuthenticated, )

  def post(self, request, *args, **kwargs):
    params = json.loads(request.body)
    Client.modify_payment_email_request(request.user.email, params.get("email"))
    return Response(status=status.HTTP_200_OK)

class AuthorizeApiView(APIView):
	def post(self, request, *args, **kwargs):
		response = Authorize.call(self, json.loads(request.body))
		print(response)
		return Response(response, status=status.HTTP_200_OK)

class SignUpApiView(APIView):
    def post(self, request, *args, **kwargs):
      # try:
        params = json.loads(request.body)
        if params.get("session_id"):
          try:
            session = UserSession.objects.get(session_id=params.get("session_id"))
          except UserSession.DoesNotExist:
              session = None
        else:
          session = None

        searches_left = session.searches_left if session else 5
        user = User(
          
        )
        user = User.objects.create_user(
          params.get("email"),
          params.get("email"),
          params.get("password"),
          searches_left=searches_left,
          company_name=params.get("company_name"),
          name=params.get("name"),
          work_type=params.get("work_type")
        )
        refresh = RefreshToken.for_user(user)
        return Response(
          {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
          },
          status=status.HTTP_200_OK
        )
      # except Exception:
      #   return Response(status=status.HTTP_400_BAD_REQUEST)

class UserApiView(APIView):
  serializer_class = CurrentUserSerializer
  permission_classes = (IsAuthenticated, )

  def get(self, request, *args, **kwargs):
    serializer = self.serializer_class(data=model_to_dict(request.user))
    if serializer.is_valid():
      return Response(serializer.data, status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_401_UNAUTHORIZED)

class SessionsApiView(APIView):
  # serializer_class = UserSessionSerializer
  
  def get(self, request, *args, **kwargs):
    session = UserSession.objects.get(session_id=request.GET.get('session_id'))
    # serializer = self.serializer_class(data=model_to_dict(session))
    if session:
      return Response({"searches_left": session.searches_left, "session_id": session.session_id}, status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_404_NOT_FOUND)
  
  def post(self, request, *args, **kwargs):
    session = UserSession.objects.create()
    # serializer = self.serializer_class(data=model_to_dict(session))
    if session:
      return Response({"searches_left": session.searches_left, "session_id": session.session_id}, status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_404_NOT_FOUND)

class LoginApiView(APIView):
  def post(self, request, *args, **kwargs):
    params = json.loads(request.body)
    user = authenticate(username=params.get('email'), password=params.get('password'))
    if user is not None:
      refresh = RefreshToken.for_user(user)
      return Response(
        {
          'refresh': str(refresh),
          'access': str(refresh.access_token),
        },
        status=status.HTTP_200_OK
      )
    else:
      return Response(status=status.HTTP_401_UNAUTHORIZED)

class LogoutApiView(APIView):
  permission_classes = (IsAuthenticated,)
  def post(self, request):
    try:
      refresh_token = request.data["refresh_token"]
      token = RefreshToken(refresh_token)
      token.blacklist()
      return Response(status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
      return Response(status=status.HTTP_400_BAD_REQUEST)

class UploadApiView(APIView):
  authentication_classes = []
  permission_classes = []
  def post(self, request, *args, **kwargs):
    env = environ.Env()
    environ.Env.read_env()
    if request.headers["Authorization"].split(" ")[1] == env('ADMIN_TOKEN'):
      newFile = request.FILES['file']
      handle_uploaded_file(newFile)
      return Response(status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_401_UNAUTHORIZED)

class UpdateToPremiumApiView(APIView):
  authentication_classes = []
  permission_classes = []
  def post(self, request, *args, **kwargs):
    env = environ.Env()
    environ.Env.read_env()
    params = json.loads(request.body)
    # try:
    if request.headers["Authorization"].split(" ")[1] == env('ADMIN_TOKEN'):
      user = User.objects.get(email=params.get("email"))
      user.is_premium = True
      user.save()
      return Response(status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_401_UNAUTHORIZED)
    # except:
    #   return Response(status=status.HTTP_400_BAD_REQUEST)

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
        # print(
        #     "The CreateAssessment call failed because the token was "
        #     + "invalid for for the following reasons: "
        #     + str(response.token_properties.invalid_reason)
        # )
        return

    # Check if the expected action was executed.
    if response.token_properties.action != recaptcha_action:
        # print(
        #     "The action attribute in your reCAPTCHA tag does"
        #     + "not match the action you are expecting to score"
        # )
        return
    # else:
        # Get the risk score and the reason(s)
        # For more information on interpreting the assessment,
        # see: https://cloud.google.com/recaptcha-enterprise/docs/interpret-assessment
        # for reason in response.risk_analysis.reasons:
            # print(reason)
        # print(
        #     "The reCAPTCHA score for this token is: "
        #     + str(response.risk_analysis.score)
        # )
        # Get the assessment name (id). Use this to annotate the assessment.
        # assessment_name = client.parse_assessment_path(response.name).get("assessment")
        # print(f"Assessment name: {assessment_name}")
    return response
