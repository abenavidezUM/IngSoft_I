from models import Mensaje


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
        
        print(f"🔍 Buscando mensajes para autor_oid: {autor_oid}")
        
        # Buscar mensajes con pymongo
        mensajes_docs = list(
            db.mensajes.find({'autor': autor_oid, 'esPublico': True})
            .sort('fechaDeCreado', -1)
            .skip(offset)
            .limit(limit)
        )
        
        print(f"📊 Encontrados {len(mensajes_docs)} mensajes en BD")
        
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
                print(f"✅ Mensaje agregado: {mensaje.id[:8]}... - {mensaje.texto[:30]}...")
            except Exception as e:
                print(f"⚠️ Error al convertir mensaje {doc.get('_id')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Contar total
        total = db.mensajes.count_documents({'autor': autor_oid, 'esPublico': True})
        print(f"📊 Total de mensajes públicos del usuario: {total}")
        
        return mensajes, total
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error en obtener_mis_mensajes: {e}")
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
        import traceback
        traceback.print_exc()
        print(f"Error en borrar_mensaje: {e}")
        return False, f"Error interno al borrar el mensaje: {str(e)}", 500

