from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField
from datetime import datetime
from .usuario import Usuario
from .etiqueta import Etiqueta
from .mencion import Mencion

class Mensaje(Document):
    """
    Modelo de Mensaje (Público)
    
    Representa un mensaje público en el sistema (similar a un tweet/post).
    
    Atributos:
        texto: Contenido del mensaje
        fechaDeCreado: Fecha y hora de creación
        autor: Usuario que creó el mensaje (relación 1)
        etiquetas: Lista de etiquetas (relación 0..*)
        menciones: Lista de menciones a usuarios (relación 1..*)
    
    Relaciones:
        - 1 Usuario (autor)
        - 0..* Etiquetas
        - 1..* Menciones (al menos 1)
    """
    
    # Campos básicos
    texto = StringField(required=True, max_length=500)
    fechaDeCreado = DateTimeField(default=datetime.utcnow)
    
    # Relaciones
    autor = ReferenceField(Usuario, required=True, reverse_delete_rule=2)  # CASCADE
    etiquetas = ListField(ReferenceField(Etiqueta), default=[])
    menciones = ListField(ReferenceField(Mencion), default=[])
    
    # Metadata
    meta = {
        'collection': 'mensajes',
        'db_alias': 'default',
        'indexes': [
            '-fechaDeCreado',  # Índice descendente para ordenar por fecha
            'autor',
            'etiquetas'
        ]
    }
    
    def clean(self):
        """Validación personalizada"""
        # Asegurar que hay al menos 1 mención (según el diagrama: 1..*)
        if not self.menciones or len(self.menciones) == 0:
            from mongoengine.errors import ValidationError
            raise ValidationError('El mensaje debe tener al menos una mención')
    
    def to_dict(self):
        """Convierte el mensaje a diccionario"""
        return {
            'id': str(self.id),
            'texto': self.texto,
            'fechaDeCreado': self.fechaDeCreado.isoformat(),
            'autor': self.autor.to_dict() if self.autor else None,
            'etiquetas': [etiqueta.to_dict() for etiqueta in self.etiquetas],
            'menciones': [mencion.to_dict() for mencion in self.menciones]
        }
    
    def __str__(self):
        return f"Mensaje(autor={self.autor.nickName if self.autor else 'Unknown'}, texto='{self.texto[:50]}...')"
