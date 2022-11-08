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
        fields = ('lender', 'borrower', "amount", 'expiration_date')


class Query(graphene.ObjectType):
    expired_debts = graphene.List(DebtType, datetime=graphene.DateTime())

    def resolve_expired_debts(self, info, datetime):
        """Return the debts that expires after the datetime"""

        return Debt.objects.filter(expiration_date__lt=datetime)


schema = graphene.Schema(query=Query)
