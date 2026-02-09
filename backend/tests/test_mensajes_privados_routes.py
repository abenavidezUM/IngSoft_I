from datetime import datetime


class FakeUsuario:
    def __init__(self, user_id, nick="user"):
        self.id = user_id
        self.nickName = nick
        self.nombre = "Nombre"
        self.apellido = "Apellido"
        self.fotoUsuario = ""

    def to_dict(self):
        return {
            "id": str(self.id),
            "nickName": self.nickName,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "fotoUsuario": self.fotoUsuario,
        }


class FakeMensajePrivado:
    def __init__(self, texto, emisor, receptor):
        self.id = "msg_1"
        self.texto = texto
        self.emisor = emisor
        self.receptor = receptor
        self.leido = None
        self.fechaDeCreado = datetime(2026, 1, 1, 10, 0, 0)

    def marcar_como_leido(self):
        self.leido = datetime(2026, 1, 1, 10, 5, 0)

    def save(self):
        return self

    def to_dict(self):
        return {
            "id": str(self.id),
            "texto": self.texto,
            "fechaDeCreado": self.fechaDeCreado.isoformat(),
            "emisor": self.emisor.to_dict(),
            "receptor": self.receptor.to_dict(),
            "leido": self.leido.isoformat() if self.leido else None,
        }


class FakeQuerySet:
    def __init__(self, data, count_value=None):
        self._data = list(data)
        self._count = count_value if count_value is not None else len(self._data)

    def select_related(self, *args):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def skip(self, value):
        self._data = self._data[value:]
        return self

    def limit(self, value):
        self._data = self._data[:value]
        return self

    def count(self):
        return self._count

    def first(self):
        return self._data[0] if self._data else None

    def __iter__(self):
        return iter(self._data)


def test_listar_conversaciones(app_client, auth_headers, monkeypatch):
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers
    import services.mensajes_privados_service as mensajes_service

    usuario_actual = FakeUsuario("user_1", "juan")
    otro_usuario = FakeUsuario("user_2", "maria")
    mensaje = FakeMensajePrivado("hola", usuario_actual, otro_usuario)

    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == "user_1":
            return usuario_actual
        if usuario_id == "user_2":
            return otro_usuario
        return None

    def fake_listar_conversaciones(usuario_id):
        return [{
            'usuario': otro_usuario.to_dict(),
            'ultimoMensaje': mensaje.to_dict(),
            'mensajesNoLeidos': 0
        }]

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_service, "listar_conversaciones", fake_listar_conversaciones)

    response = app_client.get("/api/mensajes-privados/conversaciones", headers=auth_headers)

    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_json()}")
    
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert len(payload["data"]) == 1
    assert payload["data"][0]["usuario"]["id"] == "user_2"


def test_obtener_conversacion(app_client, auth_headers, monkeypatch):
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers
    import services.mensajes_privados_service as mensajes_service

    usuario_actual = FakeUsuario("user_1", "juan")
    otro_usuario = FakeUsuario("user_2", "maria")
    mensaje = FakeMensajePrivado("hola", usuario_actual, otro_usuario)

    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == "user_1":
            return usuario_actual
        if usuario_id == "user_2":
            return otro_usuario
        return None

    def fake_obtener_conversacion(usuario_actual_id, otro_usuario_id, limit, offset):
        return {
            'conversacion': [mensaje.to_dict()],
            'total': 1,
            'limit': limit,
            'offset': offset,
            'hasMore': False
        }

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_service, "obtener_conversacion", fake_obtener_conversacion)

    response = app_client.get("/api/mensajes-privados/conversacion/user_2", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["total"] == 1
    assert payload["data"]["conversacion"][0]["texto"] == "hola"


def test_crear_mensaje_privado(app_client, auth_headers, monkeypatch):
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers
    import services.mensajes_privados_service as mensajes_service

    usuario_actual = FakeUsuario("user_1", "juan")
    receptor = FakeUsuario("user_2", "maria")
    mensaje = FakeMensajePrivado("hola", usuario_actual, receptor)

    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == "user_1":
            return usuario_actual
        if usuario_id == "user_2":
            return receptor
        return None

    def fake_crear_mensaje_privado(emisor_id, receptor_id, texto):
        return mensaje

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_privados, "validar_mensaje_privado", lambda *args: (True, ""))
    monkeypatch.setattr(mensajes_privados.Log, "log_event", lambda **_kwargs: None)
    monkeypatch.setattr(mensajes_service, "crear_mensaje_privado", fake_crear_mensaje_privado)

    response = app_client.post(
        "/api/mensajes-privados",
        json={"receptor_id": "user_2", "texto": "hola"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["texto"] == "hola"


def test_crear_mensaje_privado_invalido(app_client, auth_headers, monkeypatch):
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers

    usuario_actual = FakeUsuario("user_1", "juan")

    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == "user_1":
            return usuario_actual
        return None

    # Mockear en ambos módulos
    # Mockear en ambos módulos
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_privados, "validar_mensaje_privado", lambda *args: (False, "error"))

    response = app_client.post(
        "/api/mensajes-privados",
        json={"receptor_id": "user_2", "texto": ""},
        headers=auth_headers,
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False


# Tests adicionales para casos de error
def test_listar_conversaciones_sin_autenticacion(app_client):
    """Test que verifica que sin token se retorna 401"""
    response = app_client.get("/api/mensajes-privados/conversaciones")
    assert response.status_code == 401


def test_listar_conversaciones_usuario_no_encontrado(app_client, auth_headers, monkeypatch):
    """Test que verifica el comportamiento cuando el usuario no existe"""
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers

    def fake_get_usuario_by_id(usuario_id):
        return None

    # Mockear en ambos módulos
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/mensajes-privados/conversaciones", headers=auth_headers)
    assert response.status_code == 401
    payload = response.get_json()
    assert payload["success"] is False


def test_obtener_conversacion_sin_autenticacion(app_client):
    """Test que verifica que sin token se retorna 401"""
    response = app_client.get("/api/mensajes-privados/conversacion/user_2")
    assert response.status_code == 401


def test_obtener_conversacion_usuario_no_encontrado(app_client, auth_headers, monkeypatch):
    """Test que verifica el comportamiento cuando el otro usuario no existe"""
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers

    usuario_actual = FakeUsuario("user_1", "juan")

    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == "user_1":
            return usuario_actual
        return None  # Otro usuario no existe

    # Mockear en ambos módulos
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/mensajes-privados/conversacion/user_2", headers=auth_headers)
    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert "no encontrado" in payload["error"].lower()


def test_crear_mensaje_privado_sin_autenticacion(app_client):
    """Test que verifica que sin token se retorna 401"""
    response = app_client.post(
        "/api/mensajes-privados",
        json={"receptor_id": "user_2", "texto": "hola"}
    )
    assert response.status_code == 401


def test_crear_mensaje_privado_receptor_no_encontrado(app_client, auth_headers, monkeypatch):
    """Test que verifica el comportamiento cuando el receptor no existe"""
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers
    import services.mensajes_privados_service as mensajes_service

    usuario_actual = FakeUsuario("user_1", "juan")

    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == "user_1":
            return usuario_actual
        return None  # Receptor no existe

    def fake_crear_mensaje_privado(emisor_id, receptor_id, texto):
        return None  # Simula que no se pudo crear

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_privados, "validar_mensaje_privado", lambda *args: (True, ""))
    monkeypatch.setattr(mensajes_service, "crear_mensaje_privado", fake_crear_mensaje_privado)

    response = app_client.post(
        "/api/mensajes-privados",
        json={"receptor_id": "user_2", "texto": "hola"},
        headers=auth_headers,
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert "no se pudo crear" in payload["error"].lower()


def test_contar_no_leidos(app_client, auth_headers, monkeypatch):
    """Test que verifica el conteo de mensajes no leídos"""
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers
    import services.mensajes_privados_service as mensajes_service

    usuario_actual = FakeUsuario("user_1", "juan")

    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == "user_1":
            return usuario_actual
        return None

    def fake_contar_mensajes_no_leidos(usuario_id):
        return 3

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_service, "contar_mensajes_no_leidos", fake_contar_mensajes_no_leidos)

    response = app_client.get("/api/mensajes-privados/no-leidos", headers=auth_headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["noLeidos"] == 3


def test_contar_no_leidos_sin_autenticacion(app_client):
    """Test que verifica que sin token se retorna 401"""
    response = app_client.get("/api/mensajes-privados/no-leidos")
    assert response.status_code == 401


def test_marcar_como_leido(app_client, auth_headers, monkeypatch):
    """Test que verifica marcar un mensaje como leído"""
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers
    import services.mensajes_privados_service as mensajes_service

    usuario_actual = FakeUsuario("user_1", "juan")
    otro_usuario = FakeUsuario("user_2", "maria")
    mensaje = FakeMensajePrivado("hola", otro_usuario, usuario_actual)

    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == "user_1":
            return usuario_actual
        return None

    def fake_get_mensaje_privado_by_id(mensaje_id):
        return mensaje

    def fake_marcar_mensaje_como_leido(mensaje_id, usuario_id):
        mensaje.marcar_como_leido()
        return True

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(utils.mongo_helpers, "get_mensaje_privado_by_id", fake_get_mensaje_privado_by_id)
    monkeypatch.setattr(mensajes_service, "marcar_mensaje_como_leido", fake_marcar_mensaje_como_leido)

    response = app_client.put("/api/mensajes-privados/msg_1/leer", headers=auth_headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert mensaje.leido is not None


def test_marcar_como_leido_mensaje_no_encontrado(app_client, auth_headers, monkeypatch):
    """Test que verifica el comportamiento cuando el mensaje no existe"""
    import routes.mensajes_privados as mensajes_privados
    import utils.mongo_helpers
    import services.mensajes_privados_service as mensajes_service

    usuario_actual = FakeUsuario("user_1", "juan")

    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == "user_1":
            return usuario_actual
        return None

    def fake_get_mensaje_privado_by_id(mensaje_id):
        return None

    def fake_marcar_mensaje_como_leido(mensaje_id, usuario_id):
        return False  # Simula que no se encontró

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(utils.mongo_helpers, "get_mensaje_privado_by_id", fake_get_mensaje_privado_by_id)
    monkeypatch.setattr(mensajes_service, "marcar_mensaje_como_leido", fake_marcar_mensaje_como_leido)

    response = app_client.put("/api/mensajes-privados/msg_1/leer", headers=auth_headers)
    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert "no encontrado" in payload["error"].lower() or "no tienes permiso" in payload["error"].lower()

