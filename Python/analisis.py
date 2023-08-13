# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 22:05:34 2023

@author: pilar
"""

import numpy as np
from pid import PID
import matplotlib.pyplot as plt

ruta = "Datos/Kd1-0.csv"

t, setpoint, pwm, error = np.loadtxt(ruta, delimiter = ",", skiprows=3, unpack=True)

# Leer coeficientes del header
f = open(ruta)
str_coeficientes = f.readline()[2:]
Kp, Ki, Kd, alpha = None, None, None, None
exec(str_coeficientes)

coeficientes = (Kp, Ki, Kd, alpha)

# Reconstruir valores de la señal de control
controlador = PID.gen_controlador(Kp, Ki, Kd, alpha)
T = len(t)
P = [0] * T
I = [0] * T
D = [0] * T
controlador.send(None)

for j in range(T):
    P[j], I[j], D[j] = controlador.send([t[j], error[j]])

# Calcular alturas
alturas = setpoint - error

# Graficar
t = t[2:]

t = t - t[0]

P = P[2:]
I = I[2:]
D = D[2:]

setpoint = setpoint[2:]
error = error[2:]

pwm = pwm[2:]

alturas = alturas[2:]

plt.style.use("seaborn-v0_8-poster")
fig, ax = plt.subplots(2, 1, sharex=True)

ax[0].set_xlim(0, np.max(t))
ax[0].plot(t, P, color="C0", zorder=8, label = "Proporcional")
ax[0].plot(t, I, color="C1", zorder=10, label = "Integral")
ax[0].plot(t, D, color="C2", zorder=7, label = "Derivativo")
ax[0].plot(t, pwm, color="C3", zorder=9, label="PWM")

ax[0].axvspan(0, 2.44, color="lightgrey")
ax[0].axvspan(2.44, 8.63, color="whitesmoke")

ax[1].plot(t, alturas, color="C4", lw="5", zorder=6, label = "Vaso")
ax[1].plot(t, setpoint, "--", color="tomato", lw=3, zorder=5, label = "Setpoint")

ax[1].axvspan(0, 2.44, color="lightgrey")
ax[1].axvspan(2.44, 8.63, color="whitesmoke")

ax[0].grid()
ax[1].grid()

ax[1].set_xlabel("Tiempo [s]")
ax[0].set_ylabel("Señales de control")
ax[1].set_ylabel("Altura [Px]")

ax[0].legend(loc = "lower right", ncols = 4)

ax[1].legend()