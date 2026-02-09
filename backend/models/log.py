from mongoengine import Document, StringField, DateTimeField, DictField
from datetime import datetime

class Log(Document):
    """
    Modelo de Log (Base de datos logs_db)
    
    Almacena logs y eventos del sistema para auditoría.
    
    Atributos:
        level: Nivel del log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Mensaje del log
        timestamp: Fecha y hora del evento
        user_id: ID del usuario relacionado (opcional)
        action: Acción realizada
        ip_address: Dirección IP del cliente
        metadata: Datos adicionales en formato JSON
    """
    
    # Campos básicos
    level = StringField(required=True, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    message = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    
    # Campos opcionales
    user_id = StringField(default=None)
    action = StringField(default=None)
    ip_address = StringField(default=None)
    metadata = DictField(default={})
    
    # Metadata
    meta = {
        'collection': 'logs',
        'db_alias': 'logs',  # Base de datos de logs
        'indexes': [
            '-timestamp',  # Índice descendente
            'level',
            'user_id',
            'action'
        ]
    }
    
    @staticmethod
    def log_event(level, message, user_id=None, action=None, ip_address=None, metadata=None):
        """Método estático para crear logs fácilmente"""
        log = Log(
            level=level,
            message=message,
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            metadata=metadata or {}
        )
        log.save(using='logs')  # Especificar el alias de la base de datos
        return log
    
    def to_dict(self):
        """Convierte el log a diccionario"""
        return {
            'id': str(self.id),
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'action': self.action,
            'ip_address': self.ip_address,
            'metadata': self.metadata
        }
    
    def __str__(self):
        return f"Log({self.level} - {self.message[:50]})"
