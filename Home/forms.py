# forms.py
from django import forms

class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label="Import a csv file :")
