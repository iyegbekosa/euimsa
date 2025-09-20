# forms.py
from django import forms
from django.contrib.auth.forms import SetPasswordForm

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = "Enter New Password"
        self.fields['new_password2'].label = "Confirm New Password"
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
