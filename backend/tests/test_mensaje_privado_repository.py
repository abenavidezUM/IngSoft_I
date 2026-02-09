"""
Tests para MensajePrivadoRepository (Experto de BD)
"""

import pytest
from datetime import datetime
from bson import ObjectId
from repositories.mensaje_privado_repository import MensajePrivadoRepository


class FakeMensajePrivado:
    def __init__(self, msg_id, texto, emisor_id, receptor_id, leido=None):
        self.id = msg_id
        self.texto = texto
        self.emisor_id = emisor_id
        self.receptor_id = receptor_id
        self.leido = leido
        self.fechaDeCreado = datetime(2026, 1, 1, 10, 0, 0)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "texto": self.texto,
            "fechaDeCreado": self.fechaDeCreado.isoformat(),
            "emisor": {"id": str(self.emisor_id)},
            "receptor": {"id": str(self.receptor_id)},
            "leido": self.leido.isoformat() if self.leido else None
        }


def test_gets_mensaje_privados(monkeypatch):
    """Test que verifica obtener mensajes privados de un usuario"""
    usuario_oid = ObjectId()
    otro_usuario_oid = ObjectId()
    mensajes_docs = [
        {
            '_id': ObjectId(),
            'texto': 'Mensaje 1',
            'emisor': usuario_oid,
            'receptor': otro_usuario_oid,
            'fechaDeCreado': datetime(2026, 1, 1, 10, 0, 0),
            'leido': None
        },
        {
            '_id': ObjectId(),
            'texto': 'Mensaje 2',
            'emisor': otro_usuario_oid,
            'receptor': usuario_oid,
            'fechaDeCreado': datetime(2026, 1, 1, 11, 0, 0),
            'leido': None
        }
    ]
    usuario_id = str(usuario_oid)
    
    class FakeDB:
        def __init__(self):
            self.mensajes_privados = FakeCollection(mensajes_docs)
    
    class FakeCollection:
        def __init__(self, docs):
            self._docs = docs
        
        def find(self, query):
            return FakeCursor(self._docs)
    
    class FakeCursor:
        def __init__(self, docs):
            self._docs = docs
        
        def sort(self, field, direction):
            return self
        
        def __iter__(self):
            return iter(self._docs)
    
    def fake_get_db(alias):
        return FakeDB()
    
    # Mockear _from_son para crear objetos MensajePrivado
    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    
    mensajes = MensajePrivadoRepository.gets_mensaje_privados(usuario_id)
    
    assert len(mensajes) == 2
    # Verificar que los mensajes tienen texto
    textos = [msg.texto for msg in mensajes if hasattr(msg, 'texto') and msg.texto]
    assert 'Mensaje 1' in textos or 'Mensaje 2' in textos


def test_gets_mensaje_privado(monkeypatch):
    """Test que verifica obtener conversación entre dos usuarios"""
    usuario_actual_oid = ObjectId()
    otro_usuario_oid = ObjectId()
    usuario_actual_id = str(usuario_actual_oid)
    otro_usuario_id = str(otro_usuario_oid)
    
    mensajes_docs = [
        {
            '_id': ObjectId(),
            'texto': 'Hola',
            'emisor': usuario_actual_oid,
            'receptor': otro_usuario_oid,
            'fechaDeCreado': datetime(2026, 1, 1, 10, 0, 0),
            'leido': None
        }
    ]
    
    class FakeDB:
        def __init__(self):
            self.mensajes_privados = FakeCollection(mensajes_docs)
    
    class FakeCollection:
        def __init__(self, docs):
            self._docs = docs
        
        def find(self, query):
            return FakeCursor(self._docs)
        
        def count_documents(self, query):
            return len(self._docs)
    
    class FakeCursor:
        def __init__(self, docs):
            self._docs = docs
        
        def sort(self, field, direction):
            return self
        
        def skip(self, n):
            return self
        
        def limit(self, n):
            return self
        
        def __iter__(self):
            return iter(self._docs)
    
    def fake_get_db(alias):
        return FakeDB()
    
    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    
    mensajes, total = MensajePrivadoRepository.gets_mensaje_privado(
        usuario_actual_id, otro_usuario_id, limit=50, offset=0
    )
    
    assert len(mensajes) == 1
    assert total == 1
    assert mensajes[0].texto == 'Hola'


def test_post_mensaje(monkeypatch):
    """Test que verifica crear un nuevo mensaje privado"""
    # Este test verifica que el método post_mensaje llama correctamente a MensajePrivado
    # Para evitar problemas con MongoEngine, simplemente verificamos que se crea la instancia
    # El test real de guardado se hace en los tests de integración
    
    from models.mensaje_privado import MensajePrivado
    from models.usuario import Usuario
    
    # Crear usuarios reales de MongoEngine (sin guardar)
    emisor = Usuario()
    emisor.id = ObjectId()
    emisor.nickName = "juan"
    
    receptor = Usuario()
    receptor.id = ObjectId()
    receptor.nickName = "maria"
    
    texto = "Hola, ¿cómo estás?"
    
    mensaje_guardado = None
    
    # Mockear el método save directamente
    original_save = MensajePrivado.save
    
    def mock_save(self):
        nonlocal mensaje_guardado
        mensaje_guardado = self
        return self
    
    monkeypatch.setattr(MensajePrivado, "save", mock_save)
    
    try:
        mensaje = MensajePrivadoRepository.post_mensaje(texto, emisor, receptor)
        
        assert mensaje is not None
        assert mensaje.texto == texto
        assert mensaje.emisor == emisor
        assert mensaje.receptor == receptor
        assert mensaje_guardado is not None
    finally:
        # Restaurar el método original
        monkeypatch.setattr(MensajePrivado, "save", original_save)


def test_marcar_como_leido(monkeypatch):
    """Test que verifica marcar un mensaje como leído"""
    mensaje_oid = ObjectId()
    usuario_oid = ObjectId()
    mensaje_id = str(mensaje_oid)
    usuario_id = str(usuario_oid)
    
    mensaje_doc = {
        '_id': mensaje_oid,
        'emisor': ObjectId(),
        'receptor': usuario_oid,
        'leido': None
    }
    
    class FakeDB:
        def __init__(self):
            self.mensajes_privados = FakeCollection()
    
    class FakeCollection:
        def find_one(self, query):
            if query.get('_id') == mensaje_doc['_id']:
                return mensaje_doc
            return None
        
        def update_one(self, filter_query, update_query):
            mensaje_doc['leido'] = datetime.utcnow()
            return True
    
    def fake_get_db(alias):
        return FakeDB()
    
    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    
    resultado = MensajePrivadoRepository.marcar_como_leido(mensaje_id, usuario_id)
    
    assert resultado is True


def test_contar_no_leidos(monkeypatch):
    """Test que verifica contar mensajes no leídos"""
    emisor_id = str(ObjectId())
    receptor_id = str(ObjectId())
    
    class FakeDB:
        def __init__(self):
            self.mensajes_privados = FakeCollection()
    
    class FakeCollection:
        def count_documents(self, query):
            # Simular 3 mensajes no leídos
            return 3
    
    def fake_get_db(alias):
        return FakeDB()
    
    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    
    no_leidos = MensajePrivadoRepository.contar_no_leidos(emisor_id, receptor_id)
    
    assert no_leidos == 3


def test_contar_no_leidos_por_receptor(monkeypatch):
    """Test que verifica contar todos los mensajes no leídos de un receptor"""
    receptor_id = str(ObjectId())
    
    class FakeDB:
        def __init__(self):
            self.mensajes_privados = FakeCollection()
    
    class FakeCollection:
        def count_documents(self, query):
            # Simular 5 mensajes no leídos
            return 5
    
    def fake_get_db(alias):
        return FakeDB()
    
    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    
    no_leidos = MensajePrivadoRepository.contar_no_leidos_por_receptor(receptor_id)
    
    assert no_leidos == 5


class FakeUsuario:
    def __init__(self, user_id, nick="user"):
        self.id = user_id if isinstance(user_id, ObjectId) else ObjectId() if len(str(user_id)) == 24 else user_id
        self.nickName = nick

