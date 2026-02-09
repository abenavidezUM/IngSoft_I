# 🎨 Frontend - Angular 17+ Application

Aplicación web moderna desarrollada con Angular para el sistema de mensajería social.

## 🚀 Tecnologías

- **Framework**: Angular 17+
- **Lenguaje**: TypeScript 5.0+
- **Estilo**: CSS3 / SCSS
- **Estado**: RxJS / Observables
- **HTTP**: HttpClient
- **Formularios**: Reactive Forms
- **Routing**: Angular Router
- **Hosting**: Firebase Hosting
- **Pruebas**: Jasmine + Karma

## 🎯 Casos de Uso Implementados

### CU0010 - Envío de Mensajes Privados (Alta Complejidad)

**Descripción**: Sistema completo de mensajería privada entre usuarios.

**Componentes**:
- `MensajePrivadoComponent` - Componente principal
- `MensajesPrivadosService` - Servicio de API
- Ver documentación detallada: [CU0010_FRONTEND_IMPLEMENTACION.md](../docs/CU0010/FRONTEND_IMPLEMENTACION.md)

**Características**:
- ✅ Envío de mensajes privados
- ✅ Lista de conversaciones con últimos mensajes
- ✅ Visualización de conversaciones individuales
- ✅ Paginación infinita de mensajes
- ✅ Búsqueda de usuarios con debounce
- ✅ Contador de mensajes no leídos
- ✅ Notificaciones en tiempo real (SSE)
- ✅ Validación de formularios
- ✅ Optimistic UI
- ✅ Manejo de errores robusto
- ✅ Diseño responsivo

**Uso**:
```typescript
// Importar en módulo
import { MensajePrivadoComponent } from './components/mensaje-privado/mensaje-privado.component';
import { MensajesPrivadosService } from './services/mensajes-privados.service';

@NgModule({
  declarations: [MensajePrivadoComponent],
  providers: [MensajesPrivadosService]
})

// Ruta en app-routing.module.ts
{
  path: 'mensajes',
  component: MensajePrivadoComponent,
  canActivate: [AuthGuard]
}
```

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/          # Componentes reutilizables
│   │   │   ├── header/
│   │   │   ├── footer/
│   │   │   ├── mensaje-privado/  # CU0010: Mensajes privados
│   │   │   │   ├── mensaje-privado.component.ts
│   │   │   │   ├── mensaje-privado.component.html
│   │   │   │   └── mensaje-privado.component.css
│   │   │   └── ...
│   │   ├── pages/               # Páginas/Vistas
│   │   │   ├── home/
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   └── ...
│   │   ├── services/            # Servicios
│   │   │   ├── api.service.ts
│   │   │   ├── auth.service.ts
│   │   │   ├── websocket.service.ts
│   │   │   └── mensajes-privados.service.ts  # CU0010
│   │   ├── guards/              # Route Guards
│   │   │   └── auth.guard.ts
│   │   ├── interceptors/        # HTTP Interceptors
│   │   │   ├── auth.interceptor.ts
│   │   │   └── error.interceptor.ts
│   │   ├── models/              # Interfaces y Models
│   │   │   ├── user.model.ts
│   │   │   └── ...
│   │   ├── pipes/               # Pipes personalizados
│   │   ├── directives/          # Directivas personalizadas
│   │   ├── app-routing.module.ts
│   │   ├── app.component.ts
│   │   └── app.module.ts
│   ├── assets/                  # Recursos estáticos
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/
│   ├── environments/            # Configuraciones de entorno
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   ├── index.html
│   ├── main.ts
│   └── styles.css
├── angular.json
├── package.json
├── tsconfig.json
├── firebase.json
├── .firebaserc
└── Dockerfile
```

## 🔧 Configuración

### Variables de Entorno

#### Development (`src/environments/environment.ts`)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:5000/api',
  wsUrl: 'ws://localhost:5000',
  firebaseConfig: {
    apiKey: 'your-api-key',
    authDomain: 'your-app.firebaseapp.com',
    projectId: 'your-project-id',
    storageBucket: 'your-app.appspot.com',
    messagingSenderId: '123456789',
    appId: '1:123456789:web:abcdef'
  }
};
```

#### Production (`src/environments/environment.prod.ts`)
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-backend.herokuapp.com/api',
  wsUrl: 'wss://your-backend.herokuapp.com',
  firebaseConfig: {
    // Firebase production config
  }
};
```

## 🏃 Ejecutar el Proyecto

### Desarrollo Local

```bash
# Instalar dependencias
npm install

# Servir en modo desarrollo
ng serve

# Abrir en navegador
http://localhost:4200
```

### Build para Producción

```bash
# Build optimizado
ng build --configuration production

# Los archivos se generan en dist/
```

### Docker

```bash
# Build de la imagen
docker build -t frontend-app .

# Ejecutar contenedor
docker run -p 80:80 frontend-app
```

### Docker Compose (desde raíz del proyecto)

```bash
# Levantar todos los servicios
docker-compose up

# Solo frontend
docker-compose up frontend
```

## 📦 Dependencias Principales

```json
{
  "dependencies": {
    "@angular/core": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/router": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "rxjs": "^7.8.0",
    "zone.js": "~0.14.2"
  },
  "devDependencies": {
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "typescript": "~5.2.2"
  }
}
```

## 🔑 Autenticación

### AuthGuard

```typescript
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.isAuthenticated()) {
    return true;
  }
  
  router.navigate(['/login']);
  return false;
};
```

### Uso en Rutas

```typescript
const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { 
    path: 'mensajes', 
    component: MensajePrivadoComponent,
    canActivate: [authGuard]
  }
];
```

## 🔌 Servicios

### API Service (Base)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private apiUrl = environment.apiUrl;
  
  constructor(private http: HttpClient) {}
  
  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    });
  }
  
  get<T>(endpoint: string): Observable<T> {
    return this.http.get<T>(
      `${this.apiUrl}${endpoint}`,
      { headers: this.getHeaders() }
    );
  }
  
  post<T>(endpoint: string, data: any): Observable<T> {
    return this.http.post<T>(
      `${this.apiUrl}${endpoint}`,
      data,
      { headers: this.getHeaders() }
    );
  }
  
  put<T>(endpoint: string, data: any): Observable<T> {
    return this.http.put<T>(
      `${this.apiUrl}${endpoint}`,
      data,
      { headers: this.getHeaders() }
    );
  }
  
  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(
      `${this.apiUrl}${endpoint}`,
      { headers: this.getHeaders() }
    );
  }
}
```

### Auth Service

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../environments/environment';

interface LoginResponse {
  token: string;
  usuario: any;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<any>(null);
  public currentUser$ = this.currentUserSubject.asObservable();
  
  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadUserFromStorage();
  }
  
  login(email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `${this.apiUrl}/auth/login`,
      { email, password }
    ).pipe(
      tap(response => {
        localStorage.setItem('token', response.token);
        localStorage.setItem('user', JSON.stringify(response.usuario));
        this.currentUserSubject.next(response.usuario);
      })
    );
  }
  
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }
  
  isAuthenticated(): boolean {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    // Verificar si el token ha expirado
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp > Date.now() / 1000;
    } catch {
      return false;
    }
  }
  
  private loadUserFromStorage(): void {
    const user = localStorage.getItem('user');
    if (user) {
      this.currentUserSubject.next(JSON.parse(user));
    }
  }
  
  getToken(): string | null {
    return localStorage.getItem('token');
  }
  
  getCurrentUser(): any {
    return this.currentUserSubject.value;
  }
}
```

## 🔄 Interceptores

### Auth Interceptor

```typescript
import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();
  
  if (token) {
    const cloned = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    return next(cloned);
  }
  
  return next(req);
};
```

### Error Interceptor

```typescript
import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  
  return next(req).pipe(
    catchError(error => {
      if (error.status === 401) {
        // Token expirado o inválido
        localStorage.removeItem('token');
        router.navigate(['/login']);
      } else if (error.status === 403) {
        // Sin permisos
        console.error('Acceso denegado');
      } else if (error.status === 500) {
        // Error del servidor
        console.error('Error del servidor');
      }
      
      return throwError(() => error);
    })
  );
};
```

## 🎨 Estilos Globales

### Paleta de Colores

```css
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --info-color: #17a2b8;
  --light-color: #f8f9fa;
  --dark-color: #343a40;
}
```

### Tipografía

```css
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: #333;
}

h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  margin-bottom: 1rem;
}
```

## 📱 Responsive Design

### Breakpoints

```scss
// Móvil
@media (max-width: 576px) { }

// Tablet
@media (min-width: 577px) and (max-width: 768px) { }

// Desktop
@media (min-width: 769px) and (max-width: 992px) { }

// Desktop grande
@media (min-width: 993px) { }
```

## 🧪 Testing

### Unit Tests

```bash
# Ejecutar tests
ng test

# Con cobertura
ng test --code-coverage

# Ver reporte
open coverage/index.html
```

### E2E Tests

```bash
# Ejecutar tests end-to-end
ng e2e
```

## 🚀 Deployment

### Firebase Hosting

```bash
# Login en Firebase
firebase login

# Inicializar proyecto
firebase init hosting

# Build y deploy
ng build --configuration production
firebase deploy --only hosting
```

### GitHub Actions (CI/CD)

```yaml
name: Deploy to Firebase

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build
        run: ng build --configuration production
      
      - name: Deploy to Firebase
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: '${{ secrets.GITHUB_TOKEN }}'
          firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
          channelId: live
          projectId: your-project-id
```

## 📊 Performance

### Optimizaciones

- **Lazy Loading**: Carga módulos bajo demanda
- **OnPush Change Detection**: Reduce ciclos de detección
- **TrackBy**: Optimiza ngFor
- **Pure Pipes**: Pipes sin efectos secundarios
- **Ahead-of-Time (AOT)**: Compilación anticipada
- **Tree Shaking**: Elimina código no usado
- **Service Workers**: Cacheo offline

### Bundle Analyzer

```bash
# Analizar tamaño del bundle
npm run build -- --stats-json
npx webpack-bundle-analyzer dist/stats.json
```

## 🔒 Seguridad

### Buenas Prácticas

- ✅ **XSS Protection**: Angular sanitiza HTML automáticamente
- ✅ **CSRF Protection**: Tokens en cada petición
- ✅ **HTTPS Only**: Forzar conexiones seguras
- ✅ **Content Security Policy**: Políticas restrictivas
- ✅ **JWT Storage**: Tokens en localStorage (considerar httpOnly cookies)
- ✅ **Input Validation**: Validación en cliente y servidor
- ✅ **Rate Limiting**: Límite de peticiones

## 📚 Recursos

- [Angular Documentation](https://angular.io/docs)
- [RxJS Documentation](https://rxjs.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Firebase Hosting](https://firebase.google.com/docs/hosting)
- [Backend API Documentation](../backend/README.md)
- [Database Schema](../docs/DATABASE.md)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

**Versión**: 1.0  
**Última actualización**: Enero 2026
