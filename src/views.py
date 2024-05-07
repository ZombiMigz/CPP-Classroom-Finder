from typing import Any, List
from django.http import HttpRequest
from django.shortcuts import render
from src.forms import ClassroomForm
from src.models import ScheduleBlock
from datetime import datetime, timedelta

DAY_OF_THE_WEEK_MAPPING = {
    0: "M",
    1: "Tu",
    2: "W",
    3: "Th",
    4: "F",
    5: "Sa",
    6: "Su",
}


def index(request: HttpRequest):
    # Default Input
    now = datetime.now()
    form = ClassroomForm(
        initial={
            "day": now.weekday(),
            "start_time": now.time(),
            "end_time": (now + timedelta(hours=1)).time(),
        }
    )

    classrooms: List[dict[str, Any]] = []

    if request.method == "POST":
        form = ClassroomForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Get all bldgs + rooms that have conflicting blocks
            query = (
                ScheduleBlock.objects.filter(
                    start_time__lt=data["end_time"],
                    end_time__gt=data["start_time"],
                    day_of_the_week=DAY_OF_THE_WEEK_MAPPING[int(data["day"])],
                )
                .values("building", "room")
                .distinct()
            )
            used_rooms = list(query)
            # Find all bldg+rooms on a specific day and filter by used rooms
            all_classrooms = list(
                ScheduleBlock.objects.filter(
                    day_of_the_week=DAY_OF_THE_WEEK_MAPPING[int(data["day"])],
                    ).values("building", "room").distinct()
            )

            classrooms = list(
                filter(
                    lambda classroom: classroom not in used_rooms,
                    all_classrooms,
                )
            )

            # Create dictionary mapping each building to list of rooms
            class_map = dict()
            for classroom in classrooms:
                building = classroom['building']
                room = classroom['room']

                if building not in class_map:
                    class_map[building] = []
                class_map[building].append(room)
            # Sort classes
            for building in class_map:
                class_map[building].sort()

    return render(request, "index.html", {"form": form,
                                          "classes": class_map,
                                          "classes_count": len(classrooms)})
