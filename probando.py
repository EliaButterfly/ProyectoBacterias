import gi
import random
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject

# CLASE Bacteria
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

    def alimentar(self, nutrientes_disponibles):
        if self.__estado != "activa":
            print("Bacteria Muerta. No se puede alimentar")
            return 0

        if nutrientes_disponibles == 0:
            print("No hay nutrientes disponibles")
        consumo = random.randint(5, 15)
        consumido = min(consumo, nutrientes_disponibles)
        self.__energia += consumido
        return consumido

    def dividirse(self):
        if self.__energia >= 50 and self.__estado == "activa":
            self.__energia = self.__energia // 2
            nueva_id = f"{self.__id}_hija"
            return Bacteria(nueva_id, self.__raza, self.__energia, self.__resistente, "activa")
        return None

    def mutar(self):
        # 80% probabilidad de mutar, si no es resistente puede formar biofilm
        if self.__estado == "activa":
            r = random.random()
            if r < 0.6:
                self.__resistente = not self.__resistente
            elif 0.6 <= r < 0.7:
                self.__estado = "biofilm"

    def morir(self): # morir por antibiótico es externo, así que se define en PASO
        self.__estado = "inactiva"


# CLASE Ambiente
class Ambiente:
    def __init__(self):
        # Crear bacterias random con atributos random 
        self.razas_disponibles = ["cocos", "bacilos", "espirilos"]
        
        ###  Grilla vacía (empty) -> maneja los datos tipo objeto  ###
        self.grilla = np.empty((5, 5), dtype=object)
        self.nutrientes = np.full((5, 5), 100) # comienzan con 100 nutrientes por celda

    def grilla_objetos(self):
        # No llenar todo, solo crear una bacteria inicial
        i, j = random.randint(0,4), random.randint(0,4)
        raza = random.choice(self.razas_disponibles)
        energia = random.randint(20, 100)
        resistente = random.choice([True, False])
        estado = "activa"
        id_bacteria = f"{raza}_{i}_{j}"
        self.grilla[i, j] = Bacteria(id_bacteria, raza, energia, resistente, estado)


    ### Grilla numerica (zeros) -> maneja los datos numericos ###
    def sincronizar_visual(self):
        self.grilla_visual = np.zeros((5, 5))

        # Recorrer la grilla y transformar segun el estado en un numero
        for i in range(5):
            for j in range(5):
                bacteria = self.grilla[i, j]

                if bacteria is None:
                    self.grilla_visual[i, j] = 0

                elif bacteria.get_estado() == "inactiva":
                    self.grilla_visual[i, j] = 2

                #elif bacteria.get_estado() == "biofilm":
                #    self.grilla_visual[i, j] = 4

                elif bacteria.get_estado() == "activa" and bacteria.get_resistente():
                    self.grilla_visual[i, j] = 3

                elif bacteria.get_estado() == "activa" and not bacteria.get_resistente():
                    self.grilla_visual[i, j] = 1

    def graficar_grilla(self):
        cmap = plt.cm.get_cmap('Set1', 5)
        fig, ax = plt.subplots(figsize=(5,5))
        cax = ax.matshow(self.grilla_visual, cmap=cmap)

        legend_elements = [
            Patch(facecolor=cmap(1/5), label='Bacteria activa'),
            Patch(facecolor=cmap(2/5), label='Bacteria muerta'),
            Patch(facecolor=cmap(3/5), label='Bacteria resistente'),
            #Patch(facecolor=cmap(4/5), label='Biofilm'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.45, 1))
        ax.set_xticks(np.arange(0, 5, 1))
        ax.set_yticks(np.arange(0, 5, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(color='gray', linestyle='-', linewidth=0.5)

        for i in range(5):
            for j in range(5):
                val = self.grilla_visual[i, j]
                if val > 0:
                    ax.text(j, i, int(val), va='center', ha='center', color='white', fontsize=12)

        plt.title("Estado actual de la colonia bacteriana (5x5")
        plt.tight_layout()
        plt.savefig("grilla_colonia.png")
        plt.close()


# CLASE Colonia
class Colonia:
    def __init__(self, ambiente):
        self.ambiente = ambiente
        #Recomendación Fabio -> lista de bacterias random ya creadas, para recorrerlas facil y manipular los datos
        self.bacterias = [
            self.ambiente.grilla[i, j]
            for i in range(5)
            for j in range(5)
            if self.ambiente.grilla[i, j] is not None
        ]

    def paso(self): 
        for i in range(5):
            for j in range(5):
                bacteria = self.ambiente.grilla[i, j]
                if bacteria and bacteria.get_estado() == "activa":
                    # 20% de probabilidad de morir por antibiótico si no es resistente
                    # el antibiótico es externo, por eso no va en los métodos de Bacteria
                    if not bacteria.get_resistente() and random.random() < 0.2:
                        bacteria.morir()
                        continue

                    consumido = bacteria.alimentar(self.ambiente.nutrientes[i, j])
                    self.ambiente.nutrientes[i, j] -= consumido
                    bacteria.mutar()

                    if bacteria.get_energia() < 20:
                        bacteria.morir()

                    hija = bacteria.dividirse() # aquí dividimos la bacteria, pero ¿dónde la ponemos?
                    if hija: # aquí se busca donde poner la bacteria hija
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            ni, nj = i + dx, j + dy
                            if 0 <= ni <5 and 0 <= nj <5 and self.ambiente.grilla[ni, nj] is None:
                                self.ambiente.grilla[ni, nj] = hija
                                self.bacterias.append(hija)
                                break
        print(f"[DEBUG] En ({i},{j}) -> {bacteria}")
        self.ambiente.sincronizar_visual()
        print(f"[VISUAL] Valor en visual ({i},{j}):", self.ambiente.grilla_visual[i, j])


    def depurar_grilla(self):
        print("\n=== Grilla de Estados de Bacterias (Texto) ===")
        for i in range(5):
            for j in range(5):
                b = self.ambiente.grilla[i, j]
                estado = b.get_estado() if b else "None"
                res = "R" if (b and b.get_resistente()) else "-"
                print(f"{estado[:1]}{res}", end=" ")
            print()

        print("\n=== Grilla Visual (Números) ===")
        print(self.ambiente.grilla_visual.astype(int))  


# INTERFAZ GTK INTEGRADA
class MiAplicacion(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.ejemplo.SimuladorColonia")
        self.ventana = None

        self.ambiente = Ambiente()
        self.ambiente.grilla_objetos()
        self.ambiente.sincronizar_visual()
        self.colonia = Colonia(self.ambiente)

    def do_activate(self):
        self.ventana = Gtk.ApplicationWindow(application=self)
        self.ventana.set_title("Simulador de Colonia Bacteriana")
        self.ventana.set_default_size(800, 600)

        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Simulador de Colonia Bacteriana"))
        header.set_show_title_buttons(True)

        menu = Gio.Menu()
        menu.append("Paso de simulación", "app.simular")
        menu.append("Mostrar grilla", "app.grafico")

        btn_menu = Gtk.MenuButton()
        btn_menu.set_icon_name("open-menu-symbolic")
        btn_menu.set_menu_model(menu)
        header.pack_end(btn_menu)

        self.ventana.set_titlebar(header)

        self.contenedor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_top=10)
        self.ventana.set_child(self.contenedor)

        self.label_estado = Gtk.Label(label="Simulación iniciada. Presione un botón para comenzar.")
        self.contenedor.append(self.label_estado)

        boton_paso = Gtk.Button(label="Ejecutar un paso")
        boton_paso.connect("clicked", self.on_paso_click)
        self.contenedor.append(boton_paso)

        boton_graficar = Gtk.Button(label="Mostrar Grilla")
        boton_graficar.connect("clicked", self.on_graficar_click)
        self.contenedor.append(boton_graficar)

        self.ventana.present()

    def on_paso_click(self, button):
        self.colonia.paso()
        self.label_estado.set_text("Paso de simulación ejecutado.")


    def on_graficar_click(self, button):
        self.ambiente.graficar_grilla()
        imagen = Gtk.Image.new_from_file("grilla_colonia.png")
        imagen.set_hexpand(True)
        imagen.set_vexpand(True)
        self.colonia.depurar_grilla()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(imagen)

        dialogo = Gtk.Dialog(
            title="Grilla de Bacterias",
            transient_for=self.ventana,
            modal=True
        )
        dialogo.set_default_size(900, 900)
        dialogo.get_content_area().append(scroll)
        dialogo.add_button("Cerrar", Gtk.ResponseType.CLOSE)
        dialogo.connect("response", lambda d, r: d.destroy())
        dialogo.show()


if __name__ == "__main__":
    app = MiAplicacion()
    app.run()

