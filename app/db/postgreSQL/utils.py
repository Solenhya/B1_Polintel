from sqlalchemy.dialects.postgresql import insert

#Fonction qui transform un model sqlalchemy en un dictionaire de valeur en utilisant le __table__.columns
def orm_to_dict(obj):
    return {
        c.name: getattr(obj, c.name)
        for c in obj.__table__.columns
    }

def upsert_orm(session,model,list_obj,conflict_cols):
    list_dict = [orm_to_dict(obj) for obj in list_obj]
    upsert(session,model,list_dict,conflict_cols)

#Fonction d'upsert qui utilise le On CONFLICT de postgreSQL
def upsert(session, model, data_list, conflict_cols):
    """
    session: la sessions sqlalchemy
    model:le model definit dans models pour l'orm
    data_list:la liste des dictionnaire qui chacun correspond a un élement a inserer
    conflict_cols:la liste des noms de colonnes primarykey sur lequel le conflict peut s'effectuer
    """
    if(len(data_list)==0):
        return
    #On fait appel au operation bas niveau et on ne passe donc pas par de l'orm
    table = model.__table__

    #On creer l'insertion de toute les instance dans la liste
    stmt = insert(table).values(data_list)
    
    #On definit que l'on veut upsert to les champs sauf les clefs primaire
    update_dict = {
        col.name: getattr(stmt.excluded, col.name)
        for col in table.columns
        if col.name not in conflict_cols  
    }

    stmt = stmt.on_conflict_do_update(
        index_elements=conflict_cols,
        set_=update_dict
    )

    session.execute(stmt)
    session.commit()