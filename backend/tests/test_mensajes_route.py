class FakeUsuario:
    def __init__(self, user_id):
        self.id = user_id


class FakeMensaje:
    def to_dict(self):
        return {
            "id": "msg_1",
            "texto": "hola",
            "fechaDeCreado": "2026-01-01T10:00:00Z"
        }


class FakeQuery:
    def __init__(self, usuario):
        self._usuario = usuario

    def select_related(self, *args):
        return self

    def first(self):
        return self._usuario


def test_obtener_mensajes_mios(app_client, auth_headers, monkeypatch):
    import models
    import routes.mensajes as mensajes_route
    import utils.mongo_helpers

    usuario = FakeUsuario("user_1")

    def fake_objects(**kwargs):
        return FakeQuery(usuario)

    def fake_get_usuario_by_id(usuario_id):
        return usuario

    def fake_obtener_mis_mensajes(user, limit, offset):
        return [FakeMensaje()], 1

    monkeypatch.setattr(models.Usuario, "objects", staticmethod(fake_objects))
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_route, "obtener_mis_mensajes", fake_obtener_mis_mensajes)

    response = app_client.get("/api/mensajes/mios", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["total"] == 1
    assert payload["data"]["mensajes"][0]["id"] == "msg_1"


def test_obtener_mensajes_mios_sin_autenticacion(app_client):
    """Test que verifica que sin token se retorna 401"""
    response = app_client.get("/api/mensajes/mios")
    assert response.status_code == 401


def test_obtener_mensajes_mios_usuario_no_encontrado(app_client, auth_headers, monkeypatch):
    """Test que verifica el comportamiento cuando el usuario no existe"""
    import utils.mongo_helpers

    def fake_get_usuario_by_id(usuario_id):
        return None

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/mensajes/mios", headers=auth_headers)
    assert response.status_code == 401
    payload = response.get_json()
    assert payload["success"] is False
    assert "no autenticado" in payload["error"].lower() or "no encontrado" in payload["error"].lower()


def test_obtener_mensajes_mios_con_paginacion(app_client, auth_headers, monkeypatch):
    """Test que verifica la paginación de mensajes"""
    import models
    import routes.mensajes as mensajes_route
    import utils.mongo_helpers

    usuario = FakeUsuario("user_1")

    def fake_objects(**kwargs):
        return FakeQuery(usuario)

    def fake_get_usuario_by_id(usuario_id):
        return usuario

    def fake_obtener_mis_mensajes(user, limit, offset):
        mensajes = [FakeMensaje() for _ in range(limit)]
        return mensajes, 50  # Total de 50 mensajes

    monkeypatch.setattr(models.Usuario, "objects", staticmethod(fake_objects))
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_route, "obtener_mis_mensajes", fake_obtener_mis_mensajes)

    response = app_client.get("/api/mensajes/mios?limit=10&offset=0", headers=auth_headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["limit"] == 10
    assert payload["data"]["offset"] == 0
    assert payload["data"]["total"] == 50
    assert payload["data"]["hasMore"] is True


# =====================
# Tests CU0008 - Borrar Mensajes Propios
# =====================

def test_borrar_mensaje_exitoso(app_client, auth_headers, monkeypatch):
    """Test que verifica el borrado exitoso de un mensaje propio"""
    import utils.mongo_helpers
    import routes.mensajes as mensajes_route

    usuario = FakeUsuario("user_1")

    def fake_get_usuario_by_id(usuario_id):
        return usuario

    def fake_borrar_mensaje(user, mensaje_id):
        return True, "Mensaje borrado exitosamente", 200

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_route, "borrar_mensaje", fake_borrar_mensaje)

    response = app_client.delete("/api/mensajes/msg_123", headers=auth_headers)
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "borrado exitosamente" in payload["message"].lower()


def test_borrar_mensaje_sin_autenticacion(app_client):
    """Test que verifica que sin token se retorna 401"""
    response = app_client.delete("/api/mensajes/msg_123")
    assert response.status_code == 401


def test_borrar_mensaje_usuario_no_encontrado(app_client, auth_headers, monkeypatch):
    """Test que verifica el comportamiento cuando el usuario no existe"""
    import utils.mongo_helpers

    def fake_get_usuario_by_id(usuario_id):
        return None

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.delete("/api/mensajes/msg_123", headers=auth_headers)
    assert response.status_code == 401
    payload = response.get_json()
    assert payload["success"] is False
    assert "no autenticado" in payload["error"].lower() or "no encontrado" in payload["error"].lower()


def test_borrar_mensaje_no_existe(app_client, auth_headers, monkeypatch):
    """Test que verifica el comportamiento cuando el mensaje no existe"""
    import utils.mongo_helpers
    import routes.mensajes as mensajes_route

    usuario = FakeUsuario("user_1")

    def fake_get_usuario_by_id(usuario_id):
        return usuario

    def fake_borrar_mensaje(user, mensaje_id):
        return False, "Mensaje no encontrado", 404

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_route, "borrar_mensaje", fake_borrar_mensaje)

    response = app_client.delete("/api/mensajes/msg_999", headers=auth_headers)
    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert "no encontrado" in payload["error"].lower()


def test_borrar_mensaje_no_es_autor(app_client, auth_headers, monkeypatch):
    """Test que verifica que un usuario no puede borrar mensajes de otros"""
    import utils.mongo_helpers
    import routes.mensajes as mensajes_route

    usuario = FakeUsuario("user_1")

    def fake_get_usuario_by_id(usuario_id):
        return usuario

    def fake_borrar_mensaje(user, mensaje_id):
        return False, "No tienes permiso para borrar este mensaje", 403

    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(mensajes_route, "borrar_mensaje", fake_borrar_mensaje)

    response = app_client.delete("/api/mensajes/msg_otros", headers=auth_headers)
    assert response.status_code == 403
    payload = response.get_json()
    assert payload["success"] is False
    assert "permiso" in payload["error"].lower()

