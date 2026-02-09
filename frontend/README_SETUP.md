# Guía para Probar la Interfaz

## Prerrequisitos

1. **Node.js y npm** instalados (versión 18 o superior)
2. **Backend Flask corriendo** en `http://localhost:5000`

## Pasos para Ejecutar el Frontend

### 1. Instalar Dependencias

```powershell
cd frontend
npm install
```

### 2. Iniciar el Backend (si no está corriendo)

En otra terminal:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```

El backend debe estar corriendo en `http://localhost:5000`

### 3. Iniciar el Frontend

```powershell
cd frontend
npm start
```

O alternativamente:

```powershell
ng serve
```

### 4. Abrir en el Navegador

Abre tu navegador y ve a:
```
http://localhost:4200
```

## Estructura de la Aplicación

La aplicación tiene 3 módulos principales accesibles desde el menú:

1. **Mensajes Propios** - Ver tus mensajes públicos
2. **Seguidores** - Ver tus seguidores
3. **Mensajes Privados** - Enviar y recibir mensajes privados

## Nota sobre Autenticación

Actualmente la aplicación no tiene implementado el sistema de login. Para probar los endpoints que requieren autenticación, necesitarás:

1. Implementar un componente de login, o
2. Usar herramientas como Postman para probar los endpoints directamente con tokens JWT

## Solución de Problemas

### Error: "Cannot find module '@angular/core'"
- Ejecuta `npm install` en el directorio frontend

### Error: "Port 4200 is already in use"
- Cambia el puerto: `ng serve --port 4201`

### Error de conexión con el backend
- Verifica que el backend esté corriendo en `http://localhost:5000`
- Revisa `src/environments/environment.ts` para confirmar la URL del API

