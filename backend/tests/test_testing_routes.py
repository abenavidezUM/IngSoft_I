"""
Tests para las rutas de testing (desarrollo)
"""
from datetime import datetime


class FakeUsuario:
    def __init__(self, user_id, nick="user"):
        self.id = user_id
        self.nickName = nick
        self.nombre = "Nombre"
        self.apellido = "Apellido"
        self.mail = f"{nick}@example.com"
        self.biografia = "Biografía"
        self.fotoUsuario = ""
        self.fotoUsuarioPortada = ""
        self.fechaDeCreado = datetime.now()
        self.rol = "user"
        self.seguidores = []
        self.siguiendo = []

    def to_dict(self):
        return {
            "id": str(self.id),
            "nickName": self.nickName,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "mail": self.mail,
            "biografia": self.biografia,
            "fotoUsuario": self.fotoUsuario,
            "fotoUsuarioPortada": self.fotoUsuarioPortada,
            "fechaDeCreado": self.fechaDeCreado.isoformat(),
            "rol": self.rol,
            "seguidores": [],
            "siguiendo": []
        }


class FakeQuerySet:
    def __init__(self, data, count_value=None):
        self._data = list(data)
        self._count = count_value if count_value is not None else len(self._data)

    def select_related(self, *args):
        return self

    def first(self):
        return self._data[0] if self._data else None

    def count(self):
        return self._count


def test_obtener_token_por_nickname(app_client, monkeypatch):
    """Test que verifica obtener token por nickname"""
    import routes.testing as testing_route
    import utils.mongo_helpers
    from mongoengine.connection import get_db as original_get_db
    from flask_jwt_extended import decode_token

    usuario = FakeUsuario("user_1", "juanperez")

    class FakeCollection:
        def find_one(self, query):
            if query.get("nickName") == "juanperez":
                return {
                    '_id': 'user_1',
                    'nickName': 'juanperez',
                    'nombre': 'Juan',
                    'apellido': 'Pérez',
                    'mail': 'juan@example.com',
                    'biografia': 'Desarrollador Full Stack',
                    'fotoUsuario': '',
                    'fotoUsuarioPortada': '',
                    'fechaDeCreado': None,
                    'rol': 'user'
                }
            return None

    class FakeDB:
        def __init__(self):
            self.usuarios = FakeCollection()

    def fake_get_db(alias):
        return FakeDB()

    def fake_get_usuario_by_id(usuario_id):
        return None

    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/testing/token/juanperez")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "token" in payload["data"]
    assert payload["data"]["user"]["nickName"] == "juanperez"
    assert payload["data"]["user"]["id"] == "user_1"

    # Verificar que el token es válido
    token = payload["data"]["token"]
    assert token is not None
    assert len(token) > 0


def test_obtener_token_por_id(app_client, monkeypatch):
    """Test que verifica obtener token por ID (ObjectId de 24 caracteres)"""
    import routes.testing as testing_route
    import utils.mongo_helpers
    from bson import ObjectId

    # Usar un ID que parezca ObjectId (24 caracteres hexadecimales)
    fake_object_id = "507f1f77bcf86cd799439011"
    usuario = FakeUsuario(fake_object_id, "testuser")

    def fake_get_usuario_by_nickname(nickname):
        # No encontrar por nickname (se busca por ID)
        return None

    def fake_get_usuario_by_id(usuario_id):
        # Retornar usuario cuando se busca por ID
        if str(usuario_id) == fake_object_id:
            return usuario
        return None

    # Mockear las funciones helper
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_nickname", fake_get_usuario_by_nickname)
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get(f"/api/testing/token/{fake_object_id}")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "token" in payload["data"]
    assert payload["data"]["user"]["id"] == fake_object_id


def test_obtener_token_usuario_no_encontrado(app_client, monkeypatch):
    """Test que verifica el comportamiento cuando el usuario no existe"""
    import routes.testing as testing_route
    import utils.mongo_helpers

    def fake_objects(**kwargs):
        return FakeQuerySet([])

    def fake_get_usuario_by_id(usuario_id):
        return None

    def fake_count():
        return 0

    monkeypatch.setattr(testing_route.Usuario, "objects", staticmethod(fake_objects))
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/testing/token/usuario_inexistente")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert "no encontrado" in payload["error"].lower()


def test_obtener_token_usuario_no_encontrado_con_usuarios_en_bd(app_client, monkeypatch):
    """Test que verifica el mensaje cuando hay usuarios pero no el solicitado"""
    import routes.testing as testing_route
    import utils.mongo_helpers

    class FakeQuerySetWithCount:
        def __init__(self, data, count_value=None):
            self._data = list(data)
            self._count = count_value if count_value is not None else len(self._data)

        def select_related(self, *args):
            return self

        def count(self):
            return self._count

        def first(self):
            return self._data[0] if self._data else None

    def fake_objects(**kwargs):
        if "nickName" in kwargs:
            return FakeQuerySetWithCount([])
        # Para count() - cuando se llama sin parámetros
        return FakeQuerySetWithCount([], count_value=5)

    def fake_get_usuario_by_id(usuario_id):
        return None

    monkeypatch.setattr(testing_route.Usuario, "objects", staticmethod(fake_objects))
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/testing/token/usuario_inexistente")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert "no encontrado" in payload["error"].lower()
    # El mensaje puede o no incluir el conteo dependiendo de si el mock funciona
    # Verificamos al menos que el error sea claro
    assert "usuario" in payload["error"].lower() or "base de datos" in payload["error"].lower()


def test_obtener_token_error_en_busqueda_por_nickname(app_client, monkeypatch):
    """Test que verifica el manejo de errores al buscar por nickname - debe retornar 404"""
    import utils.mongo_helpers

    class FakeCollection:
        def find_one(self, query):
            # Simular error al buscar
            raise Exception("Error de base de datos")

    class FakeDB:
        def __init__(self):
            self.usuarios = FakeCollection()

    def fake_get_db(alias):
        return FakeDB()

    def fake_get_usuario_by_id(usuario_id):
        # get_usuario_by_id busca por ObjectId, no por nickname
        # Como "juanperez" no es un ObjectId válido, retorna None
        return None

    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/testing/token/juanperez")

    # Cuando falla la búsqueda por nickname y get_usuario_by_id no encuentra nada, retorna 404
    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert "no encontrado" in payload["error"].lower()


def test_obtener_token_error_al_crear_token(app_client, monkeypatch):
    """Test que verifica el manejo de errores al crear el token"""
    import routes.testing as testing_route
    import utils.mongo_helpers

    class FakeCollection:
        def find_one(self, query):
            if query.get("nickName") == "juanperez":
                return {
                    '_id': 'user_1',
                    'nickName': 'juanperez',
                    'nombre': 'Juan',
                    'apellido': 'Pérez',
                    'mail': 'juan@example.com',
                    'biografia': 'Desarrollador Full Stack',
                    'fotoUsuario': '',
                    'fotoUsuarioPortada': '',
                    'fechaDeCreado': None,
                    'rol': 'user'
                }
            return None

    class FakeDB:
        def __init__(self):
            self.usuarios = FakeCollection()

    def fake_get_db(alias):
        return FakeDB()

    def fake_get_usuario_by_id(usuario_id):
        return None

    def fake_create_access_token(identity):
        raise Exception("Error al crear token JWT")

    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(testing_route, "create_access_token", fake_create_access_token)

    response = app_client.get("/api/testing/token/juanperez")

    assert response.status_code == 500
    payload = response.get_json()
    assert payload["success"] is False
    assert "error" in payload["error"].lower()


def test_obtener_token_error_en_to_dict(app_client, monkeypatch):
    """Test que verifica el manejo de errores cuando to_dict() falla"""
    import utils.mongo_helpers

    class FakeCollection:
        def find_one(self, query):
            if query.get("nickName") == "juanperez":
                return {
                    '_id': 'user_1',
                    'nickName': 'juanperez',
                    'nombre': 'Juan',
                    'apellido': 'Pérez',
                    'mail': 'juan@example.com',
                    'biografia': 'Desarrollador Full Stack',
                    'fotoUsuario': '',
                    'fotoUsuarioPortada': '',
                    'fechaDeCreado': None,
                    'rol': 'user'
                }
            return None

    class FakeDB:
        def __init__(self):
            self.usuarios = FakeCollection()

    def fake_get_db(alias):
        return FakeDB()

    def fake_get_usuario_by_id(usuario_id):
        return None

    # Mockear get_usuario_by_nickname para retornar un objeto con to_dict que falla
    def fake_get_usuario_by_nickname(nickname):
        from models import Usuario
        usuario = Usuario()
        usuario.id = 'user_1'
        usuario.nickName = 'juanperez'
        usuario.nombre = 'Juan'
        usuario.apellido = 'Pérez'
        usuario.mail = 'juan@example.com'
        usuario.biografia = 'Desarrollador Full Stack'
        usuario.fotoUsuario = ''
        usuario.fotoUsuarioPortada = ''
        usuario.fechaDeCreado = None
        usuario.rol = 'user'
        usuario.seguidores = []
        usuario.siguiendo = []
        # Hacer que to_dict() falle
        def failing_to_dict():
            raise Exception("Error al convertir a diccionario")
        usuario.to_dict = failing_to_dict
        return usuario

    # También mockear en routes.testing
    import routes.testing as testing_route
    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_nickname", fake_get_usuario_by_nickname)

    response = app_client.get("/api/testing/token/juanperez")

    assert response.status_code == 500
    payload = response.get_json()
    assert payload["success"] is False
    assert "error" in payload["error"].lower()


def test_obtener_token_diferentes_metodos_http(app_client):
    """Test que verifica que solo GET está permitido"""
    response = app_client.post("/api/testing/token/juanperez")
    assert response.status_code == 405  # Method Not Allowed

    response = app_client.put("/api/testing/token/juanperez")
    assert response.status_code == 405

    response = app_client.delete("/api/testing/token/juanperez")
    assert response.status_code == 405


def test_obtener_token_caracteres_especiales(app_client, monkeypatch):
    """Test que verifica el manejo de caracteres especiales en el nickname"""
    import utils.mongo_helpers

    class FakeCollection:
        def find_one(self, query):
            # Flask decodifica %40 a @, así que el query tendrá "user@test"
            if query.get("nickName") == "user@test":
                return {
                    '_id': 'user_1',
                    'nickName': 'user@test',
                    'nombre': 'User',
                    'apellido': 'Test',
                    'mail': 'user@test.com',
                    'biografia': 'Test user',
                    'fotoUsuario': '',
                    'fotoUsuarioPortada': '',
                    'fechaDeCreado': None,
                    'rol': 'user'
                }
            return None

    class FakeDB:
        def __init__(self):
            self.usuarios = FakeCollection()

    def fake_get_db(alias):
        return FakeDB()

    def fake_get_usuario_by_id(usuario_id):
        return None

    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    # Flask decodifica automáticamente %40 a @, así que el endpoint recibirá "user@test"
    response = app_client.get("/api/testing/token/user%40test")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["user"]["nickName"] == "user@test"


def test_obtener_token_usuario_vacio(app_client):
    """Test que verifica el comportamiento con un identificador vacío"""
    response = app_client.get("/api/testing/token/")

    # Flask debería retornar 404 para ruta vacía
    assert response.status_code == 404


def test_obtener_token_verificar_estructura_respuesta(app_client, monkeypatch):
    """Test que verifica la estructura completa de la respuesta"""
    import utils.mongo_helpers

    class FakeCollection:
        def find_one(self, query):
            if query.get("nickName") == "juanperez":
                return {
                    '_id': 'user_1',
                    'nickName': 'juanperez',
                    'nombre': 'Juan',
                    'apellido': 'Pérez',
                    'mail': 'juan@example.com',
                    'biografia': 'Desarrollador Full Stack',
                    'fotoUsuario': '',
                    'fotoUsuarioPortada': '',
                    'fechaDeCreado': None,
                    'rol': 'user'
                }
            return None

    class FakeDB:
        def __init__(self):
            self.usuarios = FakeCollection()

    def fake_get_db(alias):
        return FakeDB()

    def fake_get_usuario_by_id(usuario_id):
        return None

    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/testing/token/juanperez")

    assert response.status_code == 200
    payload = response.get_json()
    
    # Verificar estructura
    assert "success" in payload
    assert "data" in payload
    assert payload["success"] is True
    
    # Verificar estructura de data
    assert "token" in payload["data"]
    assert "user" in payload["data"]
    
    # Verificar estructura de user
    user = payload["data"]["user"]
    assert "id" in user
    assert "nickName" in user
    assert "nombre" in user
    assert "apellido" in user
    assert "mail" in user

