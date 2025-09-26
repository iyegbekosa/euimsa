from django.db.models import Sum
from user.models import NewUser
from django.db import models
import uuid



class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="candidates")
    name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='candidates/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def total_votes(self):
        return (
            self.votetransaction_set.filter(status="success")
            .aggregate(Sum("votes"))["votes__sum"] or 0
        )


class VoteTransaction(models.Model):
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)  # For anonymous voters

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    votes = models.PositiveIntegerField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    transaction_ref = models.CharField(max_length=100, unique=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            identifier = self.user.get_full_name()
        else:
            identifier = self.email or "Anonymous"
        return f"{identifier} → {self.candidate.name} ({self.votes} votes)"
