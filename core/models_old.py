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
    session = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.session} Association Fees"

class SkillAquisition(models.Model):
    skill_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

class Payment(models.Model):
    name = models.CharField(max_length=20)
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE, blank=True, null=True)
    level = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ref = models.CharField(max_length=50)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    payment_for = GenericForeignKey('content_type', 'object_id')



    class Meta:
        ordering = ('-date_created',)

    def amount_value(self):
        return int(self.amount) * 100

    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.amount)
        if status:
            if result['amount'] / 100 == self.amount:
                self.verified = True
            self.save()
        if self.verified:
            return True
        return False
    
    def __str__(self):
        return f"Payment: {self.amount}"

    def save(self, *args, **kwargs):
        if not self.ref:
            while True:
                session_digits = ''.join(re.findall(r'\d+', self.session))[:4]
                if len(session_digits) >= 4:
                    session_code = session_digits[:2] + session_digits[2:4]
                else:
                    session_code = "0000" 

                random_digits = random.randint(100000000, 999999999)
                ref = f"EUIMSA-{session_code}-{random_digits}"
                if not Payment.objects.filter(ref=ref).exists():
                    self.ref = ref
                    break

        super().save(*args, **kwargs)
