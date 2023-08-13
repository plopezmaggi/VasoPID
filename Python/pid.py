# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 23:23:21 2023

@author: pilar
"""

import numpy as np
from tracking import trackTemplate
from matplotlib import pyplot as plt
import time
import cv2

# Para modificar la memoria del término integral (así como está no se usa en el algoritmo de control)
def exponential_smoothing(current, last, alpha):
    return alpha * current + (1-alpha) * last


class PID ():
    def __init__(self, Kp, Ki, Kd, alpha):
        self.fijarCoeficientes(Kp, Ki, Kd, alpha)
        
        # Crear arrays vacíos para mediciones
        self.reset()
        
        self.controlador = self.gen_controlador(self.Kp, self.Ki, self.Kd, self.alpha)
        
        # Se usa para cortar el loop mientras controla
        self.fin = False
        
    def fijarCoeficientes(self, Kp, Ki, Kd, alpha):
        self.Kp, self.Ki, self.Kd, self.alpha = Kp, Ki, Kd, alpha
        self.controlador = self.gen_controlador(self.Kp, self.Ki, self.Kd, self.alpha)
        
    @staticmethod
    def gen_controlador(Kp, Ki, Kd, alpha):
        # Valores iniciales para error, tiempo y términos de control
        eAnterior = 0
        tAnterior = 0
        P = 0
        I = 0
        D = 0
        
        while True:
            # Devolver señal de control actual, tomar nuevo valor de (t, e)
            t, e = yield P, I, D
            
            # Calcular los tres términos de la señal de control
            P = Kp * e
            
            I = I + Ki * e * (t - tAnterior)
            if I > 255:
                I = 255
            if I < 0:
                I = 0
            D = Kd * (e - eAnterior) / (t - tAnterior)
            
            # Guardar datos para el próximo ciclo
            tAnterior = t
            eAnterior = e
            
    def guardarDatos(self, t, setpoint, pwm, e, archivo, header, ruta="Datos/26-06/"):
        
        if archivo == "cancelar":
            return
        
        np.savetxt(ruta + archivo,
                   np.array([t, setpoint, pwm, e]).T,
                   header = f"(Kp, Ki, Kd, alpha) = ({self.Kp}, {self.Ki}, {self.Kd}, {self.alpha})\n {header}\n tiempo, setpoint, pwm, error",
                   delimiter=","
                   )
        
    def reset(self):
        """
        Borrar todas las mediciones guardadas.
        """
        self.t = []
        self.pwm = []
        self.h = []
        self.setpoint = []
    
    def controlar(self, setpoint, vs, arduino, template, duracion=np.inf, CAMARA=True, GRAFICO=True, nombre=None):
        """
        Controla la altura según el setpoint que le pasemos.
        """
        
        # Inicializar controlador
        self.controlador.send(None)

        # Tiempo inicial
        t0 = time.time()

        # Listas para la serie temporal
        tiempos = []
        errores = []
        setpoints = []
        pwms = []
        p = []
        i = []
        d = []
        
        if GRAFICO:
            # Para ir graficando el eje x (y que se note la oscilación del error)
            eje = []
            
            # Figura para graficar mientras se mide
            fig, ax = plt.subplots(1, 1, figsize=(12, 16))
            hPlot, = ax.plot(0, 0, "o", color = "tomato", animated=True)
            ejePlot, = ax.plot(0, 0, color = "slateblue", animated=True)
            propPlot, = ax.plot(0, 0, color = "C1", animated=True)
            intPlot, = ax.plot(0, 0, color = "C2", animated=True)
            derPlot, = ax.plot(0, 0, color = "C3", animated=True)
            
            tmin = 0
            rango = 60
            
            ax.set_ylim(-500, 500)
            ax.set_xlim(tmin, tmin + rango)

            # Cortar con la tecla l
            def cortar(event):
                if event.key == "l":
                    print("eventos")
                    self.fin = True

            fig.canvas.mpl_connect('key_press_event', cortar)
            
            plt.show(block=False)
            plt.pause(0.1)
            
            background = fig.canvas.copy_from_bbox(fig.bbox)
            ax.draw_artist(hPlot)
            ax.draw_artist(ejePlot)
            ax.draw_artist(propPlot)
            ax.draw_artist(intPlot)
            ax.draw_artist(derPlot)
            fig.canvas.blit(fig.bbox)
        
        arduino.write(bytes("a0\n", 'utf-8'))
        time.sleep(2.0)

        while True:
            # Medir posición
            r = trackTemplate(vs, template, GRAFICAR=CAMARA)
            print(r)
            y, x = r
            
            # Si no se detectó la posición, no hacemos nada
            if y is None:
                continue
            
            # Calcular tiempo
            t = time.time() - t0
            
            # Cortar después de un cierto tiempo
            if t > duracion:
                break
            
            # Calcular error
            e = setpoint(t) - y
            
            # Calcular señal de control
            P, I, D = self.controlador.send([t, e])
            
            pwm = np.sum((P, I, D))
            pwm = 0 if pwm < 0 else pwm
            pwm = 255 if pwm > 255 else pwm
            
            print(pwm)
            
            # Aplicar señal de control
            dato = 'a' + str(pwm) + '\n'
            arduino.write(bytes(dato, 'utf-8'))
            
            # Guardar datos
            tiempos.append(t)
            errores.append(e)
            setpoints.append(setpoint(t))
            pwms.append(pwm)
            p.append(P)
            i.append(I)
            d.append(D)
            
            if GRAFICO:
                eje.append(0)
                
                # Graficar
                hPlot.set_data(tiempos, errores)
                ejePlot.set_data(tiempos, eje)
                propPlot.set_data(tiempos, p)
                intPlot.set_data(tiempos, i)
                derPlot.set_data(tiempos, d)
                
                if t - tmin > rango:
                    tmin += rango
                    
                    ax.set_xlim(tmin, tmin + rango)
                    
                    plt.pause(0.0001)
                    
                    background = fig.canvas.copy_from_bbox(fig.bbox)
                    
                
                else:
                    fig.canvas.restore_region(background)

                    # redraw just the points
                    ax.draw_artist(hPlot)
                    ax.draw_artist(ejePlot)
                    ax.draw_artist(propPlot)
                    ax.draw_artist(intPlot)
                    ax.draw_artist(derPlot)
        
                    # fill in the axes rectangle
                    fig.canvas.blit(fig.bbox)
                    
                    fig.canvas.flush_events()
            
                
            
            # Si terminó el video o cortamos, romper el loop
            if self.fin:
                break
        
        # Cerrar la webcam
        vs.release()

        # Cerrar ventanas
        cv2.destroyAllWindows()

        # Cerrar gráfico
        plt.close('all')
        
        if nombre is None:
            archivo = input("Nombre de archivo: ")
            header = input("Descripción (no hacen falta los coeficientes): ")
        else:
            archivo = nombre
            header = " "
        
        # Guardar datos
        self.guardarDatos(tiempos, setpoints, pwms, errores, archivo, header, ruta="Datos/")