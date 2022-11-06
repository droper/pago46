from rest_framework import routers, serializers, viewsets

from django.contrib.auth.models import User

from .models import Debt


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = ['lender', 'borrower', 'amount', 'expiration_date']