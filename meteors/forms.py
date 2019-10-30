from django import forms

class DateForm(forms.Form):
    datetime = forms.DateField(
        widget = forms.SelectDateWidget(years = range(2009, 2029)),
        label = 'date'
    )
