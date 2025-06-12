from datetime import datetime

def get_date(datestring):
    try:
        date = datetime.strptime(datestring,"%Y-%m-%d").date()
        return date
    except Exception as e:
        print(f"Erreur lor du formatage de la date : {e}")
        return