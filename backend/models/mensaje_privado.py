from mongoengine import Document, StringField, DateTimeField, ReferenceField
from datetime import datetime
from .usuario import Usuario

class MensajePrivado(Document):
    """
    Modelo de Mensaje Privado
    
    Representa un mensaje privado entre dos usuarios (similar a DM).
    
    Atributos:
        texto: Contenido del mensaje privado
        fechaDeCreado: Fecha y hora de creación
        emisor: Usuario que envía el mensaje
        receptor: Usuario que recibe el mensaje
    
    Relaciones:
        - 2 Usuarios (emisor y receptor)
    """
    
    # Campos básicos
    texto = StringField(required=True, max_length=1000)
    fechaDeCreado = DateTimeField(default=datetime.utcnow)
    
    # Relaciones (2 usuarios según el diagrama)
    emisor = ReferenceField(Usuario, required=True, reverse_delete_rule=2)  # CASCADE
    receptor = ReferenceField(Usuario, required=True, reverse_delete_rule=2)  # CASCADE
    
    # Estado del mensaje
    leido = DateTimeField(default=None)  # null si no ha sido leído
    
    # Metadata
    meta = {
        'collection': 'mensajes_privados',
        'db_alias': 'default',
        'indexes': [
            '-fechaDeCreado',  # Índice descendente para ordenar por fecha
            'emisor',
            'receptor',
            ('emisor', 'receptor'),  # Índice compuesto para búsquedas de conversaciones
            'leido'
        ]
    }
    
    def marcar_como_leido(self):
        """Marca el mensaje como leído"""
        if not self.leido:
            self.leido = datetime.utcnow()
            self.save()
    
    def to_dict(self):
        """Convierte el mensaje privado a diccionario"""
        # Manejar emisor y receptor que pueden ser ObjectIds o objetos Usuario
        emisor_dict = None
        receptor_dict = None
        
        try:
            # Si emisor es un objeto Usuario, usar to_dict()
            if hasattr(self.emisor, 'to_dict'):
                emisor_dict = self.emisor.to_dict()
            # Si es un ObjectId, intentar obtener el usuario
            elif hasattr(self, '_data') and 'emisor' in self._data:
                from utils.mongo_helpers import get_usuario_by_id
                emisor_obj = get_usuario_by_id(str(self._data['emisor']))
                emisor_dict = emisor_obj.to_dict() if emisor_obj else None
            elif self.emisor:
                from utils.mongo_helpers import get_usuario_by_id
                emisor_obj = get_usuario_by_id(str(self.emisor))
                emisor_dict = emisor_obj.to_dict() if emisor_obj else None
        except Exception as e:
            print(f"⚠️ Error obteniendo emisor en to_dict: {e}")
        
        try:
            # Si receptor es un objeto Usuario, usar to_dict()
            if hasattr(self.receptor, 'to_dict'):
                receptor_dict = self.receptor.to_dict()
            # Si es un ObjectId, intentar obtener el usuario
            elif hasattr(self, '_data') and 'receptor' in self._data:
                from utils.mongo_helpers import get_usuario_by_id
                receptor_obj = get_usuario_by_id(str(self._data['receptor']))
                receptor_dict = receptor_obj.to_dict() if receptor_obj else None
            elif self.receptor:
                from utils.mongo_helpers import get_usuario_by_id
                receptor_obj = get_usuario_by_id(str(self.receptor))
                receptor_dict = receptor_obj.to_dict() if receptor_obj else None
        except Exception as e:
            print(f"⚠️ Error obteniendo receptor en to_dict: {e}")
        
        return {
            'id': str(self.id),
            'texto': self.texto,
            'fechaDeCreado': self.fechaDeCreado.isoformat() if self.fechaDeCreado else None,
            'emisor': emisor_dict,
            'receptor': receptor_dict,
            'leido': self.leido.isoformat() if self.leido else None
        }
    
    def __str__(self):
        return f"MensajePrivado(de={self.emisor.nickName if self.emisor else 'Unknown'}, " \
               f"para={self.receptor.nickName if self.receptor else 'Unknown'})"
