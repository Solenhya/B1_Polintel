from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_date(datestring):
    try:
        date = datetime.strptime(datestring,"%Y-%m-%d").date()
        return date
    except Exception as e:
        logger.debug(f"Erreur lor du formatage de la date : {e}")
        return