import psycopg2
from psycopg2.extras import RealDictCursor
from db.postgreSQL.db_connection import get_connection_dump ,get_session
from db.postgreSQL.models import HommePolitique
from scrapping.scrappinghatvp import recuperate_data
from datetime import datetime
import logging
logger = logging.getLogger(__name__)


addProcesscol = "ALTER TABLE sen ADD COLUMN traitement_insertion_datetime DATE;"
addProccesscomment = "COMMENT ON COLUMN sen.traitement_insertion_datetime IS 'La date de traitement d'insertion dans la base de donnée Polintel';"
select = "select * from elusen join sen on elusen.senmat = sen.senmat where sen.etasencod = 'ACTIF' and sen.traitement_insertion_datetime IS NULL"
count_select = "select count(*) from elusen join sen on elusen.senmat = sen.senmat where sen.etasencod = 'ACTIF' and sen.traitement_insertion_datetime IS NULL"

def add_col():
    with get_connection_dump() as connection:
        with connection.cursor() as cur:
            cur.execute(addProcesscol)
            cur.execute(addProccesscomment)
        print("Done")

def insert_hopol_decla():
    with get_connection_dump() as connection,connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(select)
        cursor.execute(count_select)
        total = cursor.fetchone()[0]
        with get_session() as session:
            count = 0
            for result in cursor:
                try:
                    process_row(result,session)
                    count+=1
                except Exception as e:
                    logger.error(f"Erreur lors de l'import des senateurs: {e}. Sur {result}")
    return count,total


def process_row(row,session):
    hopol = HommePolitique()
    hopol.hopol_id=row["senmat"]
    hopol.nom=row["sennomuse"]
    hopol.prenom=row["senprenomuse"]
    hopol.profession=row["sendespro"]
    #hopol.profession_cat= besoin de plus d'exploration pour retrouver des catégorie correspondantes
    hopol.date_naissance=row["sendatnai"]
    url = row["sendaiurl"]
    session.merge(hopol)
    dateTraitement = datetime.now()
    recuperate_data(url,hopol.hopol_id,session,dateTraitement)