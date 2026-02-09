"""
Rutas para seguidores del usuario

Endpoints:
- GET /api/usuarios/seguidores - Obtener seguidores del usuario actual
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Usuario
import services.seguidores_service
import utils.mongo_helpers

seguidores_bp = Blueprint("seguidores", __name__)


@seguidores_bp.route("/usuarios/seguidores", methods=["GET"])
@jwt_required()
def listar_seguidores():
    try:
        usuario_id = get_jwt_identity()
        usuario = utils.mongo_helpers.get_usuario_by_id(usuario_id)

        if not usuario:
            return jsonify({
                "success": False,
                "error": "Usuario no autenticado",
                "code": "AUTH_ERROR",
            }), 401

        seguidores = services.seguidores_service.obtener_seguidores(usuario)
        # Convertir a lista para evitar problemas de thread local
        seguidores_list = list(seguidores) if seguidores else []
        data = [seguidor.to_dict() for seguidor in seguidores_list]

        if not data:
            return jsonify({
                "success": True,
                "data": [],
                "message": "Sin seguidores",
                "code": "NO_FOLLOWERS"
            }), 200

        return jsonify({
            "success": True,
            "data": data,
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Error al obtener seguidores: {str(e)}",
            "code": "INTERNAL_ERROR",
        }), 500

