"""
Validadores para el sistema

Funciones de validación de datos de entrada.
"""

import re
from html import escape


def validar_email(email):
    """
    Valida formato de email
    
    Args:
        email: string del email
    
    Returns:
        bool: True si es válido
    """
    if not email or len(email) > 255:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validar_password(password):
    """
    Valida contraseña
    Requisitos: mínimo 8 caracteres, 1 mayúscula, 1 minúscula, 1 número
    
    Args:
        password: string de la contraseña
    
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    if not password:
        return False, "La contraseña es requerida"
    
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    
    return True, ""


def validar_nickname(nickname):
    """
    Valida nickname del usuario
    
    Args:
        nickname: string del nickname
    
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    if not nickname:
        return False, "El nickname es requerido"
    
    if len(nickname) < 3:
        return False, "El nickname debe tener al menos 3 caracteres"
    
    if len(nickname) > 50:
        return False, "El nickname no puede exceder 50 caracteres"
    
    # Solo alfanuméricos y guiones bajos
    if not re.match(r'^[a-zA-Z0-9_]+$', nickname):
        return False, "El nickname solo puede contener letras, números y guiones bajos"
    
    return True, ""


def validar_mensaje_privado(texto, emisor_id, receptor_id):
    """
    Valida un mensaje privado
    
    Args:
        texto: contenido del mensaje
        emisor_id: ID del emisor
        receptor_id: ID del receptor
    
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    # Validar que el texto no esté vacío
    if not texto or not texto.strip():
        return False, "El mensaje no puede estar vacío"
    
    # Validar longitud
    if len(texto) > 1000:
        return False, "El mensaje no puede exceder 1000 caracteres"
    
    # Validar que existan IDs
    if not emisor_id or not receptor_id:
        return False, "Emisor y receptor son requeridos"
    
    # Validar que emisor y receptor sean diferentes
    if str(emisor_id) == str(receptor_id):
        return False, "No puedes enviarte mensajes a ti mismo"
    
    return True, ""


def sanitizar_html(texto):
    """
    Sanitiza HTML para prevenir XSS
    
    Args:
        texto: string a sanitizar
    
    Returns:
        string: texto sanitizado
    """
    return escape(texto)


def validar_mensaje_publico(texto, menciones):
    """
    Valida un mensaje público
    Debe tener al menos 1 mención según el modelo
    
    Args:
        texto: contenido del mensaje
        menciones: lista de menciones
    
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    # Validar que el texto no esté vacío
    if not texto or not texto.strip():
        return False, "El mensaje no puede estar vacío"
    
    # Validar longitud
    if len(texto) > 500:
        return False, "El mensaje no puede exceder 500 caracteres"
    
    # Validar que haya al menos 1 mención (según el diagrama: 1..*)
    if not menciones or len(menciones) == 0:
        return False, "El mensaje debe tener al menos una mención"
    
    return True, ""


def validar_etiqueta(texto):
    """
    Valida formato de etiqueta/hashtag
    
    Args:
        texto: texto de la etiqueta (debe empezar con #)
    
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    if not texto:
        return False, "La etiqueta es requerida"
    
    if not texto.startswith('#'):
        return False, "La etiqueta debe comenzar con #"
    
    if len(texto) > 50:
        return False, "La etiqueta no puede exceder 50 caracteres"
    
    # Solo alfanuméricos después del #
    if not re.match(r'^#[a-zA-Z0-9_]+$', texto):
        return False, "La etiqueta solo puede contener letras, números y guiones bajos"
    
    return True, ""
