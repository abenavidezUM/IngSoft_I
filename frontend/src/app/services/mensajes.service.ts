import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface Mensaje {
  id: string;
  texto: string;
  fechaDeCreado: string;
}

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  code?: string;
}

@Injectable({
  providedIn: 'root'
})
export class MensajesService {
  private apiUrl = `${environment.apiUrl}/mensajes`;

  constructor(private http: HttpClient) {}

  obtenerMensajesPropios(limit: number = 20, offset: number = 0): Observable<{
    mensajes: Mensaje[];
    total: number;
    hasMore: boolean;
  }> {
    const params = new HttpParams()
      .set('limit', limit.toString())
      .set('offset', offset.toString());

    return this.http.get<ApiResponse<any>>(`${this.apiUrl}/mios`, { params }).pipe(
      map(response => {
        if (!response.success || !response.data) {
          // Retornar estructura vacía en lugar de lanzar error
          return { mensajes: [], total: 0, hasMore: false };
        }
        return response.data;
      }),
      catchError(() => {
        // En caso de error, retornar estructura vacía
        return of({ mensajes: [], total: 0, hasMore: false });
      })
    );
  }

  /**
   * Borra un mensaje propio del usuario
   * CU0008 - Borrar Mensajes Propios
   * 
   * @param mensajeId ID del mensaje a borrar
   * @returns Observable con la respuesta del servidor
   */
  borrarMensaje(mensajeId: string): Observable<ApiResponse<any>> {
    return this.http.delete<ApiResponse<any>>(`${this.apiUrl}/${mensajeId}`).pipe(
      map(response => {
        if (!response.success) {
          throw new Error(response.error || 'Error al borrar el mensaje');
        }
        return response;
      }),
      catchError(error => {
        console.error('Error al borrar mensaje:', error);
        throw error;
      })
    );
  }
}

