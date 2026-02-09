"""
Helper functions para consultas de MongoEngine que evitan problemas de thread local
Usa pymongo directamente para evitar problemas de thread local
"""
from bson import ObjectId


def get_usuario_by_id(usuario_id):
    """
    Obtiene un usuario por ID de forma segura usando select_related(0) para evitar thread local
    """
    from models import Usuario
    from mongoengine.connection import get_db
    
    try:
        try:
            oid = ObjectId(usuario_id)
        except:
            oid = usuario_id
        
        print(f"🔍 Buscando usuario con ID: {oid} (tipo: {type(oid)})")
        
        # Intentar primero con pymongo directamente para evitar problemas de thread local
        try:
            db = get_db('default')
            user_doc = db.usuarios.find_one({'_id': oid})
            if user_doc:
                print(f"✅ Usuario encontrado con pymongo: {user_doc.get('nickName', 'N/A')}")
                # Crear objeto Usuario desde el documento
                usuario = Usuario()
                usuario.id = user_doc['_id']
                usuario.nickName = user_doc.get('nickName', '')
                usuario.nombre = user_doc.get('nombre', '')
                usuario.apellido = user_doc.get('apellido', '')
                usuario.mail = user_doc.get('mail', '')
                usuario.biografia = user_doc.get('biografia', '')
                usuario.fotoUsuario = user_doc.get('fotoUsuario', '')
                usuario.fotoUsuarioPortada = user_doc.get('fotoUsuarioPortada', '')
                usuario.fechaDeCreado = user_doc.get('fechaDeCreado', None)
                usuario.rol = user_doc.get('rol', 'user')
                usuario.seguidores = []
                usuario.siguiendo = []
                return usuario
            else:
                print(f"❌ Usuario no encontrado con pymongo para ID: {oid}")
        except Exception as e:
            print(f"⚠️ Error usando pymongo: {e}")
        
        # Fallback: intentar obtener con MongoEngine sin select_related para evitar thread local
        try:
            # Usar list() para forzar evaluación y evitar problemas de thread local
            usuarios = list(Usuario.objects(id=oid).limit(1))
            if usuarios:
                usuario = usuarios[0]
                print(f"✅ Usuario encontrado con MongoEngine: {usuario.nickName}")
                return usuario
            else:
                print(f"❌ Usuario no encontrado con MongoEngine para ID: {oid}")
        except Exception as e:
            print(f"⚠️ Error en fallback MongoEngine: {e}")
        
        return None
    except Exception as e:
        print(f"❌ Error en get_usuario_by_id: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_usuario_by_nickname(nickname):
    """
    Obtiene un usuario por nickname de forma segura usando pymongo directamente
    """
    from models import Usuario
    from mongoengine.connection import get_db
    
    try:
        db = get_db('default')
        
        # Buscar documento directamente con pymongo
        user_doc = db.usuarios.find_one({'nickName': nickname})
        
        if user_doc:
            # Crear objeto Usuario desde el documento
            usuario = Usuario()
            usuario.id = user_doc['_id']
            usuario.nickName = user_doc.get('nickName', '')
            usuario.nombre = user_doc.get('nombre', '')
            usuario.apellido = user_doc.get('apellido', '')
            usuario.mail = user_doc.get('mail', '')
            usuario.biografia = user_doc.get('biografia', '')
            usuario.fotoUsuario = user_doc.get('fotoUsuario', '')
            usuario.fotoUsuarioPortada = user_doc.get('fotoUsuarioPortada', '')
            usuario.fechaDeCreado = user_doc.get('fechaDeCreado', None)
            usuario.rol = user_doc.get('rol', 'user')
            # Cargar referencias básicas (sin resolver completamente para evitar recursión)
            usuario.seguidores = []  # Se cargarán cuando se necesiten
            usuario.siguiendo = []  # Se cargarán cuando se necesiten
            return usuario
        
        return None
    except Exception as e:
        print(f"Error en get_usuario_by_nickname: {e}")
        return None


def get_mensaje_privado_by_id(mensaje_id):
    """
    Obtiene un mensaje privado por ID de forma segura usando pymongo directamente
    """
    from models import MensajePrivado
    from mongoengine.connection import get_db
    
    try:
        db = get_db('default')
        
        try:
            oid = ObjectId(mensaje_id)
        except:
            oid = mensaje_id
        
        msg_doc = db.mensajes_privados.find_one({'_id': oid})
        
        if msg_doc:
            # Crear objeto MensajePrivado manualmente para evitar auto-dereferencing
            from datetime import datetime
            mensaje = MensajePrivado()
            # Asignar ID primero
            mensaje._id = msg_doc['_id']
            mensaje.id = msg_doc['_id']
            # Asignar campos usando _data para evitar auto-dereferencing
            mensaje._data = {
                'texto': msg_doc.get('texto', ''),
                'fechaDeCreado': msg_doc.get('fechaDeCreado', datetime.utcnow()),
                'leido': msg_doc.get('leido'),
                'emisor': msg_doc.get('emisor'),
                'receptor': msg_doc.get('receptor')
            }
            # Asignar campos directamente también
            mensaje.texto = msg_doc.get('texto', '')
            mensaje.fechaDeCreado = msg_doc.get('fechaDeCreado', datetime.utcnow())
            mensaje.leido = msg_doc.get('leido')
            # Asignar los ObjectIds directamente a los campos para evitar auto-dereferencing
            mensaje.emisor = msg_doc.get('emisor')
            mensaje.receptor = msg_doc.get('receptor')
            return mensaje
        
        return None
    except:
        return None

