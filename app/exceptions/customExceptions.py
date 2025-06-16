class DatabaseError(Exception):
    """Erreur de base de données"""
    def __init__(self, operation: str,dbName,collection,origine):
        self.message = f"Erreur lors de l'opération: {operation} sur la base {dbName} et la collection {collection}. Erreur : {origine}"
        super().__init__(self.message)

