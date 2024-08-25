from django import forms


class CustomCharField(forms.CharField):
    def __init__(self, *args, **kwargs):
        # Ensure 'strip' is only passed once
        kwargs['strip'] = kwargs.get('strip', True)
        super().__init__(*args, **kwargs)

