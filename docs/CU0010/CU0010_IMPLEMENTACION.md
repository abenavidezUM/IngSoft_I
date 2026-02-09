# CU0010 - Envío de Mensajes Privados

## 📋 Descripción del Caso de Uso

**ID**: CU0010  
**Nombre**: Enviar Mensajes Privados  
**Actores**: Usuario autenticado  
**Complejidad**: Alta  
**Prioridad**: Alta  

### Objetivo

Permitir a los usuarios enviar mensajes privados (DM - Direct Messages) a otros usuarios del sistema, estableciendo conversaciones privadas uno-a-uno.

### Precondiciones

1. El usuario debe estar autenticado en el sistema
2. El usuario debe tener un token JWT válido
3. El usuario receptor debe existir en el sistema
4. El emisor y receptor deben ser usuarios diferentes

### Postcondiciones

1. El mensaje privado se almacena en la base de datos
2. El mensaje aparece en la conversación entre ambos usuarios
3. El receptor puede ver el mensaje no leído
4. Se genera un log del evento

## 🔄 Flujo Principal

### 1. Usuario Selecciona Receptor

```
Usuario → Frontend: Selecciona usuario destinatario
Frontend → Backend: GET /api/usuarios?search=nickname
Backend → MongoDB: Busca usuarios
MongoDB → Backend: Retorna lista de usuarios
Backend → Frontend: Lista de usuarios encontrados
Frontend → Usuario: Muestra usuarios disponibles
```

### 2. Usuario Escribe Mensaje

```
Usuario → Frontend: Escribe mensaje en el campo de texto
Frontend: Valida mensaje (no vacío, max 1000 caracteres)
```

### 3. Envío del Mensaje

```
Usuario → Frontend: Click en "Enviar"
Frontend → Backend: POST /api/mensajes-privados
                     Headers: { Authorization: "Bearer <token>" }
                     Body: { 
                       receptor_id: "user_id",
                       texto: "mensaje"
                     }
Backend: Valida JWT
Backend: Valida datos de entrada
Backend: Verifica que emisor != receptor
Backend → MongoDB: Inserta MensajePrivado
MongoDB → Backend: Confirmación
Backend → Logs DB: Registra evento
Backend → Frontend: { success: true, mensaje: {...} }
Frontend → Usuario: Muestra mensaje enviado
Frontend: Actualiza conversación en tiempo real
```

### 4. Notificación en Tiempo Real (Opcional con SSE/WebSocket)

```
Backend → EventStream: Emite evento "nuevo_mensaje_privado"
Frontend (Receptor): Recibe evento
Frontend (Receptor): Actualiza conversación
Frontend (Receptor): Muestra notificación/badge
```

## 🚨 Flujos Alternativos

### A1: Usuario no autenticado

```
Usuario → Frontend: Intenta enviar mensaje sin login
Frontend → Login: Redirige a página de login
```

### A2: Token JWT expirado

```
Frontend → Backend: POST /api/mensajes-privados (token expirado)
Backend → Frontend: { error: "Token expirado", code: 401 }
Frontend → Usuario: Muestra mensaje de sesión expirada
Frontend → Login: Redirige a re-autenticación
```

### A3: Usuario receptor no existe

```
Frontend → Backend: POST /api/mensajes-privados (receptor inválido)
Backend → MongoDB: Busca receptor
MongoDB → Backend: No encontrado
Backend → Frontend: { error: "Usuario no encontrado", code: 404 }
Frontend → Usuario: Muestra error "Usuario no encontrado"
```

### A4: Mensaje vacío o muy largo

```
Usuario → Frontend: Intenta enviar mensaje vacío
Frontend: Validación en tiempo real
Frontend → Usuario: Deshabilita botón "Enviar"
Frontend → Usuario: Muestra mensaje de error
```

### A5: Emisor y receptor son el mismo

```
Frontend → Backend: POST con emisor == receptor
Backend: Valida emisor != receptor
Backend → Frontend: { error: "No puedes enviarte mensajes a ti mismo", code: 400 }
Frontend → Usuario: Muestra error
```

### A6: Error de red

```
Frontend → Backend: POST (falla conexión)
Backend: No responde
Frontend: Timeout después de 30s
Frontend → Usuario: "Error de conexión. Reintentando..."
Frontend: Reintenta envío (máximo 3 intentos)
```

## 📊 Diagrama de Secuencia

Ver archivo: `CU0010_-_Diagrama_De_Secuencia.png`

```
Usuario  Frontend  Backend  MongoDB  LogsDB
  |        |         |        |        |
  |--1---->|         |        |        |  Selecciona receptor
  |        |---2---->|        |        |  GET /api/usuarios?search=
  |        |         |---3--->|        |  Query usuarios
  |        |         |<--4----|        |  Resultados
  |        |<--5-----|        |        |  Lista usuarios
  |        |         |        |        |
  |--6---->|         |        |        |  Escribe mensaje
  |        |         |        |        |
  |--7---->|         |        |        |  Click "Enviar"
  |        |---8---->|        |        |  POST /api/mensajes-privados
  |        |         |---9--->|        |  Valida JWT
  |        |         |--10--->|        |  Insert mensaje
  |        |         |<--11---|        |  Confirmación
  |        |         |--12--->|        |  Log evento
  |        |         |<--13---|        |
  |        |<--14----|        |        |  Mensaje creado
  |<--15---|         |        |        |  Muestra mensaje
```

## 🔐 Seguridad

### Autenticación

- **JWT Token**: Requerido en header `Authorization: Bearer <token>`
- **Validación**: El backend valida que el emisor del JWT coincida con el emisor del mensaje
- **Expiración**: Tokens expiran después de 1 hora (configurable)

### Autorización

- Solo el emisor puede enviar mensajes en su nombre
- No se permite enviar mensajes como otro usuario
- Validación de permisos a nivel de backend

### Validación de Datos

**Frontend:**
- Mensaje no vacío
- Longitud máxima: 1000 caracteres
- Receptor seleccionado
- Emisor != receptor

**Backend:**
- JWT válido
- Emisor existe y está autenticado
- Receptor existe
- Emisor != receptor
- Longitud del texto: 1-1000 caracteres
- Sanitización de HTML/XSS

### Prevención de Ataques

- **XSS**: Sanitización de inputs
- **SQL Injection**: No aplica (MongoDB con ODM)
- **Rate Limiting**: Máximo 10 mensajes por minuto por usuario
- **Spam**: Validación de contenido y frecuencia
- **CSRF**: Tokens en headers (no cookies)

## 📡 API Endpoints

### 1. Buscar Usuarios

**Endpoint**: `GET /api/usuarios`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters**:
```
search: string (nickname o nombre)
limit: number (default: 10)
```

**Response 200**:
```json
{
  "success": true,
  "data": [
    {
      "id": "user_id_123",
      "nickName": "juanperez",
      "nombre": "Juan",
      "apellido": "Pérez",
      "fotoUsuario": "https://..."
    }
  ]
}
```

### 2. Crear Mensaje Privado

**Endpoint**: `POST /api/mensajes-privados`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "receptor_id": "user_id_456",
  "texto": "Hola, ¿cómo estás?"
}
```

**Response 201**:
```json
{
  "success": true,
  "data": {
    "id": "mensaje_id_789",
    "texto": "Hola, ¿cómo estás?",
    "fechaDeCreado": "2026-01-31T15:30:00Z",
    "emisor": {
      "id": "user_id_123",
      "nickName": "juanperez",
      "fotoUsuario": "https://..."
    },
    "receptor": {
      "id": "user_id_456",
      "nickName": "mariagarcia",
      "fotoUsuario": "https://..."
    },
    "leido": null
  }
}
```

**Response 400** (Validación):
```json
{
  "success": false,
  "error": "El mensaje no puede estar vacío",
  "code": "VALIDATION_ERROR"
}
```

**Response 401** (No autenticado):
```json
{
  "success": false,
  "error": "Token inválido o expirado",
  "code": "AUTH_ERROR"
}
```

**Response 404** (Receptor no existe):
```json
{
  "success": false,
  "error": "Usuario receptor no encontrado",
  "code": "USER_NOT_FOUND"
}
```

**Response 429** (Rate limit):
```json
{
  "success": false,
  "error": "Demasiados mensajes. Intenta nuevamente en 1 minuto",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

### 3. Obtener Conversación

**Endpoint**: `GET /api/mensajes-privados/conversacion/:userId`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters**:
```
limit: number (default: 50)
offset: number (default: 0)
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "conversacion": [
      {
        "id": "msg_1",
        "texto": "Hola",
        "fechaDeCreado": "2026-01-31T10:00:00Z",
        "emisor": { "id": "user_1", "nickName": "juan" },
        "receptor": { "id": "user_2", "nickName": "maria" },
        "leido": "2026-01-31T10:05:00Z"
      }
    ],
    "total": 15,
    "hasMore": false
  }
}
```

### 4. Marcar como Leído

**Endpoint**: `PUT /api/mensajes-privados/:mensajeId/leer`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response 200**:
```json
{
  "success": true,
  "data": {
    "id": "mensaje_id",
    "leido": "2026-01-31T15:35:00Z"
  }
}
```

### 5. Obtener Conversaciones Recientes

**Endpoint**: `GET /api/mensajes-privados/conversaciones`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Response 200**:
```json
{
  "success": true,
  "data": [
    {
      "usuario": {
        "id": "user_2",
        "nickName": "maria",
        "fotoUsuario": "https://..."
      },
      "ultimoMensaje": {
        "texto": "Hola, ¿cómo estás?",
        "fechaDeCreado": "2026-01-31T15:00:00Z",
        "leido": null
      },
      "mensajesNoLeidos": 3
    }
  ]
}
```

## 🔔 Notificaciones en Tiempo Real

### Server-Sent Events (SSE)

**Endpoint**: `GET /api/stream/mensajes-privados`

**Headers**:
```
Authorization: Bearer <jwt_token>
```

**Event Stream**:
```
event: nuevo_mensaje_privado
data: {"mensajeId": "msg_123", "emisorId": "user_456", "texto": "Hola"}

event: mensaje_leido
data: {"mensajeId": "msg_123", "leyenteFechaDeCreado": "2026-01-31T15:35:00Z"}
```

### WebSocket (Alternativa)

**Conexión**: `wss://backend.com/ws`

**Eventos**:
```javascript
// Cliente envía
{
  "event": "subscribe",
  "channel": "mensajes_privados",
  "userId": "user_123"
}

// Servidor envía
{
  "event": "nuevo_mensaje_privado",
  "data": {
    "mensajeId": "msg_123",
    "emisor": {...},
    "texto": "Hola"
  }
}
```

## 🧪 Casos de Prueba

### Pruebas Funcionales

1. **CP01**: Enviar mensaje privado exitoso
2. **CP02**: Enviar mensaje a usuario inexistente (error 404)
3. **CP03**: Enviar mensaje sin autenticación (error 401)
4. **CP04**: Enviar mensaje vacío (error 400)
5. **CP05**: Enviar mensaje demasiado largo (error 400)
6. **CP06**: Intentar enviarse mensaje a sí mismo (error 400)
7. **CP07**: Ver conversación con otro usuario
8. **CP08**: Marcar mensaje como leído
9. **CP09**: Ver conversaciones recientes
10. **CP10**: Recibir notificación en tiempo real

### Pruebas de Seguridad

1. **SP01**: Intentar enviar mensaje con token expirado
2. **SP02**: Intentar enviar mensaje como otro usuario
3. **SP03**: Inyección XSS en el texto del mensaje
4. **SP04**: Rate limiting (exceder límite de mensajes)
5. **SP05**: Acceder a conversación de otros usuarios

### Pruebas de Rendimiento

1. **PP01**: Enviar 100 mensajes consecutivos
2. **PP02**: Cargar conversación con 1000 mensajes
3. **PP03**: 50 usuarios enviando mensajes simultáneamente

## 📊 Métricas

### KPIs

- **Tiempo de respuesta**: < 200ms para envío de mensaje
- **Disponibilidad**: 99.9%
- **Tasa de error**: < 1%
- **Mensajes por segundo**: Soportar 100 msg/s

### Monitoreo

```python
# Logs a monitorear
- Mensajes enviados por usuario
- Tiempo de respuesta promedio
- Errores de validación
- Errores de autenticación
- Rate limiting activaciones
```

## 🔧 Configuración

### Variables de Entorno

```env
# Rate Limiting
MESSAGES_RATE_LIMIT=10  # mensajes por minuto
MESSAGES_RATE_WINDOW=60  # ventana en segundos

# Validación
MAX_MESSAGE_LENGTH=1000
MIN_MESSAGE_LENGTH=1

# Notificaciones
ENABLE_SSE=true
ENABLE_WEBSOCKET=true
```

## 📝 Notas de Implementación

### Backend

1. Validar JWT en cada request
2. Implementar rate limiting con Redis (opcional) o en memoria
3. Sanitizar inputs para prevenir XSS
4. Indexar campos para búsquedas rápidas
5. Implementar logging para auditoría

### Frontend

1. Validación en tiempo real del formulario
2. Debounce en búsqueda de usuarios (300ms)
3. Paginación infinita en conversaciones
4. Optimistic UI: mostrar mensaje antes de confirmación
5. Reconexión automática en caso de pérdida de conexión
6. Cache local de conversaciones recientes

## 🚀 Mejoras Futuras

- [ ] Mensajes con archivos adjuntos
- [ ] Mensajes con imágenes/GIFs
- [ ] Indicador "escribiendo..."
- [ ] Mensajes de voz
- [ ] Reacciones a mensajes
- [ ] Búsqueda en conversaciones
- [ ] Archivar conversaciones
- [ ] Bloquear usuarios
- [ ] Eliminar mensajes
- [ ] Mensajes temporales (auto-destrucción)

---

**Versión**: 1.0  
**Última actualización**: Enero 2026  
**Responsable**: Equipo de Desarrollo
