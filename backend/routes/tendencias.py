"""
Rutas para tendencias
CU0016 - Enviar Correo Automático de Tendencias

Endpoints:
- GET /api/tendencias - Obtener tendencias actuales
- POST /api/tendencias/enviar - Enviar emails de tendencias a usuarios
"""

from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.tendencias_service import (
    obtener_tendencias,
    generar_contenido_email,
    obtener_usuarios_para_envio
)
from services.email_service import (
    enviar_tendencias_masivo,
    validar_configuracion_email
)

tendencias_bp = Blueprint("tendencias", __name__)


@tendencias_bp.route("/tendencias", methods=["GET"])
@jwt_required()
def obtener_tendencias_route():
    """
    Obtiene las tendencias actuales (etiquetas más populares).
    
    Query Parameters:
        limit: Número de tendencias a retornar (default: 10)
        horas: Ventana de tiempo en horas (default: 24)
    
    Returns:
        200: Lista de tendencias
        500: Error interno
    """
    try:
        from flask import request
        
        limit = int(request.args.get("limit", 10))
        horas = int(request.args.get("horas", 24))
        
        # Validar límites
        if limit < 1 or limit > 50:
            return jsonify({
                "success": False,
                "error": "El límite debe estar entre 1 y 50",
                "code": "INVALID_LIMIT"
            }), 400
        
        if horas < 1 or horas > 168:  # Máximo 1 semana
            return jsonify({
                "success": False,
                "error": "Las horas deben estar entre 1 y 168",
                "code": "INVALID_HOURS"
            }), 400
        
        tendencias = obtener_tendencias(limit=limit, horas_atras=horas)
        
        return jsonify({
            "success": True,
            "data": {
                "tendencias": tendencias,
                "total": len(tendencias),
                "ventana_horas": horas
            }
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Error al obtener tendencias: {str(e)}",
            "code": "INTERNAL_ERROR"
        }), 500


@tendencias_bp.route("/tendencias/enviar", methods=["POST"])
@jwt_required()
def enviar_tendencias_route():
    """
    Envía emails con las tendencias actuales a todos los usuarios.
    
    CU0016 - Enviar Correo Automático de Tendencias
    
    Este endpoint ejecuta el proceso completo:
    1. Obtiene las tendencias actuales
    2. Genera el contenido HTML del email
    3. Obtiene la lista de usuarios
    4. Envía el email a cada usuario
    
    Returns:
        200: Envío completado (con estadísticas)
        400: Configuración de email inválida
        500: Error interno
    """
    try:
        # Validar configuración de email
        config_valid, config_error = validar_configuracion_email()
        if not config_valid:
            return jsonify({
                "success": False,
                "error": config_error,
                "code": "EMAIL_CONFIG_ERROR"
            }), 400
        
        # 1. Obtener tendencias
        print("📊 Paso 1: Obteniendo tendencias...")
        tendencias = obtener_tendencias(limit=10, horas_atras=24)
        
        if not tendencias:
            return jsonify({
                "success": False,
                "error": "No hay tendencias disponibles para enviar",
                "code": "NO_TRENDS"
            }), 200  # No es un error, simplemente no hay datos
        
        # 2. Generar contenido HTML
        print("📝 Paso 2: Generando contenido del email...")
        contenido_html = generar_contenido_email(tendencias)
        
        # 3. Obtener usuarios
        print("👥 Paso 3: Obteniendo lista de usuarios...")
        usuarios = obtener_usuarios_para_envio()
        
        if not usuarios:
            return jsonify({
                "success": False,
                "error": "No hay usuarios para enviar el email",
                "code": "NO_USERS"
            }), 200
        
        # 4. Enviar emails
        print("📧 Paso 4: Enviando emails...")
        from app import mail  # Importar la instancia de mail
        stats = enviar_tendencias_masivo(mail, usuarios, contenido_html)
        
        # Determinar el código de respuesta según el resultado
        if stats['exitosos'] > 0:
            status_code = 200
            message = f"Proceso completado: {stats['exitosos']}/{stats['total']} emails enviados"
        else:
            status_code = 500
            message = "Error: No se pudo enviar ningún email"
        
        return jsonify({
            "success": stats['exitosos'] > 0,
            "message": message,
            "data": {
                "tendencias": tendencias,
                "estadisticas": {
                    "total_usuarios": stats['total'],
                    "emails_enviados": stats['exitosos'],
                    "emails_fallidos": stats['fallidos']
                },
                "errores": stats['errores'][:10] if stats['errores'] else []  # Limitar errores mostrados
            }
        }), status_code
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Error al enviar tendencias: {str(e)}",
            "code": "INTERNAL_ERROR"
        }), 500
