from django import forms


class DateForm(forms.Form):
    date = forms.DateField(
        widget = forms.SelectDateWidget(years = range(2000, 2039)),
        label = 'date'
    )
