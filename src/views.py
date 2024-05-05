from django.http import HttpRequest
from django.shortcuts import render
from src.forms import ClassroomForm
from src.models import ScheduleBlock


def index(request: HttpRequest):
    form = ClassroomForm(request.POST)
    context = {}
    context['form'] = form
    if request.method == 'POST' and form.is_valid():
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        open_classes = get_open_classes(day, start_time, end_time)
        context['day'] = day
        context['start_time'] = start_time
        context['end_time'] = end_time
        context['classes'] = open_classes

        return render(request, 'index.html', context)
    return render(request, 'index.html', context)


def get_open_classes(day, start_time, end_time):
    # implementation of filting/excluding class objects from database
    open_classes = ScheduleBlock.objects.filter(day_of_the_week=day)
    return open_classes
