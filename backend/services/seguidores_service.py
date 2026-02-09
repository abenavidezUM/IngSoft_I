from datetime import datetime

def obtener_seguidores(usuario):
    """
    Obtiene la lista de seguidores de un usuario usando pymongo directamente.
    """
    from mongoengine.connection import get_db
    from bson import ObjectId
    from models import Usuario as UsuarioModel
    
    try:
        if not usuario or not hasattr(usuario, 'id'):
            return []
        
        usuario_id = usuario.id if hasattr(usuario, 'id') else usuario
        
        # Convertir a ObjectId si es necesario
        try:
            usuario_oid = ObjectId(usuario_id)
        except:
            usuario_oid = usuario_id
        
        # Obtener usuario desde la BD usando pymongo para evitar auto-dereferencing
        db = get_db('default')
        usuario_doc = db.usuarios.find_one({'_id': usuario_oid})
        
        if not usuario_doc:
            return []
        
        # Obtener IDs de seguidores directamente del documento
        seguidores_ids = usuario_doc.get('seguidores', [])
        
        if not seguidores_ids:
            return []
        
        # Obtener usuarios seguidores usando pymongo
        seguidores_docs = list(db.usuarios.find({'_id': {'$in': seguidores_ids}}))
        
        # Convertir a objetos Usuario sin auto-dereferencing
        seguidores = []
        for doc in seguidores_docs:
            try:
                seguidor = UsuarioModel()
                seguidor.id = doc['_id']
                seguidor.nickName = doc.get('nickName', '')
                seguidor.nombre = doc.get('nombre', '')
                seguidor.apellido = doc.get('apellido', '')
                seguidor.mail = doc.get('mail', '')
                seguidor.biografia = doc.get('biografia', '')
                seguidor.fotoUsuario = doc.get('fotoUsuario', '')
                seguidor.fotoUsuarioPortada = doc.get('fotoUsuarioPortada', '')
                seguidor.fechaDeCreado = doc.get('fechaDeCreado', datetime.utcnow())
                seguidor.rol = doc.get('rol', 'user')
                seguidor.seguidores = []
                seguidor.siguiendo = []
                seguidores.append(seguidor)
            except Exception as e:
                print(f"⚠️ Error al convertir seguidor {doc.get('_id')}: {e}")
                continue
        
        return seguidores
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error en obtener_seguidores: {e}")
        return []

