from django import forms

class MicrosecondDateTimeWidget(forms.SplitDateTimeWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.supports_microseconds = True

