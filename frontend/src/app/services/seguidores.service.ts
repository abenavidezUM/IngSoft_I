import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface Usuario {
  id: string;
  nickName: string;
  nombre: string;
  apellido: string;
  fotoUsuario?: string;
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
export class SeguidoresService {
  private apiUrl = `${environment.apiUrl}/usuarios`;

  constructor(private http: HttpClient) {}

  obtenerSeguidores(): Observable<Usuario[]> {
    return this.http.get<ApiResponse<Usuario[]>>(`${this.apiUrl}/seguidores`).pipe(
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
}

