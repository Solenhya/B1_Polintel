import os,sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Remonte jusqu'au dossier parent
sys.path.append(parent_dir)

from app.utils import date_utils

def testDateBase():
    date = date_utils.get_date("2025-12-28")
    print(date)
    assert date!=None

def testDateWrong():
    datewrong = date_utils.get_date("bonjour")
    assert datewrong == None
    datewrong = date_utils.get_date(None)
    assert datewrong == None