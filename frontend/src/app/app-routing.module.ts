import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomeComponent } from './components/home/home.component';
import { LoginComponent } from './components/login/login.component';
import { MensajePrivadoComponent } from './components/mensaje-privado/mensaje-privado.component';
import { MensajesPropiosComponent } from './components/mensajes-propios/mensajes-propios.component';
import { SeguidoresComponent } from './components/seguidores/seguidores.component';
import { TendenciasComponent } from './components/tendencias/tendencias.component';

const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'home', component: HomeComponent },
  { path: 'mensajes-propios', component: MensajesPropiosComponent },
  { path: 'seguidores', component: SeguidoresComponent },
  { path: 'mensajes-privados', component: MensajePrivadoComponent },
  { path: 'tendencias', component: TendenciasComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}

