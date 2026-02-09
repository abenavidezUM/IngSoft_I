from models import Mensaje


def obtener_tablon(usuario, limit=50, offset=0):
    """
    Obtiene el tablón del usuario: mensajes propios + mensajes de usuarios seguidos.
    Según el enunciado, el tablón muestra mensajes de usuarios a los que sigue y los propios.
    
    Args:
        usuario: Usuario autenticado
        limit: Cantidad máxima de mensajes a retornar
        offset: Desplazamiento para paginación
    
    Returns:
        tuple: (mensajes: list, total: int)
    """
    try:
        usuario_id = usuario.id if hasattr(usuario, 'id') else usuario
        
        # Usar pymongo directamente
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        db = get_db('default')
        
        # Convertir a ObjectId si es necesario
        try:
            usuario_oid = ObjectId(usuario_id)
        except:
            usuario_oid = usuario_id
        
        # Obtener el documento del usuario para ver a quiénes sigue
        usuario_doc = db.usuarios.find_one({'_id': usuario_oid})
        if not usuario_doc:
            return [], 0
        
        siguiendo_ids = usuario_doc.get('siguiendo', [])
        autores_ids = [usuario_oid] + siguiendo_ids
        
        # Buscar mensajes de esos autores
        mensajes_docs = list(
            db.mensajes.find({
                'autor': {'$in': autores_ids}
            })
            .sort('fechaDeCreado', -1)
            .skip(offset)
            .limit(limit)
        )
        
        # Crear objetos de mensaje con información adicional
        mensajes = []
        for doc in mensajes_docs:
            try:
                # Obtener información del autor
                autor_id = doc.get('autor')
                autor_doc = db.usuarios.find_one({'_id': autor_id})
                
                class MensajeTablon:
                    def __init__(self, doc, autor_doc, usuario_actual_id):
                        self.id = str(doc['_id'])
                        self.texto = doc.get('texto', '')
                        self.fechaDeCreado = doc.get('fechaDeCreado')
                        self.esPublico = doc.get('esPublico', True)
                        self.autor_id = str(doc.get('autor'))
                        self.autor_nickName = autor_doc.get('nickName', 'Usuario') if autor_doc else 'Usuario'
                        self.autor_nombre = autor_doc.get('nombre', '') if autor_doc else ''
                        self.autor_apellido = autor_doc.get('apellido', '') if autor_doc else ''
                        self.etiquetas = doc.get('etiquetas', [])
                        self.menciones = doc.get('menciones', [])
                        # Marcar si es propio para que el frontend sepa si mostrar el botón de borrar
                        self.esPropio = str(doc.get('autor')) == str(usuario_actual_id)
                    
                    def to_dict(self):
                        return {
                            'id': self.id,
                            'texto': self.texto,
                            'fechaDeCreado': self.fechaDeCreado.isoformat() if self.fechaDeCreado else None,
                            'esPublico': self.esPublico,
                            'autor': {
                                'id': self.autor_id,
                                'nickName': self.autor_nickName,
                                'nombre': self.autor_nombre,
                                'apellido': self.autor_apellido
                            },
                            'etiquetas': [str(e) if hasattr(e, '__str__') else e for e in (self.etiquetas or [])],
                            'menciones': [str(m) if hasattr(m, '__str__') else m for m in (self.menciones or [])],
                            'esPropio': self.esPropio
                        }
                
                mensaje = MensajeTablon(doc, autor_doc, usuario_oid)
                mensajes.append(mensaje)
            except Exception as e:
                continue
        
        # Contar total
        total = db.mensajes.count_documents({
            'autor': {'$in': autores_ids}
        })
        
        return mensajes, total
    except Exception as e:
        return [], 0


def obtener_mis_mensajes(usuario, limit=50, offset=0):
    """
    Obtiene mensajes del usuario usando pymongo directamente para evitar problemas de thread local
    """
    try:
        autor_id = usuario.id if hasattr(usuario, 'id') else usuario
        
        # Usar pymongo directamente para evitar problemas de thread local
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        db = get_db('default')
        
        # Convertir autor_id a ObjectId si es necesario
        try:
            autor_oid = ObjectId(autor_id)
        except:
            autor_oid = autor_id
        
        # Buscar mensajes con pymongo
        mensajes_docs = list(
            db.mensajes.find({'autor': autor_oid})
            .sort('fechaDeCreado', -1)
            .skip(offset)
            .limit(limit)
        )
        
        # Crear objetos simples con los campos necesarios
        mensajes = []
        for doc in mensajes_docs:
            try:
                # Crear un objeto simple con los datos
                class MensajeSimple:
                    def __init__(self, doc):
                        self.id = str(doc['_id'])
                        self.texto = doc.get('texto', '')
                        self.fechaDeCreado = doc.get('fechaDeCreado')
                        self.esPublico = doc.get('esPublico', True)
                        self.autor = doc.get('autor')
                        self.etiquetas = doc.get('etiquetas', [])
                        self.menciones = doc.get('menciones', [])
                    
                    def to_dict(self):
                        return {
                            'id': self.id,
                            'texto': self.texto,
                            'fechaDeCreado': self.fechaDeCreado.isoformat() if self.fechaDeCreado else None,
                            'esPublico': self.esPublico
                        }
                
                mensaje = MensajeSimple(doc)
                mensajes.append(mensaje)
            except Exception as e:
                continue
        
        # Contar total
        total = db.mensajes.count_documents({'autor': autor_oid})
        
        return mensajes, total
    except Exception as e:
        return [], 0


def borrar_mensaje(usuario, mensaje_id):
    """
    Borra un mensaje del usuario.
    
    Args:
        usuario: Usuario que intenta borrar el mensaje
        mensaje_id: ID del mensaje a borrar
    
    Returns:
        tuple: (success: bool, message: str, status_code: int)
    """
    try:
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        db = get_db('default')
        
        # Convertir IDs a ObjectId
        try:
            mensaje_oid = ObjectId(mensaje_id)
        except:
            return False, "ID de mensaje inválido", 400
        
        try:
            usuario_oid = ObjectId(usuario.id) if hasattr(usuario, 'id') else ObjectId(usuario)
        except:
            return False, "ID de usuario inválido", 400
        
        # Buscar el mensaje
        mensaje_doc = db.mensajes.find_one({'_id': mensaje_oid})
        
        if not mensaje_doc:
            return False, "Mensaje no encontrado", 404
        
        # Verificar que el usuario es el autor
        if mensaje_doc.get('autor') != usuario_oid:
            return False, "No tienes permiso para borrar este mensaje", 403
        
        # Borrar el mensaje
        result = db.mensajes.delete_one({'_id': mensaje_oid})
        
        if result.deleted_count > 0:
            print(f"✅ Mensaje {mensaje_id} borrado exitosamente por usuario {usuario_oid}")
            return True, "Mensaje borrado exitosamente", 200
        else:
            return False, "Error al borrar el mensaje", 500
            
    except Exception as e:
        return False, f"Error interno al borrar el mensaje: {str(e)}", 500

