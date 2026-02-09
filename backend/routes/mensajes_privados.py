"""
Rutas para Mensajes Privados (CU0010)

Endpoints:
- POST /api/mensajes-privados - Crear mensaje privado
- GET /api/mensajes-privados/conversacion/<user_id> - Obtener conversación
- GET /api/mensajes-privados/conversaciones - Listar conversaciones
- PUT /api/mensajes-privados/<mensaje_id>/leer - Marcar como leído
- GET /api/mensajes-privados/no-leidos - Contar mensajes no leídos
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.log import Log
from utils.validators import validar_mensaje_privado
from utils.decorators import rate_limit
import utils.mongo_helpers
import services.mensajes_privados_service

# Crear blueprint
mensajes_privados_bp = Blueprint('mensajes_privados', __name__)


@mensajes_privados_bp.route('/mensajes-privados', methods=['POST'])
@jwt_required()
@rate_limit(max_requests=10, window_seconds=60)  # 10 mensajes por minuto
def crear_mensaje_privado_route():
    """
    Crear un nuevo mensaje privado
    
    Body:
        {
            "receptor_id": "user_id",
            "texto": "mensaje"
        }
    
    Returns:
        201: Mensaje creado exitosamente
        400: Datos inválidos
        404: Receptor no encontrado
        429: Rate limit excedido
    """
    try:
        # Obtener usuario autenticado (emisor)
        emisor_id = get_jwt_identity()
        emisor = utils.mongo_helpers.get_usuario_by_id(emisor_id)
        
        if not emisor:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Obtener datos del request
        data = request.get_json()
        receptor_id = data.get('receptor_id')
        texto = data.get('texto', '').strip()
        
        # Validar datos
        es_valido, mensaje_error = validar_mensaje_privado(texto, emisor_id, receptor_id)
        if not es_valido:
            return jsonify({
                'success': False,
                'error': mensaje_error,
                'code': 'VALIDATION_ERROR'
            }), 400
        
        # Usar servicio (Gestor de Mensajes) para crear mensaje
        mensaje = services.mensajes_privados_service.crear_mensaje_privado(emisor_id, receptor_id, texto)
        
        if not mensaje:
            return jsonify({
                'success': False,
                'error': 'No se pudo crear el mensaje. Verifica que el receptor exista y no sea el mismo que el emisor.',
                'code': 'MESSAGE_CREATION_ERROR'
            }), 400
        
        # Registrar en logs
        emisor = utils.mongo_helpers.get_usuario_by_id(emisor_id)
        receptor = utils.mongo_helpers.get_usuario_by_id(receptor_id)
        if emisor and receptor:
            Log.log_event(
                level='INFO',
                message=f'Mensaje privado enviado de {emisor.nickName} a {receptor.nickName}',
                user_id=str(emisor.id),
                action='send_private_message',
                ip_address=request.remote_addr,
                metadata={
                    'mensaje_id': str(mensaje.id),
                    'receptor_id': str(receptor.id),
                    'texto_length': len(texto)
                }
            )
        
        # Retornar respuesta
        return jsonify({
            'success': True,
            'data': mensaje.to_dict()
        }), 201
        
    except Exception as e:
        # Log del error
        Log.log_event(
            level='ERROR',
            message=f'Error al crear mensaje privado: {str(e)}',
            user_id=emisor_id if 'emisor_id' in locals() else None,
            action='send_private_message_error',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/conversacion/<user_id>', methods=['GET'])
@jwt_required()
def obtener_conversacion_route(user_id):
    """
    Obtener conversación con un usuario específico
    
    Query params:
        limit: número de mensajes (default: 50)
        offset: offset para paginación (default: 0)
    
    Returns:
        200: Conversación obtenida
        404: Usuario no encontrado
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = utils.mongo_helpers.get_usuario_by_id(usuario_actual_id)
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Verificar que el otro usuario existe
        otro_usuario = utils.mongo_helpers.get_usuario_by_id(user_id)
        if not otro_usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'code': 'USER_NOT_FOUND'
            }), 404
        
        # Obtener parámetros de paginación
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Usar servicio (Gestor de Mensajes) para obtener conversación
        data = services.mensajes_privados_service.obtener_conversacion(usuario_actual_id, user_id, limit, offset)
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error al obtener conversación',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/conversaciones', methods=['GET'])
@jwt_required()
def listar_conversaciones_route():
    """
    Listar todas las conversaciones del usuario actual
    
    Returns:
        200: Lista de conversaciones con último mensaje y contador de no leídos
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = utils.mongo_helpers.get_usuario_by_id(usuario_actual_id)
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Usar servicio (Gestor de Mensajes) para listar conversaciones
        conversaciones = services.mensajes_privados_service.listar_conversaciones(usuario_actual_id)
        
        return jsonify({
            'success': True,
            'data': conversaciones
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error al listar conversaciones: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/<mensaje_id>/leer', methods=['PUT'])
@jwt_required()
def marcar_como_leido_route(mensaje_id):
    """
    Marcar un mensaje como leído
    
    Returns:
        200: Mensaje marcado como leído
        404: Mensaje no encontrado
        403: No autorizado
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = utils.mongo_helpers.get_usuario_by_id(usuario_actual_id)
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Usar servicio (Gestor de Mensajes) para marcar como leído
        exito = services.mensajes_privados_service.marcar_mensaje_como_leido(mensaje_id, usuario_actual_id)
        
        if not exito:
            return jsonify({
                'success': False,
                'error': 'Mensaje no encontrado o no tienes permiso para marcarlo',
                'code': 'MESSAGE_NOT_FOUND_OR_FORBIDDEN'
            }), 404
        
        # Obtener mensaje actualizado para retornar
        mensaje = utils.mongo_helpers.get_mensaje_privado_by_id(mensaje_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': str(mensaje.id) if mensaje else mensaje_id,
                'leido': mensaje.leido.isoformat() if mensaje and mensaje.leido else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error al marcar mensaje como leído',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/no-leidos', methods=['GET'])
@jwt_required()
def contar_no_leidos_route():
    """
    Contar mensajes no leídos del usuario actual
    
    Returns:
        200: Contador de mensajes no leídos
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = utils.mongo_helpers.get_usuario_by_id(usuario_actual_id)
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Usar servicio (Gestor de Mensajes) para contar no leídos
        no_leidos = services.mensajes_privados_service.contar_mensajes_no_leidos(usuario_actual_id)
        
        return jsonify({
            'success': True,
            'data': {
                'noLeidos': no_leidos
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error al contar mensajes no leídos: {str(e)}',
            'code': 'INTERNAL_ERROR'
        }), 500


@mensajes_privados_bp.route('/mensajes-privados/<mensaje_id>', methods=['DELETE'])
@jwt_required()
def eliminar_mensaje(mensaje_id):
    """
    Eliminar un mensaje privado (solo el emisor)
    
    Returns:
        200: Mensaje eliminado
        404: Mensaje no encontrado
        403: No autorizado
    """
    try:
        # Obtener usuario autenticado
        usuario_actual_id = get_jwt_identity()
        usuario_actual = utils.mongo_helpers.get_usuario_by_id(usuario_actual_id)
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'code': 'AUTH_ERROR'
            }), 401
        
        # Buscar mensaje para verificar permisos
        mensaje = utils.mongo_helpers.get_mensaje_privado_by_id(mensaje_id)
        if not mensaje:
            return jsonify({
                'success': False,
                'error': 'Mensaje no encontrado',
                'code': 'MESSAGE_NOT_FOUND'
            }), 404
        
        # Verificar que el usuario actual es el emisor
        # Obtener ID del emisor sin intentar dereferenciar
        emisor_id = None
        if hasattr(mensaje, '_data') and 'emisor' in mensaje._data:
            emisor_id = str(mensaje._data['emisor'])
        elif hasattr(mensaje.emisor, 'id'):
            emisor_id = str(mensaje.emisor.id)
        else:
            emisor_id = str(mensaje.emisor)
        
        if emisor_id != str(usuario_actual.id):
            return jsonify({
                'success': False,
                'error': 'No tienes permiso para eliminar este mensaje',
                'code': 'FORBIDDEN'
            }), 403
        
        # Eliminar mensaje (operación directa de BD, no requiere servicio)
        mensaje.delete()
        
        # Log del evento
        Log.log_event(
            level='INFO',
            message=f'Mensaje privado eliminado por {usuario_actual.nickName}',
            user_id=str(usuario_actual.id),
            action='delete_private_message',
            ip_address=request.remote_addr,
            metadata={'mensaje_id': mensaje_id}
        )
        
        return jsonify({
            'success': True,
            'message': 'Mensaje eliminado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error al eliminar mensaje',
            'code': 'INTERNAL_ERROR'
        }), 500
