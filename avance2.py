import gi
import random
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject

""""Bacteria
id: identificador ´unico.
raza: identificador gen´etico o especie.
energia: nivel de energ´ıa actual.
resistente: booleano que indica si es resistente.
estado: activa o muerta.
M´etodos: alimentar(), dividirse(), mutar(), morir()."""



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


    def grilla_visual(self):
        # Crear una grilla 10x10 (todo vacío inicialmente)
        grilla = np.zeros((10, 10))

        # Definir posiciones de bacterias activas (1), muertas (2), resistentes (3), y biofilm (4)
        grilla[2, 3] = 1  # activa
        grilla[2, 4] = 1  # activa
        grilla[3, 3] = 1  # activa
        grilla[3, 4] = 3  # resistente
        grilla[5, 5] = 4  # biofilm
        grilla[5, 6] = 4  # biofilm
        grilla[6, 5] = 4  # biofilm
        grilla[6, 6] = 4  # biofilm
        grilla[7, 2] = 2  # muerta
        grilla[1, 8] = 1  # activa
        grilla[2, 8] = 3  # resistente

        # Crear un mapa de colores con 5 categorías (0 = vacío)
        cmap = plt.cm.get_cmap('Set1', 5)

        # Dibujar la grilla
        fig, ax = plt.subplots(figsize=(6, 6))
        cax = ax.matshow(grilla, cmap=cmap)

        # Agregar leyenda
        legend_elements = [
            Patch(facecolor=cmap(1/5), label='Bacteria activa'),
            Patch(facecolor=cmap(2/5), label='Bacteria muerta'),
            Patch(facecolor=cmap(3/5), label='Bacteria resistente'),
            Patch(facecolor=cmap(4/5), label='Biofilm'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.45, 1))

        # Configuración de la grilla
        ax.set_xticks(np.arange(0, 10, 1))
        ax.set_yticks(np.arange(0, 10, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(color='gray', linestyle='-', linewidth=0.5)

        # Mostrar valores en cada celda
        for i in range(10):
            for j in range(10):
                val = grilla[i, j]
                if val > 0:
                    ax.text(j, i, int(val), va='center', ha='center', color='white')

        plt.title("Ejemplo de grilla bacteriana (10x10)")
        plt.tight_layout()
        plt.show()



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


# CLASE Colonia Commit 3
class Colonia():
    def __init__(self, bacterias, ambiente):
        self.bacterias = bacterias
        self.ambiente = ambiente


### INTERFAZ GTK
class MiAplicacion(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.ejemplo.SimuladorColonia")
        self.ventana = None

    # Ambiente asociado a objetos pasa a Ambiente asociado a numeros     
        self.ambiente = Ambiente()
        self.ambiente.grilla_objetos()
        self.ambiente.sincronizar_visual()


    def do_activate(self):
        self.ventana = Gtk.ApplicationWindow(application=self)
        self.ventana.set_title("Simulador de Colonia Bacteriana")
        self.ventana.set_default_size(800, 600)

        # HeaderBar con menú
        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Simulador de Colonia Bacteriana"))
        header.set_show_title_buttons(True)

# metodos a implementar
        menu = Gio.Menu()
        menu.append("Simular", "simular")
        menu.append("Exportar CSV", "app.exportar")
        menu.append("Mostrar gráfico", "app.grafico")
        menu.append("Acerca de", "app.acerca")

        btn_menu = Gtk.MenuButton()
        btn_menu.set_icon_name("open-menu-symbolic")
        btn_menu.set_menu_model(menu)
        header.pack_end(btn_menu)

        self.ventana.set_titlebar(header)

        # Contenedor principal
        self.contenedor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_top=10)
        self.ventana.set_child(self.contenedor)

        # Mostrar datos de la bacteria
        self.label_info = Gtk.Label(label=str(self.bacteria))
        self.contenedor.append(self.label_info)

        # Botón alimentar
        boton_alimentar = Gtk.Button(label="Alimentar Bacteria")
        boton_alimentar.connect("clicked", self.on_alimentar_click)
        self.contenedor.append(boton_alimentar)

        self.ventana.present()

    def on_alimentar_click(self, button):
        nutrientes_disponibles = 100
        consumido = self.bacteria.alimentar(nutrientes_disponibles)
        texto = f"Bacteria se alimentó con {consumido} unidades.\nEstado actual:\n{self.bacteria}"
        self.label_info.set_text(texto)


app = MiAplicacion()
app.run()


