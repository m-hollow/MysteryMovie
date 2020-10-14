from django.utils.timezone import make_aware
from datetime import date

def reformat_date(date_string):
    """
    Takes a date as a string, returns the date as a timezone-aware datetime.date object
    this expects the string to follow format:  YEAR-MONTH-DAY
    as 0000-00-00
    """
    date_object = date.fromisoformat(date_string)

    return date_object


# this creates 'timezone aware' datetime objects
def reformat_date_two(date_string):
    """
    Takes a date as a string, returns the date as a timezone-aware datetime.date object
    this expects the string to follow format:  YEAR-MONTH-DAY
    as 0000-00-00
    """
    date_object = date.fromisoformat(date_string)
    aware_object = make_aware(date_object)

    return aware_object


