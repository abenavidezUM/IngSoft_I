# Documentación de Base de Datos MongoDB

## 📊 Modelo de Dominio

Este documento describe el modelo de datos completo del sistema basado en MongoDB Atlas.

## 🗂️ Arquitectura de Datos

### Bases de Datos

El sistema utiliza **2 bases de datos** en MongoDB Atlas:

1. **main_db** - Base de datos principal
   - Usuarios
   - Mensajes públicos
   - Mensajes privados
   - Etiquetas
   - Menciones

2. **logs_db** - Base de datos de auditoría
   - Logs del sistema
   - Eventos de seguridad
   - Historial de acciones

## 📋 Colecciones

### 1. Usuarios (usuarios)

Almacena información de los usuarios del sistema.

**Campos:**

| Campo | Tipo | Obligatorio | Único | Descripción |
|-------|------|-------------|-------|-------------|
| _id | ObjectId | ✅ | ✅ | ID generado por MongoDB |
| nickName | String | ✅ | ✅ | Nombre de usuario (max 50) |
| nombre | String | ✅ | ❌ | Nombre real (max 100) |
| apellido | String | ✅ | ❌ | Apellido (max 100) |
| mail | String | ✅ | ✅ | Email (max 255) |
| contraseña | String | ✅ | ❌ | Contraseña hasheada (bcrypt) |
| biografia | String | ❌ | ❌ | Biografía del usuario (max 500) |
| fechaDeCreado | DateTime | ✅ | ❌ | Fecha de creación (auto) |
| fotoUsuario | String | ❌ | ❌ | URL de foto de perfil |
| fotoUsuarioPortada | String | ❌ | ❌ | URL de foto de portada |
| rol | String | ✅ | ❌ | Rol: admin/user/guest |

**Índices:**
- nickName (único)
- mail (único)
- fechaDeCreado (descendente)

**Ejemplo:**
```json
{
  "_id": ObjectId("..."),
  "nickName": "juanperez",
  "nombre": "Juan",
  "apellido": "Pérez",
  "mail": "juan@example.com",
  "contraseña": "$2b$12$...",
  "biografia": "Desarrollador Full Stack",
  "fechaDeCreado": ISODate("2026-01-31T10:00:00Z"),
  "fotoUsuario": "https://...",
  "fotoUsuarioPortada": "https://...",
  "rol": "user"
}
```

### 2. Etiquetas (etiquetas)

Almacena hashtags/etiquetas del sistema.

**Campos:**

| Campo | Tipo | Obligatorio | Único | Descripción |
|-------|------|-------------|-------|-------------|
| _id | ObjectId | ✅ | ✅ | ID generado por MongoDB |
| texto | String | ✅ | ✅ | Texto de la etiqueta (max 50, ej: #python) |

**Índices:**
- texto (único)

**Ejemplo:**
```json
{
  "_id": ObjectId("..."),
  "texto": "#python"
}
```

### 3. Menciones (menciones)

Almacena menciones a usuarios (@usuario).

**Campos:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| _id | ObjectId | ✅ | ID generado por MongoDB |
| usuario | ObjectId | ✅ | Referencia a Usuario |

**Índices:**
- usuario

**Ejemplo:**
```json
{
  "_id": ObjectId("..."),
  "usuario": ObjectId("user_id_123")
}
```

### 4. Mensajes (mensajes)

Almacena mensajes públicos (similar a tweets/posts).

**Campos:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| _id | ObjectId | ✅ | ID generado por MongoDB |
| texto | String | ✅ | Contenido del mensaje (max 500) |
| fechaDeCreado | DateTime | ✅ | Fecha de creación (auto) |
| autor | ObjectId | ✅ | Referencia a Usuario (autor) |
| etiquetas | Array[ObjectId] | ❌ | Array de referencias a Etiqueta (0..*) |
| menciones | Array[ObjectId] | ✅ | Array de referencias a Mencion (1..* - mínimo 1) |

**Restricciones:**
- ⚠️ **IMPORTANTE**: Un mensaje DEBE tener al menos 1 mención
- El autor es obligatorio
- Las etiquetas son opcionales (0 o más)

**Índices:**
- fechaDeCreado (descendente)
- autor
- etiquetas

**Ejemplo:**
```json
{
  "_id": ObjectId("..."),
  "texto": "¡Hola @mariagarcia! ¿Qué tal el proyecto? #python #mongodb",
  "fechaDeCreado": ISODate("2026-01-31T14:30:00Z"),
  "autor": ObjectId("user_id_123"),
  "etiquetas": [
    ObjectId("tag_id_456"),
    ObjectId("tag_id_789")
  ],
  "menciones": [
    ObjectId("mention_id_111")
  ]
}
```

### 5. Mensajes Privados (mensajes_privados)

Almacena mensajes privados entre usuarios (DM).

**Campos:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| _id | ObjectId | ✅ | ID generado por MongoDB |
| texto | String | ✅ | Contenido del mensaje (max 1000) |
| fechaDeCreado | DateTime | ✅ | Fecha de creación (auto) |
| emisor | ObjectId | ✅ | Referencia a Usuario (emisor) |
| receptor | ObjectId | ✅ | Referencia a Usuario (receptor) |
| leido | DateTime | ❌ | Fecha en que se leyó (null = no leído) |

**Índices:**
- fechaDeCreado (descendente)
- emisor
- receptor
- (emisor, receptor) - índice compuesto
- leido

**Ejemplo:**
```json
{
  "_id": ObjectId("..."),
  "texto": "Hola, ¿cómo estás?",
  "fechaDeCreado": ISODate("2026-01-31T15:00:00Z"),
  "emisor": ObjectId("user_id_123"),
  "receptor": ObjectId("user_id_456"),
  "leido": ISODate("2026-01-31T15:05:00Z")
}
```

### 6. Logs (logs) - Base de datos: logs_db

Almacena logs y eventos del sistema para auditoría.

**Campos:**

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| _id | ObjectId | ✅ | ID generado por MongoDB |
| level | String | ✅ | Nivel: DEBUG/INFO/WARNING/ERROR/CRITICAL |
| message | String | ✅ | Mensaje del log |
| timestamp | DateTime | ✅ | Fecha y hora del evento (auto) |
| user_id | String | ❌ | ID del usuario relacionado |
| action | String | ❌ | Acción realizada (login, create, delete, etc.) |
| ip_address | String | ❌ | IP del cliente |
| metadata | Object | ❌ | Datos adicionales en formato JSON |

**Índices:**
- timestamp (descendente)
- level
- user_id
- action

**Ejemplo:**
```json
{
  "_id": ObjectId("..."),
  "level": "INFO",
  "message": "Usuario inició sesión",
  "timestamp": ISODate("2026-01-31T10:00:00Z"),
  "user_id": "user_id_123",
  "action": "login",
  "ip_address": "192.168.1.100",
  "metadata": {
    "browser": "Chrome",
    "os": "Windows 11",
    "device": "Desktop"
  }
}
```

## 🔗 Relaciones

### Diagrama de Relaciones

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       │ autor (1)
       ├──────────────────────────> ┌─────────────┐
       │                             │   Mensaje   │
       │                             └──────┬──────┘
       │                                    │
       │                                    │ menciones (1..*)
       │                             ┌──────┴──────┐
       │                             │   Mencion   │
       │                             └──────┬──────┘
       │                                    │
       │ usuario (1)                        │ usuario (1)
       ├────────────────────────────────────┘
       │
       │ emisor (1)
       ├──────────────────────────> ┌──────────────────┐
       │                             │ MensajePrivado   │
       │ receptor (1)                └──────────────────┘
       └──────────────────────────>
       
       
┌─────────────┐
│  Mensaje    │
└──────┬──────┘
       │
       │ etiquetas (0..*)
       └──────────────────────────> ┌─────────────┐
                                     │  Etiqueta   │
                                     └─────────────┘
```

### Descripción de Relaciones

1. **Usuario → Mensaje**
   - Tipo: Uno a Muchos (1:N)
   - Un usuario puede crear múltiples mensajes
   - Cada mensaje tiene un autor (usuario)
   - Cascade: Si se elimina el usuario, se eliminan sus mensajes

2. **Mensaje → Mencion**
   - Tipo: Uno a Muchos (1:N)
   - Un mensaje puede tener múltiples menciones (mínimo 1)
   - Cada mención pertenece a un mensaje

3. **Mencion → Usuario**
   - Tipo: Muchos a Uno (N:1)
   - Una mención referencia a un usuario
   - Un usuario puede ser mencionado en múltiples mensajes

4. **Mensaje → Etiqueta**
   - Tipo: Muchos a Muchos (N:M)
   - Un mensaje puede tener múltiples etiquetas (0 o más)
   - Una etiqueta puede estar en múltiples mensajes

5. **Usuario → MensajePrivado**
   - Tipo: Uno a Muchos (1:N) - Emisor
   - Tipo: Uno a Muchos (1:N) - Receptor
   - Un usuario puede enviar/recibir múltiples mensajes privados
   - Cada mensaje privado tiene 2 usuarios: emisor y receptor
   - Cascade: Si se elimina el usuario, se eliminan sus mensajes privados

## 🔐 Seguridad

### Contraseñas

- **Hashing**: Werkzeug's generate_password_hash (bcrypt)
- **Salt**: Generado automáticamente
- **Nunca** se almacena la contraseña en texto plano
- **Nunca** se devuelve la contraseña en las respuestas de API

### Índices de Seguridad

- nickName y mail son únicos para prevenir duplicados
- Índices en campos de búsqueda frecuente para prevenir escaneos completos
- Índice compuesto en (emisor, receptor) para conversaciones privadas

### Validaciones

- Email válido (formato)
- NickName: 3-50 caracteres
- Contraseña: mínimo 8 caracteres (recomendado)
- Mensajes públicos: máximo 500 caracteres
- Mensajes privados: máximo 1000 caracteres
- Biografía: máximo 500 caracteres

## 🚀 Inicialización

### Crear la Base de Datos

```bash
# Crear estructura
python backend/init_db.py

# Crear estructura + datos de prueba
python backend/init_db.py --with-sample-data
```

### Datos de Prueba

El script crea:
- **3 usuarios** (juanperez, mariagarcia, admin)
- **3 etiquetas** (#python, #angular, #mongodb)
- **2 mensajes públicos** con menciones
- **2 mensajes privados**

Credenciales:
- Usuario: `juanperez` / `password123`
- Usuario: `mariagarcia` / `password123`
- Admin: `admin` / `admin123`

## 📈 Consultas Comunes

### 1. Obtener mensajes de un usuario

```python
mensajes = Mensaje.objects(autor=usuario).order_by('-fechaDeCreado')
```

### 2. Buscar mensajes con una etiqueta

```python
etiqueta = Etiqueta.objects(texto="#python").first()
mensajes = Mensaje.objects(etiquetas=etiqueta)
```

### 3. Obtener conversación entre dos usuarios

```python
from mongoengine import Q

conversacion = MensajePrivado.objects(
    Q(emisor=user1, receptor=user2) | Q(emisor=user2, receptor=user1)
).order_by('fechaDeCreado')
```

### 4. Mensajes no leídos de un usuario

```python
no_leidos = MensajePrivado.objects(
    receptor=usuario,
    leido=None
).count()
```

### 5. Usuarios mencionados en un mensaje

```python
mensaje = Mensaje.objects(id=mensaje_id).first()
usuarios_mencionados = [mencion.usuario for mencion in mensaje.menciones]
```

### 6. Mensajes con múltiples etiquetas

```python
mensajes = Mensaje.objects(
    etiquetas__all=[etiqueta1, etiqueta2]
)
```

## 🛠️ Mantenimiento

### Backup

```bash
# Backup de main_db
mongodump --uri="mongodb+srv://..." --db=main_db --out=./backup

# Backup de logs_db
mongodump --uri="mongodb+srv://..." --db=logs_db --out=./backup
```

### Restore

```bash
# Restore de main_db
mongorestore --uri="mongodb+srv://..." --db=main_db ./backup/main_db

# Restore de logs_db
mongorestore --uri="mongodb+srv://..." --db=logs_db ./backup/logs_db
```

### Recrear Índices

```python
# Dentro de Python
from models import Usuario, Mensaje, MensajePrivado, Etiqueta, Mencion

Usuario.ensure_indexes()
Mensaje.ensure_indexes()
MensajePrivado.ensure_indexes()
Etiqueta.ensure_indexes()
Mencion.ensure_indexes()
```

## 📊 Estadísticas

### Obtener contadores

```python
from models import Usuario, Mensaje, MensajePrivado, Etiqueta, Mencion

print(f"Usuarios: {Usuario.objects.count()}")
print(f"Mensajes: {Mensaje.objects.count()}")
print(f"Mensajes Privados: {MensajePrivado.objects.count()}")
print(f"Etiquetas: {Etiqueta.objects.count()}")
print(f"Menciones: {Mencion.objects.count()}")
```

## ⚠️ Consideraciones Importantes

1. **Mensajes requieren menciones**: Según el modelo, un mensaje público DEBE tener al menos 1 mención
2. **Dos usuarios en mensajes privados**: Siempre hay emisor y receptor
3. **Cascade delete**: Eliminar un usuario elimina sus mensajes y menciones
4. **Índices**: Importantes para rendimiento, especialmente en búsquedas por fecha
5. **Logs separados**: Base de datos separada para no afectar rendimiento de la aplicación principal

---

**Última actualización**: Enero 2026
