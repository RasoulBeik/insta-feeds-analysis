from datetime import datetime
from datetime import timedelta

def timestamp_to_date_str(timestamp, str_format='%Y-%m-%d'):
    t = datetime.fromtimestamp(timestamp)
    date_str = t.strftime(str_format)
    return date_str

def get_date_from_str(date_str):
    format_str = '%Y-%m-%d %H:%M:%S'
    if 'am' in date_str.lower():
        format_str = '%Y-%m-%d %H:%M:%S AM'
    elif 'pm' in date_str.lower():
        format_str = '%Y-%m-%d %H:%M:%S PM'
    return datetime.strptime(date_str.strip(), format_str).date()

def get_datetime_from_str(date_str):
    format_str = '%Y-%m-%d %H:%M:%S'
    if 'am' in date_str.lower():
        format_str = '%Y-%m-%d %H:%M:%S AM'
    elif 'pm' in date_str.lower():
        format_str = '%Y-%m-%d %H:%M:%S PM'
    return datetime.strptime(date_str.strip(), format_str)

### it returns utcnow as a datatime without floating part of seconds
def get_utcnow():
    str_now = str(datetime.utcnow())
    try:
        dot = str_now.index('.')
        str_now = str_now[:dot]
    except:
        pass
    return get_datetime_from_str(str_now)