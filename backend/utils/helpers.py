"""
Utilidades varias del backend
"""

from datetime import datetime
import re


def format_date(date, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Formatea una fecha
    
    Args:
        date: objeto datetime
        format_str: formato de salida
    
    Returns:
        string: fecha formateada
    """
    if not date:
        return None
    return date.strftime(format_str)


def parse_date(date_str, format_str='%Y-%m-%d'):
    """
    Parsea un string a fecha
    
    Args:
        date_str: string de fecha
        format_str: formato de entrada
    
    Returns:
        datetime: objeto datetime
    """
    try:
        return datetime.strptime(date_str, format_str)
    except:
        return None


def extract_mentions(text):
    """
    Extrae menciones (@usuario) de un texto
    
    Args:
        text: texto a procesar
    
    Returns:
        list: lista de nicknames mencionados
    """
    pattern = r'@([a-zA-Z0-9_]+)'
    mentions = re.findall(pattern, text)
    return list(set(mentions))  # Eliminar duplicados


def extract_hashtags(text):
    """
    Extrae hashtags (#tag) de un texto
    
    Args:
        text: texto a procesar
    
    Returns:
        list: lista de hashtags
    """
    pattern = r'#([a-zA-Z0-9_]+)'
    hashtags = re.findall(pattern, text)
    return [f'#{tag}' for tag in set(hashtags)]  # Eliminar duplicados


def truncate_text(text, max_length=100, suffix='...'):
    """
    Trunca un texto si excede la longitud máxima
    
    Args:
        text: texto a truncar
        max_length: longitud máxima
        suffix: sufijo a agregar si se trunca
    
    Returns:
        string: texto truncado
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def generate_slug(text):
    """
    Genera un slug a partir de un texto
    
    Args:
        text: texto fuente
    
    Returns:
        string: slug generado
    """
    # Convertir a minúsculas
    slug = text.lower()
    
    # Reemplazar espacios y caracteres especiales con guiones
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Eliminar guiones al inicio y final
    slug = slug.strip('-')
    
    return slug


def paginate_query(query, page=1, per_page=20):
    """
    Pagina un query de MongoEngine
    
    Args:
        query: query de MongoEngine
        page: número de página (empieza en 1)
        per_page: elementos por página
    
    Returns:
        dict: diccionario con datos paginados
    """
    total = query.count()
    items = query.skip((page - 1) * per_page).limit(per_page)
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': page * per_page < total
    }


def calculate_time_ago(date):
    """
    Calcula tiempo transcurrido desde una fecha
    
    Args:
        date: fecha a comparar
    
    Returns:
        string: representación legible del tiempo transcurrido
    """
    if not date:
        return "Desconocido"
    
    now = datetime.utcnow()
    diff = now - date
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Hace menos de un minuto"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"Hace {hours} hora{'s' if hours > 1 else ''}"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"Hace {days} día{'s' if days > 1 else ''}"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"Hace {weeks} semana{'s' if weeks > 1 else ''}"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"Hace {months} mes{'es' if months > 1 else ''}"
    else:
        years = int(seconds / 31536000)
        return f"Hace {years} año{'s' if years > 1 else ''}"
