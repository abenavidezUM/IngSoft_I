"""
Servicio de Email
CU0016 - Enviar Correo Automático de Tendencias

Este servicio maneja el envío de emails usando Flask-Mail.
"""

from flask_mail import Message
from flask import current_app


def enviar_email_tendencias(mail, usuario_email, usuario_nombre, contenido_html):
    """
    Envía un email con las tendencias a un usuario específico.
    
    Args:
        mail: Instancia de Flask-Mail
        usuario_email: Email del destinatario
        usuario_nombre: Nombre del usuario (para personalización)
        contenido_html: Contenido HTML del email
    
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        # Crear mensaje
        msg = Message(
            subject='🔥 Temas del Momento - Tendencias de la Red Social',
            recipients=[usuario_email],
            html=contenido_html,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@app.com')
        )
        
        # Enviar email
        mail.send(msg)
        
        print(f"✅ Email enviado exitosamente a {usuario_email} ({usuario_nombre})")
        return True, None
        
    except Exception as e:
        error_msg = f"Error al enviar email a {usuario_email}: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return False, error_msg


def enviar_tendencias_masivo(mail, usuarios, contenido_html):
    """
    Envía el email de tendencias a múltiples usuarios.
    
    Args:
        mail: Instancia de Flask-Mail
        usuarios: Lista de usuarios (con 'email' y 'nickName')
        contenido_html: Contenido HTML del email
    
    Returns:
        dict: Estadísticas del envío
              {
                  'total': int,
                  'exitosos': int,
                  'fallidos': int,
                  'errores': [str]
              }
    """
    stats = {
        'total': len(usuarios),
        'exitosos': 0,
        'fallidos': 0,
        'errores': []
    }
    
    print(f"📧 Iniciando envío masivo a {stats['total']} usuarios...")
    
    for usuario in usuarios:
        email = usuario.get('email', '')
        nombre = usuario.get('nickName', 'Usuario')
        
        if not email:
            stats['fallidos'] += 1
            stats['errores'].append(f"Usuario {nombre} no tiene email")
            continue
        
        success, error = enviar_email_tendencias(mail, email, nombre, contenido_html)
        
        if success:
            stats['exitosos'] += 1
        else:
            stats['fallidos'] += 1
            if error:
                stats['errores'].append(error)
    
    print(f"✅ Envío masivo completado:")
    print(f"  - Total: {stats['total']}")
    print(f"  - Exitosos: {stats['exitosos']}")
    print(f"  - Fallidos: {stats['fallidos']}")
    
    if stats['errores']:
        print(f"  - Errores:")
        for error in stats['errores'][:5]:  # Mostrar solo los primeros 5
            print(f"    • {error}")
    
    return stats


def validar_configuracion_email():
    """
    Valida que la configuración de email esté presente.
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        required_configs = [
            'MAIL_SERVER',
            'MAIL_PORT',
            'MAIL_USERNAME',
            'MAIL_PASSWORD'
        ]
        
        missing = []
        for config in required_configs:
            if not current_app.config.get(config):
                missing.append(config)
        
        if missing:
            error_msg = f"Configuración de email incompleta. Faltan: {', '.join(missing)}"
            print(f"⚠️ {error_msg}")
            return False, error_msg
        
        print("✅ Configuración de email validada correctamente")
        return True, None
        
    except Exception as e:
        error_msg = f"Error al validar configuración de email: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg
