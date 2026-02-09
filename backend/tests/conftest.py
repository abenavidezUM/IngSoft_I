import os
import sys
import importlib

import pytest
from flask_jwt_extended import create_access_token
from mongoengine import connect, disconnect


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Configurar conexiones de prueba a MongoDB"""
    # Desconectar cualquier conexión existente primero
    try:
        disconnect(alias="default")
    except:
        pass
    try:
        disconnect(alias="logs")
    except:
        pass
    
    # Conectar a bases de datos de prueba
    connect(
        db="test_main_db",
        host="mongodb://localhost:27017/test_main_db",
        alias="default",
        tls=False,
        uuidRepresentation='standard',
    )
    
    connect(
        db="test_logs_db",
        host="mongodb://localhost:27017/test_logs_db",
        alias="logs",
        tls=False,
        uuidRepresentation='standard',
    )
    
    yield
    
    # Limpiar después de todos los tests
    try:
        disconnect(alias="default")
        disconnect(alias="logs")
    except:
        pass


@pytest.fixture(autouse=True)
def clean_db():
    """Limpiar colecciones antes de cada test"""
    from models import Usuario, Mensaje, MensajePrivado, Etiqueta, Mencion
    from models.log import Log
    
    # Limpiar main_db
    Usuario.objects.delete()
    Mensaje.objects.delete()
    MensajePrivado.objects.delete()
    Etiqueta.objects.delete()
    Mencion.objects.delete()
    
    # Limpiar logs_db
    Log.objects.using('logs').delete()
    
    yield
    
    # Limpiar después del test también
    Usuario.objects.delete()
    Mensaje.objects.delete()
    MensajePrivado.objects.delete()
    Etiqueta.objects.delete()
    Mencion.objects.delete()
    Log.objects.using('logs').delete()


@pytest.fixture
def app_module(monkeypatch):
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    # Evitar que la app se conecte automáticamente durante los tests
    import db
    original_connect = db.connect_databases
    
    def mock_connect():
        # Ya estamos conectados por setup_test_db, no hacer nada
        pass
    
    monkeypatch.setattr(db, "connect_databases", mock_connect)

    if "app" in sys.modules:
        app_module = importlib.reload(sys.modules["app"])
    else:
        app_module = importlib.import_module("app")

    app_module.app.config["TESTING"] = True
    # Configurar JWT_SECRET_KEY más largo para evitar warnings
    app_module.app.config["JWT_SECRET_KEY"] = "test-jwt-secret-key-minimum-32-bytes-long-for-sha256"
    return app_module


@pytest.fixture
def app_client(app_module):
    with app_module.app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers(app_module):
    with app_module.app.app_context():
        token = create_access_token(identity="user_1")
    return {"Authorization": f"Bearer {token}"}

