"""
Rutas para mensajes públicos

Endpoints:
- GET /api/mensajes/tablon - Obtener tablón (mensajes propios + de seguidos)
- GET /api/mensajes/mios - Obtener mensajes propios
- DELETE /api/mensajes/<mensaje_id> - Borrar mensaje propio
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Usuario
from services.mensajes_service import obtener_tablon, obtener_mis_mensajes, borrar_mensaje

mensajes_bp = Blueprint("mensajes", __name__)


@mensajes_bp.route("/mensajes/tablon", methods=["GET"])
@jwt_required()
def obtener_tablon_route():
    """
    Obtiene el tablón del usuario: mensajes propios + mensajes de usuarios seguidos.
    
    Este es el tablón principal del microblogging según el enunciado:
    "El usuario podrá visualizar un tablón de anuncios donde irán apareciendo los
    mensajes de los usuarios a los que sigue y los propios al publicarlos."
    
    Returns:
        200: Lista de mensajes con información del autor y flag 'esPropio'
        401: Usuario no autenticado
        500: Error interno
    """
    try:
        usuario_id = get_jwt_identity()
        print(f"🔑 Obteniendo tablón para usuario: {usuario_id}")
        
        from utils.mongo_helpers import get_usuario_by_id
        usuario = get_usuario_by_id(usuario_id)
        
        if not usuario:
            print(f"❌ Usuario no encontrado: {usuario_id}")
            return jsonify({
                "success": False,
                "error": "Usuario no encontrado",
                "code": "USER_NOT_FOUND",
            }), 401
        
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
        
        mensajes, total = obtener_tablon(usuario, limit, offset)
        
        # Convertir mensajes a lista
        mensajes_list = list(mensajes)
        
        return jsonify({
            "success": True,
            "data": {
                "mensajes": [mensaje.to_dict() for mensaje in mensajes_list],
                "total": total,
                "limit": limit,
                "offset": offset,
                "hasMore": (offset + limit) < total,
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Error al obtener tablón: {str(e)}",
            "code": "INTERNAL_ERROR",
        }), 500


@mensajes_bp.route("/mensajes/mios", methods=["GET"])
@jwt_required()
def obtener_mis_mensajes_route():
    try:
        from flask import request
        # Debug: verificar headers
        auth_header = request.headers.get('Authorization', 'No Authorization header')
        print(f"🔑 Authorization header recibido: {auth_header[:50] if len(auth_header) > 50 else auth_header}...")
        
        usuario_id = get_jwt_identity()
        print(f"🔑 Usuario ID del token: {usuario_id}")
        
        # Usar función helper que maneja el problema de thread local
        from utils.mongo_helpers import get_usuario_by_id
        usuario = get_usuario_by_id(usuario_id)

        if not usuario:
            print(f"❌ Usuario no encontrado para ID: {usuario_id}")
            # Verificar si hay usuarios en la base de datos
            from models import Usuario as UsuarioModel
            try:
                total_usuarios = UsuarioModel.objects.select_related(0).count()
                print(f"📊 Total de usuarios en la BD: {total_usuarios}")
                # Listar algunos IDs para debug
                if total_usuarios > 0:
                    primeros_usuarios = list(UsuarioModel.objects.select_related(0).limit(5))
                    print(f"📋 Primeros usuarios en BD:")
                    for u in primeros_usuarios:
                        print(f"  - ID: {u.id}, nickName: {u.nickName}")
            except Exception as e:
                print(f"⚠️ Error al contar usuarios: {e}")
            
            return jsonify({
                "success": False,
                "error": f"Usuario no encontrado para ID: {usuario_id}",
                "code": "USER_NOT_FOUND",
            }), 401

        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))

        mensajes, total = obtener_mis_mensajes(usuario, limit, offset)

        # Convertir mensajes a lista para evitar problemas de thread local
        mensajes_list = list(mensajes)

        return jsonify({
            "success": True,
            "data": {
                "mensajes": [mensaje.to_dict() for mensaje in mensajes_list],
                "total": total,
                "limit": limit,
                "offset": offset,
                "hasMore": (offset + limit) < total,
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Error al obtener mensajes propios: {str(e)}",
            "code": "INTERNAL_ERROR",
        }), 500


@mensajes_bp.route("/mensajes/<mensaje_id>", methods=["DELETE"])
@jwt_required()
def borrar_mensaje_route(mensaje_id):
    """
    Borra un mensaje propio del usuario autenticado.
    
    CU0008 - Borrar Mensajes Propios
    
    Args:
        mensaje_id: ID del mensaje a borrar
    
    Returns:
        200: Mensaje borrado exitosamente
        401: Usuario no autenticado o no encontrado
        403: Usuario no es el autor del mensaje
        404: Mensaje no encontrado
        500: Error interno del servidor
    """
    try:
        # Obtener usuario autenticado
        usuario_id = get_jwt_identity()
        print(f"🔑 Usuario ID del token: {usuario_id}")
        
        # Obtener usuario desde la BD
        from utils.mongo_helpers import get_usuario_by_id
        usuario = get_usuario_by_id(usuario_id)
        
        if not usuario:
            print(f"❌ Usuario no encontrado para ID: {usuario_id}")
            return jsonify({
                "success": False,
                "error": "Usuario no autenticado",
                "code": "USER_NOT_FOUND",
            }), 401
        
        # Intentar borrar el mensaje
        success, message, status_code = borrar_mensaje(usuario, mensaje_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
            }), status_code
        else:
            error_codes = {
                400: "INVALID_ID",
                403: "FORBIDDEN",
                404: "MESSAGE_NOT_FOUND",
                500: "INTERNAL_ERROR"
            }
            return jsonify({
                "success": False,
                "error": message,
                "code": error_codes.get(status_code, "ERROR"),
            }), status_code
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Error al borrar mensaje: {str(e)}",
            "code": "INTERNAL_ERROR",
        }), 500

