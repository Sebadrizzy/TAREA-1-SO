
import threading
import pygame
import time

# Inicializo la matriz de 5 pisos, cada uno de 50x30
matriz = [[['.' for _ in range(30)] for _ in range(50)] for _ in range(5)]
camino = []
sem_maximohebras = threading.Semaphore(10)  # Semáforo para limitar cantidad de hebras

# Variables globales
inicio = (0, 0, 0)  # Posición de inicio, actualizable desde archivo
salida = None  # Posición de la salida
ventana = None  # Ventana global de Pygame

# Cargar laberinto desde archivo
def cargar_laberinto(ruta):
    global inicio, salida
    with open(ruta, 'r') as f:
        datos = f.readlines()

    for dato in datos:
        columna, fila, piso, construccion = dato.strip().split(';')
        columna, fila, piso = int(columna), int(fila), int(piso)

        matriz[piso][columna][fila] = construccion

        # Identificar la posición de inicio y salida
        if construccion == 'I':
            inicio = (columna, fila, piso)
        elif construccion == 'V':
            salida = (columna, fila, piso)

# Dibujar el laberinto en Pygame
def dibujar_laberinto():
    global ventana
    pygame.init()
    ventana = pygame.display.set_mode((800, 600))
    colorfondo = (0, 0, 255)  # Azul
    colormuralla = (255, 0, 0)  # Rojo
    colorpasillo = (255, 255, 255)  # Blanco
    colorinicio = (0, 255, 0)  # Verde
    colorsalida = (255, 255, 0)  # Amarillo

    ventana.fill(colorfondo)

    for piso in range(5):
        for x in range(50):
            for y in range(30):
                if matriz[piso][x][y] == 'X':  # Muro
                    color = colormuralla
                elif matriz[piso][x][y] == 'I':  # Inicio
                    color = colorinicio
                elif matriz[piso][x][y] == 'V':  # Salida
                    color = colorsalida
                else:
                    color = colorpasillo

                pygame.draw.rect(ventana, color, (x * 15, y * 15, 15, 15))

    pygame.display.update()

# Recorrer laberinto con hebras
def buscar_salida(x, y, z, r, g, b):
    global salida, ventana
    sem_maximohebras.acquire()

    if x < 0 or y < 0 or z < 0 or x >= 50 or y >= 30 or z >= 5:
        sem_maximohebras.release()
        return  # Evitar salir de los límites de la matriz

    while matriz[z][x][y] == '.':
        matriz[z][x][y] = '-'  # Marcar el camino visitado
        camino.append((x, y, z))

        # Dibujo en pygame
        pygame.draw.rect(ventana, (r, g, b), (x * 15, y * 15, 15, 15))
        pygame.display.update()

        # Ver si llegamos a la salida
        if (x, y, z) == salida:
            print(f'Salida encontrada en la posición ({x}, {y}, {z})')
            sem_maximohebras.release()
            return  # Terminar el hilo si se encuentra la salida

        # Generar hebras en las 4 direcciones
        threading.Thread(target=buscar_salida, args=(x + 1, y, z, r, g, b)).start()  # Derecha
        threading.Thread(target=buscar_salida, args=(x - 1, y, z, r, g, b)).start()  # Izquierda
        threading.Thread(target=buscar_salida, args=(x, y + 1, z, r, g, b)).start()  # Abajo
        threading.Thread(target=buscar_salida, args=(x, y - 1, z, r, g, b)).start()  # Arriba

        # Pausa para visualizar el recorrido
        time.sleep(0.1)

    sem_maximohebras.release()

# Inicializar el proceso de búsqueda
def iniciar_busqueda():
    r, g, b = (120, 30, 200)  # Colores para el camino
    buscar_salida(inicio[0], inicio[1], inicio[2], r, g, b)

if __name__ == "__main__":
    cargar_laberinto('datosdeprueba.txt')  # Archivo de entrada
    dibujar_laberinto()
    iniciar_busqueda()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
