import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // Usuario y token hardcodeados para desarrollo
  private readonly HARDCODED_USER = {
    id: '698747cabcb575739d9209fe',
    nickName: 'juanperez',
    nombre: 'Juan',
    apellido: 'Pérez',
    mail: 'juan@example.com',
    biografia: 'Desarrollador Full Stack',
    fotoUsuario: '',
    fotoUsuarioPortada: '',
    fechaDeCreado: '2026-02-07T14:10:18.527000',
    rol: 'user',
    seguidores: [],
    siguiendo: ['698747cabcb575739d9209ff', '698747cabcb575739d920a00', '698747cabcb575739d920a01', '698747cabcb575739d920a02', '698747cabcb575739d920a03']
  };

  // Token JWT válido generado para este usuario
  private readonly HARDCODED_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3MDQ3NDEzNiwianRpIjoiMDNlOTNlMzctYWQzOC00MGFmLWExYmUtYWVlZDQwOGQwNjNjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY5ODc0N2NhYmNiNTc1NzM5ZDkyMDlmZSIsIm5iZiI6MTc3MDQ3NDEzNiwiY3NyZiI6IjYwMzc4MWZmLTIxZDMtNGZiMi04MmI5LTM2MWE4NGY0OGI5NiIsImV4cCI6MTc3MDQ3NzczNn0.WTOZi6SGmAlXRQ7L_K_0xesO52aJ_M8QRHi7x-7HtRE';

  constructor() {
    // Ya no inicializamos automáticamente - el usuario debe hacer login desde el Home
    // this.initializeUser();
  }

  initializeUser(): void {
    // Inicializar usuario y token hardcodeados directamente (método de respaldo)
    localStorage.setItem('user', JSON.stringify(this.HARDCODED_USER));
    localStorage.setItem('access_token', this.HARDCODED_TOKEN);
    console.log('✅ Usuario hardcodeado inicializado:', this.HARDCODED_USER.nickName);
  }

  getCurrentUser(): any {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

