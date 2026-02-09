"""
Script de Inicialización de Base de Datos MongoDB

Este script:
1. Conecta a MongoDB Atlas
2. Crea las colecciones necesarias
3. Crea índices
4. (Opcional) Inserta datos de prueba

Uso:
    python init_db.py
    python init_db.py --with-sample-data
"""

import os
import sys
from dotenv import load_dotenv
from mongoengine import disconnect
import argparse

# Cargar variables de entorno
load_dotenv()

# Importar modelos
from models import Usuario, Mensaje, MensajePrivado, Etiqueta, Mencion
from models.log import Log
from db import connect_databases

def connect_db():
    """Conecta a MongoDB (local por defecto)."""
    try:
        connect_databases()
        print("✅ Conectado a MongoDB")
        return True
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return False

def create_collections():
    """Crea las colecciones y sus índices"""
    try:
        print("\n📦 Creando colecciones e índices...")
        
        # Las colecciones se crean automáticamente al insertar el primer documento
        # Pero podemos asegurar que los índices existan
        
        # Usuario
        Usuario.ensure_indexes()
        print("✅ Colección 'usuarios' e índices creados")
        
        # Etiqueta
        Etiqueta.ensure_indexes()
        print("✅ Colección 'etiquetas' e índices creados")
        
        # Mencion
        Mencion.ensure_indexes()
        print("✅ Colección 'menciones' e índices creados")
        
        # Mensaje
        Mensaje.ensure_indexes()
        print("✅ Colección 'mensajes' e índices creados")
        
        # MensajePrivado
        MensajePrivado.ensure_indexes()
        print("✅ Colección 'mensajes_privados' e índices creados")
        
        # Log (en logs_db)
        Log.ensure_indexes()
        print("✅ Colección 'logs' e índices creados (en logs_db)")
        
        return True
    except Exception as e:
        print(f"❌ Error creando colecciones: {e}")
        return False

def insert_sample_data():
    """Inserta datos de prueba - mínimo 10 de cada tipo"""
    try:
        print("\n📝 Insertando datos de prueba...")
        
        # Limpiar datos existentes (solo en desarrollo)
        Usuario.objects.delete()
        Etiqueta.objects.delete()
        Mencion.objects.delete()
        Mensaje.objects.delete()
        MensajePrivado.objects.delete()
        Log.objects.using('logs').delete()  # Limpiar logs también
        print("🗑️  Datos anteriores eliminados")
        
        # Crear 12 usuarios
        usuarios = []
        nombres = [
            ("juanperez", "Juan", "Pérez", "juan@example.com", "Desarrollador Full Stack"),
            ("mariagarcia", "María", "García", "maria@example.com", "Diseñadora UX/UI"),
            ("carloslopez", "Carlos", "López", "carlos@example.com", "Ingeniero de Software"),
            ("anatorres", "Ana", "Torres", "ana@example.com", "Product Manager"),
            ("luisrodriguez", "Luis", "Rodríguez", "luis@example.com", "DevOps Engineer"),
            ("sofiamartinez", "Sofía", "Martínez", "sofia@example.com", "Data Scientist"),
            ("pedrosanchez", "Pedro", "Sánchez", "pedro@example.com", "Backend Developer"),
            ("laurafernandez", "Laura", "Fernández", "laura@example.com", "Frontend Developer"),
            ("miguelgomez", "Miguel", "Gómez", "miguel@example.com", "Mobile Developer"),
            ("elenaruiz", "Elena", "Ruiz", "elena@example.com", "QA Engineer"),
            ("davidmoreno", "David", "Moreno", "david@example.com", "Tech Lead"),
            ("admin", "Admin", "System", "admin@example.com", "Administrador del sistema")
        ]
        
        for nick, nombre, apellido, mail, bio in nombres:
            usuario = Usuario(
                nickName=nick,
                nombre=nombre,
                apellido=apellido,
                mail=mail,
                biografia=bio,
                rol="admin" if nick == "admin" else "user"
            )
            usuario.set_password("password123")
            usuario.save()
            usuarios.append(usuario)
            print(f"✅ Usuario creado: {usuario.nickName}")
        
        # Configurar relaciones de seguimiento (usuario1 sigue a varios)
        usuario1 = usuarios[0]  # juanperez
        usuario1.siguiendo = usuarios[1:6]  # Sigue a 5 usuarios
        for u in usuarios[1:6]:
            u.seguidores.append(usuario1)
            u.save()
        usuario1.save()
        print("✅ Relaciones de seguimiento configuradas")
        
        # Crear 12 etiquetas
        etiquetas_texto = [
            "#python", "#angular", "#mongodb", "#react", "#nodejs",
            "#javascript", "#typescript", "#docker", "#kubernetes", "#aws",
            "#devops", "#frontend"
        ]
        etiquetas = []
        for texto in etiquetas_texto:
            etiqueta = Etiqueta(texto=texto).save()
            etiquetas.append(etiqueta)
        print(f"✅ {len(etiquetas)} etiquetas creadas")
        
        # Crear 15 mensajes públicos (todos deben tener al menos una mención)
        mensajes_texto = [
            ("¡Hola @mariagarcia! ¿Qué tal el proyecto? #python #mongodb", 0, [0, 2], [1]),
            ("¡Muy bien @juanperez! El diseño está quedando genial #angular", 1, [1], [0]),
            ("Acabo de terminar una nueva feature @carloslopez #react #frontend", 2, [3, 11], [2]),
            ("Revisando el código de @carloslopez, muy buen trabajo #nodejs", 3, [4], [2]),
            ("Nueva actualización del sistema @luisrodriguez #docker #kubernetes", 4, [7, 8], [4]),
            ("¿Alguien más está trabajando con @sofiamartinez #typescript? Muy recomendado", 5, [6], [5]),
            ("Feliz de anunciar nuestro nuevo proyecto @pedrosanchez #aws #devops", 6, [9, 10], [6]),
            ("Gran trabajo del equipo en el sprint pasado @laurafernandez #javascript", 7, [5], [7]),
            ("Compartiendo algunos tips de #python que aprendí hoy @mariagarcia", 0, [0], [1]),
            ("El diseño de @anatorres quedó increíble #angular #frontend", 1, [1, 11], [3]),
            ("Implementando nuevas funcionalidades @miguelgomez #mongodb #nodejs", 2, [2, 4], [8]),
            ("Reunión de equipo mañana, no olviden @elenaruiz #react", 3, [3], [9]),
            ("Nuevo blog post sobre #docker, échenle un vistazo @davidmoreno", 4, [7], [10]),
            ("Celebrando 1000 commits en el proyecto @admin #devops", 5, [10], [11]),
            ("Gracias a todos por el apoyo @juanperez #javascript #typescript", 6, [5, 6], [0])
        ]
        
        mensajes = []
        for texto, autor_idx, etiquetas_idx, menciones_idx in mensajes_texto:
            autor = usuarios[autor_idx]
            etiquetas_list = [etiquetas[i] for i in etiquetas_idx]
            menciones_list = [Mencion(usuario=usuarios[i]).save() for i in menciones_idx]
            
            mensaje = Mensaje(
                texto=texto,
                autor=autor,
                etiquetas=etiquetas_list,
                menciones=menciones_list
            )
            mensaje.save()
            mensajes.append(mensaje)
        print(f"✅ {len(mensajes)} mensajes públicos creados")
        
        # Crear 15 mensajes privados
        mensajes_privados_texto = [
            ("Hola María, ¿podemos hablar sobre el proyecto?", 0, 1),
            ("¡Claro! Dime, ¿qué necesitas?", 1, 0),
            ("¿Tienes tiempo para revisar el código?", 0, 2),
            ("Sí, puedo revisarlo esta tarde", 2, 0),
            ("Gracias por la ayuda con el diseño", 0, 3),
            ("De nada, fue un placer trabajar contigo", 3, 0),
            ("¿Podrías ayudarme con la configuración?", 0, 4),
            ("Por supuesto, te paso los detalles", 4, 0),
            ("Excelente trabajo en la última feature", 1, 2),
            ("Gracias, tu feedback fue muy útil", 2, 1),
            ("¿Cuándo podemos hacer la demo?", 3, 4),
            ("Propongo el viernes a las 3pm", 4, 3),
            ("Perfecto, nos vemos entonces", 3, 4),
            ("¿Tienes el documento actualizado?", 5, 6),
            ("Sí, te lo envío ahora mismo", 6, 5)
        ]
        
        mensajes_privados = []
        for texto, emisor_idx, receptor_idx in mensajes_privados_texto:
            mensaje_priv = MensajePrivado(
                texto=texto,
                emisor=usuarios[emisor_idx],
                receptor=usuarios[receptor_idx]
            )
            mensaje_priv.save()
            mensajes_privados.append(mensaje_priv)
            # Marcar algunos como leídos
            if len(mensajes_privados) % 3 == 0:
                mensaje_priv.marcar_como_leido()
        print(f"✅ {len(mensajes_privados)} mensajes privados creados")
        
        # Crear 15 logs
        from datetime import datetime
        log_events = [
            ('INFO', 'Sistema inicializado con datos de prueba', None, 'init_db', {'usuarios_creados': len(usuarios)}),
            ('INFO', f'Usuario {usuarios[0].nickName} creado', str(usuarios[0].id), 'user_created', {'rol': usuarios[0].rol}),
            ('INFO', f'Mensaje privado enviado de {usuarios[0].nickName} a {usuarios[1].nickName}', str(usuarios[0].id), 'send_private_message', {'receptor_id': str(usuarios[1].id)}),
            ('INFO', f'Mensaje público creado por {usuarios[0].nickName}', str(usuarios[0].id), 'create_message', {}),
            ('INFO', f'Usuario {usuarios[1].nickName} inició sesión', str(usuarios[1].id), 'login', {}),
            ('WARNING', f'Intento de acceso no autorizado', None, 'unauthorized_access', {}),
            ('INFO', f'Usuario {usuarios[2].nickName} actualizó su perfil', str(usuarios[2].id), 'update_profile', {}),
            ('INFO', f'Mensaje privado leído por {usuarios[1].nickName}', str(usuarios[1].id), 'read_message', {}),
            ('ERROR', f'Error al procesar solicitud', str(usuarios[3].id), 'error', {'error_type': 'validation'}),
            ('INFO', f'Usuario {usuarios[4].nickName} siguió a {usuarios[5].nickName}', str(usuarios[4].id), 'follow_user', {'followed_id': str(usuarios[5].id)}),
            ('INFO', f'Usuario {usuarios[6].nickName} dejó de seguir a {usuarios[7].nickName}', str(usuarios[6].id), 'unfollow_user', {'unfollowed_id': str(usuarios[7].id)}),
            ('INFO', f'Mensaje eliminado por {usuarios[8].nickName}', str(usuarios[8].id), 'delete_message', {}),
            ('INFO', f'Usuario {usuarios[9].nickName} cambió su contraseña', str(usuarios[9].id), 'change_password', {}),
            ('WARNING', f'Múltiples intentos de login fallidos para {usuarios[10].nickName}', str(usuarios[10].id), 'failed_login', {'attempts': 3}),
            ('INFO', f'Sistema actualizado correctamente', None, 'system_update', {'version': '1.0.0'})
        ]
        
        for level, message, user_id, action, metadata in log_events:
            Log.log_event(
                level=level,
                message=message,
                user_id=user_id,
                action=action,
                metadata=metadata
            )
        print(f"✅ {len(log_events)} logs creados en logs_db")
        
        print("\n✅ Datos de prueba insertados correctamente")
        print("\n📊 Resumen:")
        print(f"   - Usuarios: {Usuario.objects.count()}")
        print(f"   - Etiquetas: {Etiqueta.objects.count()}")
        print(f"   - Mensajes públicos: {Mensaje.objects.count()}")
        print(f"   - Mensajes privados: {MensajePrivado.objects.count()}")
        print(f"   - Logs: {Log.objects.using('logs').count()}")
        
        return True
    except Exception as e:
        print(f"❌ Error insertando datos de prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Inicializar base de datos MongoDB')
    parser.add_argument('--with-sample-data', action='store_true', 
                       help='Insertar datos de prueba')
    args = parser.parse_args()
    
    print("🚀 Iniciando proceso de inicialización de base de datos...")
    print("=" * 60)
    
    # Conectar a la base de datos
    if not connect_db():
        sys.exit(1)
    
    # Crear colecciones e índices
    if not create_collections():
        sys.exit(1)
    
    # Insertar datos de prueba si se solicita
    if args.with_sample_data:
        if not insert_sample_data():
            # No desconectar aquí, dejar que Python lo maneje al finalizar
            sys.exit(1)
    else:
        print("\n💡 Para insertar datos de prueba, ejecuta:")
        print("   python init_db.py --with-sample-data")
    
    # No desconectar inmediatamente para asegurar que los datos se escriban
    # La conexión se cerrará automáticamente al finalizar el script
    print("\n" + "=" * 60)
    print("✅ Proceso completado exitosamente")
    print("🎉 La base de datos está lista para usar")

if __name__ == '__main__':
    main()
