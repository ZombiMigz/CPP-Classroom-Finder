from django import forms


class ClassroomForm(forms.Form):
    DAYS_CHOICES = (
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    )

    day = forms.ChoiceField(choices=DAYS_CHOICES)
    start_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "type": "time",
                "class": "timepicker",
                "name": "start_time",
                "required": "true",
            }
        )
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "type": "time",
                "class": "timepicker",
                "name": "end_time",
                "required": "true",
            }
        )
    )
