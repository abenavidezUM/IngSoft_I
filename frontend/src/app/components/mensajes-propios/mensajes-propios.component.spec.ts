import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { of, throwError } from 'rxjs';

import { MensajesPropiosComponent } from './mensajes-propios.component';
import { MensajesService } from '../../services/mensajes.service';

describe('MensajesPropiosComponent', () => {
  let component: MensajesPropiosComponent;
  let fixture: ComponentFixture<MensajesPropiosComponent>;
  let mensajesService: jasmine.SpyObj<MensajesService>;

  beforeEach(async () => {
    const mensajesServiceSpy = jasmine.createSpyObj('MensajesService', [
      'obtenerMensajesPropios',
      'borrarMensaje'
    ]);

    await TestBed.configureTestingModule({
      declarations: [ MensajesPropiosComponent ],
      imports: [ HttpClientTestingModule ],
      providers: [
        { provide: MensajesService, useValue: mensajesServiceSpy }
      ]
    })
    .compileComponents();

    mensajesService = TestBed.inject(MensajesService) as jasmine.SpyObj<MensajesService>;
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MensajesPropiosComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load messages on init', () => {
    const mockData = {
      mensajes: [
        { id: '1', texto: 'Mensaje 1', fechaDeCreado: '2026-01-01' },
        { id: '2', texto: 'Mensaje 2', fechaDeCreado: '2026-01-02' }
      ],
      total: 2,
      hasMore: false
    };

    mensajesService.obtenerMensajesPropios.and.returnValue(of(mockData));

    fixture.detectChanges(); // Triggers ngOnInit

    expect(mensajesService.obtenerMensajesPropios).toHaveBeenCalledWith(20, 0);
    expect(component.mensajes.length).toBe(2);
    expect(component.cargando).toBeFalse();
  });

  // =====================
  // Tests CU0008 - Borrar Mensajes Propios
  // =====================

  describe('CU0008 - Borrar Mensajes', () => {
    beforeEach(() => {
      // Setup inicial con mensajes
      component.mensajes = [
        { id: '1', texto: 'Mensaje 1', fechaDeCreado: '2026-01-01' },
        { id: '2', texto: 'Mensaje 2', fechaDeCreado: '2026-01-02' },
        { id: '3', texto: 'Mensaje 3', fechaDeCreado: '2026-01-03' }
      ];
    });

    it('should delete message when user confirms', () => {
      spyOn(window, 'confirm').and.returnValue(true);
      mensajesService.borrarMensaje.and.returnValue(of({ success: true, message: 'Borrado' }));

      component.borrarMensaje('2');

      expect(window.confirm).toHaveBeenCalledWith('¿Confirma el borrado de su mensaje?');
      expect(mensajesService.borrarMensaje).toHaveBeenCalledWith('2');
      expect(component.mensajes.length).toBe(2);
      expect(component.mensajes.find(m => m.id === '2')).toBeUndefined();
    });

    it('should not delete message when user cancels', () => {
      spyOn(window, 'confirm').and.returnValue(false);

      component.borrarMensaje('2');

      expect(window.confirm).toHaveBeenCalledWith('¿Confirma el borrado de su mensaje?');
      expect(mensajesService.borrarMensaje).not.toHaveBeenCalled();
      expect(component.mensajes.length).toBe(3);
    });

    it('should show alert on delete error', () => {
      spyOn(window, 'confirm').and.returnValue(true);
      spyOn(window, 'alert');
      mensajesService.borrarMensaje.and.returnValue(
        throwError(() => new Error('Error de red'))
      );

      component.borrarMensaje('2');

      expect(mensajesService.borrarMensaje).toHaveBeenCalledWith('2');
      expect(window.alert).toHaveBeenCalledWith('Error al borrar el mensaje. Por favor, intente nuevamente.');
      expect(component.mensajes.length).toBe(3); // Mensaje no se borra del array
    });

    it('should set mensajeBorrando during deletion', () => {
      spyOn(window, 'confirm').and.returnValue(true);
      mensajesService.borrarMensaje.and.returnValue(of({ success: true, message: 'Borrado' }));

      expect(component.mensajeBorrando).toBeNull();

      component.borrarMensaje('2');

      // Después del borrado exitoso, mensajeBorrando debe volver a null
      expect(component.mensajeBorrando).toBeNull();
    });

    it('should check if message is being deleted', () => {
      component.mensajeBorrando = '2';

      expect(component.estaBoorrando('2')).toBeTrue();
      expect(component.estaBoorrando('1')).toBeFalse();
      expect(component.estaBoorrando('3')).toBeFalse();
    });
  });
});
