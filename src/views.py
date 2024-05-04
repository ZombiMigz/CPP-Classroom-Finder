from django.http import HttpRequest
from django.shortcuts import render
from src.models import ScheduleBlock
from datetime import datetime


def index(request: HttpRequest):
    classes = ScheduleBlock.objects.all()
    date = datetime.now()
    return render(request, 'index.html', {"classes": classes, "date": date})
