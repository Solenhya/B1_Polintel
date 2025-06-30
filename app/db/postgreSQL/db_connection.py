from .database import SessionLocal
from sqlalchemy import text
from contextlib import contextmanager
import psycopg2
import os
from exceptions.customExceptions import DatabaseError

HOST = os.getenv("SQL_HOST")
USER = os.getenv("SQL_USER")
DATABASEDUMP = os.getenv("SQL_DATABASE_DUMP")
PORT = os.getenv("SQL_PORT")
PASSWORD = os.getenv("SQL_PASSWORD")

# Vérifier si toutes les variables d'environnement sont définies
if not all([HOST, USER, DATABASEDUMP, PORT, PASSWORD]):
    raise ValueError("Une ou plusieurs variables d'environnement ne sont pas définies.")

#for var in [HOST, DATABASEDUMP, USER, PASSWORD]: DEBUG
#    print(var, type(var), var.encode('utf-8'))
#Fonction a utiliser
@contextmanager
def get_session():
    """Creer une session sqlalchemy vers la base de donnée definit dans database"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise #relance l’erreur après rollback
    finally:
        db.close()

@contextmanager
def get_connection_dump():
    """Creer une connection psycopg2 vers la base dumps"""
    print(f"Host:{HOST}")
    print(f"database:{DATABASEDUMP}")
    print(f"Host:{USER}")
    print(f"Host:{PASSWORD}")
    print(f"Host:{HOST}")
    conn = psycopg2.connect(
        host=HOST,
        database=DATABASEDUMP,
        user=USER,
        password=PASSWORD
        )
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()




# Test de la connexion à la base de données
# def test_db_connection():
if __name__ == "__main__":
    pass