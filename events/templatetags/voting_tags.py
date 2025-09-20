from django import template
from events.models import VoteTransaction
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def get_candidate_votes(candidate):
    return (
        VoteTransaction.objects.filter(candidate=candidate, status="success")
        .aggregate(Sum("votes"))["votes__sum"] or 0
    )
