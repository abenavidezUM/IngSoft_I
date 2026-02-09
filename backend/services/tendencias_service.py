"""
Servicio de Tendencias
CU0016 - Enviar Correo Automático de Tendencias

Este servicio se encarga de:
1. Recopilar mensajes recientes
2. Identificar las etiquetas más utilizadas
3. Generar lista de tendencias
"""

from datetime import datetime, timedelta
from mongoengine.connection import get_db
from bson import ObjectId


def obtener_tendencias(limit=10, horas_atras=24):
    """
    Obtiene las etiquetas más populares basadas en mensajes recientes.
    
    Args:
        limit: Número máximo de tendencias a retornar (default: 10)
        horas_atras: Ventana de tiempo en horas para considerar mensajes (default: 24)
    
    Returns:
        list: Lista de diccionarios con formato:
              [{'etiqueta': '#python', 'texto': 'python', 'count': 15}, ...]
              Ordenado por count descendente
    """
    try:
        db = get_db('default')
        
        # Calcular fecha límite
        fecha_limite = datetime.utcnow() - timedelta(hours=horas_atras)
        
        print(f"📊 Analizando mensajes desde {fecha_limite.isoformat()}")
        
        # Agregación de MongoDB para contar etiquetas
        # Pipeline:
        # 1. Filtrar mensajes recientes
        # 2. Descomponer array de etiquetas
        # 3. Agrupar y contar por etiqueta
        # 4. Ordenar por frecuencia descendente
        # 5. Limitar resultados
        pipeline = [
            {
                '$match': {
                    'fechaDeCreado': {'$gte': fecha_limite},
                    'etiquetas': {'$exists': True, '$ne': []}
                }
            },
            {
                '$unwind': '$etiquetas'
            },
            {
                '$group': {
                    '_id': '$etiquetas',
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'count': -1}
            },
            {
                '$limit': limit
            }
        ]
        
        resultado = list(db.mensajes.aggregate(pipeline))
        
        print(f"✅ Agregación completada: {len(resultado)} tendencias encontradas")
        
        # Obtener información completa de las etiquetas
        tendencias = []
        for item in resultado:
            etiqueta_id = item['_id']
            count = item['count']
            
            # Buscar el texto de la etiqueta
            etiqueta_doc = db.etiquetas.find_one({'_id': etiqueta_id})
            
            if etiqueta_doc:
                tendencias.append({
                    'id': str(etiqueta_id),
                    'texto': etiqueta_doc.get('texto', ''),
                    'etiqueta': etiqueta_doc.get('texto', ''),
                    'count': count
                })
        
        print(f"📈 Tendencias procesadas:")
        for t in tendencias:
            print(f"  - {t['etiqueta']}: {t['count']} menciones")
        
        return tendencias
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error en obtener_tendencias: {e}")
        return []


def generar_contenido_email(tendencias):
    """
    Genera el contenido HTML del email con las tendencias.
    
    Args:
        tendencias: Lista de tendencias obtenida de obtener_tendencias()
    
    Returns:
        str: Contenido HTML formateado del email
    """
    if not tendencias:
        return """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #C81D25;">Temas del Momento</h2>
            <p>No hay tendencias disponibles en este momento.</p>
        </body>
        </html>
        """
    
    # Generar lista de tendencias en HTML
    items_html = ""
    for i, tendencia in enumerate(tendencias, 1):
        items_html += f"""
            <li style="margin-bottom: 15px; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
                <span style="font-weight: bold; color: #C81D25; font-size: 18px;">#{i}</span>
                <span style="font-size: 20px; font-weight: bold; color: #333; margin-left: 10px;">{tendencia['etiqueta']}</span>
                <span style="color: #666; margin-left: 10px;">({tendencia['count']} menciones)</span>
            </li>
        """
    
    # Fecha actual
    fecha_actual = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
                background-color: #ffffff;
            }}
            .header {{
                background-color: #C81D25;
                color: white;
                padding: 20px;
                border-radius: 5px;
                text-align: center;
            }}
            .content {{
                margin-top: 20px;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
                font-size: 12px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="margin: 0;">🔥 Temas del Momento</h1>
            <p style="margin: 5px 0 0 0;">Las tendencias más populares en nuestra red social</p>
        </div>
        
        <div class="content">
            <p>Estas son las etiquetas más utilizadas en las últimas 24 horas:</p>
            
            <ol style="padding-left: 20px;">
                {items_html}
            </ol>
            
            <p style="margin-top: 30px;">
                ¡Únete a la conversación y participa en los temas del momento!
            </p>
        </div>
        
        <div class="footer">
            <p>Generado el {fecha_actual}</p>
            <p>Este es un correo automático. Por favor no responder.</p>
        </div>
    </body>
    </html>
    """
    
    return html_content


def obtener_usuarios_para_envio():
    """
    Obtiene la lista de usuarios que deben recibir el email de tendencias.
    
    Por ahora retorna todos los usuarios que tienen email válido.
    Se puede extender para filtrar por preferencias, suscripciones, etc.
    
    Returns:
        list: Lista de diccionarios con formato:
              [{'id': 'user_id', 'email': 'user@example.com', 'nickName': 'username'}, ...]
    """
    try:
        db = get_db('default')
        
        # Buscar usuarios con email válido
        usuarios_cursor = db.usuarios.find(
            {'mail': {'$exists': True, '$ne': ''}},
            {'_id': 1, 'mail': 1, 'nickName': 1}
        )
        
        usuarios = []
        for user_doc in usuarios_cursor:
            usuarios.append({
                'id': str(user_doc['_id']),
                'email': user_doc.get('mail', ''),
                'nickName': user_doc.get('nickName', 'Usuario')
            })
        
        print(f"📧 {len(usuarios)} usuarios encontrados para envío de email")
        
        return usuarios
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error en obtener_usuarios_para_envio: {e}")
        return []
