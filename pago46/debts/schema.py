import graphene
from graphene_django import DjangoObjectType

from django.contrib.auth import get_user_model

from .models import Debt

User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ('username',)


class DebtType(DjangoObjectType):
    class Meta:
        model = Debt
        fields = ('id', 'lender', 'borrower', 'expiration_date')


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    debts = graphene.List(DebtType)

    def resolve_users(root, info, **kwargs):
        # Querying a list
        return User.objects.all()

    def resolve_debts(root, info, **kwargs):
        # Querying a list
        return Debt.objects.all()


schema = graphene.Schema(query=Query)
