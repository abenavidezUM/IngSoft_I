# Implementación CU0008 y CU0016

Documentación de la implementación de los casos de uso:
- **CU0008**: Borrar Mensajes Propios
- **CU0016**: Enviar Correo Automático de Tendencias

## 📋 Resumen de Implementación

### ✅ CU0008 - Borrar Mensajes Propios

#### Backend
- **Endpoint**: `DELETE /api/mensajes/<mensaje_id>`
- **Archivo**: `backend/routes/mensajes.py`
- **Servicio**: `backend/services/mensajes_service.py::borrar_mensaje()`
- **Tests**: `backend/tests/test_mensajes_route.py`

**Funcionalidad**:
1. Usuario autenticado puede borrar sus propios mensajes
2. Validación de que el usuario es el autor del mensaje
3. Respuestas HTTP adecuadas (200, 401, 403, 404)

#### Frontend
- **Servicio**: `frontend/src/app/services/mensajes.service.ts::borrarMensaje()`
- **Componente**: `frontend/src/app/components/mensajes-propios/`
- **Tests**: `frontend/src/app/components/mensajes-propios/mensajes-propios.component.spec.ts`

**Funcionalidad**:
1. Botón "Borrar" en cada mensaje
2. Confirmación con `window.confirm()`
3. Actualización automática de la vista tras borrado exitoso
4. Manejo de errores con alertas

### ✅ CU0016 - Enviar Correo Automático de Tendencias

#### Backend

**Servicios**:
- `backend/services/tendencias_service.py`
  - `obtener_tendencias()`: Analiza mensajes recientes y cuenta etiquetas
  - `generar_contenido_email()`: Genera HTML del email con las tendencias
  - `obtener_usuarios_para_envio()`: Obtiene usuarios con email válido

- `backend/services/email_service.py`
  - `enviar_email_tendencias()`: Envía email a un usuario
  - `enviar_tendencias_masivo()`: Envía emails a múltiples usuarios
  - `validar_configuracion_email()`: Valida configuración SMTP

**Endpoints**:
- `GET /api/tendencias`: Obtener tendencias actuales
- `POST /api/tendencias/enviar`: Enviar emails de tendencias

**Archivo**: `backend/routes/tendencias.py`

**Script Standalone**: `backend/enviar_tendencias.py`
- Ejecutar manualmente: `python enviar_tendencias.py`
- Con opciones: `python enviar_tendencias.py --limit 5 --horas 48`
- Modo prueba: `python enviar_tendencias.py --test`

**Tests**:
- `backend/tests/test_tendencias_service.py`
- `backend/tests/test_email_service.py`

## 🚀 Cómo Usar

### Configuración Inicial

1. **Instalar dependencias** (si aún no está hecho):
```bash
cd backend
pip install -r requirements.txt
```

2. **Configurar variables de entorno** (`.env`):
```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/main_db
MONGODB_LOGS_URI=mongodb://localhost:27017/logs_db

# JWT
JWT_SECRET_KEY=tu-clave-secreta-min-32-caracteres

# Email (para CU0016)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password
MAIL_DEFAULT_SENDER=noreply@app.com
```

3. **Inicializar base de datos con datos de prueba**:
```bash
cd backend
python init_db.py --with-sample-data
```

### Uso de CU0008 - Borrar Mensajes Propios

#### Backend API

**Borrar un mensaje**:
```bash
curl -X DELETE http://localhost:5000/api/mensajes/mensaje_id_123 \
  -H "Authorization: Bearer tu_token_jwt"
```

**Respuestas**:
- `200`: Mensaje borrado exitosamente
- `401`: Usuario no autenticado
- `403`: Usuario no es el autor del mensaje
- `404`: Mensaje no encontrado

#### Frontend

1. Iniciar sesión en la aplicación
2. Ir a "Mensajes propios"
3. Click en botón "Borrar" junto a un mensaje
4. Confirmar en el diálogo
5. El mensaje desaparece de la vista

### Uso de CU0016 - Enviar Correo Automático de Tendencias

#### Opción 1: Endpoint API

**Obtener tendencias actuales**:
```bash
curl http://localhost:5000/api/tendencias?limit=10&horas=24 \
  -H "Authorization: Bearer tu_token_jwt"
```

**Enviar emails de tendencias**:
```bash
curl -X POST http://localhost:5000/api/tendencias/enviar \
  -H "Authorization: Bearer tu_token_jwt"
```

#### Opción 2: Script Standalone (Recomendado para producción)

**Modo normal** (envía emails reales):
```bash
cd backend
python enviar_tendencias.py
```

**Modo prueba** (no envía emails):
```bash
python enviar_tendencias.py --test
```

**Con opciones personalizadas**:
```bash
python enviar_tendencias.py --limit 5 --horas 48
```

#### Programar con Cron (Linux/Mac)

Agregar a crontab para enviar diariamente a las 9 AM:
```bash
0 9 * * * cd /ruta/al/backend && python enviar_tendencias.py >> /var/log/tendencias.log 2>&1
```

## 🧪 Ejecutar Tests

### Backend

**Todos los tests**:
```bash
cd backend
pytest tests/ -v
```

**Solo tests de CU0008**:
```bash
pytest tests/test_mensajes_route.py -v -k "borrar"
```

**Solo tests de CU0016**:
```bash
pytest tests/test_tendencias_service.py tests/test_email_service.py -v
```

**Con cobertura**:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Frontend

```bash
cd frontend
npm test
```

## 📊 Datos de Prueba

El script `init_db.py --with-sample-data` crea:
- 12 usuarios con emails válidos
- 12 etiquetas (#python, #angular, #mongodb, etc.)
- 15 mensajes públicos con diferentes distribuciones de etiquetas
- 15 mensajes privados
- 15 logs del sistema

**Usuarios de prueba**:
- `juanperez` / `password123`
- `mariagarcia` / `password123`
- `admin` / `password123`

## 📁 Archivos Creados/Modificados

### Backend - Nuevos
```
backend/
├── services/
│   ├── tendencias_service.py      # CU0016: Lógica de tendencias
│   └── email_service.py            # CU0016: Servicio de emails
├── routes/
│   └── tendencias.py               # CU0016: Endpoints de tendencias
├── tests/
│   ├── test_tendencias_service.py # CU0016: Tests
│   └── test_email_service.py      # CU0016: Tests
└── enviar_tendencias.py            # CU0016: Script standalone
```

### Backend - Modificados
```
backend/
├── app.py                          # Registrar blueprint de tendencias
├── routes/mensajes.py              # CU0008: Agregar DELETE endpoint
├── services/mensajes_service.py    # CU0008: Agregar borrar_mensaje()
└── tests/test_mensajes_route.py   # CU0008: Agregar tests de borrado
```

### Frontend - Modificados
```
frontend/src/app/
├── components/mensajes-propios/
│   ├── mensajes-propios.component.ts    # CU0008: Lógica de borrado
│   ├── mensajes-propios.component.html  # CU0008: UI con botón borrar
│   ├── mensajes-propios.component.css   # CU0008: Estilos
│   └── mensajes-propios.component.spec.ts # CU0008: Tests
└── services/
    └── mensajes.service.ts              # CU0008: Método borrarMensaje()
```

## 🔐 Seguridad

### CU0008
- ✅ Autenticación JWT requerida
- ✅ Validación de autoría (usuario solo puede borrar sus mensajes)
- ✅ Manejo de errores apropiado

### CU0016
- ✅ Autenticación JWT requerida en endpoints
- ✅ Validación de configuración de email
- ✅ Manejo de errores en envío masivo
- ✅ Sanitización de contenido HTML

## 📈 Flujo de Datos CU0016

```
1. obtener_tendencias()
   ↓ Agregación MongoDB
   [Mensajes recientes] → [Contar etiquetas] → [Top N etiquetas]

2. generar_contenido_email()
   ↓ Formateo HTML
   [Tendencias] → [HTML con estilos]

3. obtener_usuarios_para_envio()
   ↓ Query MongoDB
   [Usuarios con email válido]

4. enviar_tendencias_masivo()
   ↓ Flask-Mail SMTP
   [Envío a cada usuario] → [Estadísticas]
```

## 🐛 Troubleshooting

### CU0008 - Borrar Mensajes

**Error 403 "No tienes permiso"**:
- Verificar que el usuario está intentando borrar su propio mensaje
- Revisar que el token JWT corresponde al autor del mensaje

**Error 404 "Mensaje no encontrado"**:
- Verificar que el ID del mensaje es correcto
- El mensaje puede haber sido borrado previamente

### CU0016 - Enviar Emails

**Error "Configuración de email incompleta"**:
```bash
# Verificar variables de entorno
echo $MAIL_SERVER
echo $MAIL_PORT
echo $MAIL_USERNAME
echo $MAIL_PASSWORD
```

**Emails no se envían (Gmail)**:
1. Habilitar "Acceso de aplicaciones menos seguras" (no recomendado)
2. O usar "App Passwords" (recomendado):
   - Ir a Google Account → Security
   - Habilitar 2-Step Verification
   - Crear App Password
   - Usar esa contraseña en `MAIL_PASSWORD`

**No hay tendencias**:
- Verificar que hay mensajes en la base de datos
- Verificar que los mensajes tienen etiquetas
- Ajustar la ventana de tiempo con `--horas`

## ✅ Checklist de Prueba

### CU0008
- [ ] Usuario puede ver sus mensajes propios
- [ ] Botón "Borrar" aparece en cada mensaje
- [ ] Click en "Borrar" muestra confirmación
- [ ] Confirmar borra el mensaje
- [ ] Cancelar mantiene el mensaje
- [ ] Mensaje desaparece de la vista tras borrado
- [ ] Usuario no puede borrar mensajes de otros
- [ ] Tests pasan correctamente

### CU0016
- [ ] Endpoint `/api/tendencias` retorna tendencias
- [ ] Tendencias ordenadas por frecuencia
- [ ] Script standalone ejecuta correctamente
- [ ] Modo `--test` no envía emails
- [ ] Emails se envían con formato HTML correcto
- [ ] Estadísticas muestran envíos exitosos/fallidos
- [ ] Manejo de errores en usuarios sin email
- [ ] Tests pasan correctamente

## 📞 Soporte

Para dudas o problemas:
1. Revisar logs del backend: `tail -f /var/log/tendencias.log`
2. Revisar logs de la aplicación Flask
3. Verificar configuración de MongoDB y email
4. Consultar tests para ejemplos de uso

---

**Versión**: 1.0  
**Fecha**: Febrero 2026  
**Autor**: Implementación de CU0008 y CU0016
