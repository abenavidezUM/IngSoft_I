# Backend - Flask API RESTful

## 📋 Descripción

Backend desarrollado en **Python 3.11** con **Flask** que proporciona una API RESTful sobre HTTPS. Se conecta a MongoDB Atlas con TLS/SSL habilitado y está preparado para desplegarse en Heroku.

## 🏗️ Arquitectura

### Stack Tecnológico

- **Lenguaje**: Python 3.11
- **Framework**: Flask
- **Base de Datos**: MongoDB Atlas (2 instancias)
  - Main Database: Base de datos principal
  - Logs Database: Base de datos de logs y auditoría
- **Autenticación**: JWT (JSON Web Tokens)
- **Hosting**: Heroku
- **Protocolo**: HTTPS con JSON

### Dependencias Principales

```python
Flask==3.0.0                    # Framework web
python-dotenv==1.0.0           # Gestión de variables de entorno
flask-restful==0.3.10          # API RESTful
mongoengine==0.28.0            # ODM para MongoDB
flask-jwt-extended==4.6.0      # Autenticación JWT
flask-mail==0.9.1              # Envío de emails
flask-cors==4.0.0              # CORS para comunicación con frontend
gunicorn==21.2.0               # Servidor WSGI para producción
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.11+
- pip
- MongoDB Atlas account
- Heroku CLI (para deployment)

### Instalación Local

1. **Clonar el repositorio y navegar al backend**:
```bash
cd backend
```

2. **Crear entorno virtual**:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
# MongoDB Atlas URIs con TLS/SSL
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/main_db?retryWrites=true&w=majority&tls=true
MONGODB_LOGS_URI=mongodb+srv://user:pass@cluster.mongodb.net/logs_db?retryWrites=true&w=majority&tls=true

# JWT Secret (generar uno seguro)
JWT_SECRET_KEY=tu-clave-super-secreta-aqui

# Configuración de Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-app-password
```

5. **Ejecutar la aplicación**:
```bash
python app.py
```

La API estará disponible en: `http://localhost:5000`

## � Modelo de Base de Datos

### Diagrama de Dominio

El sistema utiliza MongoDB con el siguiente modelo de datos:

#### Colecciones Principales

1. **Usuario**
   - `nickName` (String, único, requerido)
   - `nombre` (String, requerido)
   - `apellido` (String, requerido)
   - `mail` (String, único, requerido)
   - `contraseña` (String, hasheada, requerido)
   - `biografia` (String, opcional)
   - `fechaDeCreado` (DateTime, auto)
   - `fotoUsuario` (String, URL)
   - `fotoUsuarioPortada` (String, URL)
   - `rol` (String: admin/user/guest)

2. **Mensaje** (Mensajes públicos)
   - `texto` (String, max 500 caracteres)
   - `fechaDeCreado` (DateTime, auto)
   - `autor` (Referencia a Usuario) - **1 usuario**
   - `etiquetas` (Lista de referencias a Etiqueta) - **0..* etiquetas**
   - `menciones` (Lista de referencias a Mencion) - **1..* menciones (mínimo 1)**

3. **MensajePrivado** (Mensajes privados/DM)
   - `texto` (String, max 1000 caracteres)
   - `fechaDeCreado` (DateTime, auto)
   - `emisor` (Referencia a Usuario) - **Usuario 1**
   - `receptor` (Referencia a Usuario) - **Usuario 2**
   - `leido` (DateTime, opcional)

4. **Etiqueta** (Tags/Hashtags)
   - `texto` (String, único, ej: #python)

5. **Mencion** (Menciones @usuario)
   - `usuario` (Referencia a Usuario)

6. **Log** (Base de datos logs_db)
   - `level` (String: DEBUG/INFO/WARNING/ERROR/CRITICAL)
   - `message` (String)
   - `timestamp` (DateTime, auto)
   - `user_id` (String, opcional)
   - `action` (String, opcional)
   - `ip_address` (String, opcional)
   - `metadata` (Dict/JSON)

#### Relaciones

```
Usuario (1) ──── crea ───> (0..*) Mensaje
Usuario (1) ──── envía ──> (0..*) MensajePrivado (emisor)
Usuario (1) ──── recibe ─> (0..*) MensajePrivado (receptor)
Mensaje (1) ──── tiene ──> (0..*) Etiqueta
Mensaje (1) ──── tiene ──> (1..*) Mencion [mínimo 1]
Mencion (1) ──── refiere> (1) Usuario
```

#### Características del Modelo

- **Mensajes públicos** requieren al menos **1 mención** (@usuario)
- **Etiquetas** pueden estar en 0 o más mensajes
- **Mensajes privados** siempre tienen 2 usuarios (emisor y receptor)
- **Cascading delete**: Si se elimina un usuario, se eliminan sus mensajes
- **Índices**: Optimizados para búsquedas por fecha, usuario, etiquetas

### Inicialización de la Base de Datos

Para crear la estructura de la base de datos y opcionalmente insertar datos de prueba:

```bash
# Solo crear colecciones e índices
python init_db.py

# Crear estructura + datos de prueba
python init_db.py --with-sample-data
```

El script `init_db.py`:
1. ✅ Conecta a MongoDB Atlas
2. ✅ Crea todas las colecciones
3. ✅ Genera índices optimizados
4. ✅ Inserta datos de prueba (opcional)
5. ✅ Valida la estructura

### Datos de Prueba

Los datos de prueba incluyen:
- **3 usuarios**: juanperez, mariagarcia, admin
- **3 etiquetas**: #python, #angular, #mongodb
- **2 mensajes públicos** con menciones y etiquetas
- **2 mensajes privados** entre usuarios

Credenciales de prueba:
- Usuario: `juanperez` / Password: `password123`
- Usuario: `mariagarcia` / Password: `password123`
- Admin: `admin` / Password: `admin123`

## 🔒 MongoDB Atlas con TLS/SSL

### Configuración de Seguridad

El proyecto está configurado para conectarse a MongoDB Atlas usando:

- **TLS/SSL habilitado**: Todas las conexiones están cifradas
- **Autenticación**: Usuario y contraseña
- **IP Whitelist**: Configurar IPs permitidas en MongoDB Atlas
- **Dos bases de datos separadas**:
  - `main_db`: Datos de la aplicación (usuarios, mensajes, etiquetas, menciones)
  - `logs_db`: Logs y auditoría

### String de Conexión

```python
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=false
```

**Parámetros importantes**:
- `tls=true`: Habilita TLS/SSL
- `retryWrites=true`: Reintentos automáticos
- `w=majority`: Write concern para replicación
- `tlsAllowInvalidCertificates=false`: Validación estricta de certificados

## 📡 API Endpoints

### Caso de Uso: CU0010 - Envío de Mensajes Privados

#### 1. Enviar Mensaje Privado

**POST** `/api/mensajes-privados`

Crea un nuevo mensaje privado entre dos usuarios.

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
      "nickName": "juanperez"
    },
    "receptor": {
      "id": "user_id_456",
      "nickName": "mariagarcia"
    },
    "leido": null
  }
}
```

**Errores**:
- 400: Validación (mensaje vacío, muy largo, emisor == receptor)
- 401: No autenticado / token expirado
- 404: Receptor no encontrado
- 429: Rate limit excedido (máx 10 msg/minuto)

#### 2. Obtener Conversación

**GET** `/api/mensajes-privados/conversacion/:userId`

Obtiene los mensajes de una conversación específica.

**Query Parameters**:
- `limit`: Número de mensajes (default: 50)
- `offset`: Offset para paginación (default: 0)

**Response 200**:
```json
{
  "success": true,
  "data": {
    "conversacion": [...],
    "total": 15,
    "hasMore": false
  }
}
```

#### 3. Listar Conversaciones

**GET** `/api/mensajes-privados/conversaciones`

Lista todas las conversaciones del usuario actual.

**Response 200**:
```json
{
  "success": true,
  "data": [
    {
      "usuario": {...},
      "ultimoMensaje": {...},
      "mensajesNoLeidos": 3
    }
  ]
}
```

#### 4. Marcar como Leído

**PUT** `/api/mensajes-privados/:mensajeId/leer`

Marca un mensaje como leído.

#### 5. Contar No Leídos

**GET** `/api/mensajes-privados/no-leidos`

Retorna contador de mensajes no leídos.

#### 6. Eliminar Mensaje

**DELETE** `/api/mensajes-privados/:mensajeId`

Elimina un mensaje (solo el emisor).

Ver documentación completa: [CU0010_IMPLEMENTACION.md](../docs/CU0010/CU0010_IMPLEMENTACION.md)

### Autenticación
```
POST /api/auth/register    # Registro de usuario
POST /api/auth/login       # Login (devuelve JWT)
POST /api/auth/refresh     # Refrescar token
POST /api/auth/logout      # Cerrar sesión
```

### Health Check
```
GET /health               # Estado del servicio
```

### Server-Sent Events
```
GET /api/stream          # Conexión SSE para eventos en tiempo real
```

### Formato de Respuesta

Todas las respuestas son en formato JSON:

```json
{
  "success": true,
  "data": {},
  "message": "Operación exitosa"
}
```

En caso de error:

```json
{
  "success": false,
  "error": "Descripción del error",
  "code": "ERROR_CODE"
}
```

## 🔐 Autenticación JWT

### Implementación

```python
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Generar token
access_token = create_access_token(identity=user_id)

# Proteger endpoint
@app.route('/api/protected')
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return {'user': current_user}
```

### Headers requeridos

```http
Authorization: Bearer <token>
Content-Type: application/json
```

## 📧 Flask-Mail

### Configuración

El sistema está configurado para enviar emails usando SMTP (Gmail por defecto):

```python
from flask_mail import Message

msg = Message(
    'Asunto',
    recipients=['destinatario@email.com']
)
msg.body = 'Contenido del email'
mail.send(msg)
```

### Variables de entorno necesarias

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=app-password  # Usar App Password de Google
```

## 🌊 Server-Sent Events (SSE)

### Implementación

El backend soporta Server-Sent Events para comunicación en tiempo real unidireccional (servidor → cliente):

```python
@app.route('/api/stream')
def stream():
    def generate():
        while True:
            data = get_real_time_data()
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(1)
    
    return app.response_class(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )
```

## 🐳 Docker

### Construcción de imagen

```bash
docker build -t backend-flask .
```

### Ejecución local

```bash
docker run -p 5000:5000 --env-file .env backend-flask
```

### Docker Compose

Desde la raíz del proyecto:

```bash
docker-compose up backend
```

## 🚀 Deployment en Heroku

### Preparación

1. **Instalar Heroku CLI**:
```bash
# Windows
choco install heroku-cli

# Mac
brew tap heroku/brew && brew install heroku
```

2. **Login en Heroku**:
```bash
heroku login
```

3. **Crear aplicación**:
```bash
heroku create nombre-de-tu-app
```

### Configuración

4. **Configurar variables de entorno en Heroku**:
```bash
heroku config:set MONGODB_URI="tu-uri-de-mongodb"
heroku config:set MONGODB_LOGS_URI="tu-uri-de-logs"
heroku config:set JWT_SECRET_KEY="tu-jwt-secret"
heroku config:set MAIL_USERNAME="tu-email"
heroku config:set MAIL_PASSWORD="tu-password"
```

5. **Verificar configuración**:
```bash
heroku config
```

### Deployment

6. **Deploy**:
```bash
git push heroku main
```

7. **Verificar logs**:
```bash
heroku logs --tail
```

8. **Abrir aplicación**:
```bash
heroku open
```

### Estructura de archivos para Heroku

```
backend/
├── app.py              # Aplicación Flask
├── requirements.txt    # Dependencias Python
├── Procfile           # Comando para ejecutar en Heroku
├── runtime.txt        # Versión de Python (opcional)
└── .env               # Variables locales (no subir a git)
```

**Procfile**:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 4
```

## � Uso de Modelos

### Crear Usuario

```python
from models import Usuario

# Crear usuario
usuario = Usuario(
    nickName="johndoe",
    nombre="John",
    apellido="Doe",
    mail="john@example.com",
    biografia="Desarrollador Python"
)
usuario.set_password("securepassword")
usuario.save()

# Verificar contraseña
if usuario.check_password("securepassword"):
    print("Contraseña correcta")
```

### Crear Mensaje Público

```python
from models import Usuario, Mensaje, Etiqueta, Mencion

# Obtener usuarios
autor = Usuario.objects(nickName="johndoe").first()
mencionado = Usuario.objects(nickName="janedoe").first()

# Crear etiquetas
etiqueta = Etiqueta(texto="#python").save()

# Crear mención
mencion = Mencion(usuario=mencionado).save()

# Crear mensaje (requiere al menos 1 mención)
mensaje = Mensaje(
    texto="¡Hola @janedoe! ¿Qué tal? #python",
    autor=autor,
    etiquetas=[etiqueta],
    menciones=[mencion]  # Mínimo 1 mención
)
mensaje.save()
```

### Crear Mensaje Privado

```python
from models import Usuario, MensajePrivado

# Obtener usuarios
user1 = Usuario.objects(nickName="johndoe").first()
user2 = Usuario.objects(nickName="janedoe").first()

# Crear mensaje privado
mensaje_privado = MensajePrivado(
    texto="Hola, ¿cómo estás?",
    emisor=user1,
    receptor=user2
)
mensaje_privado.save()

# Marcar como leído
mensaje_privado.marcar_como_leido()
```

### Consultas

```python
# Buscar mensajes de un usuario
mensajes = Mensaje.objects(autor=usuario).order_by('-fechaDeCreado')

# Buscar mensajes con una etiqueta
etiqueta = Etiqueta.objects(texto="#python").first()
mensajes = Mensaje.objects(etiquetas=etiqueta)

# Buscar conversación entre dos usuarios
conversacion = MensajePrivado.objects(
    Q(emisor=user1, receptor=user2) | Q(emisor=user2, receptor=user1)
).order_by('fechaDeCreado')

# Mensajes no leídos
no_leidos = MensajePrivado.objects(receptor=usuario, leido=None)
```

### Logging

```python
from models import Log

# Crear log
Log.log_event(
    level='INFO',
    message='Usuario inició sesión',
    user_id=str(usuario.id),
    action='login',
    ip_address='192.168.1.1',
    metadata={'browser': 'Chrome', 'os': 'Windows'}
)
```

## 📁 Estructura del Proyecto

```
backend/
├── app.py                 # Aplicación principal
├── init_db.py            # Script de inicialización de BD
├── requirements.txt       # Dependencias
├── Dockerfile            # Configuración Docker
├── Procfile              # Configuración Heroku
├── .env.example          # Ejemplo de variables de entorno
├── .env                  # Variables de entorno (no versionar)
├── models/               # Modelos de MongoDB (MongoEngine)
│   ├── __init__.py
│   ├── usuario.py       # Modelo Usuario
│   ├── mensaje.py       # Modelo Mensaje (público)
│   ├── mensaje_privado.py  # Modelo MensajePrivado
│   ├── etiqueta.py      # Modelo Etiqueta (hashtag)
│   ├── mencion.py       # Modelo Mencion (@usuario)
│   └── log.py           # Modelo Log (logs_db)
├── routes/               # Rutas de la API
│   ├── __init__.py
│   ├── auth.py          # Rutas de autenticación
│   ├── usuarios.py      # CRUD usuarios
│   ├── mensajes.py      # CRUD mensajes públicos
│   └── mensajes_privados.py  # CRUD mensajes privados
├── services/             # Lógica de negocio
│   ├── __init__.py
│   ├── auth_service.py
│   └── email_service.py
├── middleware/           # Middlewares personalizados
│   ├── __init__.py
│   └── auth_middleware.py
├── utils/                # Utilidades
│   ├── __init__.py
│   ├── validators.py
│   └── helpers.py
└── tests/                # Tests unitarios
    ├── __init__.py
    ├── test_models.py   # Tests de modelos
    └── test_api.py      # Tests de API
```

## 🧪 Testing

### Ejecutar tests

```bash
# Todos los tests
pytest

# Con coverage
pytest --cov=. --cov-report=html

# Test específico
pytest tests/test_api.py::test_health_check
```

### Ejemplo de test

```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

## 📊 Logging

### Configuración

Los logs se guardan en MongoDB Atlas (base de datos `logs_db`):

```python
from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class Log(Document):
    meta = {'db_alias': 'logs'}
    
    level = StringField(required=True)
    message = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    user_id = StringField()
    
    def save_log(level, message, user_id=None):
        log = Log(level=level, message=message, user_id=user_id)
        log.save()
```

## 🔧 Desarrollo

### Activar modo desarrollo

```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows

python app.py
```

### Hot reload

Flask recargará automáticamente los cambios en modo desarrollo.

### Debugging

```python
import pdb

# Punto de interrupción
pdb.set_trace()
```

## 📚 Recursos Adicionales

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [MongoEngine Documentation](http://docs.mongoengine.org/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [Heroku Python Support](https://devcenter.heroku.com/categories/python-support)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

## ⚠️ Seguridad

### Checklist de Seguridad

- ✅ Usar HTTPS en producción
- ✅ Nunca commitear `.env` al repositorio
- ✅ Usar contraseñas fuertes para MongoDB
- ✅ Implementar rate limiting
- ✅ Validar todos los inputs
- ✅ Mantener dependencias actualizadas
- ✅ Configurar CORS apropiadamente
- ✅ Usar JWT con expiración corta
- ✅ Habilitar TLS/SSL en MongoDB

### Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/endpoint')
@limiter.limit("10 per minute")
def endpoint():
    return {'message': 'OK'}
```

## 🐛 Troubleshooting

### Error: Connection to MongoDB failed

**Solución**: Verificar que la IP esté en la whitelist de MongoDB Atlas y que las credenciales sean correctas.

### Error: Port already in use

**Solución**: Cambiar el puerto en `.env` o matar el proceso:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Error: Module not found

**Solución**: Reinstalar dependencias:
```bash
pip install -r requirements.txt --upgrade
```

## 📄 Licencia

Este proyecto es parte de un sistema de ingeniería de software educativo.

---

**Última actualización**: Enero 2026
