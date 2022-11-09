# encoding: utf-8
"""Serializers for the models in the api"""

from django.contrib.auth.models import User

from rest_framework import routers, serializers, viewsets

from .models import Debt


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ["username"]


class DebtSerializer(serializers.ModelSerializer):
    """Serializer for Debt model"""

    class Meta:
        model = Debt
        fields = ["lender", "borrower", "amount", "expiration_date"]
