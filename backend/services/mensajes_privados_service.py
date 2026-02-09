"""
Servicio de Mensajes Privados (Gestor de Mensajes)
Contiene la lógica de negocio para mensajes privados según CU0010

Este servicio actúa como intermediario entre las rutas y los expertos de BD
(MensajePrivado y Usuario), implementando la lógica de negocio.
"""

from typing import List, Dict, Optional, Tuple
from utils.mongo_helpers import get_usuario_by_id
from models import MensajePrivado, Usuario
from repositories.mensaje_privado_repository import MensajePrivadoRepository
from repositories.usuario_repository import UsuarioRepository


def obtener_mensajes_privados(usuario_id: str) -> Tuple[List[MensajePrivado], bool]:
    """
    Obtiene todos los mensajes privados de un usuario (equivalente a obtenerMenPriv del diagrama)
    
    Args:
        usuario_id: ID del usuario
        
    Returns:
        Tuple[List[MensajePrivado], bool]: (lista de mensajes, hay_mensajes)
    """
    try:
        # Usar experto de BD (Repository)
        mensajes = MensajePrivadoRepository.gets_mensaje_privados(usuario_id)
        hay_mensajes = len(mensajes) > 0
        return mensajes, hay_mensajes
    except Exception as e:
        print(f"Error en obtener_mensajes_privados: {e}")
        return [], False


def obtener_conversacion(usuario_actual_id: str, otro_usuario_id: str, 
                         limit: int = 50, offset: int = 0) -> Dict:
    """
    Obtiene la conversación entre dos usuarios (equivalente a getsMenPriv del diagrama)
    
    Args:
        usuario_actual_id: ID del usuario actual
        otro_usuario_id: ID del otro usuario
        limit: Límite de mensajes
        offset: Offset para paginación
        
    Returns:
        Dict con conversación, total, limit, offset, hasMore
    """
    try:
        # Usar experto de BD (Repository)
        mensajes, total = MensajePrivadoRepository.gets_mensaje_privado(
            usuario_actual_id, otro_usuario_id, limit, offset
        )
        
        # Marcar como leídos los mensajes recibidos
        MensajePrivadoRepository.marcar_como_leido_por_receptor(otro_usuario_id, usuario_actual_id)
        
        # Obtener usuarios para el to_dict
        usuario_actual_obj = get_usuario_by_id(usuario_actual_id)
        otro_usuario_obj = get_usuario_by_id(otro_usuario_id)
        
        # Convertir mensajes a dict sin intentar dereferenciar
        conversacion_dicts = []
        for mensaje in mensajes:
            try:
                # Obtener IDs directamente
                if hasattr(mensaje, '_data') and 'emisor' in mensaje._data:
                    emisor_id = str(mensaje._data['emisor'])
                else:
                    emisor_id = str(mensaje.emisor) if hasattr(mensaje.emisor, '__str__') else str(mensaje.emisor)
                
                # Determinar qué usuario es emisor y receptor
                es_emisor = (emisor_id == usuario_actual_id)
                emisor_obj = usuario_actual_obj if es_emisor else otro_usuario_obj
                receptor_obj = otro_usuario_obj if es_emisor else usuario_actual_obj
                
                conversacion_dicts.append({
                    'id': str(mensaje.id),
                    'texto': mensaje.texto,
                    'fechaDeCreado': mensaje.fechaDeCreado.isoformat() if mensaje.fechaDeCreado else None,
                    'emisor': emisor_obj.to_dict() if emisor_obj else None,
                    'receptor': receptor_obj.to_dict() if receptor_obj else None,
                    'leido': mensaje.leido.isoformat() if mensaje.leido else None
                })
            except Exception as e:
                print(f"⚠️ Error creando dict de mensaje en conversación: {e}")
                continue
        
        return {
            'conversacion': conversacion_dicts,
            'total': total,
            'limit': limit,
            'offset': offset,
            'hasMore': (offset + limit) < total
        }
    except Exception as e:
        print(f"Error en obtener_conversacion: {e}")
        return {
            'conversacion': [],
            'total': 0,
            'limit': limit,
            'offset': offset,
            'hasMore': False
        }


def crear_mensaje_privado(emisor_id: str, receptor_id: str, texto: str) -> Optional[MensajePrivado]:
    """
    Crea un nuevo mensaje privado (equivalente a postMensaje del diagrama)
    
    Args:
        emisor_id: ID del emisor
        receptor_id: ID del receptor
        texto: Texto del mensaje
        
    Returns:
        MensajePrivado creado o None si hay error
    """
    try:
        # Validar que emisor y receptor existen
        emisor = get_usuario_by_id(emisor_id)
        receptor = get_usuario_by_id(receptor_id)
        
        if not emisor or not receptor:
            return None
        
        # Validar que no se envíe a sí mismo
        if str(emisor.id) == str(receptor.id):
            return None
        
        # Usar experto de BD (Repository)
        mensaje = MensajePrivadoRepository.post_mensaje(texto, emisor, receptor)
        return mensaje
    except Exception as e:
        print(f"Error en crear_mensaje_privado: {e}")
        return None


def listar_conversaciones(usuario_id: str) -> List[Dict]:
    """
    Lista todas las conversaciones del usuario con último mensaje y contador de no leídos
    
    Args:
        usuario_id: ID del usuario
        
    Returns:
        Lista de conversaciones con usuario, último mensaje y mensajes no leídos
    """
    try:
        # Obtener todos los mensajes del usuario usando experto de BD (Repository)
        mensajes = MensajePrivadoRepository.gets_mensaje_privados(usuario_id)
        
        # Agrupar por conversación
        conversaciones_dict = {}
        usuario_actual = get_usuario_by_id(usuario_id)
        
        if not usuario_actual:
            return []
        
        for mensaje in mensajes:
            # Obtener IDs directamente sin intentar dereferenciar
            # Los mensajes vienen del repositorio con emisor/receptor como ObjectIds
            try:
                # Intentar obtener IDs de diferentes formas para evitar problemas de thread local
                if hasattr(mensaje, '_data') and 'emisor' in mensaje._data:
                    emisor_id = str(mensaje._data['emisor'])
                elif hasattr(mensaje.emisor, 'id'):
                    emisor_id = str(mensaje.emisor.id)
                else:
                    emisor_id = str(mensaje.emisor)
                
                if hasattr(mensaje, '_data') and 'receptor' in mensaje._data:
                    receptor_id = str(mensaje._data['receptor'])
                elif hasattr(mensaje.receptor, 'id'):
                    receptor_id = str(mensaje.receptor.id)
                else:
                    receptor_id = str(mensaje.receptor)
            except Exception as e:
                print(f"⚠️ Error obteniendo IDs de mensaje: {e}")
                # Si falla, intentar obtener del documento original
                from mongoengine.connection import get_db
                from bson import ObjectId
                db = get_db('default')
                msg_doc = db.mensajes_privados.find_one({'_id': ObjectId(str(mensaje.id))})
                if msg_doc:
                    emisor_id = str(msg_doc.get('emisor', ''))
                    receptor_id = str(msg_doc.get('receptor', ''))
                else:
                    continue
            
            usuario_actual_id_str = str(usuario_actual.id)
            
            if emisor_id == usuario_actual_id_str:
                otro_usuario_id = receptor_id
            else:
                otro_usuario_id = emisor_id
            
            # Si es la primera vez que vemos este usuario, agregarlo
            if otro_usuario_id not in conversaciones_dict:
                otro_usuario = get_usuario_by_id(otro_usuario_id)
                if not otro_usuario:
                    continue
                
                # Contar mensajes no leídos usando experto de BD (Repository)
                no_leidos = MensajePrivadoRepository.contar_no_leidos(otro_usuario_id, usuario_actual_id_str)
                
                # Crear un dict del mensaje sin intentar dereferenciar
                try:
                    mensaje_dict = {
                        'id': str(mensaje.id),
                        'texto': mensaje.texto,
                        'fechaDeCreado': mensaje.fechaDeCreado.isoformat() if mensaje.fechaDeCreado else None,
                        'emisor': otro_usuario.to_dict() if emisor_id == otro_usuario_id else usuario_actual.to_dict(),
                        'receptor': usuario_actual.to_dict() if receptor_id == usuario_actual_id_str else otro_usuario.to_dict(),
                        'leido': mensaje.leido.isoformat() if mensaje.leido else None
                    }
                except Exception as e:
                    print(f"⚠️ Error creando dict de mensaje: {e}")
                    mensaje_dict = mensaje.to_dict()
                
                conversaciones_dict[otro_usuario_id] = {
                    'usuario': otro_usuario.to_dict(),
                    'ultimoMensaje': mensaje_dict,
                    'mensajesNoLeidos': no_leidos
                }
        
        return list(conversaciones_dict.values())
    except Exception as e:
        print(f"Error en listar_conversaciones: {e}")
        return []


def marcar_mensaje_como_leido(mensaje_id: str, usuario_id: str) -> bool:
    """
    Marca un mensaje como leído
    
    Args:
        mensaje_id: ID del mensaje
        usuario_id: ID del usuario (debe ser el receptor)
        
    Returns:
        True si se marcó correctamente, False en caso contrario
    """
    try:
        # Usar experto de BD (Repository)
        return MensajePrivadoRepository.marcar_como_leido(mensaje_id, usuario_id)
    except Exception as e:
        print(f"Error en marcar_mensaje_como_leido: {e}")
        return False


def contar_mensajes_no_leidos(usuario_id: str) -> int:
    """
    Cuenta los mensajes no leídos del usuario
    
    Args:
        usuario_id: ID del usuario
        
    Returns:
        Número de mensajes no leídos
    """
    try:
        # Usar experto de BD (Repository)
        return MensajePrivadoRepository.contar_no_leidos_por_receptor(usuario_id)
    except Exception as e:
        print(f"Error en contar_mensajes_no_leidos: {e}")
        return 0


def obtener_usuarios_por_ids(usuario_ids: List[str]) -> List[Usuario]:
    """
    Obtiene una lista de usuarios por sus IDs (equivalente a getsUsuarios del diagrama)
    
    Args:
        usuario_ids: Lista de IDs de usuarios
        
    Returns:
        Lista de usuarios
    """
    try:
        # Usar experto de BD (Repository)
        return UsuarioRepository.gets_usuarios(usuario_ids)
    except Exception as e:
        print(f"Error en obtener_usuarios_por_ids: {e}")
        return []

