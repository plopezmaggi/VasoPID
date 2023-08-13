# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 14:11:06 2023

@author: pilar
"""

# -*- coding: utf-8 -*-

import imutils
import cv2

def trackColor (vs, lower, upper, GRAFICAR=False):
    """
    Trackear un color en particular (elige el objeto más grande que sea de ese color).
    
    vs : Webcam.
    lower, upper : Rango de tolerancia para cada coordenada (en HSV).
    GRAFICAR : Si es True, muestra la imagen de la webcam, junto con el contorno
    y el centroide del objeto que está trackeando.
    """
    
    # Leer frame
    frame = vs.read()[1]
    
    # Romper el loop cuando termina el video
    if frame is None:
        return True, None, None
    
    # Cortar zona del tubo
    #frame = frame[200:300, :, :]
    
    # Rotar la imagen
    #frame = np.transpose(frame, (1, 0, 2))
    
    # Achicar la imagen
    frame = imutils.resize(frame, height=600)
    
    # Hacerla borrosa para sacar un poco de ruido
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    
    # Pasar a HSV
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # Filtrar los colores en el rango que queremos
    mask = cv2.inRange(hsv, lower, upper)
    
    # Sirve para tirar puntos sueltos
    mask = cv2.erode(mask, None, iterations=2)
    
    # Hace lo contrario, puede hacer que se defina mejor el objeto
    mask = cv2.dilate(mask, None, iterations=2)

    # Buscar contornos
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    # Inicializar posición del centroide
    x, y = None, None
    
    
    if len(cnts) > 0:
        # Buscar el mayor contorno
        mayorCnt = max(cnts, key=cv2.contourArea)
        
        # Calcular centroide
        M = cv2.moments(mayorCnt)
        x, y = M["m10"] / M["m00"], M["m01"] / M["m00"]
        
        
        if GRAFICAR:
            # Graficar contorno
            cv2.drawContours(frame, [mayorCnt], -1, (0,255,0), 3)

            # Graficar centroide
            cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
            
            
    
    if GRAFICAR:
        # Mostrar el frame actual
        cv2.imshow("Frame", frame)
    
        key = cv2.waitKey(1) & 0xFF
    
        # fin = False
        
        # # if the 'q' key is pressed, stop the loop
        # if key == ord("q"):
        #     fin = True
    
    return x, y

def trackTemplate(vs, template, GRAFICAR=True):
    # Leer frame
    frame = vs.read()[1]
    
    # Romper el loop cuando termina el video
    if frame is None:
        return None, None
    
    # Cortar zona del tubo
    frame = frame[170:230, 130:580, :]
    
    # Rotar la imagen
    # frame = np.transpose(frame, (1, 0, 2))
    
    # Dimensiones del template (para dibujar el rectángulo)
    w, h = template.shape[:-1]
    
    # Trackear el template
    res = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    
    if GRAFICAR:
        cv2.rectangle(frame, top_left, bottom_right, 255, 2)
        cv2.imshow("Frame", frame)
    
        key = cv2.waitKey(1) & 0xFF
        # fin = False
        
        # # if the 'q' key is pressed, stop the loop
        # if key == ord("l"):
        #     print("track")
        #     fin = True  
    
    return top_left