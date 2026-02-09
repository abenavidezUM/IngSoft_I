"""
Rutas de testing para desarrollo
Solo deben estar disponibles en modo desarrollo
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token
from models import Usuario
import utils.mongo_helpers

testing_bp = Blueprint('testing', __name__)

@testing_bp.route('/testing/token/<user_identifier>', methods=['GET'])
def get_test_token(user_identifier):
    """
    Genera un token JWT para testing.
    Solo para desarrollo - NO usar en producción.
    Puede recibir ID o nickName del usuario.
    """
    try:
        # Intentar buscar por nickName primero (más común para testing)
        usuario = utils.mongo_helpers.get_usuario_by_nickname(user_identifier)
        
        # Si no se encontró por nickName, intentar por ID
        if not usuario:
            usuario = utils.mongo_helpers.get_usuario_by_id(user_identifier)
        
        if not usuario:
            # Verificar si hay usuarios en la base de datos (con manejo de errores)
            mensaje_error = f'Usuario "{user_identifier}" no encontrado.'
            try:
                # Usar pymongo directamente para evitar problemas de thread local
                from mongoengine.connection import get_db
                db = get_db('default')
                total_usuarios = db.usuarios.count_documents({})
                if total_usuarios == 0:
                    mensaje_error += ' La base de datos está vacía. Ejecuta: python init_db.py --with-sample-data'
                else:
                    mensaje_error += f' Hay {total_usuarios} usuarios en la base de datos.'
            except Exception:
                # Si no se puede contar (por ejemplo, en tests con mocks), usar mensaje genérico
                mensaje_error += ' Verifica que el usuario exista en la base de datos.'
            
            return jsonify({
                'success': False,
                'error': mensaje_error
            }), 404
        
        # Crear token
        try:
            token = create_access_token(identity=str(usuario.id))
        except Exception as e:
            print(f"Error al crear token: {e}")
            return jsonify({
                'success': False,
                'error': f'Error al crear token: {str(e)}'
            }), 500
        
        # Convertir usuario a diccionario
        try:
            user_dict = usuario.to_dict()
        except Exception as e:
            print(f"Error al convertir usuario a diccionario: {e}")
            return jsonify({
                'success': False,
                'error': f'Error al obtener datos del usuario: {str(e)}'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'user': user_dict
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500

