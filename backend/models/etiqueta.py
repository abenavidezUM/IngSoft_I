from mongoengine import Document, StringField

class Etiqueta(Document):
    """
    Modelo de Etiqueta (Tag/Hashtag)
    
    Atributos:
        texto: Texto de la etiqueta (ej: #python, #angular)
    """
    
    texto = StringField(required=True, unique=True, max_length=50)
    
    # Metadata
    meta = {
        'collection': 'etiquetas',
        'db_alias': 'default',
        'indexes': [
            'texto'
        ]
    }
    
    def to_dict(self):
        """Convierte la etiqueta a diccionario"""
        return {
            'id': str(self.id),
            'texto': self.texto
        }
    
    def __str__(self):
        return f"Etiqueta({self.texto})"
