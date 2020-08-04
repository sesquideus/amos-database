from django import forms

class MicrosecondDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, **kwargs):
        self.supports_microseconds = True
        super().__init__(
            date_format='%Y-%m-%d',
            time_format='%H:%M:%S.%f',
            attrs={'style': 'width: 100px;'},
            **kwargs,
        )

