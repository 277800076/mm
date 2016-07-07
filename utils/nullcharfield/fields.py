from django import forms
class NullCharField(forms.CharField):
    def clean(self, value):
        value = super(NullCharField, self).clean(value)
        if value in forms.fields.EMPTY_VALUES:
            return None
        return value
