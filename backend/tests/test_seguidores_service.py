from services.seguidores_service import obtener_seguidores
from bson import ObjectId
from datetime import datetime


class FakeUser:
    def __init__(self, user_id, seguidores_ids=None):
        self.id = user_id
        self.seguidores_ids = seguidores_ids or []


def test_obtener_seguidores(monkeypatch):
    from models import Usuario as UsuarioModel
    
    usuario_id = ObjectId()
    seguidor1_id = ObjectId()
    seguidor2_id = ObjectId()
    
    usuario = FakeUser(usuario_id, [seguidor1_id, seguidor2_id])
    
    # Mockear la BD
    seguidores_docs = [
        {
            '_id': seguidor1_id,
            'nickName': 'seguidor1',
            'nombre': 'Seguidor',
            'apellido': 'Uno',
            'mail': 'seg1@example.com',
            'biografia': '',
            'fotoUsuario': '',
            'fotoUsuarioPortada': '',
            'fechaDeCreado': datetime.utcnow(),
            'rol': 'user',
            'seguidores': [],
            'siguiendo': []
        },
        {
            '_id': seguidor2_id,
            'nickName': 'seguidor2',
            'nombre': 'Seguidor',
            'apellido': 'Dos',
            'mail': 'seg2@example.com',
            'biografia': '',
            'fotoUsuario': '',
            'fotoUsuarioPortada': '',
            'fechaDeCreado': datetime.utcnow(),
            'rol': 'user',
            'seguidores': [],
            'siguiendo': []
        }
    ]
    
    usuario_doc = {
        '_id': usuario_id,
        'seguidores': [seguidor1_id, seguidor2_id]
    }
    
    class FakeDB:
        def __init__(self):
            self.usuarios = FakeCollection(usuario_doc, seguidores_docs)
    
    class FakeCollection:
        def __init__(self, usuario_doc, seguidores_docs):
            self._usuario_doc = usuario_doc
            self._seguidores_docs = seguidores_docs
        
        def find_one(self, query):
            if '_id' in query:
                if query['_id'] == usuario_doc['_id']:
                    return usuario_doc
            return None
        
        def find(self, query):
            if '$in' in query.get('_id', {}):
                return self._seguidores_docs
            return []
    
    def fake_get_db(alias):
        return FakeDB()
    
    monkeypatch.setattr("mongoengine.connection.get_db", fake_get_db)
    
    seguidores = obtener_seguidores(usuario)
    
    assert len(seguidores) == 2
    assert seguidores[0].nickName in ['seguidor1', 'seguidor2']
    assert seguidores[1].nickName in ['seguidor1', 'seguidor2']

