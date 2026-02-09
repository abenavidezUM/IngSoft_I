import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

import { 
  MensajesPrivadosService, 
  MensajePrivado, 
  Usuario 
} from '../../services/mensajes-privados.service';

@Component({
  selector: 'app-mensaje-privado',
  templateUrl: './mensaje-privado.component.html',
  styleUrls: ['./mensaje-privado.component.css']
})
export class MensajePrivadoComponent implements OnInit, OnDestroy {
  @ViewChild('mensajesContainer') private mensajesContainer!: ElementRef;
  @ViewChild('searchInput') private searchInput!: ElementRef;

  // Estado de la vista
  vistaActual: 'lista' | 'conversacion' = 'lista';
  currentUserId = '';
  
  // Conversaciones
  conversaciones: any[] = [];
  conversacionActual: MensajePrivado[] = [];
  usuarioSeleccionado: Usuario | null = null;
  
  // Formularios
  mensajeForm: FormGroup;
  searchForm: FormGroup;
  
  // Búsqueda de usuarios
  usuariosBuscados: Usuario[] = [];
  buscandoUsuarios = false;
  
  // Estados de carga
  cargandoConversaciones = false;
  cargandoMensajes = false;
  enviandoMensaje = false;
  
  // Paginación
  paginaActual = 0;
  hayMasMensajes = false;
  readonly MENSAJES_POR_PAGINA = 50;
  
  // Subscripciones
  private subscriptions: Subscription[] = [];
  private sseConnection: EventSource | null = null;

  constructor(
    private mensajesService: MensajesPrivadosService,
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // Formulario de mensaje
    this.mensajeForm = this.fb.group({
      texto: ['', [
        Validators.required,
        Validators.maxLength(1000),
        Validators.minLength(1)
      ]]
    });

    // Formulario de búsqueda
    this.searchForm = this.fb.group({
      busqueda: ['', [Validators.minLength(2)]]
    });
  }

  ngOnInit(): void {
    this.cargarUsuarioActual();
    // Cargar lista de conversaciones
    this.cargarConversaciones();

    // Configurar búsqueda con debounce
    const searchSub = this.searchForm.get('busqueda')?.valueChanges
      .pipe(
        debounceTime(300),
        distinctUntilChanged()
      )
      .subscribe(valor => {
        if (valor && valor.length >= 2) {
          this.buscarUsuarios(valor);
        } else {
          this.usuariosBuscados = [];
        }
      });
    
    if (searchSub) {
      this.subscriptions.push(searchSub);
    }

    // Suscribirse a nuevos mensajes
    const nuevoMensajeSub = this.mensajesService.nuevoMensaje$.subscribe(mensaje => {
      if (mensaje && this.usuarioSeleccionado) {
        // Si el mensaje es de/para el usuario actual, agregarlo a la conversación
        const esDelUsuario = mensaje.emisor.id === this.usuarioSeleccionado.id;
        const esParaElUsuario = mensaje.receptor.id === this.usuarioSeleccionado.id;
        
        if (esDelUsuario || esParaElUsuario) {
          this.conversacionActual.push(mensaje);
          this.scrollToBottom();
        }
      }
    });
    this.subscriptions.push(nuevoMensajeSub);

    // Conectar a SSE para notificaciones en tiempo real
    this.sseConnection = this.mensajesService.conectarSSE();

    // Verificar si hay un usuario en la ruta (para abrir conversación directa)
    const userId = this.route.snapshot.paramMap.get('userId');
    if (userId) {
      // TODO: Cargar usuario y abrir conversación
    }
  }

  private cargarUsuarioActual(): void {
    try {
      const stored = localStorage.getItem('user');
      if (stored) {
        const parsed = JSON.parse(stored);
        this.currentUserId = parsed?.id || '';
      } else {
        // Fallback: esperar a que el servicio de auth inicialice
        setTimeout(() => {
          const stored2 = localStorage.getItem('user');
          if (stored2) {
            const parsed = JSON.parse(stored2);
            this.currentUserId = parsed?.id || '';
          }
        }, 500);
      }
    } catch (error) {
      console.error('Error al leer usuario actual:', error);
    }
  }

  ngOnDestroy(): void {
    // Limpiar subscripciones
    this.subscriptions.forEach(sub => sub.unsubscribe());
    
    // Cerrar conexión SSE
    if (this.sseConnection) {
      this.sseConnection.close();
    }
  }

  /**
   * Cargar lista de conversaciones
   */
  cargarConversaciones(): void {
    this.cargandoConversaciones = true;
    
    this.mensajesService.listarConversaciones().subscribe({
      next: (conversaciones) => {
        this.conversaciones = conversaciones;
        this.cargandoConversaciones = false;
      },
      error: (error) => {
        console.error('Error al cargar conversaciones:', error);
        this.cargandoConversaciones = false;
      }
    });
  }

  /**
   * Abrir conversación con un usuario
   */
  abrirConversacion(usuario: Usuario): void {
    this.usuarioSeleccionado = usuario;
    this.vistaActual = 'conversacion';
    this.paginaActual = 0;
    this.conversacionActual = [];
    this.cargarMensajes();
  }

  /**
   * Cargar mensajes de la conversación actual
   */
  cargarMensajes(): void {
    if (!this.usuarioSeleccionado) return;

    this.cargandoMensajes = true;
    
    this.mensajesService.obtenerConversacion(
      this.usuarioSeleccionado.id,
      this.MENSAJES_POR_PAGINA,
      this.paginaActual * this.MENSAJES_POR_PAGINA
    ).subscribe({
      next: (data) => {
        this.conversacionActual = [
          ...this.conversacionActual,
          ...data.conversacion
        ];
        this.hayMasMensajes = data.hasMore;
        this.cargandoMensajes = false;
        
        // Scroll al final en la primera carga
        if (this.paginaActual === 0) {
          setTimeout(() => this.scrollToBottom(), 100);
        }
      },
      error: (error) => {
        console.error('Error al cargar mensajes:', error);
        this.cargandoMensajes = false;
      }
    });
  }

  /**
   * Cargar más mensajes (scroll infinito hacia arriba)
   */
  cargarMasMensajes(): void {
    if (this.cargandoMensajes || !this.hayMasMensajes) return;
    
    this.paginaActual++;
    this.cargarMensajes();
  }

  /**
   * Enviar mensaje
   */
  enviarMensaje(): void {
    if (this.mensajeForm.invalid || !this.usuarioSeleccionado) return;

    const texto = this.mensajeForm.get('texto')?.value.trim();
    if (!texto) return;

    this.enviandoMensaje = true;
    this.mensajeForm.get('texto')?.disable();

    this.mensajesService.enviarMensaje(this.usuarioSeleccionado.id, texto).subscribe({
      next: (mensaje) => {
        // Agregar mensaje a la conversación (optimistic UI)
        this.conversacionActual.push(mensaje);
        
        // Limpiar formulario
        this.mensajeForm.reset();
        
        // Scroll al final
        this.scrollToBottom();
        
        this.enviandoMensaje = false;
        this.mensajeForm.get('texto')?.enable();
      },
      error: (error) => {
        console.error('Error al enviar mensaje:', error);
        alert(error.message || 'Error al enviar mensaje');
        this.enviandoMensaje = false;
        this.mensajeForm.get('texto')?.enable();
      }
    });
  }

  /**
   * Buscar usuarios
   */
  buscarUsuarios(busqueda: string): void {
    this.buscandoUsuarios = true;
    
    this.mensajesService.buscarUsuarios(busqueda).subscribe({
      next: (usuarios) => {
        this.usuariosBuscados = usuarios;
        this.buscandoUsuarios = false;
      },
      error: (error) => {
        console.error('Error al buscar usuarios:', error);
        this.buscandoUsuarios = false;
      }
    });
  }

  enfocarBusqueda(): void {
    if (this.searchInput?.nativeElement) {
      this.searchInput.nativeElement.focus();
    }
  }

  /**
   * Seleccionar usuario de la búsqueda
   */
  seleccionarUsuario(usuario: Usuario): void {
    this.usuariosBuscados = [];
    this.searchForm.reset();
    this.abrirConversacion(usuario);
  }

  /**
   * Volver a la lista de conversaciones
   */
  volverALista(): void {
    this.vistaActual = 'lista';
    this.usuarioSeleccionado = null;
    this.conversacionActual = [];
    this.cargarConversaciones();
  }

  /**
   * Scroll al final del contenedor de mensajes
   */
  private scrollToBottom(): void {
    try {
      if (this.mensajesContainer) {
        const element = this.mensajesContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) {
      console.error('Error al hacer scroll:', err);
    }
  }

  /**
   * Formatear fecha del mensaje
   */
  formatearFecha(fecha: string): string {
    const date = new Date(fecha);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    
    if (seconds < 60) return 'Ahora';
    if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `Hace ${Math.floor(seconds / 3600)}h`;
    if (seconds < 604800) return `Hace ${Math.floor(seconds / 86400)}d`;
    
    return date.toLocaleDateString();
  }

  /**
   * Obtener clases CSS para el mensaje
   */
  obtenerClasesMensaje(mensaje: MensajePrivado, usuarioActualId: string): string {
    const esPropio = mensaje.emisor.id === usuarioActualId;
    return esPropio ? 'mensaje-propio' : 'mensaje-ajeno';
  }

  /**
   * Verificar si el formulario es válido
   */
  get puedeEnviar(): boolean {
    return this.mensajeForm.valid && 
           !this.enviandoMensaje && 
           !!this.usuarioSeleccionado;
  }

  /**
   * Obtener longitud del texto actual
   */
  get longitudTexto(): number {
    return this.mensajeForm.get('texto')?.value?.length || 0;
  }
}
