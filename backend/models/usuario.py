from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(Document):
    """
    Modelo de Usuario
    
    Atributos:
        nickName: Nombre de usuario único
        nombre: Nombre real del usuario
        apellido: Apellido del usuario
        mail: Correo electrónico (único)
        contraseña: Contraseña hasheada
        biografia: Biografía del usuario
        fechaDeCreado: Fecha de creación de la cuenta
        fotoUsuario: URL de la foto de perfil
        fotoUsuarioPortada: URL de la foto de portada
        rol: Rol del usuario (admin, user, guest)
    """
    
    # Campos básicos
    nickName = StringField(required=True, unique=True, max_length=50)
    nombre = StringField(required=True, max_length=100)
    apellido = StringField(required=True, max_length=100)
    mail = StringField(required=True, unique=True, max_length=255)
    contraseña = StringField(required=True)
    
    # Campos opcionales
    biografia = StringField(max_length=500, default="")
    fotoUsuario = StringField(default="")
    fotoUsuarioPortada = StringField(default="")
    
    # Campos de sistema
    fechaDeCreado = DateTimeField(default=datetime.utcnow)
    rol = StringField(choices=['admin', 'user', 'guest'], default='user')
    
    # Relaciones de seguidores
    seguidores = ListField(ReferenceField('self'), default=[])
    siguiendo = ListField(ReferenceField('self'), default=[])

    # Metadata
    meta = {
        'collection': 'usuarios',
        'db_alias': 'default',
        'indexes': [
            'nickName',
            'mail',
            'fechaDeCreado',
            'seguidores',
            'siguiendo'
        ]
    }
    
    def set_password(self, password):
        """Hashea y guarda la contraseña"""
        self.contraseña = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        return check_password_hash(self.contraseña, password)
    
    def to_dict(self):
        """Convierte el usuario a diccionario (sin contraseña)"""
        return {
            'id': str(self.id),
            'nickName': self.nickName,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'mail': self.mail,
            'biografia': self.biografia,
            'fotoUsuario': self.fotoUsuario,
            'fotoUsuarioPortada': self.fotoUsuarioPortada,
            'fechaDeCreado': self.fechaDeCreado.isoformat(),
            'rol': self.rol,
            'seguidores': [str(u.id) for u in self.seguidores],
            'siguiendo': [str(u.id) for u in self.siguiendo]
        }
    
    def __str__(self):
        return f"Usuario({self.nickName})"
        """
        Experto de BD: Obtiene una lista de usuarios por sus IDs
        (equivalente a getsUsuarios del diagrama)
        
        Args:
            usuario_ids: Lista de IDs de usuarios (pueden ser strings o ObjectIds)
            
        Returns:
            Lista de Usuario
        """
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        try:
            db = get_db('default')
            
            # Convertir IDs a ObjectId
            usuario_oids = []
            for uid in usuario_ids:
                try:
                    usuario_oids.append(ObjectId(uid))
                except:
                    usuario_oids.append(uid)
            
            # Buscar usuarios
            usuarios_docs = list(
                db.usuarios.find({'_id': {'$in': usuario_oids}})
            )
            
            # Convertir a objetos Usuario
            usuarios = []
            for doc in usuarios_docs:
                try:
                    usuario = cls._from_son(doc)
                    usuarios.append(usuario)
                except Exception as e:
                    print(f"⚠️ Error al convertir usuario {doc.get('_id')}: {e}")
                    continue
            
            return usuarios
        except Exception as e:
            print(f"Error en gets_usuarios: {e}")
            return []
