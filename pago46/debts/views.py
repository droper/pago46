# encoding: utf-8
"""Views of debts app"""
from datetime import datetime

from django.db.models import Sum, F, Count

from rest_framework import generics
from rest_framework.response import Response

from .serializers import UserSerializer, DebtSerializer
from .models import User, Debt, DebtAccumulate


class SettleUpView(generics.GenericAPIView):

    queryset = User.objects.all()

    def get(self, request):
        """Return a list of user objects"""
        user_objects = []
        # Obtain the users names from the request, delete blank spaces
        # and filter in the User model.
        users = self.get_queryset()
        users_names = request.query_params.get("users")

        if users_names:
            user_names_list = list(map(str.strip, request.query_params.get("users").split(",")))
            users = users.filter(username__in=user_names_list).order_by("username")

        for user in users:
            # Obtain the sum of debts by each lender and borrower
            owes = (
                Debt.objects.filter(borrower=user)
                .values("lender__username")
                .order_by("lender__username")
                .annotate(amount=Sum("amount"))
            )
            owed_by = (
                Debt.objects.filter(lender=user)
                .values("borrower__username")
                .order_by("borrower__username")
                .annotate(amount=Sum("amount"))
            )
            owes_dict = {}
            owes_sum = 0
            for item in owes:
                owes_dict[item["lender__username"]] = item["amount"]
                owes_sum += item["amount"]
            owed_by_dict = {}
            owed_by_sum = 0
            for item in owed_by:
                owed_by_dict[item["borrower__username"]] = item["amount"]
                owed_by_sum += item["amount"]

            user_object = {
                "name": user.username,
                "owes": DebtAccumulate.owed(user),
                "owed_by": DebtAccumulate.owers(user),
                "balance": DebtAccumulate.balance(user)
            }
            user_objects.append(user_object)

        return Response(user_objects)


class AddUserView(generics.ListCreateAPIView):
    """Add new user"""

    def post(self, request):
        """Create a new user"""

        # If there is a user parameter and the username is not repeated
        # Create a new user and return the user object, else, return nothing
        if "user" in request.query_params:
            username = request.query_params.get("user")
            if not User.objects.filter(username=username).exists():
                new_user = User(username=username)
                new_user.save()
                user_object = {
                    "name": new_user.username,
                    "owes": {},
                    "owed_by": {},
                    "balance": 0
                }
                return Response(user_object)
        return Response()


class CreateIOUView(generics.ListCreateAPIView):
    """Add new IOU"""

    def post(self, request):
        """Create a new debt"""
        try:
            lender = request.query_params["lender"]
            borrower = request.query_params["borrower"]
            amount = float(request.query_params["amount"])
        except KeyError as e:
            print(f"There is no {e} data in the request")
        except ValueError as v:
            print(f"Invalid {v} value for amount")

        lender = User.objects.get(username=lender)
        borrower = User.objects.get(username=borrower)
        expiration_date = datetime.now()

        # If there are a lender and a borrower
        if lender and borrower:
            debt = Debt(
                lender=lender,
                borrower=borrower,
                amount=amount,
                expiration_date=expiration_date
            )
            debt.save()
