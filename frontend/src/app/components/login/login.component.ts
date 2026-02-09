import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

interface User {
  nickName: string;
  nombre: string;
  apellido: string;
}

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  usuarios: User[] = [
    { nickName: 'juanperez', nombre: 'Juan', apellido: 'Pérez' },
    { nickName: 'mariagarcia', nombre: 'María', apellido: 'García' },
    { nickName: 'carloslopez', nombre: 'Carlos', apellido: 'López' },
    { nickName: 'agusbenavid', nombre: 'Agustín', apellido: 'Benavídez' }
  ];

  usuarioSeleccionado: string = '';
  loading: boolean = false;
  error: string = '';

  constructor(
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    // Si ya está autenticado, redirigir
    if (localStorage.getItem('access_token') || localStorage.getItem('token')) {
      this.router.navigate(['/mensajes-propios']);
    }
  }

  async login(): Promise<void> {
    if (!this.usuarioSeleccionado) {
      this.error = 'Por favor selecciona un usuario';
      return;
    }

    this.loading = true;
    this.error = '';

    try {
      const response: any = await this.http
        .get(`${environment.apiUrl}/testing/token/${this.usuarioSeleccionado}`)
        .toPromise();

      if (response.success && response.data.token) {
        // Guardar token y datos de usuario (usar 'access_token' para que el interceptor lo encuentre)
        localStorage.setItem('access_token', response.data.token);
        localStorage.setItem('token', response.data.token); // Mantener para compatibilidad
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        console.log('✅ Login exitoso:', response.data.user.nickName);
        
        // Redirigir a mensajes propios
        this.router.navigate(['/mensajes-propios']);
      } else {
        this.error = 'Error al obtener el token';
      }
    } catch (err: any) {
      console.error('Error en login:', err);
      this.error = err.error?.error || 'Error al conectar con el servidor';
    } finally {
      this.loading = false;
    }
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    this.router.navigate(['/login']);
  }
}
