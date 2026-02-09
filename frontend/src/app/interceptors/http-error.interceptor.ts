import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable()
export class HttpErrorInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Agregar token si existe
    const token = localStorage.getItem('access_token');
    let authReq = req;
    
    if (token) {
      authReq = req.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('🔑 Token agregado a la petición:', req.url);
      console.log('🔑 Token (primeros 20 caracteres):', token.substring(0, 20) + '...');
    } else {
      console.warn('⚠️ No hay token disponible para:', req.url);
    }

    return next.handle(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        // Manejar errores de forma más amigable
        if (error.status === 401) {
          console.warn('No autenticado. Algunas funciones pueden no estar disponibles.');
        } else if (error.status === 403) {
          console.warn('Acceso denegado.');
        } else if (error.status === 0) {
          console.error('No se puede conectar al servidor. ¿Está corriendo el backend?');
        }
        
        // No lanzar el error, permitir que la aplicación continúe
        return throwError(() => error);
      })
    );
  }
}

