from db.postgreSQL.db_connection import get_session
from db.postgreSQL.models import Organe,OrganeRelation
from sqlalchemy import select,func
from tqdm import tqdm
import logging
logger = logging.getLogger(__name__)

def fill_up_from_member():
    with get_session() as session:
        toProcess = select(Organe).where((Organe.debut.is_(None)))
        #Recupere le count du nombre de ligne a traité
        count_query = select(func.count()).select_from(toProcess.subquery())
        count = session.execute(count_query).scalar_one()
        results = session.execute(toProcess).all()
        done = 0
        for result in tqdm(results,total=count):
            (organe,) = result #Le fonctionnement 2.x implique que le retour est un tuple mais dans ce cas d'une seule dimension il faut donc le déballé
            querymini = select(func.min(OrganeRelation.date_debut)).where(OrganeRelation.organe_id==organe.organe_id)
            mini = session.execute(querymini).scalar_one_or_none()
            if not mini:
                #Si la commande ne trouve pas de membres on remplis l'erreur (Passage en info ?)
                logger.error(f"Erreur dans le remplissage des dates sur {result.nom}")
                continue
            organe.debut=mini
            session.merge(organe)
            session.commit()
            done+=1
    return done , count