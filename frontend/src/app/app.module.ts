import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MensajePrivadoComponent } from './components/mensaje-privado/mensaje-privado.component';
import { MensajesPropiosComponent } from './components/mensajes-propios/mensajes-propios.component';
import { SeguidoresComponent } from './components/seguidores/seguidores.component';
import { HomeComponent } from './components/home/home.component';
import { TendenciasComponent } from './components/tendencias/tendencias.component';
import { LoginComponent } from './components/login/login.component';
import { HttpErrorInterceptor } from './interceptors/http-error.interceptor';

@NgModule({
  declarations: [
    AppComponent,
    MensajePrivadoComponent,
    MensajesPropiosComponent,
    SeguidoresComponent,
    HomeComponent,
    TendenciasComponent,
    LoginComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule,
    AppRoutingModule
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: HttpErrorInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}

