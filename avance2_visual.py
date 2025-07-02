import gi
import random
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Requerido para usar GTK 4.0
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject

#""""Bacteria
#id: identificador ´unico.
#raza: identificador gen´etico o especie.
#energia: nivel de energ´ıa actual.
#resistente: booleano que indica si es resistente.
#estado: activa o muerta.
#M´etodos: alimentar(), dividirse(), mutar(), morir().""""#

### CLASE Bacteria - Commit 1
class Bacteria:
    def __init__(self, id_bacteria, raza, energia, resistente, estado):
        self.__raza = raza 
        self.__energia = energia 
        self.__resistente = resistente
        self.__estado = estado  # "activa" o "muerta"
        self.__id = id_bacteria

    def get_energia(self):
        return self.__energia

    def set_energia(self, energia):
        self.__energia = energia

    def get_resistente(self):
        return self.__resistente

    def set_resistente(self, resistente):
        self.__resistente = resistente

    def get_estado(self):
        return self.__estado

    def set_estado(self, estado):
        self.__estado = estado

# Metodos
    def alimentar(self, nutrientes_disponibles):
        if self.__estado != "activa":
            print("Bacteria Muerta. No se puede alimentar")
            return 0  # no se alimenta

        if nutrientes_disponibles == 0:
            print("No hay nutrientes disponibles")
        consumo = random.randint(5, 15) #Compite por nutrientes.
        consumido = min(consumo, nutrientes_disponibles) # la bacteria comienza con 100 unidades de nutrientes_disponibles
        self.__energia += consumido
        return consumido  # lo que se consumió efectivamente

    def dividirse(self): # Se reproduce (mitosis).
        if self.__energia >= 50 and self.__estado == "activa":
            self.__energia = self.__energia // 2
            nueva_id = f"{self.__id}_hija"
            return Bacteria(nueva_id, self.__raza, self.__energia, self.__resistente, "activa")
        return None

    def mutar(self): # Puede mutar (resistencia).
        if random.random() < 0.5 and self.__estado == "activa":
            self.__resistente = not self.__resistente

    def morir(self): # Muere por falta de recursos o antibióticos.
        self.__estado = "inactiva"

    # por si hay que imprimir
    def __str__(self):
        return f"Bacteria(id={self.__id}, raza={self.__raza}, energia={self.__energia}, resistente={self.__resistente}, estado={self.__estado})"


### CLASE Ambiente - Commit 2
class Ambiente:
    def __init__(self):
        # Crear bacterias random con atributos random 
        self.razas_disponibles = ["cocos", "bacilos", "espirilos"]
        self.grilla = np.empty((10, 10), dtype=object)  # matriz 10x10 de bacterias vacía (usa empty para pasarle objetos)
        self.nutrientes = np.full((10, 10), 100)  # Cada celda comienza con 100 nutrientes

#  Grilla vacía (empty) -> maneja los datos tipo objeto
    def grilla_objetos(self):
        for i in range(10):
            for j in range(10): # usamos los atributos de Bacteria
                raza = random.choice(self.razas_disponibles)
                energia = random.randint(20, 100)
                resistente = random.choice([True, False])
                estado = "activa"
                id_bacteria = f"{raza}_{i}_{j}" # el id es la raza y su coordenada
                self.grilla[i, j] = Bacteria(id_bacteria, raza, energia, resistente, estado) # Relaciona Ambiente con Bacteria


    def sincronizar_visual(self):
        """
        Sincroniza la grilla visual con la grilla de objetos bacterianos.
        Convierte las bacterias en códigos numéricos para visualización.
        """
        self.grilla_visual = np.zeros((10, 10))  # Reinicia la grilla visual a ceros

        for i in range(10):
            for j in range(10):
                bacteria = self.grilla[i, j]

                if bacteria is None:
                    self.grilla_visual[i, j] = 0  # Vacío
                elif bacteria.get_estado() == "inactiva":
                    self.grilla_visual[i, j] = 2  # Bacteria muerta
                elif bacteria.get_estado() == "activa" and bacteria.get_resistente():
                    self.grilla_visual[i, j] = 3  # Bacteria resistente
                elif bacteria.get_estado() == "activa":
                    self.grilla_visual[i, j] = 1  # Bacteria activa

    def graficar_grilla(self):
        """
        Dibuja la grilla visual de bacterias usando matplotlib.
        """
        cmap = plt.cm.get_cmap('Set1', 5)
        fig, ax = plt.subplots(figsize=(6, 6))
        cax = ax.matshow(self.grilla_visual, cmap=cmap)

        legend_elements = [
            Patch(facecolor=cmap(1/5), label='Bacteria activa'),
            Patch(facecolor=cmap(2/5), label='Bacteria muerta'),
            Patch(facecolor=cmap(3/5), label='Bacteria resistente'),
            Patch(facecolor=cmap(4/5), label='Biofilm'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.45, 1))
        ax.set_xticks(np.arange(0, 10, 1))
        ax.set_yticks(np.arange(0, 10, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(color='gray', linestyle='-', linewidth=0.5)

        for i in range(10):
            for j in range(10):
                val = self.grilla_visual[i, j]
                if val > 0:
                    ax.text(j, i, int(val), va='center', ha='center', color='white')

        plt.title("Estado actual de la colonia bacteriana (10x10)")
        plt.tight_layout()
        plt.show()


# CLASE Colonia Commit 3
class Colonia():
    def __init__(self, bacterias, ambiente):
        self.bacterias = bacterias  # Lista de objetos bacteria
        self.ambiente = ambiente

    def paso(self):
        """Ejecuta un paso de simulación sobre todas las bacterias"""
        for i in range(10):
            for j in range(10):
                bacteria = self.ambiente.grilla[i, j]
                if bacteria and bacteria.get_estado() == "activa":
                    consumido = bacteria.alimentar(self.ambiente.nutrientes[i, j])
                    self.ambiente.nutrientes[i, j] -= consumido
                    bacteria.mutar()
                    if bacteria.get_energia() < 20:
                        bacteria.morir()
                    hija = bacteria.dividirse()
                    if hija:
                        # Buscar celda vacía vecina para colocar hija
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            ni, nj = i + dx, j + dy
                            if 0 <= ni < 10 and 0 <= nj < 10 and self.ambiente.grilla[ni, nj] is None:
                                self.ambiente.grilla[ni, nj] = hija
                                break
        self.ambiente.sincronizar_visual()


# BLOQUE DE PRUEBA MANUAL
if __name__ == "__main__":
    ambiente = Ambiente()
    ambiente.grilla_objetos()
    ambiente.sincronizar_visual()
    ambiente.graficar_grilla()  # Visualizar estado inicial

    colonia = Colonia(None, ambiente)
    colonia.paso()              # Ejecutar un paso de simulación
    ambiente.graficar_grilla()  # Visualizar estado tras 1 paso
