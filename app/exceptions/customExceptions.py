from typing import Optional , List
import logging

class DatabaseError(Exception):
    """Erreur de base de données"""
    def __init__(self, operation: str,dbName,collection,origine):
        self.message = f"Erreur lors de l'opération: {operation} sur la base {dbName} et la collection {collection}. Erreur : {origine}"
        super().__init__(self.message)

class NoTokenException(Exception):
    def __init__(self):
        self.message = f"Erreur dans l'acces a un endpoint protegé aucun token n'a été fourni"
        super().__init__(self.message)

class RoleRequiredAllException(Exception):
    def __init__(self,rightRequired : Optional[List]=None):
        self.message = f"Erreur dans l'acces a un endpoint protegé"
        super().__init__(self.message)

class IncorrectInputException(Exception):
    def __init__(self,origine,message=None):
        self.message=message if message else f"Erreur dans l'input qui n'est pas au format attendu"
        self.origne = origine
        super().__init__(self.message)