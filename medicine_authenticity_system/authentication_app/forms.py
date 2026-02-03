from django import forms

class DrugForm(forms.Form):
    drug_id = forms.CharField(
        max_length=66,
        required=True,
        help_text="Unique identifier for the medicine"
    )
    name = forms.CharField(max_length=100)
    batch = forms.CharField(max_length=100)
    manufacturer = forms.CharField(max_length=100)
    expiry = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select the expiry date"
    )
