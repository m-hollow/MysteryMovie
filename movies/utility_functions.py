from django.utils.timezone import make_aware
from datetime import date
from .models import Trophy, RoundRank

def reformat_date(date_string):
    """
    Takes a date as a string, returns the date as a datetime.date object
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


def create_ranks():
    """This needs to be called once, on the server, after the database is hooked up, to populate these fields"""
    int_list = list(range(1,11))
    string_list = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eigth', 'Ninth', 'Tenth']

    for value, string_val in zip(int_list, string_list):
        new_rank = RoundRank(rank_int=value, rank_string=string_val)
        new_rank.save()




def add_trophies():
    """Add the currently defined Trophies to the database Trophy table"""

    t1 = {
    'name': 'Deepest Hurting',
    'condition': 'User with Lowest rated movie',
    'point_value': 2,
    }

    t2 = {
        'name': 'Light On Hurting',
        'condition': 'User with Highest rated movie',
        'point_value': 2,
    }

    t3 = {
        'name': 'A True Mystery',
        'condition': 'User with a movie nobody had heard of',
        'point_value': 2,
    }

    t4 = {
        'name': 'The Wiseman',
        'condition': 'User who guessed all movies correctly',
        'point_value': 2,
    }

    t5 = {
        'name': 'The Seer',
        'conditon': 'User who had seen all the movies',
        'point_value': 2,
    }

    trophy_dicts = [t1, t2, t3, t4, t5]

    for t in trophy_dicts:
        trophy = Trophy(name=t['name'], condition=t['condition'], point_value=['point_value'])
        trophy.save()





