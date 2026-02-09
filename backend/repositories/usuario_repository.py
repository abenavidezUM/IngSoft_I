"""
Repositorio de Usuario (Experto de BD)
Contiene métodos para acceder a la base de datos de usuarios
"""

from typing import List
from models.usuario import Usuario


class UsuarioRepository:
    """
    Experto de BD para Usuario
    Implementa métodos de acceso a datos según el diagrama de secuencia
    """
    
    @staticmethod
    def gets_usuarios(usuario_ids: List[str]) -> List[Usuario]:
        """
        Obtiene una lista de usuarios por sus IDs
        (equivalente a getsUsuarios del diagrama)
        
        Args:
            usuario_ids: Lista de IDs de usuarios (pueden ser strings o ObjectIds)
            
        Returns:
            Lista de Usuario
        """
        from mongoengine.connection import get_db
        from bson import ObjectId
        
        try:
            db = get_db('default')
            
            # Convertir IDs a ObjectId
            usuario_oids = []
            for uid in usuario_ids:
                try:
                    usuario_oids.append(ObjectId(uid))
                except:
                    usuario_oids.append(uid)
            
            # Buscar usuarios
            usuarios_docs = list(
                db.usuarios.find({'_id': {'$in': usuario_oids}})
            )
            
            # Convertir a objetos Usuario
            usuarios = []
            for doc in usuarios_docs:
                try:
                    usuario = Usuario._from_son(doc)
                    usuarios.append(usuario)
                except Exception as e:
                    print(f"⚠️ Error al convertir usuario {doc.get('_id')}: {e}")
                    continue
            
            return usuarios
        except Exception as e:
            print(f"Error en gets_usuarios: {e}")
            return []

