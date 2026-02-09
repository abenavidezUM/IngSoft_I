class FakeUsuario:
    def __init__(self, user_id, seguidores=None):
        self.id = user_id
        self.seguidores = seguidores or []

    def to_dict(self):
        return {
            "id": str(self.id),
            "nickName": "user",
            "nombre": "User",
            "apellido": "Test"
        }


class FakeQuery:
    def __init__(self, usuario):
        self._usuario = usuario

    def select_related(self, *args):
        return self

    def first(self):
        return self._usuario


def test_listar_seguidores_ok(app_client, auth_headers, monkeypatch):
    import utils.mongo_helpers
    import services.seguidores_service as seguidores_service

    seguidor = FakeUsuario("seg_1")
    usuario = FakeUsuario("user_1", seguidores=[seguidor])

    def fake_get_usuario_by_id(usuario_id):
        return usuario

    def fake_obtener_seguidores(usuario):
        return [seguidor]

    # Mockear en ambos módulos
    import routes.seguidores as seguidores_route
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(seguidores_service, "obtener_seguidores", fake_obtener_seguidores)

    response = app_client.get("/api/usuarios/seguidores", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert len(payload["data"]) == 1


def test_listar_seguidores_vacio(app_client, auth_headers, monkeypatch):
    import utils.mongo_helpers
    import services.seguidores_service as seguidores_service

    usuario = FakeUsuario("user_1", seguidores=[])

    def fake_get_usuario_by_id(usuario_id):
        return usuario

    def fake_obtener_seguidores(usuario):
        return []

    # Mockear en ambos módulos
    import routes.seguidores as seguidores_route
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr(seguidores_service, "obtener_seguidores", fake_obtener_seguidores)

    response = app_client.get("/api/usuarios/seguidores", headers=auth_headers)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"] == []
    assert payload["code"] == "NO_FOLLOWERS"


def test_listar_seguidores_sin_autenticacion(app_client):
    """Test que verifica que sin token se retorna 401"""
    response = app_client.get("/api/usuarios/seguidores")
    assert response.status_code == 401


def test_listar_seguidores_usuario_no_encontrado(app_client, auth_headers, monkeypatch):
    """Test que verifica el comportamiento cuando el usuario no existe"""
    import utils.mongo_helpers

    def fake_get_usuario_by_id(usuario_id):
        return None

    # Mockear en ambos módulos
    import routes.seguidores as seguidores_route
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/usuarios/seguidores", headers=auth_headers)
    assert response.status_code == 401
    payload = response.get_json()
    assert payload["success"] is False
    assert "no autenticado" in payload["error"].lower()


def test_listar_seguidores_error_interno(app_client, auth_headers, monkeypatch):
    """Test que verifica el manejo de errores internos"""
    import utils.mongo_helpers

    def fake_get_usuario_by_id(usuario_id):
        raise Exception("Error de base de datos")

    # Mockear en ambos módulos
    import routes.seguidores as seguidores_route
    monkeypatch.setattr(utils.mongo_helpers, "get_usuario_by_id", fake_get_usuario_by_id)

    response = app_client.get("/api/usuarios/seguidores", headers=auth_headers)
    assert response.status_code == 500
    payload = response.get_json()
    assert payload["success"] is False
    assert "error" in payload or "Error" in payload

