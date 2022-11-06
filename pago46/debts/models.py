# encoding: utf-8
"""Models for debts app"""

from django.contrib.auth.models import User

from django.db import models
from django.db.models import Sum, Q


class Debt(models.Model):
    """Debts from one user to another"""

    lender = models.ForeignKey(User, related_name='lender_user', on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, related_name='borrower_user', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateTimeField()

    class Meta:
        ordering = ['-expiration_date']

    def save(self):
        """Update the accumulated debt when creating a new debt"""

        # If there is an accumulated debt for the pair, obtain it and update the amount,
        # if not, create a new one.
        debt_accumulated, created = (
            DebtAccumulate.objects.get_or_create(
                lender=self.lender,
                borrower=self.borrower,
                defaults={"amount": self.amount}
            )
        )
        if created:
            debt_accumulated.amount += self.amount
            debt_accumulated.save()
        super(Debt, self).save()


class DebtAccumulate(models.Model):
    """Saves the accumulated debt between users"""

    lender = models.ForeignKey(User, related_name='lender', on_delete=models.CASCADE, unique=True)
    borrower = models.ForeignKey(User, related_name='borrower', on_delete=models.CASCADE, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    @classmethod
    def owers(cls, lender):
        """Returns all the users that have borrowed from the lender and the amount"""

        debts = cls.objects.filter(lender=lender).values("borrower_username", "amount")
        owers_dict = {}
        for item in debts:
            owers_dict[item["borrower__username"]] = item["amount"]
        return owers_dict

    @classmethod
    def owed(cls, borrower):
        """Returns all the users that have lended to the borrower and the amount"""

        debts = cls.objects.filter(borrower=borrower).values("lender__username", "amount")
        owed_dict = {}
        for item in debts:
            owed_dict[item["lender__username"]] = item["amount"]
        return owed_dict

    @classmethod
    def update(cls, lender, borrower):
        """Update the amount for the lender and borrower"""

        # Filter the debt with the lender and borrower and obtain the total amount
        # if there are no debts, return False
        amount = (
            Debt.objects.filter(lender=lender, borrower=borrower)
            .annotate(amount=Sum("amount"))
        )

        if not amount:
            return False

        # If there is a register, update the accumulated amount, if not
        # create a new one with the amount
        debt_accumulate = cls.objects.update_or_create(lender=lender, borrower=borrower, defaults={"amount": amount})
        debt_accumulate.save()
        return True

    @classmethod
    def balance(cls, user):
        """Return the balance of a user"""

        owed_by_dict = cls.owers(user)
        owes_dict = cls.owed(user)

        owed_by_sum = sum([item["amount"] for item in owed_by_dict])
        owes_sum = sum([item["amount"] for item in owes_dict])

        return owed_by_sum - owes_sum




