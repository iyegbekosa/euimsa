from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .paystack  import  Paystack
from user.models import NewUser
from django.db import models
import secrets
import random
import re

class AssociationFee(models.Model):
    session = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_code = models.CharField(max_length=4, default="COLL")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.session} Association Fees"

class SkillAquisition(models.Model):
    skill_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_code = models.CharField(max_length=4, default="SKIL")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.skill_type


class Payment(models.Model):
    name = models.CharField(max_length=100)  # Dynamic name for the payment
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE, blank=True, null=True)
    level = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ref = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    payment_for = models.CharField(max_length=50, choices=[
        ('association_fee', 'Association Fee'),
        ('skill_acquisition', 'Skill Acquisition')
    ], null=True, blank=True)  # Added payment_for field

    class Meta:
        ordering = ('-date_created',)

    def amount_value(self):
        return int(self.amount * 100)  # Return the value in kobo (integer)

    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status and result['amount'] / 100 == self.amount:
            self.verified = True
            self.save()
        return self.verified

    def __str__(self):
        return f"Payment: {self.name} - ₦{self.amount}"

    def save(self, *args, **kwargs):
        if not self.ref:
            PAYMENT_CODE_MAP = {
                'association_fee': 'DUES',
                'skill_acquisition': 'SKIL'
            }
            payment_code = PAYMENT_CODE_MAP.get(self.payment_for, 'GEN')

            while True:
                random_digits = random.randint(100000000, 999999999)
                ref = f"EUIMSA-{payment_code}-{random_digits}"
                if not Payment.objects.filter(ref=ref).exists():
                    self.ref = ref
                    break

        super().save(*args, **kwargs)
