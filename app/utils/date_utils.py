from datetime import datetime

def get_date(datestring):
    return datestring.strptime(datestring,"%Y-%m-%d").date()