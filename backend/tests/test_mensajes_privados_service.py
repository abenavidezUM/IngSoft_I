"""
Tests para MensajesPrivadosService (Gestor de Mensajes)
"""

import pytest
from datetime import datetime
from services.mensajes_privados_service import (
    obtener_mensajes_privados,
    obtener_conversacion,
    crear_mensaje_privado,
    listar_conversaciones,
    marcar_mensaje_como_leido,
    contar_mensajes_no_leidos,
    obtener_usuarios_por_ids
)


class FakeUsuario:
    def __init__(self, user_id, nick="user"):
        from bson import ObjectId
        # Aceptar ObjectId o string
        if isinstance(user_id, ObjectId):
            self.id = user_id
        elif isinstance(user_id, str) and len(user_id) == 24:
            try:
                self.id = ObjectId(user_id)
            except:
                self.id = user_id
        else:
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
            "fotoUsuario": self.fotoUsuario
        }


class FakeMensajePrivado:
    def __init__(self, texto, emisor, receptor):
        self.id = "msg_1"
        self.texto = texto
        self.emisor = emisor
        self.receptor = receptor
        self.leido = None
        self.fechaDeCreado = datetime(2026, 1, 1, 10, 0, 0)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "texto": self.texto,
            "fechaDeCreado": self.fechaDeCreado.isoformat(),
            "emisor": self.emisor.to_dict(),
            "receptor": self.receptor.to_dict(),
            "leido": self.leido.isoformat() if self.leido else None
        }


def test_obtener_mensajes_privados(monkeypatch):
    """Test que verifica obtener mensajes privados de un usuario"""
    usuario_id = "user_1"
    mensajes = [
        FakeMensajePrivado("Hola", FakeUsuario("user_1"), FakeUsuario("user_2")),
        FakeMensajePrivado("Adiós", FakeUsuario("user_2"), FakeUsuario("user_1"))
    ]
    
    def fake_gets_mensaje_privados(usuario_id):
        return mensajes
    
    monkeypatch.setattr("repositories.mensaje_privado_repository.MensajePrivadoRepository.gets_mensaje_privados", 
                        staticmethod(fake_gets_mensaje_privados))
    
    resultado, hay_mensajes = obtener_mensajes_privados(usuario_id)
    
    assert len(resultado) == 2
    assert hay_mensajes is True


def test_obtener_mensajes_privados_vacio(monkeypatch):
    """Test que verifica obtener mensajes cuando no hay ninguno"""
    usuario_id = "user_1"
    
    def fake_gets_mensaje_privados(usuario_id):
        return []
    
    monkeypatch.setattr("repositories.mensaje_privado_repository.MensajePrivadoRepository.gets_mensaje_privados", 
                        staticmethod(fake_gets_mensaje_privados))
    
    resultado, hay_mensajes = obtener_mensajes_privados(usuario_id)
    
    assert len(resultado) == 0
    assert hay_mensajes is False


def test_obtener_conversacion(monkeypatch):
    """Test que verifica obtener conversación entre dos usuarios"""
    usuario_actual_id = "user_1"
    otro_usuario_id = "user_2"
    mensajes = [
        FakeMensajePrivado("Hola", FakeUsuario("user_1"), FakeUsuario("user_2")),
        FakeMensajePrivado("Hola de vuelta", FakeUsuario("user_2"), FakeUsuario("user_1"))
    ]
    
    def fake_gets_mensaje_privado(usuario_actual_id, otro_usuario_id, limit, offset):
        return mensajes, 2
    
    def fake_marcar_como_leido_por_receptor(emisor_id, receptor_id):
        pass
    
    monkeypatch.setattr("repositories.mensaje_privado_repository.MensajePrivadoRepository.gets_mensaje_privado", 
                        staticmethod(fake_gets_mensaje_privado))
    monkeypatch.setattr("repositories.mensaje_privado_repository.MensajePrivadoRepository.marcar_como_leido_por_receptor", 
                        staticmethod(fake_marcar_como_leido_por_receptor))
    
    resultado = obtener_conversacion(usuario_actual_id, otro_usuario_id, limit=50, offset=0)
    
    assert resultado['total'] == 2
    assert len(resultado['conversacion']) == 2
    assert resultado['hasMore'] is False


def test_crear_mensaje_privado(monkeypatch):
    """Test que verifica crear un mensaje privado"""
    from bson import ObjectId
    emisor_oid = ObjectId()
    receptor_oid = ObjectId()
    emisor_id = str(emisor_oid)
    receptor_id = str(receptor_oid)
    texto = "Hola, ¿cómo estás?"
    
    emisor = FakeUsuario(emisor_oid, "juan")
    receptor = FakeUsuario(receptor_oid, "maria")
    mensaje = FakeMensajePrivado(texto, emisor, receptor)
    
    def fake_get_usuario_by_id(usuario_id):
        # Comparar como strings para evitar problemas de tipo
        usuario_id_str = str(usuario_id)
        if usuario_id_str == emisor_id or usuario_id_str == str(emisor_oid):
            return emisor
        if usuario_id_str == receptor_id or usuario_id_str == str(receptor_oid):
            return receptor
        return None
    
    def fake_post_mensaje(texto, emisor, receptor):
        return mensaje
    
    # Mockear get_usuario_by_id en el módulo de servicio también
    monkeypatch.setattr("services.mensajes_privados_service.get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr("utils.mongo_helpers.get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr("repositories.mensaje_privado_repository.MensajePrivadoRepository.post_mensaje", 
                        staticmethod(fake_post_mensaje))
    
    resultado = crear_mensaje_privado(emisor_id, receptor_id, texto)
    
    assert resultado is not None
    assert resultado.texto == texto
    assert resultado.emisor == emisor
    assert resultado.receptor == receptor


def test_crear_mensaje_privado_usuario_no_existe(monkeypatch):
    """Test que verifica crear mensaje cuando el receptor no existe"""
    emisor_id = "user_1"
    receptor_id = "user_inexistente"
    texto = "Hola"
    
    emisor = FakeUsuario(emisor_id, "juan")
    
    def fake_get_usuario_by_id(usuario_id):
        if usuario_id == emisor_id:
            return emisor
        return None
    
    monkeypatch.setattr("utils.mongo_helpers.get_usuario_by_id", fake_get_usuario_by_id)
    
    resultado = crear_mensaje_privado(emisor_id, receptor_id, texto)
    
    assert resultado is None


def test_crear_mensaje_privado_a_si_mismo(monkeypatch):
    """Test que verifica que no se puede enviar mensaje a sí mismo"""
    usuario_id = "user_1"
    texto = "Hola"
    
    usuario = FakeUsuario(usuario_id, "juan")
    
    def fake_get_usuario_by_id(usuario_id):
        return usuario
    
    monkeypatch.setattr("utils.mongo_helpers.get_usuario_by_id", fake_get_usuario_by_id)
    
    resultado = crear_mensaje_privado(usuario_id, usuario_id, texto)
    
    assert resultado is None


def test_listar_conversaciones(monkeypatch):
    """Test que verifica listar conversaciones"""
    from bson import ObjectId
    usuario_oid = ObjectId()
    otro_usuario_oid1 = ObjectId()
    otro_usuario_oid2 = ObjectId()
    usuario_id = str(usuario_oid)
    
    mensaje1 = FakeMensajePrivado("Hola", FakeUsuario(usuario_oid), FakeUsuario(otro_usuario_oid1))
    mensaje2 = FakeMensajePrivado("Hola", FakeUsuario(usuario_oid), FakeUsuario(otro_usuario_oid2))
    mensajes = [mensaje1, mensaje2]
    
    def fake_gets_mensaje_privados(usuario_id):
        return mensajes
    
    def fake_get_usuario_by_id(usuario_id):
        usuario_id_str = str(usuario_id)
        # El servicio busca usuarios por el ID del otro usuario en los mensajes
        if usuario_id_str == str(otro_usuario_oid1):
            return FakeUsuario(otro_usuario_oid1, "maria")
        if usuario_id_str == str(otro_usuario_oid2):
            return FakeUsuario(otro_usuario_oid2, "carlos")
        if usuario_id_str == str(usuario_oid):
            return FakeUsuario(usuario_oid, "juan")
        return None
    
    def fake_contar_no_leidos(emisor_id, receptor_id):
        # Comparar como strings
        emisor_id_str = str(emisor_id)
        receptor_id_str = str(receptor_id)
        if (emisor_id_str == str(otro_usuario_oid1) and receptor_id_str == str(usuario_oid)) or \
           (emisor_id_str == str(otro_usuario_oid2) and receptor_id_str == str(usuario_oid)):
            return 0
        return 0
    
    monkeypatch.setattr("repositories.mensaje_privado_repository.MensajePrivadoRepository.gets_mensaje_privados", 
                        staticmethod(fake_gets_mensaje_privados))
    monkeypatch.setattr("services.mensajes_privados_service.get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr("utils.mongo_helpers.get_usuario_by_id", fake_get_usuario_by_id)
    monkeypatch.setattr("repositories.mensaje_privado_repository.MensajePrivadoRepository.contar_no_leidos", 
                        staticmethod(fake_contar_no_leidos))
    
    conversaciones = listar_conversaciones(usuario_id)
    
    assert len(conversaciones) == 2
    assert conversaciones[0]['usuario']['nickName'] in ['maria', 'carlos']
    assert conversaciones[1]['usuario']['nickName'] in ['maria', 'carlos']


def test_marcar_mensaje_como_leido(monkeypatch):
    """Test que verifica marcar mensaje como leído"""
    mensaje_id = "msg_1"
    usuario_id = "user_2"
    
    def fake_marcar_como_leido(mensaje_id, usuario_id):
        return True
    
    monkeypatch.setattr("repositories.mensaje_privado_repository.MensajePrivadoRepository.marcar_como_leido", 
                        staticmethod(fake_marcar_como_leido))
    
    resultado = marcar_mensaje_como_leido(mensaje_id, usuario_id)
    
    assert resultado is True


def test_contar_mensajes_no_leidos(monkeypatch):
    """Test que verifica contar mensajes no leídos"""
    usuario_id = "user_2"
    
    def fake_contar_no_leidos_por_receptor(receptor_id):
        return 5
    
    monkeypatch.setattr("repositories.mensaje_privado_repository.MensajePrivadoRepository.contar_no_leidos_por_receptor", 
                        staticmethod(fake_contar_no_leidos_por_receptor))
    
    no_leidos = contar_mensajes_no_leidos(usuario_id)
    
    assert no_leidos == 5


def test_obtener_usuarios_por_ids(monkeypatch):
    """Test que verifica obtener usuarios por IDs"""
    from bson import ObjectId
    usuario_oid1 = ObjectId()
    usuario_oid2 = ObjectId()
    usuario_ids = [str(usuario_oid1), str(usuario_oid2)]
    usuarios = [
        FakeUsuario(usuario_oid1, "juan"),
        FakeUsuario(usuario_oid2, "maria")
    ]
    
    def fake_gets_usuarios(usuario_ids):
        return usuarios
    
    monkeypatch.setattr("repositories.usuario_repository.UsuarioRepository.gets_usuarios", 
                        staticmethod(fake_gets_usuarios))
    
    resultado = obtener_usuarios_por_ids(usuario_ids)
    
    assert len(resultado) == 2
    assert resultado[0].nickName in ['juan', 'maria']
    assert resultado[1].nickName in ['juan', 'maria']

