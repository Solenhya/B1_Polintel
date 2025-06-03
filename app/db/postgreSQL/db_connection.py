from .database import SessionLocal
from sqlalchemy import text
from contextlib import contextmanager

#Fonction a utiliser
@contextmanager
def get_session():
    """create a new session to the database"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise #relance l’erreur après rollback
    finally:
        db.close()

#Fonction a déprécier
def get_connection():
    """maje la fonction de connexion à la base de données"""
    # Test de la connexion à la base de données
    
    try:
       with get_session() as db:  # Récupération de la session
        # Test de la connexion à la base de données
            db.execute(text("select 1"))
            print("Connexion reussie")
    except Exception as e :
        print("Erreur de connexion à la base de données :", e)
        raise



# Test de la connexion à la base de données
# def test_db_connection():
if __name__ == "__main__":
    get_connection()