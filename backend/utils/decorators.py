"""
Decoradores personalizados

Incluye rate limiting, validación, etc.
"""

from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import hashlib

# Almacenamiento en memoria para rate limiting
# En producción, usar Redis
rate_limit_storage = {}


def rate_limit(max_requests=10, window_seconds=60):
    """
    Decorador para rate limiting
    
    Args:
        max_requests: número máximo de requests
        window_seconds: ventana de tiempo en segundos
    
    Usage:
        @rate_limit(max_requests=10, window_seconds=60)
        def my_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener identificador del cliente (IP + user_agent)
            client_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            client_id = hashlib.md5(f"{client_ip}{user_agent}".encode()).hexdigest()
            
            # Obtener timestamp actual
            now = datetime.utcnow()
            
            # Inicializar si no existe
            if client_id not in rate_limit_storage:
                rate_limit_storage[client_id] = []
            
            # Limpiar requests antiguos (fuera de la ventana)
            rate_limit_storage[client_id] = [
                timestamp for timestamp in rate_limit_storage[client_id]
                if now - timestamp < timedelta(seconds=window_seconds)
            ]
            
            # Verificar si excede el límite
            if len(rate_limit_storage[client_id]) >= max_requests:
                return jsonify({
                    'success': False,
                    'error': f'Demasiadas solicitudes. Máximo {max_requests} por {window_seconds} segundos',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': window_seconds
                }), 429
            
            # Agregar request actual
            rate_limit_storage[client_id].append(now)
            
            # Ejecutar función
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_role(required_role):
    """
    Decorador para verificar rol del usuario
    
    Args:
        required_role: rol requerido ('admin', 'user', etc.)
    
    Usage:
        @require_role('admin')
        def admin_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_jwt_extended import get_jwt_identity
            from models import Usuario
            
            # Obtener usuario actual
            user_id = get_jwt_identity()
            user = Usuario.objects(id=user_id).first()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Usuario no autenticado',
                    'code': 'AUTH_ERROR'
                }), 401
            
            # Verificar rol
            if user.rol != required_role:
                return jsonify({
                    'success': False,
                    'error': 'No tienes permisos para esta acción',
                    'code': 'FORBIDDEN'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_json(*required_fields):
    """
    Decorador para validar que el request tenga JSON y campos requeridos
    
    Args:
        *required_fields: campos requeridos en el JSON
    
    Usage:
        @validate_json('email', 'password')
        def login():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar que el content-type sea JSON
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'El content-type debe ser application/json',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400
            
            # Obtener datos
            data = request.get_json()
            
            # Verificar campos requeridos
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Campos requeridos faltantes: {", ".join(missing_fields)}',
                    'code': 'MISSING_FIELDS'
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def log_request(action_name):
    """
    Decorador para registrar requests en los logs
    
    Args:
        action_name: nombre de la acción para el log
    
    Usage:
        @log_request('user_login')
        def login():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from models.log import Log
            from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
            
            # Intentar obtener user_id si está autenticado
            user_id = None
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
            except:
                pass
            
            # Ejecutar función
            response = f(*args, **kwargs)
            
            # Registrar en logs
            try:
                Log.log_event(
                    level='INFO',
                    message=f'Request: {action_name}',
                    user_id=user_id,
                    action=action_name,
                    ip_address=request.remote_addr,
                    metadata={
                        'method': request.method,
                        'path': request.path,
                        'user_agent': request.headers.get('User-Agent', '')
                    }
                )
            except:
                pass  # No fallar si el log falla
            
            return response
        
        return decorated_function
    return decorator
