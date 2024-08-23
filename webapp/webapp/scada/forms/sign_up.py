from django import forms
from .custom_fields import CustomCharField


class SignUpForm(forms.Form):
    username = CustomCharField(
        label="Please enter your username",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "username",
                "class": "span12",
                "placeholder": "* Username (Note: MaRk = mark)",
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
                "placeholder": "* Password",
                "type": "password",
            }
        ),
        error_messages={
            "required": "Please enter your password.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    email = forms.EmailField(
        label="Please enter your email",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "email",
                "class": "span12",
                "placeholder": "* Email",
                "type": "email",
            }
        ),
        error_messages={
            "required": "Please enter a valid email address.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
