"""API for Yasno outages."""

import datetime
import logging
from pathlib import Path

import recurring_ical_events
from icalendar import Calendar
import pytz

from .const import CALENDAR_PATH

LOGGER = logging.getLogger(__name__)


class YasnoOutagesApi:
    """Class to interact with calendar files for Yasno outages."""

    calendar: recurring_ical_events.UnfoldableCalendar | None

    def __init__(self, group: int) -> None:
        """Initialize the YasnoOutagesApi."""
        self.group = group
        self.calendar = None

    @property
    def calendar_path(self) -> Path:
        """Return the path to the ICS file."""
        return Path(__file__).parent / CALENDAR_PATH.format(group=self.group)

    def fetch_calendar(self) -> None:
        """Fetch outages from the ICS file."""
        if not self.calendar:
            with self.calendar_path.open() as file:
                ical = Calendar.from_ical(file.read())
                self.calendar = recurring_ical_events.of(ical)
        return self.calendar

    def convert_to_local_time(self, utc_time: datetime.datetime) -> datetime.datetime:
        """Convert UTC time to local time."""
        local_tz = pytz.timezone("Europe/Kiev")
        return utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)

    def get_current_event(self, at: datetime.datetime) -> dict:
        """Get the current event."""
        if not self.calendar:
            return None
        local_time = self.convert_to_local_time(at)
        events_at = self.calendar.at(local_time)
        if not events_at:
            return None
        return events_at[0]  # return only the first event

    def get_events(
        self,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[dict]:
        """Get all events."""
        if not self.calendar:
            return []
        local_start_date = self.convert_to_local_time(start_date)
        local_end_date = self.convert_to_local_time(end_date)
        return self.calendar.between(local_start_date, local_end_date)
