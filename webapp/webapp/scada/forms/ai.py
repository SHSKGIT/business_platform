from django import forms
from .custom_fields import CustomCharField


class AiForm(forms.Form):
    comment = CustomCharField(
        label="Please enter query",
        max_length=1000,
        min_length=1,
        required=True,
        widget=forms.Textarea(
            attrs={
                "id": "comment",
                "class": "span12",
                "placeholder": "* Your query...",
            }
        ),
        error_messages={
            "required": "Please enter your query.",
            "max_length": "Please enter no more than 1000 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
