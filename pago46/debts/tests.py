from datetime import datetime, timedelta

#from model_bakery import baker
import factory
import json
import pytest

from django.core.exceptions import ValidationError

from debts.models import User, Debt, DebtAccumulate


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

    @pytest.mark.django_db
    def test_clean(self, users):
        """Test if clean validates that lender and borrower are different"""

        # Test if the debt with two different users is created
        debt1 = self.model(lender=users["user1"], borrower=users["user2"], amount=50,
                           expiration_date=datetime.now() + timedelta(days=20))
        debt1.save()
        assert debt1.lender == users["user1"]

        # Test if the debt with the same user as lender and borrower raises an exception
        debt2 = self.model(lender=users["user1"], borrower=users["user1"], amount=50,
                           expiration_date=datetime.now() + timedelta(days=20))
        with pytest.raises(ValidationError) as exc:
            debt2.save()
        assert exc.value == ValidationError({'__all__': ["Lender and borrower can't be the same"]})


    def test_save(self, users):
        """Test if save updates the DebtAccumulate model"""

        amount = 50
        # Test if DebtAccumulate is created when adding a debt with a new pair of lender and borrower
        debt1 = self.model(lender=users["user1"], borrower=users["user2"], amount=amount,
                           expiration_date=datetime.now() + timedelta(days=20))
        debt1.save()
        acc = DebtAccumulate.objects.get(lender=users["user1"], borrower=users["user2"])
        assert acc.total_amount == amount

        # Test if a DebtAccumulate row is updated adding a debt with an existing pair of lender and borrower
        debt2 = self.model(lender=users["user1"], borrower=users["user2"], amount=amount,
                           expiration_date=datetime.now() + timedelta(days=20))
        debt2.save()
        acc = DebtAccumulate.objects.get(lender=users["user1"], borrower=users["user2"])
        assert acc.total_amount == amount*2


class TestDebtAccumulateModel:
    """Tests for the DebtAccumulate models"""

    model = DebtAccumulate
    debt = Debt

    def test_user_debtors(self, users):
        """Test owers method"""

        amount = 50
        # Test if the user_debtors method return a dict with the borrowers and the amount
        debt1 = self.debt(lender=users["user1"], borrower=users["user2"], amount=amount,
                          expiration_date=datetime.now() + timedelta(days=20))
        debt1.save()
        debt2 = self.debt(lender=users["user1"], borrower=users["user2"], amount=amount,
                          expiration_date=datetime.now() + timedelta(days=20))
        debt2.save()
        debt3 = self.debt(lender=users["user1"], borrower=users["user3"], amount=amount,
                          expiration_date=datetime.now() + timedelta(days=20))
        debt3.save()

        data = {
            users["user2"].username: 2*amount,
            users["user3"].username: amount,
        }

        assert DebtAccumulate.user_debtors(users["user1"]) == data

    def test_user_creditors(self, users):
        """Test owed method"""

        amount = 50
        # Test if the user_creditors method return a dict with the lenders and the amount
        debt1 = self.debt(lender=users["user2"], borrower=users["user1"], amount=amount,
                          expiration_date=datetime.now() + timedelta(days=20))
        debt1.save()
        debt2 = self.debt(lender=users["user2"], borrower=users["user1"], amount=amount,
                          expiration_date=datetime.now() + timedelta(days=20))
        debt2.save()
        debt3 = self.debt(lender=users["user3"], borrower=users["user1"], amount=amount,
                          expiration_date=datetime.now() + timedelta(days=20))
        debt3.save()

        data = {
            users["user2"].username: 2*amount,
            users["user3"].username: amount,
        }

        assert DebtAccumulate.user_creditors(users["user1"]) == data

    def test_balance(self, users):
        """Test balance method"""

        amount = 50
        # Create debts
        debt1 = self.debt(lender=users["user1"], borrower=users["user2"], amount=amount,
                          expiration_date=datetime.now() + timedelta(days=20))
        debt1.save()
        debt2 = self.debt(lender=users["user1"], borrower=users["user2"], amount=amount,
                          expiration_date=datetime.now() + timedelta(days=20))
        debt2.save()
        debt3 = self.debt(lender=users["user2"], borrower=users["user1"], amount=amount,
                          expiration_date=datetime.now() + timedelta(days=20))
        debt3.save()

        # Test if the balance is correct
        assert DebtAccumulate.balance(users["user1"]) == amount
        assert DebtAccumulate.balance(users["user2"]) == -amount
        # Test if the balance for a user with no registers is 0
        assert DebtAccumulate.balance(users["user3"]) == 0
