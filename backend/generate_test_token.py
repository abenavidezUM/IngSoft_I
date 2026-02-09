"""
Script para generar un token JWT de testing
"""
from app import app
from flask_jwt_extended import create_access_token
from models import Usuario
from db import connect_databases

with app.app_context():
    connect_databases()
    
    # Buscar usuario juanperez
    usuarios = list(Usuario.objects(nickName='juanperez'))
    if usuarios:
        usuario = usuarios[0]
        token = create_access_token(identity=str(usuario.id))
        print(f"Token para {usuario.nickName}:")
        print(token)
        print(f"\nUsuario ID: {usuario.id}")
        print(f"Usuario: {usuario.to_dict()}")
    else:
        print("Usuario juanperez no encontrado")

