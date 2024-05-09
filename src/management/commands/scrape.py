from typing import Any, Tuple
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
import re
from django.db.models import Q
from src.models import ScheduleBlock
from django.utils import timezone
from django.db.models import Count, Max

SCHEDULE_WEBSITE = "https://schedule.cpp.edu/"
TERM = "Spring Semester 2024"


class Command(BaseCommand):
    help = "Scrapes CPP website for class schedules"

    def remove_invalid_classrooms(self):
        # Query to identify invalid entries where building or room information is missing or marked as 'TBA'
        invalid_entries_query = ScheduleBlock.objects.filter(
            Q(building__isnull=True)
            | Q(building__iexact="tba")
            | Q(room__isnull=True)
            | Q(room__iexact="tba")
        )
        # First count the invalid entries before deletion for reporting
        invalid_count = invalid_entries_query.count()

        # Then delete the entries after counting
        invalid_entries_query.delete()
        print(f"Removed {invalid_count} invalid classroom entries")

    def insert_section_into_database(
        self,
        building: str,
        room: str,
        start_time: timezone.datetime,
        end_time: timezone.datetime,
        day_of_the_week: str,
    ):
        print(building, room, start_time, end_time, day_of_the_week)
        schedule_block = ScheduleBlock(
            building=building,
            room=room,
            start_time=start_time,
            end_time=end_time,
            day_of_the_week=day_of_the_week,
        )
        schedule_block.save()

    def parse_section(self, section: WebElement):
        # Parse Time
        time = section.find_element(By.CSS_SELECTOR, "[id$='_TableCell1']").text
        time = re.match(
            r"(\d{1,2}:\d{2} [AP]M)–(\d{1,2}:\d{2} [AP]M)\s+([SuMTuWThFSa]+)", time
        )
        if not time:
            # Skip if unable to parse time
            return None
        [start_time, end_time, days] = time.groups()
        days = re.findall(r"(Su|Mo|Tu|We|Th|Fr|Sa|M|W|F)", days)
        start_time = timezone.datetime.strptime(start_time, "%I:%M %p")
        end_time = timezone.datetime.strptime(end_time, "%I:%M %p")

        # Parse Location
        location = section.find_element(By.CSS_SELECTOR, "[id$='_TableCell2']").text
        location = re.match(r"Bldg (\w+) Rm ([\w-]+)", location)
        if not location:
            # Skip if unable to parse location
            return None
        [building, room] = location.groups()

        # Parse out days of the week

        print("Inserting:", building, room, start_time, end_time, days)
        for day_of_the_week in days:
            self.insert_section_into_database(
                building, room, start_time, end_time, day_of_the_week
            )

    def remove_duplicates(self):
        unique_fields = [
            "building",
            "room",
            "start_time",
            "end_time",
            "day_of_the_week",
        ]

        # Fetches duplicate if count of row > 1
        duplicates = (
            ScheduleBlock.objects.values(*unique_fields)
            .order_by()
            .annotate(max_id=Max("id"), count_id=Count("id"))
            .filter(count_id__gt=1)
        )

        # Removes duplicates from database
        for duplicate in duplicates:
            (
                ScheduleBlock.objects.filter(**{x: duplicate[x] for x in unique_fields})
                .exclude(id=duplicate["max_id"])
                .delete()
            )

    def handle(self, *args: Tuple[Any], **kwargs: dict[str, Any]):
        print("Starting Scrape")

        # Start up browser and go to schedule website
        driver = webdriver.Chrome()
        driver.get(SCHEDULE_WEBSITE)

        # Search all classes in term

        term_selector = Select(
            driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_TermDDL")
        )
        term_selector.select_by_visible_text(TERM)

        start_time = Select(
            driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_StartTime")
        )
        start_time.select_by_visible_text("1:00 AM")

        end_time = Select(
            driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_EndTime")
        )
        end_time.select_by_visible_text("12:00 AM")

        search_button = driver.find_element(
            By.ID, "ctl00_ContentPlaceHolder1_SearchButton"
        )
        search_button.click()

        # Get all section data
        class_list: WebElement = driver.find_element(By.ID, "class_list")
        ol = class_list.find_element(By.TAG_NAME, "ol")
        sections = ol.find_elements(By.TAG_NAME, "li")

        for section in sections:
            self.parse_section(section)
        self.remove_duplicates()

        driver.close()
