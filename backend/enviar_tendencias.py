#!/usr/bin/env python3
"""
Script standalone para enviar emails de tendencias
CU0016 - Enviar Correo Automático de Tendencias

Este script puede ejecutarse manualmente o programarse con cron/scheduler.

Uso:
    python enviar_tendencias.py
    python enviar_tendencias.py --limit 5 --horas 48
"""

import sys
import os
import argparse

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, mail
from services.tendencias_service import (
    obtener_tendencias,
    generar_contenido_email,
    obtener_usuarios_para_envio
)
from services.email_service import (
    enviar_tendencias_masivo,
    validar_configuracion_email
)


def main():
    """Función principal del script"""
    
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description='Envía emails con las tendencias actuales a todos los usuarios'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Número de tendencias a incluir (default: 10)'
    )
    parser.add_argument(
        '--horas',
        type=int,
        default=24,
        help='Ventana de tiempo en horas para analizar (default: 24)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Modo de prueba: no envía emails reales'
    )
    
    args = parser.parse_args()
    
    # Ejecutar dentro del contexto de la aplicación Flask
    with app.app_context():
        print("=" * 60)
        print("🔥 Script de Envío de Tendencias")
        print("=" * 60)
        print()
        
        try:
            # Validar configuración de email
            if not args.test:
                print("🔍 Validando configuración de email...")
                config_valid, config_error = validar_configuracion_email()
                if not config_valid:
                    print(f"❌ Error: {config_error}")
                    print("\n💡 Sugerencia: Configura las variables de entorno:")
                    print("   - MAIL_SERVER")
                    print("   - MAIL_PORT")
                    print("   - MAIL_USERNAME")
                    print("   - MAIL_PASSWORD")
                    return 1
                print("✅ Configuración válida")
                print()
            else:
                print("⚠️ Modo de prueba activado - No se enviarán emails")
                print()
            
            # 1. Obtener tendencias
            print(f"📊 Paso 1/4: Obteniendo top {args.limit} tendencias de las últimas {args.horas} horas...")
            tendencias = obtener_tendencias(limit=args.limit, horas_atras=args.horas)
            
            if not tendencias:
                print("⚠️ No se encontraron tendencias")
                print("\n💡 Asegúrate de que haya:")
                print("   - Mensajes en la base de datos")
                print("   - Mensajes con etiquetas")
                print("   - Mensajes dentro de la ventana de tiempo especificada")
                return 0
            
            print(f"✅ {len(tendencias)} tendencias encontradas")
            print()
            
            # 2. Generar contenido HTML
            print("📝 Paso 2/4: Generando contenido del email...")
            contenido_html = generar_contenido_email(tendencias)
            print(f"✅ Email generado ({len(contenido_html)} caracteres)")
            print()
            
            # 3. Obtener usuarios
            print("👥 Paso 3/4: Obteniendo lista de usuarios...")
            usuarios = obtener_usuarios_para_envio()
            
            if not usuarios:
                print("⚠️ No se encontraron usuarios para enviar el email")
                print("\n💡 Asegúrate de que haya usuarios con email en la base de datos")
                return 0
            
            print(f"✅ {len(usuarios)} usuarios encontrados")
            print()
            
            # 4. Enviar emails
            if args.test:
                print("⚠️ Modo de prueba - Simulando envío...")
                print(f"   Se enviarían emails a {len(usuarios)} usuarios")
                print("\nPrimeros 5 destinatarios:")
                for i, usuario in enumerate(usuarios[:5], 1):
                    print(f"   {i}. {usuario['nickName']} <{usuario['email']}>")
                print("\n✅ Simulación completada")
                stats = {
                    'total': len(usuarios),
                    'exitosos': len(usuarios),
                    'fallidos': 0,
                    'errores': []
                }
            else:
                print("📧 Paso 4/4: Enviando emails...")
                stats = enviar_tendencias_masivo(mail, usuarios, contenido_html)
            
            print()
            print("=" * 60)
            print("📊 Resumen del Envío")
            print("=" * 60)
            print(f"Total de usuarios:    {stats['total']}")
            print(f"Emails enviados:      {stats['exitosos']}")
            print(f"Emails fallidos:      {stats['fallidos']}")
            
            if stats['errores']:
                print(f"\n⚠️ Errores encontrados ({len(stats['errores'])}):")
                for error in stats['errores'][:5]:  # Mostrar solo los primeros 5
                    print(f"   • {error}")
                if len(stats['errores']) > 5:
                    print(f"   ... y {len(stats['errores']) - 5} más")
            
            print()
            
            if stats['exitosos'] > 0:
                print("✅ Proceso completado exitosamente")
                return 0
            else:
                print("❌ No se pudo enviar ningún email")
                return 1
                
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == '__main__':
    sys.exit(main())
