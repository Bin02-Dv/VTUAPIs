from django.urls import path
from .views import SignUpView, LoginView, UserView, LogoutView, AllUserView, GenerateAPIKeyView, AirtimeTopUpAPIView, DataTopUpAPIView, AllTransactions

urlpatterns = [
    path('api-keys/', GenerateAPIKeyView.as_view(), name='generate_api_key'),
    path('user/signup', SignUpView.as_view()),
    path('user/login', LoginView.as_view()),
    path('user/logout', LogoutView.as_view()),
    path('user/', UserView.as_view()),
    path('', AllUserView.as_view()),

    # Buy Airtime
    path('vtu/airtime', AirtimeTopUpAPIView.as_view()),
    # Buy Data
    path('vtu/data', DataTopUpAPIView.as_view()),
    # All Transactions
    path('vtu/transactions', AllTransactions.as_view()),
]