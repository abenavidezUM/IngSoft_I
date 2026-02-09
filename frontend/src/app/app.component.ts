import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Usuario ya está inicializado en el constructor del servicio
  }

  tieneToken(): boolean {
    return this.authService.isAuthenticated();
  }

  getUserName(): string {
    const user = this.authService.getCurrentUser();
    if (user) {
      return `${user.nombre} ${user.apellido} (@${user.nickName})`;
    }
    return 'Usuario';
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    this.router.navigate(['/login']);
  }
}

