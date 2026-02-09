"""
Tests para UsuarioRepository (Experto de BD)
"""

import pytest
from bson import ObjectId
from repositories.usuario_repository import UsuarioRepository


class FakeUsuario:
    def __init__(self, user_id, nick="user"):
        self.id = user_id
        self.nickName = nick
        self.nombre = "Nombre"
        self.apellido = "Apellido"


def test_gets_usuarios(monkeypatch):
    """Test que verifica obtener usuarios por IDs"""
    usuario_oid1 = ObjectId()
    usuario_oid2 = ObjectId()
    usuario_oid3 = ObjectId()
    usuario_ids = [str(usuario_oid1), str(usuario_oid2), str(usuario_oid3)]
    
    usuarios_docs = [
        {
            '_id': usuario_oid1,
            'nickName': 'juan',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'mail': 'juan@example.com',
            'biografia': 'Bio',
            'fotoUsuario': '',
            'fotoUsuarioPortada': '',
            'fechaDeCreado': None,
            'rol': 'user',
            'seguidores': [],
            'siguiendo': []
        },
        {
            '_id': usuario_oid2,
            'nickName': 'maria',
            'nombre': 'María',
            'apellido': 'García',
            'mail': 'maria@example.com',
            'biografia': 'Bio',
            'fotoUsuario': '',
            'fotoUsuarioPortada': '',
            'fechaDeCreado': None,
            'rol': 'user',
            'seguidores': [],
            'siguiendo': []
        }
    ]
    
    class FakeDB:
        def __init__(self):
            self.usuarios = FakeCollection(usuarios_docs)
    
    class FakeCollection:
        def __init__(self, docs):
            self._docs = docs
        
        def find(self, query):
            return list(self._docs)
    
    def fake_get_db(alias):
        return FakeDB()
    
    def fake_from_son(doc):
        from models.usuario import Usuario
        usuario = Usuario()
        usuario.id = doc['_id']
        usuario.nickName = doc['nickName']
        usuario.nombre = doc['nombre']
        usuario.apellido = doc['apellido']
        usuario.mail = doc['mail']
        usuario.biografia = doc['biografia']
        usuario.fotoUsuario = doc['fotoUsuario']
        usuario.fotoUsuarioPortada = doc['fotoUsuarioPortada']
        usuario.fechaDeCreado = doc['fechaDeCreado']
        usuario.rol = doc['rol']
        usuario.seguidores = doc['seguidores']
        usuario.siguiendo = doc['siguiendo']
        return usuario
    
    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    monkeypatch.setattr("models.usuario.Usuario._from_son", staticmethod(fake_from_son))
    
    usuarios = UsuarioRepository.gets_usuarios(usuario_ids)
    
    assert len(usuarios) == 2
    assert usuarios[0].nickName in ['juan', 'maria']
    assert usuarios[1].nickName in ['juan', 'maria']


def test_gets_usuarios_vacio(monkeypatch):
    """Test que verifica obtener usuarios cuando no existen"""
    usuario_ids = [str(ObjectId())]
    
    class FakeDB:
        def __init__(self):
            self.usuarios = FakeCollection([])
    
    class FakeCollection:
        def __init__(self, docs):
            self._docs = docs
        
        def find(self, query):
            return []
    
    def fake_get_db(alias):
        return FakeDB()
    
    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    
    usuarios = UsuarioRepository.gets_usuarios(usuario_ids)
    
    assert len(usuarios) == 0

