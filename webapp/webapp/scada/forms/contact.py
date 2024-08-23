from django import forms
from .custom_fields import CustomCharField


class ContactForm(forms.Form):
    name = CustomCharField(
        label="Please enter name",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "name",
                "class": "span12",
                "placeholder": "* Your name...",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter your name.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    email = forms.EmailField(
        label="Please enter email",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "email",
                "class": "span12",
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
    comment = CustomCharField(
        label="Please enter comment",
        max_length=1000,
        min_length=1,
        required=True,
        widget=forms.Textarea(
            attrs={
                "id": "comment",
                "class": "span12",
                "placeholder": "* Your comment...",
            }
        ),
        error_messages={
            "required": "Please enter your comment.",
            "max_length": "Please enter no more than 1000 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
