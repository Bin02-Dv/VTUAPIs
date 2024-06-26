from rest_framework import serializers
from .models import AuthApiModel, Transaction

class AuthApiModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthApiModel
        fields = ['id', 'name', 'email', 'password', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class TransactionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'email_user', 'service', 'message', 'status']