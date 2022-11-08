# encoding: utf-8
"""Views of debts app"""
from datetime import datetime


from rest_framework import generics
from rest_framework.response import Response

from .serializers import DebtSerializer
from .models import User, DebtAccumulate


def create_user_object(user):
    """Create the user object"""
    user_object = {
        "name": user.username,
        "owes": DebtAccumulate.user_creditors(user),
        "owed_by": DebtAccumulate.user_debtors(user),
        "balance": DebtAccumulate.balance(user)
    }
    return user_object

class SettleUpView(generics.ListAPIView):

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
            user_objects.append(create_user_object(user))

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
                return Response(create_user_object(new_user))
        return Response()


class CreateIOUView(generics.ListCreateAPIView):
    """Add new IOU"""

    serializer_class = DebtSerializer

    def post(self, request):
        """Create a new debt"""

        # If there is one parameter missing raise an Exception
        try:
            lender = request.query_params["lender"]
            borrower = request.query_params["borrower"]
            amount = request.query_params["amount"]
            expiration_date = request.query_params["expiration"]
        except KeyError as e:
            raise KeyError(f"There is no {e} data in the request")

        # Validate the values of amount and expiration
        try:
            amount = float(amount)
        except ValueError as v:
            raise ValueError("Invalid value for amount")

        try:
            expiration_date = datetime.strptime(expiration_date, '%d/%m/%Y')
        except ValueError as v:
            raise ValueError("Invalid value for expiration")

        # Raise and exception if there is no lender or borrower
        try:
            lender = User.objects.get(username=lender)
        except User.DoesNotExist as u:
            raise User.DoesNotExist(f"There is no user {lender}")

        try:
            borrower = User.objects.get(username=borrower)
        except User.DoesNotExist as u:
            raise User.DoesNotExist(f"There is no user {borrower}")

        # If there are a lender and a borrower
        if lender and borrower:
            debt_data = {
                "lender": lender.id,
                "borrower": borrower.id,
                "amount": amount,
                "expiration_date": expiration_date
            }
            serializer = self.serializer_class(data=debt_data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"users": [create_user_object(lender), create_user_object(borrower)]})

        return Response()

