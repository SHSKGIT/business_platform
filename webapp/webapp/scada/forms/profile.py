from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .custom_fields import CustomCharField

from ..sqlalchemy_setup import get_dbsession
from ..models.auth_entity import AuthEntity

import re


class ProfileForm(forms.Form):
    username = CustomCharField(
        label="Please enter your username",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "username",
                "class": "span12",
                "placeholder": "* Username",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter your username.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    # password = CustomCharField(
    #     label="Please enter your password",
    #     # max_length=200,
    #     min_length=1,
    #     required=True,
    #     widget=forms.PasswordInput(  # ensure the password is hidden as the user types
    #         attrs={
    #             "id": "password",
    #             "class": "span12",
    #             "placeholder": "* Password",
    #             "type": "password",
    #         }
    #     ),
    #     error_messages={
    #         "required": "Please enter your password.",
    #         "max_length": "Please enter no more than 200 characters.",
    #         "min_length": "Please enter at least 1 character.",
    #     },
    # )
    # confirm_password = CustomCharField(
    #     label="Please confirm your password",
    #     # max_length=200,
    #     min_length=1,
    #     required=True,
    #     widget=forms.PasswordInput(  # ensure the password is hidden as the user types
    #         attrs={
    #             "id": "confirm_password",
    #             "class": "span12",
    #             "placeholder": "* Confirm Password",
    #             "type": "password",
    #         }
    #     ),
    #     error_messages={
    #         "required": "Please enter your confirmed password.",
    #         "max_length": "Please enter no more than 200 characters.",
    #         "min_length": "Please enter at least 1 character.",
    #     },
    # )
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
    first_name = CustomCharField(
        label="Please enter your first name",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "first_name",
                "class": "span12",
                "placeholder": "* First Name",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter your first name.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    last_name = CustomCharField(
        label="Please enter your last name",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "last_name",
                "class": "span12",
                "placeholder": "* Last Name",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter your last name.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    company = CustomCharField(
        label="Please enter your company name",
        max_length=200,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "company",
                "class": "span12",
                "placeholder": "* Company Name",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter your company name.",
            "max_length": "Please enter no more than 200 characters.",
            "min_length": "Please enter at least 1 character.",
        },
    )
    phone = CustomCharField(
        label="Please enter your phone number",
        max_length=15,
        min_length=1,
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "phone",
                "class": "span12",
                "placeholder": "* Phone Number",
                "type": "text",
            }
        ),
        error_messages={
            "required": "Please enter a valid phone number.",
            "invalid": "Enter a valid phone number.",
        },
    )

    """
    # In Django forms, the clean_<fieldname>() method is part of Django's form validation system. When you define a method with the name clean_<fieldname>(), Django automatically recognizes it as the validation function for that specific field and calls it during form validation.
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        # Strip spaces, dashes, and parentheses
        stripped_phone = re.sub(r"[\s()-]", "", phone)

        # Check if the phone starts with a plus and contains only digits afterwards
        if not re.match(r"^\+?\d{9,15}$", stripped_phone):
            raise ValidationError(
                "Phone number must be between 9 and 15 digits and can include an optional '+'."
            )

        # Further validation logic (optional)
        # For example, you can check country codes, or local formatting rules if needed

        return phone
    """

    def __init__(self, *args, user_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        # pre-fill a field based on user_id
        if user_id:
            dbsession = next(get_dbsession())  # Get the SQLAlchemy session
            user = dbsession.query(AuthEntity).filter_by(id=user_id).one_or_none()
            dbsession.close()

            if user:
                self.fields["username"].widget.attrs["value"] = f"{user.username}"
                self.fields["email"].widget.attrs["value"] = f"{user.email}"
                self.fields["first_name"].widget.attrs["value"] = f"{user.first_name}"
                self.fields["last_name"].widget.attrs["value"] = f"{user.last_name}"
                self.fields["company"].widget.attrs["value"] = f"{user.company}"
                self.fields["phone"].widget.attrs["value"] = f"{user.phone}"
