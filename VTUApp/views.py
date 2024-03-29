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
        email = request.data['email']
        password = request.data['password']

        user = AuthApiModel.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('Email not found!!')
        
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
        phone_number = request.data.get('mobile_number')
        amount = request.data.get('amount')
        network = request.data.get('network')

        url = 'https://www.gladtidingsdata.com/api/topup/'
        headers = {
            'Authorization': 'Token 8224e7a261e7eef4af78f922b8f8e63a6f6aecf4', 
            'Content-Type': 'application/json'
        }
        data = {
            "network": network,
            "amount": amount,
            "mobile_number": phone_number,
            "Ported_number": True,
            "airtime_type": "VTU"
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise exception for HTTP errors
        except requests.RequestException as e:
            # Handle HTTP request errors
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service=data['airtime_type'],
                message=f'Failed to top up airtime: {str(e)}', status='Failed'
            )
            new_transaction.save()
            return Response({'error': f'Failed to top up airtime: {str(e)}'}, status=500)

        if response.status_code == 200:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service=data['airtime_type'],
                message=f'Airtime top-up to {phone_number} successful', status='Successful'
            )
            new_transaction.save()
            return Response({'message': f'Airtime top-up to {phone_number} successful'}, status=200)
        else:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service=data['airtime_type'],
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
        plan_id = request.data.get('plan')

        # Validate data
        if not all([phone_number, network, plan_id]):
            return Response({'error': 'Missing required data'}, status=400)

        # Make HTTP request to VTU API endpoint
        url = 'https://www.gladtidingsdata.com/api/data/'
        headers = {
            'Authorization': 'Token 8224e7a261e7eef4af78f922b8f8e63a6f6aecf4',
            'Content-Type': 'application/json'
        }
        data = {
            "network": network,
            "mobile_number": phone_number,
            "plan": plan_id,
            "Ported_number": True,
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service=plan_id,
                message=f'Failed to send the Data: {str(e)}', status='Failed'
            )
            new_transaction.save()
            return Response({'error': f'Failed to send the Data: {str(e)}'}, status=500)

        if response.status_code == 200:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service=plan_id,
                message=f'Data was sent to {phone_number} successfully', status='Successful'
            )
            new_transaction.save()
            return Response({'message': f'Data was sent to {phone_number} successfully'}, status=200)
        else:
            new_transaction = Transaction.objects.create(
                user=user, email_user=user.email, service=plan_id,
                message='Failed to send the Data!', status='Failed'
            )
            new_transaction.save()
            return Response({'error': 'Failed to send the Data!'}, status=response.status_code)