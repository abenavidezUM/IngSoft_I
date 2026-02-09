from mongoengine import Document, ReferenceField
from .usuario import Usuario

class Mencion(Document):
    """
    Modelo de Mención
    
    Representa una mención de un usuario en un mensaje.
    Similar a @usuario en Twitter/X.
    
    Atributos:
        usuario: Referencia al usuario mencionado
    """
    
    usuario = ReferenceField(Usuario, required=True)
    
    # Metadata
    meta = {
        'collection': 'menciones',
        'db_alias': 'default',
        'indexes': [
            'usuario'
        ]
    }
    
    def to_dict(self):
        """Convierte la mención a diccionario"""
        return {
            'id': str(self.id),
            'usuario': self.usuario.to_dict() if self.usuario else None
        }
    
    def __str__(self):
        return f"Mencion(@{self.usuario.nickName if self.usuario else 'Unknown'})"
