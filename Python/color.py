# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 13:34:37 2023

@author: pilar
"""

import numpy as np
import cv2

archivo = 'Objetos/transparencia.png'

def rango(archivo, transparencia=True):
    """
    Toma la ruta a la imagen del color para trackear, y devuelve las coordenadas mínimas (lower) y máximas (upper)
    para pasarle a trackColor (con un rango más acotado en H que en las otras dos coordenadas).
    """
    imagen = cv2.cvtColor(cv2.imread(archivo), cv2.COLOR_BGR2HSV)

    """ Si recortamos con algo que no sea un rectángulo hay que tirar la zona transparente """
    if transparencia:
        # Mask para puntos transparentes
        mask_transparentes = np.all(imagen == 0, axis=2)
    
        # Nos quedamos con los puntos no transparentes
        imagen = imagen[~mask_transparentes]
        
        # Agregar una dimensión para que coincida con la forma original
        imagen = np.expand_dims(imagen, 0)

    # Calculamos promedio y std de cada coordenada HSV
    promedio = np.mean(imagen, axis=(0, 1))
    std = np.std(imagen, axis=(0, 1))
    print('Mínimo', np.min(imagen[:, :, 0]))
    print('Máximo', np.max(imagen[:, :, 0]))
    print(promedio[0], std[0])
    
    # Formar colores mínimo y máximo
    minimo = np.array([promedio[0] - std[0] / 2, np.min(imagen[:, :, 1]), np.min(imagen[:, :, 2])])
    maximo = np.array([promedio[0] + std[0] / 2, np.max(imagen[:, :, 1]), np.max(imagen[:, :, 2])])
    
    return minimo, maximo
    