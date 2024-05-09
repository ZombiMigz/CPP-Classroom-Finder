import re
from typing import List, Tuple
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
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


def sort_by_building(building: str) -> Tuple[int, str]:
    match = re.match(r"(\d+)(\D*)", building)
    if match:
        return (int(match.group(1)), match.group(2))
    return (0, "")


def get_classrooms(request: HttpRequest) -> HttpResponse:
    form = ClassroomForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest()
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
    print(used_rooms, data)
    # Find all bldg+rooms and filter by used rooms
    all_classrooms = list(
        ScheduleBlock.objects.all().values("building", "room").distinct()
    )

    classrooms = list(
        filter(
            lambda classroom: classroom not in used_rooms,
            all_classrooms,
        )
    )

    # Create dictionary mapping each building to list of rooms
    class_map: dict[str, List[str]] = dict()
    for classroom in classrooms:
        building = classroom["building"]
        room = classroom["room"]
        day_of_the_week = DAY_OF_THE_WEEK_MAPPING[int(data["day"])]

        start_times = (
            ScheduleBlock.objects.filter(
                building=building,
                room=room,
                day_of_the_week=day_of_the_week,
                start_time__gte=data["end_time"],
            )
            .order_by("start_time")
            .values("start_time")
        )

        end_times = (
            ScheduleBlock.objects.filter(
                building=building,
                room=room,
                day_of_the_week=day_of_the_week,
                end_time__lte=data["start_time"],
            )
            .order_by("-end_time")
            .values("start_time")
        )

        # string to display room, start time, and end time
        room_time_str = (
            f"Room: {room} (Open from "
            + (
                start_times[0]["start_time"].strftime("%I:%M %p")
                if len(start_times) > 0
                else " beginning of day"
            )
            + " - "
            + (
                end_times[0]["start_time"].strftime("%I:%M %p") + ")"
                if len(end_times) > 0
                else " end of day)"
            )
        )

        if building not in class_map:
            class_map[building] = []
        class_map[building].append(room_time_str)
    # Sort classes
    for building in class_map:
        class_map[building].sort()

    return render(
        request,
        "classrooms.html",
        {
            "classes": sorted(
                class_map.items(), key=lambda item: sort_by_building(item[0])
            ),
            "classes_count": len(classrooms),
        },
    )


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

    if request.method == "POST":
        return get_classrooms(request)

    return render(
        request,
        "index.html",
        {
            "form": form,
        },
    )
