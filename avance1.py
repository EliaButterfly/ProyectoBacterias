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


### CLASE Bacteria
class Bacteria:
    def __init__(self, id_bacteria, raza, energia, resistente, estado):
        self.__id = id_bacteria
        self.__raza = raza # V.cholerae - E.Coli
        self.__energia = energia # empiezan con 100
        self.__resistente = resistente
        self.__estado = estado  # "activa" o "muerta"

    def get_energia(self):
        return self.__energia

    def set_energia(self, energia):
        self.__energia = energia

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


### INTERFAZ GTK
class MiAplicacion(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.ejemplo.SimuladorColonia")
        self.ventana = None
        
# ejemplo de bacteria        
    # Bacteria(self, id_bacteria, raza, energia, resistente, estado):
        self.bacteria = Bacteria("B1", "Bacilos", 30, False, "activa")

    def do_activate(self):
        self.ventana = Gtk.ApplicationWindow(application=self)
        self.ventana.set_title("Simulador de Colonia Bacteriana")
        self.ventana.set_default_size(800, 600)

        # HeaderBar con menú
        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Simulador de Colonia Bacteriana"))
        header.set_show_title_buttons(True)

#metodos a implementar
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
