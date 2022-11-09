# encoding: utf-8
"""Tests of debts app"""

from datetime import datetime, timedelta

import pytest

from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.timezone import make_aware

from debts.models import User, Debt, DebtAccumulate
from debts.views import create_user_object


@pytest.fixture
def users(db):
    """Returns a lender and a borrower"""

    user1 = User.objects.create_user("user1", "user1@dummy.com", "pass")
    user1.save()
    user2 = User.objects.create_user("user2", "user2@dummy.com", "pass")
    user2.save()
    user3 = User.objects.create_user("user3", "user3@dummy.com", "pass")
    user3.save()
    user4 = User.objects.create_user("user4", "user4@dummy.com", "pass")
    user4.save()
    users = {
        "user1": user1,
        "user2": user2,
        "user3": user3,
        "user4": user4,
    }
    return users


class TestDebtModel:
    """Tests for the Debt model"""

    model = Debt
    date = make_aware(datetime.now() + timedelta(days=20))

    def test_clean(self, users):
        """Test if clean validates that lender and borrower are different"""

        # Test if the debt with two different users is created
        debt1 = self.model(
            lender=users["user1"],
            borrower=users["user2"],
            amount=50,
            expiration_date=self.date,
        )
        debt1.save()
        assert debt1.lender == users["user1"]

        # Test if the debt with the same user as lender and borrower raises an exception
        debt2 = self.model(
            lender=users["user1"],
            borrower=users["user1"],
            amount=50,
            expiration_date=self.date,
        )
        with pytest.raises(ValidationError) as exc:
            debt2.save()
        assert type(exc.value) == ValidationError

    def test_save(self, users):
        """Test if save updates the DebtAccumulate model"""

        amount = 50
        # Test if DebtAccumulate is created when adding a debt with a new pair of lender and borrower
        debt1 = self.model(
            lender=users["user1"],
            borrower=users["user2"],
            amount=amount,
            expiration_date=self.date,
        )
        debt1.save()
        acc = DebtAccumulate.objects.get(lender=users["user1"], borrower=users["user2"])
        assert acc.total_amount == amount

        # Test if a DebtAccumulate row is updated adding a debt with an existing pair of lender and borrower
        debt2 = self.model(
            lender=users["user1"],
            borrower=users["user2"],
            amount=amount,
            expiration_date=self.date,
        )
        debt2.save()
        acc = DebtAccumulate.objects.get(lender=users["user1"], borrower=users["user2"])
        assert acc.total_amount == amount * 2


class TestDebtAccumulateModel:
    """Tests for the DebtAccumulate models"""

    model = DebtAccumulate
    debt = Debt
    date = make_aware(datetime.now() + timedelta(days=20))

    def test_user_debtors(self, users):
        """Test owers method"""

        amount = 50
        # Test if the user_debtors method return a dict with the borrowers and the amount
        debt1 = self.debt(
            lender=users["user1"],
            borrower=users["user2"],
            amount=amount,
            expiration_date=self.date,
        )
        debt1.save()
        debt2 = self.debt(
            lender=users["user1"],
            borrower=users["user2"],
            amount=amount,
            expiration_date=self.date,
        )
        debt2.save()
        debt3 = self.debt(
            lender=users["user1"],
            borrower=users["user3"],
            amount=amount,
            expiration_date=self.date,
        )
        debt3.save()

        data = {
            users["user2"].username: 2 * amount,
            users["user3"].username: amount,
        }

        assert DebtAccumulate.user_debtors(users["user1"]) == data

    def test_user_creditors(self, users):
        """Test owed method"""

        amount = 50
        # Test if the user_creditors method return a dict with the lenders and the amount
        debt1 = self.debt(
            lender=users["user2"],
            borrower=users["user1"],
            amount=amount,
            expiration_date=self.date,
        )
        debt1.save()
        debt2 = self.debt(
            lender=users["user2"],
            borrower=users["user1"],
            amount=amount,
            expiration_date=self.date,
        )
        debt2.save()
        debt3 = self.debt(
            lender=users["user3"],
            borrower=users["user1"],
            amount=amount,
            expiration_date=self.date,
        )
        debt3.save()

        data = {
            users["user2"].username: 2 * amount,
            users["user3"].username: amount,
        }

        assert DebtAccumulate.user_creditors(users["user1"]) == data

    def test_balance(self, users):
        """Test balance method"""

        amount = 50
        # Create debts
        debt1 = self.debt(
            lender=users["user1"],
            borrower=users["user2"],
            amount=amount,
            expiration_date=self.date,
        )
        debt1.save()
        debt2 = self.debt(
            lender=users["user1"],
            borrower=users["user2"],
            amount=amount,
            expiration_date=self.date,
        )
        debt2.save()
        debt3 = self.debt(
            lender=users["user2"],
            borrower=users["user1"],
            amount=amount,
            expiration_date=self.date,
        )
        debt3.save()

        # Test if the balance is correct
        assert DebtAccumulate.balance(users["user1"]) == amount
        assert DebtAccumulate.balance(users["user2"]) == -amount
        # Test if the balance for a user with no registers is 0
        assert DebtAccumulate.balance(users["user3"]) == 0


def test_settleup(users):
    """Test the /settleup endpoint"""

    endpoint_url = reverse("settleup")
    date = make_aware(datetime.now() + timedelta(days=20))

    client = APIClient()

    # Test if the endpoint returns all the user objects if there is no data
    response = client.get(path=endpoint_url, format="json")
    data = []
    for user in users.values():
        data.append(create_user_object(user))
    assert response.status_code == status.HTTP_200_OK
    assert response.data == data

    amount = 20
    # Test if the endpoint returns the appropiate data
    debt1 = Debt(
        lender=users["user1"],
        borrower=users["user2"],
        amount=amount,
        expiration_date=date,
    )
    debt1.save()
    debt2 = Debt(
        lender=users["user1"],
        borrower=users["user2"],
        amount=amount,
        expiration_date=date,
    )
    debt2.save()
    debt3 = Debt(
        lender=users["user2"],
        borrower=users["user1"],
        amount=amount,
        expiration_date=date,
    )
    debt3.save()

    data = [create_user_object(users["user1"]), create_user_object(users["user2"])]

    response = client.get(
        path=endpoint_url, data={"users": "user1,user2"}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == data


def test_add(db):
    """Test the /add endpoint"""

    endpoint_url = reverse("add")

    client = APIClient()

    # If there is no user in the data sent, then the response is None
    response = client.post(path=endpoint_url, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data is None

    # Test if the user is created and if it returns the user object
    username = "user1"
    response = client.post(path=endpoint_url, data={"user": username}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert User.objects.filter(username=username).exists() is True
    user = User.objects.get(username=username)
    assert response.data == create_user_object(user)


def test_iou(db, users):
    """Test the /iou endpoint"""

    endpoint_url = reverse("iou")

    client = APIClient()

    # If there is no user data sent, it will raise a KeyError exception
    with pytest.raises(KeyError) as exc:
        client.post(path=endpoint_url, format="json")
    assert type(exc.value) == KeyError

    # If amount is not a number, it will raise a ValueError
    data = {
        "lender": "user1",
        "borrower": "user2",
        "amount": "text",
        "expiration": "2022-11-20",
    }
    with pytest.raises(ValueError) as exc:
        client.post(path=endpoint_url, data=data, format="json")
    assert type(exc.value) == ValueError

    # If a no existent user is pass as lender or borrower, it must raise
    # a User.DoesNotExist exception
    data["lender"] = "user_no_existent"
    data["amount"] = 50
    with pytest.raises(User.DoesNotExist) as exc:
        client.post(path=endpoint_url, data=data, format="json")
    assert type(exc.value) == User.DoesNotExist

    data["lender"] = "user1"
    data["borrower"] = "user_no_existent"
    with pytest.raises(User.DoesNotExist) as exc:
        client.post(path=endpoint_url, data=data, format="json")
    assert type(exc.value) == User.DoesNotExist

    # The happy path, test if the endpoint returns the user object
    # from lender and borrower
    data["borrower"] = "user2"
    response_data = {
        "users": [
            {"name": "user1", "owes": {}, "owed_by": {"user2": 50}, "balance": 50},
            {"name": "user2", "owes": {"user1": 50.00}, "owed_by": {}, "balance": -50},
        ]
    }
    response = client.post(path=endpoint_url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data == response_data
