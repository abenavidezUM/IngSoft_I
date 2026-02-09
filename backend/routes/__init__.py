"""
Rutas para el paquete routes
"""

from .mensajes_privados import mensajes_privados_bp
from .mensajes import mensajes_bp
from .seguidores import seguidores_bp

__all__ = ['mensajes_privados_bp', 'mensajes_bp', 'seguidores_bp']
