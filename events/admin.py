from django.contrib import admin
from .models import Category, Candidate, VoteTransaction


admin.site.register(Category)
admin.site.register(Candidate)
admin.site.register(VoteTransaction)
