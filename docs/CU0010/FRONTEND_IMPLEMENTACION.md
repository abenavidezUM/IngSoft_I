# CU0010 - Implementación Frontend

## 📱 Componente Angular: Mensajes Privados

### Estructura de Archivos

```
frontend/src/app/
├── services/
│   └── mensajes-privados.service.ts    # Servicio de API
├── components/
│   └── mensaje-privado/
│       ├── mensaje-privado.component.ts
│       ├── mensaje-privado.component.html
│       └── mensaje-privado.component.css
└── models/
    └── mensaje.model.ts                # Interfaces TypeScript
```

## 🔧 Servicio: MensajesPrivadosService

### Funcionalidades

El servicio proporciona:

- ✅ **enviarMensaje**: Enviar mensaje privado
- ✅ **obtenerConversacion**: Cargar mensajes con paginación
- ✅ **listarConversaciones**: Obtener lista de conversaciones
- ✅ **marcarComoLeido**: Marcar mensaje como leído
- ✅ **contarNoLeidos**: Obtener contador de no leídos
- ✅ **eliminarMensaje**: Eliminar mensaje propio
- ✅ **buscarUsuarios**: Buscar usuarios por nickname
- ✅ **conectarSSE**: Conectar a Server-Sent Events para tiempo real

### Uso del Servicio

```typescript
import { MensajesPrivadosService } from './services/mensajes-privados.service';

constructor(private mensajesService: MensajesPrivadosService) {}

// Enviar mensaje
this.mensajesService.enviarMensaje(receptorId, texto).subscribe({
  next: (mensaje) => console.log('Mensaje enviado', mensaje),
  error: (error) => console.error('Error', error)
});

// Obtener conversación
this.mensajesService.obtenerConversacion(userId, 50, 0).subscribe({
  next: (data) => {
    this.mensajes = data.conversacion;
    this.hayMasMensajes = data.hasMore;
  }
});

// Suscribirse a nuevos mensajes (tiempo real)
this.mensajesService.nuevoMensaje$.subscribe(mensaje => {
  if (mensaje) {
    this.conversacionActual.push(mensaje);
  }
});

// Contador de no leídos
this.mensajesService.mensajesNoLeidos$.subscribe(count => {
  this.noLeidos = count;
});
```

## 🎨 Componente: MensajePrivadoComponent

### Estados de Vista

El componente maneja 2 vistas principales:

1. **Lista de Conversaciones**
   - Muestra todas las conversaciones del usuario
   - Badge con contador de mensajes no leídos
   - Búsqueda de usuarios para iniciar nueva conversación
   - Último mensaje y timestamp

2. **Conversación Individual**
   - Mensajes ordenados cronológicamente
   - Paginación infinita (scroll hacia arriba)
   - Formulario de envío con validación
   - Indicador de mensaje leído (✓✓)
   - Timestamps formatados relativos

### Características Implementadas

#### 1. Validación en Tiempo Real

```typescript
// Formulario reactivo con validadores
this.mensajeForm = this.fb.group({
  texto: ['', [
    Validators.required,
    Validators.maxLength(1000),
    Validators.minLength(1)
  ]]
});

// Deshabilitar botón si inválido
get puedeEnviar(): boolean {
  return this.mensajeForm.valid && 
         !this.enviandoMensaje && 
         !!this.usuarioSeleccionado;
}
```

#### 2. Búsqueda con Debounce

```typescript
// Esperar 300ms antes de buscar
this.searchForm.get('busqueda')?.valueChanges
  .pipe(
    debounceTime(300),
    distinctUntilChanged()
  )
  .subscribe(valor => {
    if (valor && valor.length >= 2) {
      this.buscarUsuarios(valor);
    }
  });
```

#### 3. Paginación Infinita

```typescript
// Cargar más mensajes al hacer scroll hacia arriba
cargarMasMensajes(): void {
  if (this.cargandoMensajes || !this.hayMasMensajes) return;
  
  this.paginaActual++;
  this.cargarMensajes();
}
```

#### 4. Optimistic UI

```typescript
// Mostrar mensaje inmediatamente antes de confirmación
enviarMensaje(): void {
  const texto = this.mensajeForm.get('texto')?.value;
  
  this.mensajesService.enviarMensaje(receptorId, texto).subscribe({
    next: (mensaje) => {
      // Agregar mensaje a la conversación
      this.conversacionActual.push(mensaje);
      this.scrollToBottom();
    }
  });
}
```

#### 5. Notificaciones en Tiempo Real

```typescript
// Conectar a Server-Sent Events
ngOnInit(): void {
  this.sseConnection = this.mensajesService.conectarSSE();
  
  // Suscribirse a nuevos mensajes
  this.mensajesService.nuevoMensaje$.subscribe(mensaje => {
    if (mensaje && this.esDeConversacionActual(mensaje)) {
      this.conversacionActual.push(mensaje);
      this.scrollToBottom();
    }
  });
}
```

#### 6. Contador de Caracteres

```html
<span class="contador">{{ longitudTexto }} / 1000</span>
```

#### 7. Scroll Automático

```typescript
private scrollToBottom(): void {
  setTimeout(() => {
    const element = this.mensajesContainer.nativeElement;
    element.scrollTop = element.scrollHeight;
  }, 100);
}
```

## 🎨 Estilos CSS

### Diseño Responsivo

- **Desktop**: Layout de 2 columnas (lista + conversación)
- **Mobile**: Vista única con navegación back
- **Tablet**: Vista optimizada

### Características Visuales

- **Burbujas de mensajes**: Estilo moderno tipo WhatsApp/Telegram
- **Avatares circulares**: Fotos de perfil
- **Badges de notificación**: Contador de mensajes no leídos
- **Estados de carga**: Spinners y skeletons
- **Animaciones**: Transiciones suaves
- **Modo oscuro**: Preparado para implementación futura

### Clases CSS Principales

```css
.mensaje-propio {
  justify-content: flex-end;
  background: #007bff;  /* Azul */
  color: white;
}

.mensaje-ajeno {
  justify-content: flex-start;
  background: white;
  color: #333;
}

.badge-no-leidos {
  background: #dc3545;  /* Rojo */
  position: absolute;
  border-radius: 50%;
}
```

## 🔒 Manejo de Errores

### Estrategia de Errores

```typescript
this.mensajesService.enviarMensaje(receptorId, texto).subscribe({
  next: (mensaje) => {
    // Éxito
    this.mostrarExito('Mensaje enviado');
  },
  error: (error) => {
    // Manejo de errores específicos
    if (error.code === 'AUTH_ERROR') {
      this.router.navigate(['/login']);
    } else if (error.code === 'RATE_LIMIT_EXCEEDED') {
      this.mostrarError('Demasiados mensajes. Espera un momento');
    } else if (error.code === 'USER_NOT_FOUND') {
      this.mostrarError('Usuario no encontrado');
    } else {
      this.mostrarError('Error al enviar mensaje');
    }
  }
});
```

### Mensajes de Error Amigables

- **Token expirado**: "Tu sesión ha expirado. Por favor inicia sesión nuevamente"
- **Rate limit**: "Demasiados mensajes. Espera un momento antes de continuar"
- **Usuario no encontrado**: "El usuario no existe o ha sido eliminado"
- **Error de red**: "Problemas de conexión. Verificando..."
- **Mensaje vacío**: "El mensaje no puede estar vacío"
- **Mensaje muy largo**: "El mensaje no puede exceder 1000 caracteres"

## 🔄 Estados de Carga

### Indicadores Visuales

```html
<!-- Loading conversaciones -->
<div *ngIf="cargandoConversaciones" class="loading">
  <div class="spinner"></div>
  <p>Cargando conversaciones...</p>
</div>

<!-- Loading mensajes -->
<div *ngIf="cargandoMensajes" class="loading">
  <div class="spinner"></div>
  <p>Cargando mensajes...</p>
</div>

<!-- Enviando mensaje -->
<button [disabled]="enviandoMensaje">
  {{ enviandoMensaje ? 'Enviando...' : 'Enviar' }}
</button>
```

### Estados Vacíos

```html
<!-- Sin conversaciones -->
<div *ngIf="conversaciones.length === 0" class="empty-state">
  <img src="assets/empty-chat.svg" alt="Sin conversaciones" />
  <h3>No tienes conversaciones</h3>
  <p>Busca un usuario para comenzar a chatear</p>
</div>

<!-- Sin mensajes en conversación -->
<div *ngIf="conversacionActual.length === 0" class="empty-state">
  <img src="assets/empty-messages.svg" alt="Sin mensajes" />
  <p>No hay mensajes en esta conversación</p>
  <p>¡Sé el primero en escribir!</p>
</div>
```

## 📱 Características Móviles

### Responsive Design

```css
@media (max-width: 768px) {
  /* Layout de columna única */
  .mensajes-privados-container {
    flex-direction: column;
  }
  
  /* Burbujas más anchas */
  .mensaje-content {
    max-width: 85%;
  }
  
  /* Header compacto */
  .header h2 {
    font-size: 1.25rem;
  }
  
  /* Botones más pequeños */
  .btn-nuevo {
    padding: 0.5rem 1rem;
  }
}
```

### Touch Gestures

- **Swipe izquierda/derecha**: Navegar entre conversaciones
- **Long press**: Opciones adicionales (eliminar, copiar)
- **Pull to refresh**: Actualizar lista de conversaciones
- **Tap fuera del teclado**: Cerrar teclado

## 🧪 Testing

### Unit Tests

```typescript
describe('MensajePrivadoComponent', () => {
  it('debe enviar mensaje correctamente', () => {
    component.mensajeForm.setValue({ texto: 'Hola' });
    component.usuarioSeleccionado = mockUsuario;
    
    component.enviarMensaje();
    
    expect(mensajesService.enviarMensaje).toHaveBeenCalled();
  });
  
  it('debe validar mensaje vacío', () => {
    component.mensajeForm.setValue({ texto: '' });
    
    expect(component.puedeEnviar).toBe(false);
  });
  
  it('debe cargar más mensajes al hacer scroll', () => {
    component.cargarMasMensajes();
    
    expect(component.paginaActual).toBe(1);
  });
});
```

## 🚀 Mejoras Futuras

### Funcionalidades Planificadas

- [ ] **Archivos adjuntos**: Enviar imágenes, documentos, videos
- [ ] **Mensajes de voz**: Grabación y reproducción
- [ ] **Indicador "escribiendo..."**: Mostrar cuando el otro usuario está escribiendo
- [ ] **Reacciones**: Emojis de reacción rápida
- [ ] **Mensajes destacados**: Pin de mensajes importantes
- [ ] **Búsqueda en conversaciones**: Buscar texto en mensajes
- [ ] **Modo oscuro**: Tema dark mode
- [ ] **Notificaciones push**: Web push notifications
- [ ] **Cifrado end-to-end**: Seguridad adicional
- [ ] **Mensajes temporales**: Auto-destrucción
- [ ] **Videollamadas**: Integración de video
- [ ] **GIFs y Stickers**: Biblioteca de stickers

### Optimizaciones

- [ ] **Virtual scrolling**: Para conversaciones muy largas
- [ ] **Service Worker**: Funcionar offline
- [ ] **IndexedDB**: Cache local de mensajes
- [ ] **WebSocket**: Reemplazar SSE para bidireccional
- [ ] **Lazy loading**: Cargar componentes bajo demanda
- [ ] **Image optimization**: Comprimir avatares y fotos
- [ ] **Typing indicators**: Mejor UX al escribir

## 📚 Recursos

- [Documentación completa del CU0010](CU0010_IMPLEMENTACION.md)
- [Backend README](../../backend/README.md)
- [Database Schema](../DATABASE.md)
- [Angular Reactive Forms](https://angular.io/guide/reactive-forms)
- [RxJS Operators](https://rxjs.dev/guide/operators)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

---

**Versión**: 1.0  
**Última actualización**: Enero 2026  
**Autor**: Equipo de Desarrollo Frontend
