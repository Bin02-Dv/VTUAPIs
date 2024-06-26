from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import AuthApiModelSerializer, TransactionModelSerializer
from .models import AuthApiModel, APIKey, Transaction
import jwt, datetime
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
import requests
from django.contrib.auth import authenticate

# Create your views here.

class GenerateAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Generate a new API key for the authenticated user
        user = AuthApiModel.objects.get(email=request.user)
        api_key = APIKey.objects.create(user=user)
        return Response({'api_key': str(api_key.key)})

class SignUpView(APIView):
    def post(self, request):
        serializer = AuthApiModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        phone_number = request.data['phone_number']
        password = request.data['password']

        user = AuthApiModel.objects.filter(phone_number=phone_number).first()

        if user is None:
            raise AuthenticationFailed('Phone Number not found!!')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password!!')
        
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        message = "Login success....."

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)

        response.data = {
            'jwt': token,
            'msg': message
        }
        
        return response

class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('User Unauthenticated!!')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('User Unauthenticated!!')
        
        user = AuthApiModel.objects.filter(id=payload['id']).first()

        serializer = AuthApiModelSerializer(user)

        return Response(serializer.data)

class LogoutView(APIView):

    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Logout Successful..'
        }

        return response
    
class AllUserView(APIView):

    def get(self, request):
        users = AuthApiModel.objects.all()
        serializer = AuthApiModelSerializer(users, many=True)
        return Response(serializer.data)
        # return JsonResponse({"users": serializer.data})

class AllTransactions(APIView):

    def get(self, request):
        transactions = Transaction.objects.all()
        serializer = TransactionModelSerializer(transactions, many=True)
        return Response(serializer.data)
    
class UserTransactions(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('User Unauthenticated!!')
        
        user = AuthApiModel.objects.filter(id=payload['id']).first()
        transactions = Transaction.objects.filter(user=user)
        serializer = TransactionModelSerializer(transactions, many=True)
        return Response(serializer.data)


from rest_framework.exceptions import AuthenticationFailed
import requests

class AirtimeTopUpAPIView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('User Unauthenticated!!')
        
        user = AuthApiModel.objects.filter(id=payload['id']).first()
        # Extract data from request
        phone_number = request.data.get('phone')
        amount = request.data.get('amount')
        network = request.data.get('network')

        url = 'https://arewaglobal.co/api/airtime/'
        headers = {
            'Authorization': 'Token xBG95yfClBAA37CxwIC4dACCD1A3BC5EzxcAk1o4hnCC0xFCmrt9cq6giC8A1695472756', 
            'Content-Type': 'application/json'
        }
        data = {
            "phone": phone_number,
            "network": network,
            "amount": amount
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise exception for HTTP errors
        except requests.RequestException as e:
            # Handle HTTP request errors
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service="VTU",
                message=f'Failed to top up airtime: {str(e)}', status='Failed'
            )
            new_transaction.save()
            return Response({'error': f'Failed to top up airtime: {str(e)}'}, status=500)

        if response.status_code == 200:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service="VTU",
                message=f'Airtime top-up {amount} to {phone_number} successful', status='Successful'
            )
            new_transaction.save()
            return Response({'message': f'Airtime top-up {amount} to {phone_number} successful'}, status=200)
        else:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service="VTU",
                message='Failed to top up airtime', status='Failed'
            )
            new_transaction.save()
            return Response({'error': 'Failed to top up airtime'}, status=response.status_code)
        
class DataTopUpAPIView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('User Unauthenticated!!')

        user = AuthApiModel.objects.filter(id=payload['id']).first()
        # Extract data from request
        phone_number = request.data.get('mobile_number')
        network = request.data.get('network')
        data_plan = request.data.get('data_plan')

        # Validate data
        if not all([phone_number, network, data_plan]):
            return Response({'error': 'Missing required data'}, status=400)

        # Make HTTP request to VTU API endpoint
        url = 'https://arewaglobal.co/api/data/'
        headers = {
            'Authorization': 'Token xBG95yfClBAA37CxwIC4dACCD1A3BC5EzxcAk1o4hnCC0xFCmrt9cq6giC8A1695472756',
            'Content-Type': 'application/json'
        }
        data = {
            "phone":phone_number,
            "network": network,
            "data_plan": data_plan
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service="Data",
                message=f'Failed to send the Data: {str(e)}', status='Failed'
            )
            new_transaction.save()
            return Response({'error': f'Failed to send the Data: {str(e)}'}, status=500)

        if response.status_code == 200:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service="Data",
                message=f'Data was sent to {phone_number} successfully', status='Successful'
            )
            new_transaction.save()
            return Response({'message': f'Data was sent to {phone_number} successfully'}, status=200)
        else:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service="Data",
                message='Failed to send the Data!', status='Failed'
            )
            new_transaction.save()
            return Response({'error': 'Failed to send the Data!'}, status=response.status_code)
        
class SmileTopUpAPIView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('User Unauthenticated!!')

        user = AuthApiModel.objects.filter(id=payload['id']).first()
        # Extract data from request
        phone_number = request.data.get('PhoneNumber')
        bundle_type_code = request.data.get('BundleTypeCode')
        data_plan = request.data.get('PlanId')

        # Validate data
        if not all([phone_number, bundle_type_code, data_plan]):
            return Response({'error': 'Missing required data'}, status=400)

        # Make HTTP request to VTU API endpoint
        url = 'https://arewaglobal.co/api/smile-data/'
        headers = {
            'Authorization': 'Token xBG95yfClBAA37CxwIC4dACCD1A3BC5EzxcAk1o4hnCC0xFCmrt9cq6giC8A1695472756',
            'Content-Type': 'application/json'
        }
        data = {
            "PhoneNumber": phone_number,
            "BundleTypeCode": bundle_type_code,
            "PlanId:": data_plan,
            "actype":"PhoneNumber"
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service="Smile",
                message=f'Failed to send the Data: {str(e)}', status='Failed'
            )
            new_transaction.save()
            return Response({'error': f'Failed to send the Data: {str(e)}'}, status=500)

        if response.status_code == 200:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service="Smile",
                message=f'Data was sent to {phone_number} successfully', status='Successful'
            )
            new_transaction.save()
            return Response({'message': f'Data was sent to {phone_number} successfully'}, status=200)
        else:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service="Smile",
                message='Failed to send the Data!', status='Failed'
            )
            new_transaction.save()
            return Response({'error': 'Failed to send the Data!'}, status=response.status_code)
        
class AlphaTopUpAPIView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('User Unauthenticated!!')

        user = AuthApiModel.objects.filter(id=payload['id']).first()
        # Extract data from request
        phone_number = request.data.get('phone')
        data_plan = request.data.get('planid')

        # Validate data
        if not all([phone_number, data_plan]):
            return Response({'error': 'Missing required data'}, status=400)

        # Make HTTP request to VTU API endpoint
        url = 'https://arewaglobal.co/api/alpha/'
        headers = {
            'Authorization': 'Token xBG95yfClBAA37CxwIC4dACCD1A3BC5EzxcAk1o4hnCC0xFCmrt9cq6giC8A1695472756',
            'Content-Type': 'application/json'
        }
        data = {
            "phone": phone_number,
            "planid:": data_plan
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service=data_plan,
                message=f'Failed to send the Data: {str(e)}', status='Failed'
            )
            new_transaction.save()
            return Response({'error': f'Failed to send the Data: {str(e)}'}, status=500)

        if response.status_code == 200:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service=data_plan,
                message=f'Data was sent to {phone_number} successfully', status='Successful'
            )
            new_transaction.save()
            return Response({'message': f'Data was sent to {phone_number} successfully'}, status=200)
        else:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service=data_plan,
                message='Failed to send the Data!', status='Failed'
            )
            new_transaction.save()
            return Response({'error': 'Failed to send the Data!'}, status=response.status_code)