import os,sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Remonte jusqu'au dossier parent
sys.path.append(parent_dir)
from app.depute.fill_postgre import create_organe , Organe
#Gros probleme dans l'import de Organe
#from app.db.postgreSQL import Organe,PartiPolitique

polTest = {
  "_id": "PO684926",
  "codeType": "PARPOL",
  "libelle": "Parti communiste français",
  "libelleAbrege": "Parti communiste français",
  "libelleAbrev": "PCF",
  "libelleEdition": "Parti communiste français",
  "organeParent": None,
  "organePrecedentRef": None,
  "preseance": None,
  "type": "OrganeExterne_Type",
  "uid": "PO684926",
  "viMoDe": {
    "dateDebut": None,
    "dateAgrement": None,
    "dateFin": None
  }
}
organeTest = {
  "_id": "PO191887",
  "chambre": None,
  "codeType": "ORGEXTPARL",
  "legislature": None,
  "libelle": "Commission nationale pour l'élimination des mines antipersonnel",
  "libelleAbrege": "Mines antipersonnel",
  "libelleAbrev": "160",
  "libelleEdition": "de la Commission nationale pour l'élimination des mines antipersonnel",
  "nombreReunionsAnnuelles": "2",
  "organeParent": None,
  "regime": "5ème République",
  "regimeJuridique": "Article L. 2345-1 du code de la défense",
  "siteInternet": "https://www.diplomatie.gouv.fr/fr/politique-etrangere-de-la-france/desarmement-et-non-proliferation/la-france-et-l-elimination-des-mines-antipersonnel/article/la-politique-francaise-en-matiere",
  "type": "OrganeExtraParlementaire_type",
  "uid": "PO191887",
  "viMoDe": {
    "dateDebut": "1999-05-11",
    "dateAgrement": None,
    "dateFin": None
  }
}


def testOrgane():
    organe = create_organe(organeTest)
    assert isinstance(organe, Organe)