# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 21:19:18 2023

@author: pilar
"""

from pid import PID
import cv2
import time
import serial as ser
import numpy as np

arduino = None
arduino = ser.Serial('COM6', baudrate=9600, bytesize=ser.EIGHTBITS,parity=ser.PARITY_NONE,stopbits=ser.STOPBITS_ONE, timeout=10)

# Definir el controlador
pid = PID(Kp = 0.7, Ki = 0.11666666666666667, Kd = 1.0, alpha = 0)

# Abrir la cámara (para usar la webcam el primer parámetro tendría que ser 0 en vez de 1)
vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
time.sleep(2)

# Elegir setpoint
setpoint = 300

def sp(t):
    return 300

# Abrir template
template = cv2.imread("Objetos/template.png")

"""
Controlar indefinidamente (hay que cortarlo a mano)
"""
# # Controlar
# pid.controlar(sp, vs, arduino, template)

"""
Barrer valores de Kp
"""
valores = np.linspace(0.6, 1, 5)

for v in valores:
    pid.fijarCoeficientes(v, 0, 0, 0)
    pid.controlar(sp, vs, arduino, template, duracion=5, nombre=f"Kp{str(v).replace('.', '-')}.csv")
    vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    time.sleep(2)

# Cerrar cámara
vs.release()

# Cerrar ventanas de OpenCV
cv2.destroyAllWindows()