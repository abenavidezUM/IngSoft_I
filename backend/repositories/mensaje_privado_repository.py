"""
Repositorio de MensajePrivado (Experto de BD)
Contiene métodos para acceder a la base de datos de mensajes privados
"""

from typing import List, Tuple, Optional
from datetime import datetime
from models.mensaje_privado import MensajePrivado
from models.usuario import Usuario


class MensajePrivadoRepository:
    """
    Experto de BD para MensajePrivado
    Implementa métodos de acceso a datos según el diagrama de secuencia
    """
    
    @staticmethod
    def gets_mensaje_privados(usuario_id: str) -> List[MensajePrivado]:
        """
        Obtiene todos los mensajes privados de un usuario
        (equivalente a getsMensajePrivados del diagrama)
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de MensajePrivado ordenados por fecha descendente
        """
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        try:
            db = get_db('default')
            
            try:
                usuario_oid = ObjectId(usuario_id)
            except:
                usuario_oid = usuario_id
            
            # Buscar mensajes donde el usuario es emisor o receptor
            mensajes_docs = list(
                db.mensajes_privados.find({
                    '$or': [
                        {'emisor': usuario_oid},
                        {'receptor': usuario_oid}
                    ]
                }).sort('fechaDeCreado', -1)
            )
            
            # Convertir a objetos MensajePrivado sin auto-dereferencing
            mensajes = []
            for doc in mensajes_docs:
                try:
                    # Crear objeto MensajePrivado manualmente para evitar auto-dereferencing
                    mensaje = MensajePrivado()
                    # Asignar ID primero
                    mensaje._id = doc['_id']
                    mensaje.id = doc['_id']
                    # Asignar campos usando _data para evitar auto-dereferencing
                    mensaje._data = {
                        'texto': doc.get('texto', ''),
                        'fechaDeCreado': doc.get('fechaDeCreado', datetime.utcnow()),
                        'leido': doc.get('leido'),
                        'emisor': doc.get('emisor'),
                        'receptor': doc.get('receptor')
                    }
                    # Asignar campos directamente también
                    mensaje.texto = doc.get('texto', '')
                    mensaje.fechaDeCreado = doc.get('fechaDeCreado', datetime.utcnow())
                    mensaje.leido = doc.get('leido')
                    # Asignar los ObjectIds directamente a los campos para evitar auto-dereferencing
                    mensaje.emisor = doc.get('emisor')
                    mensaje.receptor = doc.get('receptor')
                    mensajes.append(mensaje)
                except Exception as e:
                    print(f"⚠️ Error al convertir mensaje {doc.get('_id')}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            return mensajes
        except Exception as e:
            print(f"Error en gets_mensaje_privados: {e}")
            return []
    
    @staticmethod
    def gets_mensaje_privado(usuario_actual_id: str, otro_usuario_id: str,
                             limit: int = 50, offset: int = 0) -> Tuple[List[MensajePrivado], int]:
        """
        Obtiene la conversación entre dos usuarios
        (equivalente a getsMenPriv del diagrama)
        
        Args:
            usuario_actual_id: ID del usuario actual
            otro_usuario_id: ID del otro usuario
            limit: Límite de mensajes
            offset: Offset para paginación
            
        Returns:
            Tuple[List[MensajePrivado], int]: (mensajes, total)
        """
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        try:
            db = get_db('default')
            
            try:
                usuario_actual_oid = ObjectId(usuario_actual_id)
                otro_usuario_oid = ObjectId(otro_usuario_id)
            except:
                usuario_actual_oid = usuario_actual_id
                otro_usuario_oid = otro_usuario_id
            
            # Buscar mensajes entre los dos usuarios
            query = {
                '$or': [
                    {'emisor': usuario_actual_oid, 'receptor': otro_usuario_oid},
                    {'emisor': otro_usuario_oid, 'receptor': usuario_actual_oid}
                ]
            }
            
            # Obtener mensajes con paginación
            mensajes_docs = list(
                db.mensajes_privados.find(query)
                .sort('fechaDeCreado', 1)  # Ascendente para mostrar más antiguos primero
                .skip(offset)
                .limit(limit)
            )
            
            # Contar total
            total = db.mensajes_privados.count_documents(query)
            
            # Convertir a objetos MensajePrivado sin auto-dereferencing
            mensajes = []
            for doc in mensajes_docs:
                try:
                    # Crear objeto MensajePrivado manualmente para evitar auto-dereferencing
                    mensaje = MensajePrivado()
                    # Asignar ID primero
                    mensaje._id = doc['_id']
                    mensaje.id = doc['_id']
                    # Asignar campos usando _data para evitar auto-dereferencing
                    mensaje._data = {
                        'texto': doc.get('texto', ''),
                        'fechaDeCreado': doc.get('fechaDeCreado', datetime.utcnow()),
                        'leido': doc.get('leido'),
                        'emisor': doc.get('emisor'),
                        'receptor': doc.get('receptor')
                    }
                    # Asignar campos directamente también
                    mensaje.texto = doc.get('texto', '')
                    mensaje.fechaDeCreado = doc.get('fechaDeCreado', datetime.utcnow())
                    mensaje.leido = doc.get('leido')
                    # Asignar los ObjectIds directamente a los campos para evitar auto-dereferencing
                    mensaje.emisor = doc.get('emisor')
                    mensaje.receptor = doc.get('receptor')
                    mensajes.append(mensaje)
                except Exception as e:
                    print(f"⚠️ Error al convertir mensaje {doc.get('_id')}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            return mensajes, total
        except Exception as e:
            print(f"Error en gets_mensaje_privado: {e}")
            return [], 0
    
    @staticmethod
    def post_mensaje(texto: str, emisor: Usuario, receptor: Usuario) -> MensajePrivado:
        """
        Crea y guarda un nuevo mensaje privado
        (equivalente a postMensaje del diagrama)
        
        Args:
            texto: Texto del mensaje
            emisor: Objeto Usuario emisor
            receptor: Objeto Usuario receptor
            
        Returns:
            MensajePrivado creado
        """
        mensaje = MensajePrivado(
            texto=texto,
            emisor=emisor,
            receptor=receptor
        )
        mensaje.save()
        return mensaje
    
    @staticmethod
    def marcar_como_leido(mensaje_id: str, usuario_id: str) -> bool:
        """
        Marca un mensaje como leído
        
        Args:
            mensaje_id: ID del mensaje
            usuario_id: ID del usuario (debe ser el receptor)
            
        Returns:
            True si se marcó correctamente, False en caso contrario
        """
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        try:
            db = get_db('default')
            
            try:
                mensaje_oid = ObjectId(mensaje_id)
                usuario_oid = ObjectId(usuario_id)
            except:
                mensaje_oid = mensaje_id
                usuario_oid = usuario_id
            
            # Buscar mensaje y verificar que el usuario es el receptor
            mensaje_doc = db.mensajes_privados.find_one({
                '_id': mensaje_oid,
                'receptor': usuario_oid
            })
            
            if mensaje_doc:
                # Actualizar campo leido
                db.mensajes_privados.update_one(
                    {'_id': mensaje_oid},
                    {'$set': {'leido': datetime.utcnow()}}
                )
                return True
            
            return False
        except Exception as e:
            print(f"Error en marcar_como_leido: {e}")
            return False
    
    @staticmethod
    def marcar_como_leido_por_receptor(emisor_id: str, receptor_id: str) -> None:
        """
        Marca todos los mensajes no leídos de un emisor a un receptor como leídos
        
        Args:
            emisor_id: ID del emisor
            receptor_id: ID del receptor
        """
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        try:
            db = get_db('default')
            
            try:
                emisor_oid = ObjectId(emisor_id)
                receptor_oid = ObjectId(receptor_id)
            except:
                emisor_oid = emisor_id
                receptor_oid = receptor_id
            
            # Actualizar todos los mensajes no leídos
            db.mensajes_privados.update_many(
                {
                    'emisor': emisor_oid,
                    'receptor': receptor_oid,
                    'leido': None
                },
                {'$set': {'leido': datetime.utcnow()}}
            )
        except Exception as e:
            print(f"Error en marcar_como_leido_por_receptor: {e}")
    
    @staticmethod
    def contar_no_leidos(emisor_id: str, receptor_id: str) -> int:
        """
        Cuenta mensajes no leídos de un emisor a un receptor
        
        Args:
            emisor_id: ID del emisor
            receptor_id: ID del receptor
            
        Returns:
            Número de mensajes no leídos
        """
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        try:
            db = get_db('default')
            
            try:
                emisor_oid = ObjectId(emisor_id)
                receptor_oid = ObjectId(receptor_id)
            except:
                emisor_oid = emisor_id
                receptor_oid = receptor_id
            
            return db.mensajes_privados.count_documents({
                'emisor': emisor_oid,
                'receptor': receptor_oid,
                'leido': None
            })
        except Exception as e:
            print(f"Error en contar_no_leidos: {e}")
            return 0
    
    @staticmethod
    def contar_no_leidos_por_receptor(receptor_id: str) -> int:
        """
        Cuenta todos los mensajes no leídos de un receptor
        
        Args:
            receptor_id: ID del receptor
            
        Returns:
            Número de mensajes no leídos
        """
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        try:
            db = get_db('default')
            
            try:
                receptor_oid = ObjectId(receptor_id)
            except:
                receptor_oid = receptor_id
            
            return db.mensajes_privados.count_documents({
                'receptor': receptor_oid,
                'leido': None
            })
        except Exception as e:
            print(f"Error en contar_no_leidos_por_receptor: {e}")
            return 0

