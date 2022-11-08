# encoding: utf-8
"""Models for debts app"""

from decimal import Decimal

from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

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

    def clean(self):
        """Apply business rules to the model"""

        # The lender and the borrower fields can't be the same user
        if self.lender == self.borrower:
            raise ValidationError("Lender and borrower can't be the same")

    def save(self, *args, **kwargs):
        """Update the accumulated debt when creating a new debt"""
        self.full_clean()
        # If there is an accumulated debt for the pair, obtain it and update the amount,
        # if not, create a new one.
        debt_accumulated, created = (
            DebtAccumulate.objects.get_or_create(
                lender=self.lender,
                borrower=self.borrower,
                defaults={"total_amount": self.amount}
            )
        )
        if not created:
            debt_accumulated.total_amount += Decimal(self.amount)
            debt_accumulated.save()
        super(Debt, self).save(*args, **kwargs)


class DebtAccumulate(models.Model):
    """Saves the accumulated debt between users"""

    lender = models.ForeignKey(User, related_name='lender', on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, related_name='borrower', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('lender', 'borrower')

    @classmethod
    def owers(cls, lender):
        """Returns all the users that have borrowed from the lender and the amount"""

        debts = cls.objects.filter(lender=lender).values("borrower__username", "total_amount")
        owers_dict = {}
        for item in debts:
            owers_dict[item["borrower__username"]] = item["total_amount"]
        return owers_dict

    @classmethod
    def owed(cls, borrower):
        """Returns all the users that have lended to the borrower and the amount"""

        debts = cls.objects.filter(borrower=borrower).values("lender__username", "total_amount")
        owed_dict = {}
        for item in debts:
            owed_dict[item["lender__username"]] = item["total_amount"]
        return owed_dict

    @classmethod
    def calculate_total_amount(cls, lender, borrower):
        """Update the amount for the lender and borrower"""

        if lender == borrower:
            raise Exception("Lender and borrower can't be the same")
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
        cls.objects.update_or_create(
            lender=lender,
            borrower=borrower,
            defaults={"total_amount": amount}
        )
        return True

    @classmethod
    def balance(cls, user):
        """Return the balance of a user"""

        owed_by_dict = cls.owers(user)
        owes_dict = cls.owed(user)

        owed_by_sum = sum([value for value in owed_by_dict.values()])
        owes_sum = sum([value for value in owes_dict.values()])

        return owed_by_sum - owes_sum




