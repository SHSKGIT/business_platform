from django import forms
from .custom_fields import CustomCharField


class SignInForm(forms.Form):
    username = CustomCharField(
        label="Please enter your username",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "username",
                "class": "span12",
                "placeholder": "* Your username...",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter your username.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    password = CustomCharField(
        label="Please enter your password",
        # max_length=200,
        min_length=1,
        required=True,
        widget=forms.PasswordInput(  # ensure the password is hidden as the user types
            attrs={
                "id": "password",
                "class": "span12",
                "placeholder": "* Your password...",
                "type": "password",
            }
        ),
        error_messages={
            "required": "Please enter your password.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
