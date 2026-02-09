import { Component, OnInit } from '@angular/core';
import { SeguidoresService, Usuario } from '../../services/seguidores.service';

@Component({
  selector: 'app-seguidores',
  templateUrl: './seguidores.component.html',
  styleUrls: ['./seguidores.component.css']
})
export class SeguidoresComponent implements OnInit {
  seguidores: Usuario[] = [];
  cargando = false;
  error: string | null = null;

  constructor(private seguidoresService: SeguidoresService) {}

  ngOnInit(): void {
    this.cargarSeguidores();
  }

  cargarSeguidores(): void {
    this.cargando = true;
    this.error = null;
    this.seguidoresService.obtenerSeguidores().subscribe({
      next: (seguidores) => {
        this.seguidores = seguidores;
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar seguidores:', error);
        this.error = 'No se pudieron cargar los seguidores';
        this.cargando = false;
      }
    });
  }
}

