from flask import Flask, request, jsonify, render_template
import random
import math

# Distancia entre dos ciudades (utilizando sus coordenadas latitud/longitud)
def distancia(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

# Calcular la distancia cubierta por una ruta
def evalua_ruta(ruta, coord):
    total = 0
    for i in range(0, len(ruta)-1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        total += distancia(coord[ciudad1], coord[ciudad2])
    ciudad1 = ruta[i + 1]
    ciudad2 = ruta[0]
    total += distancia(coord[ciudad1], coord[ciudad2])
    return total

class BusquedaTabu:
    def __init__(self, coord, tiempo_persistencia=3, iteraciones=100, ciudad_origen=None, ciudad_destino=None):
        self.coord = coord
        self.tiempo_persistencia = tiempo_persistencia
        self.iteraciones = iteraciones
        self.ciudad_origen = ciudad_origen
        self.ciudad_destino = ciudad_destino
        self.n_variables = len(coord)
        self.estado_actual = list(coord.keys())

        # Colocar la ciudad de origen al inicio y la ciudad de destino al final
        if self.ciudad_origen and self.ciudad_destino:
            if self.ciudad_origen in self.estado_actual and self.ciudad_destino in self.estado_actual:
                self.estado_actual.remove(self.ciudad_origen)
                self.estado_actual.remove(self.ciudad_destino)
                self.estado_actual = [self.ciudad_origen] + self.estado_actual + [self.ciudad_destino]
        
        random.shuffle(self.estado_actual[1:-1])  # Solo permutar las ciudades intermedias (sin cambiar origen y destino)

        self.memoria_tabu = {}
        self.mejor_solucion = list(self.estado_actual)
        self.mejor_evaluacion = evalua_ruta(self.estado_actual, self.coord)

    def obtener_vecinos(self):
    vecinos = []
    # Generamos vecinos intercambiando dos ciudades entre la ciudad de origen y destino
        for i in range(1, self.n_variables - 1):  # No permutar las ciudades de origen y destino
            for j in range(i + 1, self.n_variables - 1):  # No permutar las ciudades de origen y destino
            # Crear un vecino haciendo un intercambio de las ciudades intermedias
                vecino = self.estado_actual[:]
                vecino[i], vecino[j] = vecino[j], vecino[i]
                vecinos.append(vecino)
        return vecinos


    def es_tabu(self, vecino):
        # Aquí se almacena en la memoria tabú los intercambios realizados
        for i in range(self.n_variables - 1):
            for j in range(i + 1, self.n_variables):
                if (self.estado_actual[i], self.estado_actual[j]) in self.memoria_tabu:
                    return True
        return False

    def actualizar_memoria_tabu(self, vecino):
        # Almacenar el cambio en la memoria tabú
        for i in range(self.n_variables - 1):
            for j in range(i + 1, self.n_variables):
                if (self.estado_actual[i], self.estado_actual[j]) not in self.memoria_tabu:
                    self.memoria_tabu[(self.estado_actual[i], self.estado_actual[j])] = self.tiempo_persistencia
        
        # Reducir el tiempo de persistencia para los intercambios más viejos
        for key in list(self.memoria_tabu.keys()):
            self.memoria_tabu[key] -= 1
            if self.memoria_tabu[key] <= 0:
                del self.memoria_tabu[key]  # Eliminar intercambio de la memoria si ha expirado

    def ejecutar(self):
        iteraciones_restantes = self.iteraciones
        while iteraciones_restantes > 0:
            iteraciones_restantes -= 1
            dist_actual = evalua_ruta(self.estado_actual, self.coord)

            vecinos = self.obtener_vecinos()
            mejor_vecino = None
            mejor_evaluacion = float('inf')

            for vecino in vecinos:
                dist_tmp = evalua_ruta(vecino, self.coord)
                # Si el vecino no es tabú y mejora la solución actual
                if not self.es_tabu(vecino) and dist_tmp < dist_actual:
                    self.estado_actual = vecino
                    self.actualizar_memoria_tabu(vecino)
                    if dist_tmp < mejor_evaluacion:
                        mejor_evaluacion = dist_tmp
                        mejor_vecino = vecino
                    break
                # Si no mejora, pero es mejor que la mejor ruta conocida
                elif dist_tmp < self.mejor_evaluacion:
                    self.estado_actual = vecino
                    self.actualizar_memoria_tabu(vecino)
                    mejor_vecino = vecino
                    mejor_evaluacion = dist_tmp

            # Actualizamos la mejor solución
            if mejor_vecino:
                self.mejor_solucion = mejor_vecino[:]
                self.mejor_evaluacion = mejor_evaluacion
        
        return self.mejor_solucion, self.mejor_evaluacion


# Definir las ciudades y sus coordenadas
coord = {
    'Jiloyork' :(19.916012, -99.580580),
    'Toluca':(19.289165, -99.655697),
    'Atlacomulco':(19.799520, -99.873844),
    'Guadalajara':(20.677754472859146, -103.34625354877137),
    'Monterrey':(25.69161110159454, -100.321838480256),
    'QuintanaRoo':(21.163111924844458, -86.80231502121464),
    'Michohacan':(19.701400113725654, -101.20829680213464),
    'Aguascalientes':(21.87641043660486, -102.26438663286967),
    'CDMX':(19.432713075976878, -99.13318344772986),
    'QRO':(20.59719437542255, -100.38667040246602)
}

# Crear la aplicación de Flask
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Renderiza el HTML

@app.route('/calcular_ruta', methods=['POST'])
def calcular_ruta():
    # Obtener los datos del formulario
    tiempo_persistencia = int(request.form['tiempo_persistencia'])
    iteraciones = int(request.form['iteraciones'])
    ciudad_origen = request.form.get('ciudad_origen') or None
    ciudad_destino = request.form.get('ciudad_destino') or None
    
    # Ejecutar la búsqueda tabú
    busqueda_tabu = BusquedaTabu(coord, tiempo_persistencia, iteraciones, ciudad_origen, ciudad_destino)
    mejor_solucion, mejor_evaluacion = busqueda_tabu.ejecutar()

    return render_template('index.html', mejor_solucion=mejor_solucion, mejor_evaluacion=mejor_evaluacion)

if __name__ == '__main__':
    app.run(debug=True)
