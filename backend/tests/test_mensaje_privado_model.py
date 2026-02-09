"""
Tests para el modelo MensajePrivado (Entidad)
"""

import pytest
from datetime import datetime
from models.mensaje_privado import MensajePrivado
from models.usuario import Usuario


class FakeUsuario:
    def __init__(self, user_id, nick="user"):
        self.id = user_id
        self.nickName = nick
        self.nombre = "Nombre"
        self.apellido = "Apellido"
        self.mail = f"{nick}@example.com"
        self.biografia = "Bio"
        self.fotoUsuario = ""
        self.fotoUsuarioPortada = ""
        self.fechaDeCreado = datetime.utcnow()
        self.rol = "user"
    
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
            "rol": self.rol
        }


def test_mensaje_privado_to_dict():
    """Test que verifica la conversión a diccionario"""
    emisor = FakeUsuario("user_1", "juan")
    receptor = FakeUsuario("user_2", "maria")
    
    mensaje = MensajePrivado()
    mensaje.id = "msg_1"
    mensaje.texto = "Hola, ¿cómo estás?"
    mensaje.emisor = emisor
    mensaje.receptor = receptor
    mensaje.fechaDeCreado = datetime(2026, 1, 1, 10, 0, 0)
    mensaje.leido = None
    
    resultado = mensaje.to_dict()
    
    assert resultado['id'] == "msg_1"
    assert resultado['texto'] == "Hola, ¿cómo estás?"
    assert resultado['emisor']['nickName'] == "juan"
    assert resultado['receptor']['nickName'] == "maria"
    assert resultado['leido'] is None
    assert 'fechaDeCreado' in resultado


def test_mensaje_privado_to_dict_con_leido():
    """Test que verifica to_dict cuando el mensaje está leído"""
    emisor = FakeUsuario("user_1", "juan")
    receptor = FakeUsuario("user_2", "maria")
    
    mensaje = MensajePrivado()
    mensaje.id = "msg_1"
    mensaje.texto = "Hola"
    mensaje.emisor = emisor
    mensaje.receptor = receptor
    mensaje.fechaDeCreado = datetime(2026, 1, 1, 10, 0, 0)
    mensaje.leido = datetime(2026, 1, 1, 10, 5, 0)
    
    resultado = mensaje.to_dict()
    
    assert resultado['leido'] is not None
    assert resultado['leido'] == mensaje.leido.isoformat()


def test_mensaje_privado_marcar_como_leido():
    """Test que verifica marcar mensaje como leído"""
    emisor = FakeUsuario("user_1", "juan")
    receptor = FakeUsuario("user_2", "maria")
    
    mensaje = MensajePrivado()
    mensaje.id = "msg_1"
    mensaje.texto = "Hola"
    mensaje.emisor = emisor
    mensaje.receptor = receptor
    mensaje.fechaDeCreado = datetime(2026, 1, 1, 10, 0, 0)
    mensaje.leido = None
    
    # Mockear save para evitar problemas con BD
    mensaje.save = lambda: None
    
    mensaje.marcar_como_leido()
    
    assert mensaje.leido is not None
    assert isinstance(mensaje.leido, datetime)


def test_mensaje_privado_marcar_como_leido_ya_leido():
    """Test que verifica que no se marca dos veces como leído"""
    emisor = FakeUsuario("user_1", "juan")
    receptor = FakeUsuario("user_2", "maria")
    
    fecha_leido_original = datetime(2026, 1, 1, 10, 5, 0)
    
    mensaje = MensajePrivado()
    mensaje.id = "msg_1"
    mensaje.texto = "Hola"
    mensaje.emisor = emisor
    mensaje.receptor = receptor
    mensaje.fechaDeCreado = datetime(2026, 1, 1, 10, 0, 0)
    mensaje.leido = fecha_leido_original
    
    # Mockear save para evitar problemas con BD
    mensaje.save = lambda: None
    
    mensaje.marcar_como_leido()
    
    # No debería cambiar la fecha si ya estaba leído
    assert mensaje.leido == fecha_leido_original


def test_mensaje_privado_str():
    """Test que verifica la representación en string"""
    emisor = FakeUsuario("user_1", "juan")
    receptor = FakeUsuario("user_2", "maria")
    
    mensaje = MensajePrivado()
    mensaje.emisor = emisor
    mensaje.receptor = receptor
    
    resultado = str(mensaje)
    
    assert "juan" in resultado
    assert "maria" in resultado
    assert "MensajePrivado" in resultado

