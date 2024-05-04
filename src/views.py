from django.http import HttpRequest
from django.shortcuts import render
from src.forms import ClassroomForm
from src.models import ScheduleBlock
from datetime import datetime


def index(request: HttpRequest):
    form = ClassroomForm()
    return render(request, 'index.html', {'form': form})
    classes = ScheduleBlock.objects.all()
    date = datetime.now()
    return render(request, 'index.html', {"classes": classes, "date": date})
