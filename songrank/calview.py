""" 
Utility for viewing events in calendar format.
"""

from songrank.models import Phase
from datetime import date
import calendar
from dateutil.relativedelta import relativedelta


class MonthView(object):
    """ 
    A view of a calendar month.
    """
    def __init__(self, year, month, pipeline=None):
        """ 
        Initializes the MonthView with the specified year and month, and
        optionally the specified pipeline
        """
        self.year = year
        self.month = month
        self.pipeline = pipeline
        self.baseline = date(year, month, 1) # baseline is first day of month
        self.offset = self.baseline.weekday()
    
    def _date_for(self, weekday, week):
        """ 
        Gets the specified date for the numbered weekday and week. Returns None
        if it falls outside of the month.
        """
        ask = weekday + (week * 7)
                
        if ask < self.offset:
            # before the month
            return None
        
        day_of_month = ask - self.offset + 1 # adding one for 1-indexed month days
                
        _, max_day = calendar.monthrange(self.baseline.year, self.baseline.month)
        if day_of_month > max_day:
            # after the month
            return None
        
        return date(self.baseline.year, self.baseline.month, day_of_month)
    
    def date_at(self, weekday, week):
        """ 
        Gets the date for the specified day of the the week and week of
        the month.  Returns 0 if not a legal date.
        """
        specified_date = self._date_for(weekday, week)
        return specified_date if specified_date is not None else 0
    
    def events_at(self, weekday, week):
        """ 
        Gets the phase events for the specified day.
        """
        ref_date = self._date_for(weekday, week)
        if ref_date is not None:
            if self.pipeline:
                return self.pipeline.phases.filter(due=ref_date)
            else:
                return Phase.objects.filter(due=ref_date)
        
        # if we're here it's not a valid date
        return Phase.objects.none()
    
    def __iter__(self):
        return (WeekView(self, week) for week in range(5))
    
    def days_of_week(self):
        """ 
        Gets the headers for the days of the week.
        """
        return ['M', 'T', 'W', 'Th', 'F', 'Sa', 'Su']

class WeekView(object):
    """ 
    View of a specified week.
    """
    def __init__(self, monthview, week):
        self.monthview = monthview
        self.week = week
    
    def __iter__(self):
        return (DayView(self.monthview, day_of_week, self.week) for day_of_week in range(7))

class DayView(object):
    """ 
    View of a specific day.
    """
    def __init__(self, monthview, weekday, week):
        self.monthview = monthview
        self.weekday = weekday
        self.week = week
    
    def date(self):
        """ 
        Gets the date for this day.
        """
        return self.monthview.date_at(self.weekday, self.week)
    
    def events(self):
        """ 
        Gets phase events for this day.
        """
        return self.monthview.events_at(self.weekday, self.week)


def date_for_offset(month_offset=0):
    """ 
    Gets a date for the current date offset by the specified
    number of months (may be positive or negative).
    """
    delta = relativedelta(months=month_offset)
    return date.today() + delta
