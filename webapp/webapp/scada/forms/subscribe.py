from django import forms
from .custom_fields import CustomCharField


class SubscribeForm(forms.Form):
    nlfirstname = CustomCharField(
        label="Please enter your first name",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "nlfirstname",
                "class": "span8",
                "placeholder": "* Your first name...",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter your first name.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    nllastname = CustomCharField(
        label="Please enter your last name",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "nllastname",
                "class": "span8",
                "placeholder": "* Your last name...",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter your last name.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    nlcompany = CustomCharField(
        label="Please enter your company name",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "nlcompany",
                "class": "span8",
                "placeholder": "* Your company name...",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter your company name.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    nlphone = CustomCharField(
        label="Please enter your phone number",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "nlphone",
                "class": "span8",
                "placeholder": "* Your phone number...",
                "type": "text",
            }
        ),
        error_messages={
            "required": "+1 123 456 7890 or 1234567890 or 123-456-7890",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    nlmail = forms.EmailField(
        label="Please enter your email",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "nlmail",
                "class": "span8",
                "placeholder": "* Your email...",
                "type": "email",
            }
        ),
        error_messages={
            "required": "Please enter a valid email address.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
