from calendar import timegm
from time import time
from dateutil.parser import parse
from datetime import datetime

# REMEMBER TO ERROR HANDLE

def validate_unix(time_str):
    """
    The validate_unix is a helper function for the return_unix_time function takes a time string and checks if the string is in valid unix time (milliseconds)
    :param time_str: a string that is supposed to represent a time string
    :return: True if it's a valid unix time and False if not
    """
    if time_str.isdigit():
        # Gets the current time in unix time milliseconds
        curr_unix_time = timegm(datetime.utcnow().utctimetuple()) * 1000
        # Check if our time string is between 0 and the current unit time
        if 0 <= int(time_str) <= curr_unix_time:
            return True
    return False

def to_millisec(datetime_str):
    """
    The to_millisec is a helper function for the return_unix_time function takes a datetime string and changes the time to unix time
    :param datetime_str: a string to be changed to unix time
    :return: the correlating datetime in unix time (milliseconds)
    """
    return timegm(parse(datetime_str, fuzzy=True).timetuple()) * 1000

def return_unix_time(time_str):
    """
    The return_unix_time function takes the time string and checks the value of the string and return the appropriate value depending on the input
    :param time_str: the datetime string to validate
    :return: an empty string if there's no value, the same time string if it's already in unix time, or changing the time string to unix time
    """
    # If there's no value
    if time_str is None or '':
        return None
    # If the value is already in unix time (millisec)
    elif validate_unix(time_str) is True:
        return int(time_str) * 1000
    # If the date time needs to be changed to unix time
    else:
        return to_millisec(time_str)