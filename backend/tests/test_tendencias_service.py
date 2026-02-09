"""
Tests para el servicio de tendencias
CU0016 - Enviar Correo Automático de Tendencias
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


def test_obtener_tendencias_con_datos(monkeypatch):
    """Test que verifica la obtención de tendencias con datos de prueba"""
    from services.tendencias_service import obtener_tendencias
    
    # Mock de la base de datos
    mock_db = MagicMock()
    mock_collection = MagicMock()
    
    # Simular resultado de agregación
    mock_agregacion = [
        {'_id': 'etiqueta_id_1', 'count': 20},
        {'_id': 'etiqueta_id_2', 'count': 15},
        {'_id': 'etiqueta_id_3', 'count': 10},
    ]
    mock_collection.aggregate.return_value = mock_agregacion
    mock_db.mensajes = mock_collection
    
    # Mock de etiquetas
    def mock_find_one(query):
        etiqueta_map = {
            'etiqueta_id_1': {'_id': 'etiqueta_id_1', 'texto': '#python'},
            'etiqueta_id_2': {'_id': 'etiqueta_id_2', 'texto': '#angular'},
            'etiqueta_id_3': {'_id': 'etiqueta_id_3', 'texto': '#mongodb'},
        }
        return etiqueta_map.get(query['_id'])
    
    mock_db.etiquetas.find_one = mock_find_one
    
    # Monkeypatch get_db
    def mock_get_db(alias):
        return mock_db
    
    monkeypatch.setattr('services.tendencias_service.get_db', mock_get_db)
    
    # Ejecutar
    tendencias = obtener_tendencias(limit=5, horas_atras=24)
    
    # Verificar
    assert len(tendencias) == 3
    assert tendencias[0]['etiqueta'] == '#python'
    assert tendencias[0]['count'] == 20
    assert tendencias[1]['etiqueta'] == '#angular'
    assert tendencias[1]['count'] == 15
    assert tendencias[2]['etiqueta'] == '#mongodb'
    assert tendencias[2]['count'] == 10


def test_obtener_tendencias_sin_datos(monkeypatch):
    """Test que verifica el comportamiento cuando no hay datos"""
    from services.tendencias_service import obtener_tendencias
    
    # Mock de la base de datos
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_collection.aggregate.return_value = []
    mock_db.mensajes = mock_collection
    
    def mock_get_db(alias):
        return mock_db
    
    monkeypatch.setattr('services.tendencias_service.get_db', mock_get_db)
    
    # Ejecutar
    tendencias = obtener_tendencias(limit=10, horas_atras=24)
    
    # Verificar
    assert tendencias == []


def test_generar_contenido_email_con_tendencias():
    """Test que verifica la generación de contenido HTML con tendencias"""
    from services.tendencias_service import generar_contenido_email
    
    tendencias = [
        {'etiqueta': '#python', 'count': 20},
        {'etiqueta': '#angular', 'count': 15},
        {'etiqueta': '#mongodb', 'count': 10},
    ]
    
    html = generar_contenido_email(tendencias)
    
    # Verificar que el HTML contiene elementos esperados
    assert '<html>' in html
    assert 'Temas del Momento' in html
    assert '#python' in html
    assert '#angular' in html
    assert '#mongodb' in html
    assert '20 menciones' in html
    assert '15 menciones' in html
    assert '10 menciones' in html


def test_generar_contenido_email_sin_tendencias():
    """Test que verifica la generación de contenido HTML sin tendencias"""
    from services.tendencias_service import generar_contenido_email
    
    html = generar_contenido_email([])
    
    # Verificar que el HTML contiene mensaje de "no hay tendencias"
    assert '<html>' in html
    assert 'Temas del Momento' in html
    assert 'No hay tendencias disponibles' in html


def test_obtener_usuarios_para_envio(monkeypatch):
    """Test que verifica la obtención de usuarios para envío"""
    from services.tendencias_service import obtener_usuarios_para_envio
    
    # Mock de la base de datos
    mock_db = MagicMock()
    mock_usuarios = [
        {'_id': 'user_1', 'mail': 'user1@example.com', 'nickName': 'user1'},
        {'_id': 'user_2', 'mail': 'user2@example.com', 'nickName': 'user2'},
        {'_id': 'user_3', 'mail': 'user3@example.com', 'nickName': 'user3'},
    ]
    mock_db.usuarios.find.return_value = mock_usuarios
    
    def mock_get_db(alias):
        return mock_db
    
    monkeypatch.setattr('services.tendencias_service.get_db', mock_get_db)
    
    # Ejecutar
    usuarios = obtener_usuarios_para_envio()
    
    # Verificar
    assert len(usuarios) == 3
    assert usuarios[0]['email'] == 'user1@example.com'
    assert usuarios[0]['nickName'] == 'user1'
    assert usuarios[1]['email'] == 'user2@example.com'
    assert usuarios[2]['email'] == 'user3@example.com'


def test_obtener_usuarios_para_envio_sin_usuarios(monkeypatch):
    """Test que verifica el comportamiento cuando no hay usuarios"""
    from services.tendencias_service import obtener_usuarios_para_envio
    
    # Mock de la base de datos
    mock_db = MagicMock()
    mock_db.usuarios.find.return_value = []
    
    def mock_get_db(alias):
        return mock_db
    
    monkeypatch.setattr('services.tendencias_service.get_db', mock_get_db)
    
    # Ejecutar
    usuarios = obtener_usuarios_para_envio()
    
    # Verificar
    assert usuarios == []
