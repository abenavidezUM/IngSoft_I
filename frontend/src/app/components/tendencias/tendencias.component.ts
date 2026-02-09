import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

interface Tendencia {
  etiqueta: string;
  count: number;
}

@Component({
  selector: 'app-tendencias',
  templateUrl: './tendencias.component.html',
  styleUrls: ['./tendencias.component.css']
})
export class TendenciasComponent implements OnInit {
  tendencias: Tendencia[] = [];
  cargando = false;
  error: string | null = null;
  enviando = false;
  resultadoEnvio: any = null;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.cargarTendencias();
  }

  cargarTendencias(): void {
    this.cargando = true;
    this.error = null;

    const token = localStorage.getItem('token');
    const headers = { 'Authorization': `Bearer ${token}` };

    this.http.get<any>(`${environment.apiUrl}/tendencias`, { headers }).subscribe({
      next: (response) => {
        if (response.success) {
          this.tendencias = response.data.tendencias;
        }
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar tendencias:', error);
        this.error = 'Error al cargar las tendencias';
        this.cargando = false;
      }
    });
  }

  enviarEmails(): void {
    if (!confirm('¿Confirmas el envío de emails con las tendencias a todos los usuarios?')) {
      return;
    }

    this.enviando = true;
    this.error = null;
    this.resultadoEnvio = null;

    const token = localStorage.getItem('token');
    const headers = { 'Authorization': `Bearer ${token}` };

    this.http.post<any>(`${environment.apiUrl}/tendencias/enviar`, {}, { headers }).subscribe({
      next: (response) => {
        this.resultadoEnvio = response;
        this.enviando = false;
        alert(`Envío completado: ${response.data?.estadisticas?.emails_enviados || 0} emails enviados`);
      },
      error: (error) => {
        console.error('Error al enviar emails:', error);
        this.error = 'Error al enviar emails de tendencias';
        this.enviando = false;
      }
    });
  }
}
