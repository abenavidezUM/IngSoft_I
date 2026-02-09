import { Component, OnInit } from '@angular/core';
import { MensajesService, Mensaje } from '../../services/mensajes.service';

@Component({
  selector: 'app-mensajes-propios',
  templateUrl: './mensajes-propios.component.html',
  styleUrls: ['./mensajes-propios.component.css']
})
export class MensajesPropiosComponent implements OnInit {
  mensajes: Mensaje[] = [];
  cargando = false;
  offset = 0;
  readonly limit = 20;
  hayMas = false;
  mensajeBorrando: string | null = null;

  constructor(private mensajesService: MensajesService) {}

  ngOnInit(): void {
    this.cargarMensajes();
  }

  cargarMensajes(): void {
    this.cargando = true;
    this.mensajesService.obtenerMensajesPropios(this.limit, this.offset).subscribe({
      next: (data) => {
        this.mensajes = [...this.mensajes, ...data.mensajes];
        this.hayMas = data.hasMore;
        this.offset += this.limit;
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar mensajes propios:', error);
        this.cargando = false;
      }
    });
  }

  /**
   * Borra un mensaje con confirmación del usuario
   * CU0008 - Borrar Mensajes Propios
   * 
   * @param mensajeId ID del mensaje a borrar
   */
  borrarMensaje(mensajeId: string): void {
    // Confirmación del usuario
    if (confirm('¿Confirma el borrado de su mensaje?')) {
      this.mensajeBorrando = mensajeId;
      
      this.mensajesService.borrarMensaje(mensajeId).subscribe({
        next: (response) => {
          console.log('Mensaje borrado exitosamente:', response);
          
          // Remover el mensaje de la lista local
          this.mensajes = this.mensajes.filter(m => m.id !== mensajeId);
          this.mensajeBorrando = null;
        },
        error: (error) => {
          console.error('Error al borrar mensaje:', error);
          alert('Error al borrar el mensaje. Por favor, intente nuevamente.');
          this.mensajeBorrando = null;
        }
      });
    }
  }

  /**
   * Verifica si un mensaje está siendo borrado
   * 
   * @param mensajeId ID del mensaje a verificar
   * @returns true si el mensaje está siendo borrado
   */
  estaBoorrando(mensajeId: string): boolean {
    return this.mensajeBorrando === mensajeId;
  }
}

