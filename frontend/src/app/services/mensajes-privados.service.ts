import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { tap, map, catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface Usuario {
  id: string;
  nickName: string;
  nombre: string;
  apellido: string;
  fotoUsuario?: string;
}

export interface MensajePrivado {
  id: string;
  texto: string;
  fechaDeCreado: string;
  emisor: Usuario;
  receptor: Usuario;
  leido: string | null;
}

export interface Conversacion {
  usuario: Usuario;
  ultimoMensaje: MensajePrivado;
  mensajesNoLeidos: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  code?: string;
}

@Injectable({
  providedIn: 'root'
})
export class MensajesPrivadosService {
  private apiUrl = `${environment.apiUrl}/mensajes-privados`;
  
  // Subject para mensajes no leídos (para notificaciones en tiempo real)
  private mensajesNoLeidosSubject = new BehaviorSubject<number>(0);
  public mensajesNoLeidos$ = this.mensajesNoLeidosSubject.asObservable();
  
  // Subject para nuevos mensajes (para actualizar conversación en tiempo real)
  private nuevoMensajeSubject = new BehaviorSubject<MensajePrivado | null>(null);
  public nuevoMensaje$ = this.nuevoMensajeSubject.asObservable();

  constructor(private http: HttpClient) {
    // Cargar contador inicial de mensajes no leídos
    this.cargarContadorNoLeidos();
  }

  /**
   * Enviar un mensaje privado
   */
  enviarMensaje(receptorId: string, texto: string): Observable<MensajePrivado> {
    const body = {
      receptor_id: receptorId,
      texto: texto
    };

    return this.http.post<ApiResponse<MensajePrivado>>(this.apiUrl, body).pipe(
      map(response => {
        if (!response.success || !response.data) {
          throw new Error(response.error || 'Error al enviar mensaje');
        }
        return response.data;
      }),
      tap(mensaje => {
        // Emitir nuevo mensaje para actualización en tiempo real
        this.nuevoMensajeSubject.next(mensaje);
      })
    );
  }

  /**
   * Obtener conversación con un usuario
   */
  obtenerConversacion(
    userId: string, 
    limit: number = 50, 
    offset: number = 0
  ): Observable<{ conversacion: MensajePrivado[], total: number, hasMore: boolean }> {
    let params = new HttpParams()
      .set('limit', limit.toString())
      .set('offset', offset.toString());

    return this.http.get<ApiResponse<any>>(
      `${this.apiUrl}/conversacion/${userId}`,
      { params }
    ).pipe(
      map(response => {
        if (!response.success || !response.data) {
          throw new Error(response.error || 'Error al obtener conversación');
        }
        return response.data;
      }),
      tap(() => {
        // Actualizar contador de no leídos después de ver conversación
        this.cargarContadorNoLeidos();
      })
    );
  }

  /**
   * Listar todas las conversaciones del usuario
   */
  listarConversaciones(): Observable<Conversacion[]> {
    return this.http.get<ApiResponse<Conversacion[]>>(
      `${this.apiUrl}/conversaciones`
    ).pipe(
      map(response => {
        if (!response.success || !response.data) {
          // Retornar array vacío en lugar de lanzar error
          return [];
        }
        return response.data;
      }),
      catchError(() => {
        // En caso de error (ej: 401), retornar array vacío
        return of([]);
      })
    );
  }

  /**
   * Marcar un mensaje como leído
   */
  marcarComoLeido(mensajeId: string): Observable<any> {
    return this.http.put<ApiResponse<any>>(
      `${this.apiUrl}/${mensajeId}/leer`,
      {}
    ).pipe(
      map(response => {
        if (!response.success) {
          throw new Error(response.error || 'Error al marcar mensaje como leído');
        }
        return response.data;
      }),
      tap(() => {
        // Actualizar contador de no leídos
        this.cargarContadorNoLeidos();
      })
    );
  }

  /**
   * Obtener cantidad de mensajes no leídos
   */
  contarNoLeidos(): Observable<number> {
    return this.http.get<ApiResponse<{ noLeidos: number }>>(
      `${this.apiUrl}/no-leidos`
    ).pipe(
      map(response => {
        if (!response.success || !response.data) {
          return 0;
        }
        return response.data.noLeidos;
      }),
      tap(count => {
        this.mensajesNoLeidosSubject.next(count);
      })
    );
  }

  /**
   * Eliminar un mensaje (solo el emisor)
   */
  eliminarMensaje(mensajeId: string): Observable<any> {
    return this.http.delete<ApiResponse<any>>(
      `${this.apiUrl}/${mensajeId}`
    ).pipe(
      map(response => {
        if (!response.success) {
          throw new Error(response.error || 'Error al eliminar mensaje');
        }
        return response;
      })
    );
  }

  /**
   * Buscar usuarios (para seleccionar receptor)
   */
  buscarUsuarios(search: string, limit: number = 10): Observable<Usuario[]> {
    let params = new HttpParams()
      .set('search', search)
      .set('limit', limit.toString());

    return this.http.get<ApiResponse<Usuario[]>>(
      `${environment.apiUrl}/usuarios`,
      { params }
    ).pipe(
      map(response => {
        if (!response.success || !response.data) {
          return [];
        }
        return response.data;
      }),
      catchError(() => {
        // En caso de error, retornar array vacío
        return of([]);
      })
    );
  }

  /**
   * Cargar contador de mensajes no leídos
   * (método privado usado internamente)
   */
  private cargarContadorNoLeidos(): void {
    this.contarNoLeidos().subscribe();
  }

  /**
   * Conectar a Server-Sent Events para notificaciones en tiempo real
   */
  conectarSSE(): EventSource | null {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return null;
    }

    const eventSource = new EventSource(
      `${environment.apiUrl}/stream/mensajes-privados?token=${token}`
    );

    eventSource.addEventListener('nuevo_mensaje_privado', (event: MessageEvent) => {
      const mensaje = JSON.parse(event.data);
      this.nuevoMensajeSubject.next(mensaje);
      this.cargarContadorNoLeidos();
    });

    eventSource.addEventListener('mensaje_leido', (event: MessageEvent) => {
      const data = JSON.parse(event.data);
      // Emitir evento para actualizar UI si es necesario
      this.cargarContadorNoLeidos();
    });

    eventSource.onerror = (error) => {
      console.error('Error en SSE:', error);
      eventSource.close();
    };

    return eventSource;
  }
}
