from django import forms


class ClassroomForm(forms.Form):
    DAYS_CHOICES = (
        ('M', 'Monday'),
        ('Tu', 'Tuesday'),
        ('W', 'Wednesday'),
        ('Th', 'Thursday'),
        ('F', 'Friday'),
        ('Sa', 'Saturday'),
    )

    TIMES_CHOICES = [(f"{hour}:{minute} {period}", f"{hour}:{minute} {period}")
                     for period in ['AM', 'PM']
                     for hour in range(1, 13)
                     for minute in ['00', '15', '30', '45']]

    day = forms.ChoiceField(choices=DAYS_CHOICES)
    start_time = forms.ChoiceField(choices=TIMES_CHOICES)
    end_time = forms.ChoiceField(choices=TIMES_CHOICES)
