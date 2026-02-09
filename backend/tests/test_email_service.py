"""
Tests para el servicio de email
CU0016 - Enviar Correo Automático de Tendencias
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask


@pytest.fixture
def mock_app():
    """Fixture que crea una app de Flask mock"""
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'test@example.com'
    app.config['MAIL_PASSWORD'] = 'test_password'
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@app.com'
    return app


def test_enviar_email_tendencias_exitoso(mock_app):
    """Test que verifica el envío exitoso de un email"""
    from services.email_service import enviar_email_tendencias
    
    with mock_app.app_context():
        # Mock de Flask-Mail
        mock_mail = MagicMock()
        mock_mail.send = MagicMock()
        
        contenido_html = "<html><body>Test email</body></html>"
        
        # Ejecutar
        success, error = enviar_email_tendencias(
            mock_mail,
            'usuario@example.com',
            'Test User',
            contenido_html
        )
        
        # Verificar
        assert success is True
        assert error is None
        assert mock_mail.send.called


def test_enviar_email_tendencias_con_error(mock_app):
    """Test que verifica el manejo de errores al enviar email"""
    from services.email_service import enviar_email_tendencias
    
    with mock_app.app_context():
        # Mock de Flask-Mail que lanza excepción
        mock_mail = MagicMock()
        mock_mail.send.side_effect = Exception("SMTP Error")
        
        contenido_html = "<html><body>Test email</body></html>"
        
        # Ejecutar
        success, error = enviar_email_tendencias(
            mock_mail,
            'usuario@example.com',
            'Test User',
            contenido_html
        )
        
        # Verificar
        assert success is False
        assert error is not None
        assert 'SMTP Error' in error


def test_enviar_tendencias_masivo_exitoso(mock_app):
    """Test que verifica el envío masivo exitoso"""
    from services.email_service import enviar_tendencias_masivo
    
    with mock_app.app_context():
        # Mock de Flask-Mail
        mock_mail = MagicMock()
        mock_mail.send = MagicMock()
        
        usuarios = [
            {'email': 'user1@example.com', 'nickName': 'user1'},
            {'email': 'user2@example.com', 'nickName': 'user2'},
            {'email': 'user3@example.com', 'nickName': 'user3'},
        ]
        
        contenido_html = "<html><body>Test email</body></html>"
        
        # Ejecutar
        stats = enviar_tendencias_masivo(mock_mail, usuarios, contenido_html)
        
        # Verificar
        assert stats['total'] == 3
        assert stats['exitosos'] == 3
        assert stats['fallidos'] == 0
        assert len(stats['errores']) == 0


def test_enviar_tendencias_masivo_con_fallos(mock_app):
    """Test que verifica el envío masivo con algunos fallos"""
    from services.email_service import enviar_tendencias_masivo
    
    with mock_app.app_context():
        # Mock de Flask-Mail que falla en el segundo envío
        mock_mail = MagicMock()
        send_count = [0]
        
        def mock_send(msg):
            send_count[0] += 1
            if send_count[0] == 2:
                raise Exception("SMTP Error for user 2")
        
        mock_mail.send = mock_send
        
        usuarios = [
            {'email': 'user1@example.com', 'nickName': 'user1'},
            {'email': 'user2@example.com', 'nickName': 'user2'},
            {'email': 'user3@example.com', 'nickName': 'user3'},
        ]
        
        contenido_html = "<html><body>Test email</body></html>"
        
        # Ejecutar
        stats = enviar_tendencias_masivo(mock_mail, usuarios, contenido_html)
        
        # Verificar
        assert stats['total'] == 3
        assert stats['exitosos'] == 2
        assert stats['fallidos'] == 1
        assert len(stats['errores']) == 1


def test_enviar_tendencias_masivo_sin_email(mock_app):
    """Test que verifica el manejo de usuarios sin email"""
    from services.email_service import enviar_tendencias_masivo
    
    with mock_app.app_context():
        mock_mail = MagicMock()
        
        usuarios = [
            {'email': 'user1@example.com', 'nickName': 'user1'},
            {'email': '', 'nickName': 'user2'},  # Sin email
            {'nickName': 'user3'},  # Sin campo email
        ]
        
        contenido_html = "<html><body>Test email</body></html>"
        
        # Ejecutar
        stats = enviar_tendencias_masivo(mock_mail, usuarios, contenido_html)
        
        # Verificar
        assert stats['total'] == 3
        assert stats['exitosos'] == 1
        assert stats['fallidos'] == 2


def test_validar_configuracion_email_completa(mock_app):
    """Test que verifica la validación exitosa de configuración"""
    from services.email_service import validar_configuracion_email
    
    with mock_app.app_context():
        # Ejecutar
        is_valid, error = validar_configuracion_email()
        
        # Verificar
        assert is_valid is True
        assert error is None


def test_validar_configuracion_email_incompleta():
    """Test que verifica la validación con configuración incompleta"""
    from services.email_service import validar_configuracion_email
    
    # App sin configuración completa
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    # Faltan MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
    
    with app.app_context():
        # Ejecutar
        is_valid, error = validar_configuracion_email()
        
        # Verificar
        assert is_valid is False
        assert error is not None
        assert 'incompleta' in error.lower()
