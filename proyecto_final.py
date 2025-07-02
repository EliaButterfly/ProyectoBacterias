#commit 1
import gi
import random
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
from matplotlib.patches import Patch  # Para crear leyendas 

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject

#commit 2

# CLASE Bacteria
class Bacteria:
    def __init__(self, id_bacteria, raza, energia, resistente, estado):
        self.__raza = raza 
        self.__energia = energia 
        self.__resistente = resistente
        self.__estado = estado  # "activa" o "inactiva"
        self.__id = id_bacteria
        # commit 14

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
        consumo = random.randint(5, 15)  # Número aleatorio entre 5 y 15 
        consumido = min(consumo, nutrientes_disponibles)
        self.__energia += consumido
        return consumido

 # commit 11

    def dividirse(self):
        # Si tiene suficiente energía, se divide (mitosis)
        if self.__energia >= 50 and self.__estado == "activa":
            self.__energia = self.__energia // 2
            nueva_id = f"{self.__id}_hija"
            return Bacteria(nueva_id, self.__raza, self.__energia, self.__resistente, "activa")
        return None

    def mutar(self):
        # 25% de probabilidad de mutar y volverse resistente
        # random.random() devuelve float en [0.0, 1.0)
        if self.__estado == "activa" and not self.__resistente:
            if random.random() < 0.25:
                self.__resistente = True

    def morir(self):
        self.__estado = "inactiva"


# CLASE Ambiente

# commit 5 - commit 12
class Ambiente:
    def __init__(self):
        self.razas_disponibles = ["cocos", "bacilos", "espirilos"]
        self.grilla = np.empty((5, 5), dtype=object)  # Grilla de objetos Bacteria o None
        self.nutrientes = np.full((5, 5), 100)  # Cada celda parte con 100 nutrientes
        self.contador_pasos = 0
        self.factor_ambiental = 0.2  # antibióticos 

# commit 6 - commit 13
    def grilla_objetos(self):
        # Agrega una bacteria en una posición aleatoria libre
        i, j = random.randint(0, 4), random.randint(0, 4)
        raza = random.choice(self.razas_disponibles)
        energia = random.randint(20, 100)
        resistente = False # antes eran true/false random, pero muchas resistentes es fome
        estado = "activa"
        id_bacteria = f"{raza}_{i}_{j}"
        self.grilla[i, j] = Bacteria(id_bacteria, raza, energia, resistente, estado)

    def actualizar_nutrientes(self):
        # Regenera entre 0 y 2 nutrientes por celda (np.random.randint lo hace para cada celda)
        self.nutrientes += np.random.randint(0, 3, size=(5, 5))
        self.nutrientes = np.clip(self.nutrientes, 0, 100)  # np.clip limita valores entre 0 y 100

    def difundir_nutrientes(self):
        # Difusión: cada celda se promedia con sus vecinos ortogonales (arriba, abajo, izq, der)
        nueva = self.nutrientes.copy()  # .copy() crea una copia separada
        for i in range(5):
            for j in range(5):
                # vecinos = posiciones vecinas válidas -> usa la misma lógica que posicionar una bacteria hija
                vecinos = [(i+di, j+dj) for di, dj in [(-1,0),(1,0),(0,-1),(0,1)] 
                           if 0 <= i+di < 5 and 0 <= j+dj < 5]
                promedio = sum(self.nutrientes[vi, vj] for vi, vj in vecinos) // len(vecinos)
                nueva[i, j] = (self.nutrientes[i, j] + promedio) // 2  # Valor medio entre celda actual y vecinos
        self.nutrientes = nueva

    def aplicar_antibiotico(self):
        eliminadas = 0
        for i in range(5):
            for j in range(5):
                b = self.grilla[i, j]
                if b and b.get_estado() == "activa" and not b.get_resistente():
                    if random.random() < self.factor_ambiental:
                        b.morir()
                        eliminadas += 1
        print(f"[EVENTO] Antibiótico aplicado. Bacterias eliminadas: {eliminadas}")


    def aplicar_ambiente(self):
        # Actualiza el entorno (regenera y difunde nutrientes)
        self.actualizar_nutrientes()
        self.difundir_nutrientes()

# Pasar de objetos a numeros para graficar

    def sincronizar_visual(self):
        # Crea una grilla visual numérica con valores representativos:
        # 0 = vacío, 1 = activa no resistente, 2 = inactiva, 3 = activa resistente

    # commit 7.
        self.grilla_visual = np.zeros((5, 5))  # Grilla numérica para visualización
        for i in range(5):
            for j in range(5):
                bacteria = self.grilla[i, j]
                if bacteria is None:
                    self.grilla_visual[i, j] = 0
                elif bacteria.get_estado() == "inactiva":
                    self.grilla_visual[i, j] = 2
                elif bacteria.get_estado() == "activa" and bacteria.get_resistente():
                    self.grilla_visual[i, j] = 3
                elif bacteria.get_estado() == "activa" and not bacteria.get_resistente():
                    self.grilla_visual[i, j] = 1

    # commit 8 - commit 15
    def graficar_grilla(self):
        # Guarda foto de la grilla actual como imagen PNG y con nombre del paso
        self.contador_pasos += 1
        nombre_archivo = f"grilla_colonia_paso_{self.contador_pasos}.png" # despues usamos plt.savefig

        cmap = plt.cm.get_cmap('Set1', 4)  # Mapa de colores con 4 clases
        fig, ax = plt.subplots(figsize=(5,5))

        # Representa la grilla visual como una imagen de colores (matshow)
        cax = ax.matshow(self.grilla_visual, cmap=cmap)

        # Recuadro en la grilla que muestra que significa cada color 
        legend_elements = [
            Patch(facecolor=cmap(1/3), label='1 = Bacteria no resistente'),
            Patch(facecolor=cmap(2/3), label='2 = Bacteria inactiva'),
            Patch(facecolor=cmap(3/4), label='3 = Bacteria resistente'),
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.45, 1))
        ax.set_xticks(np.arange(0, 5, 1))
        ax.set_yticks(np.arange(0, 5, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(color='gray', linestyle='-', linewidth=0.5)

        # Coloca el número (estado) en cada celda si corresponde
        for i in range(5):
            for j in range(5):
                val = self.grilla_visual[i, j]
                if val > 0:
                    ax.text(j, i, int(val), va='center', ha='center', color='white', fontsize=12)

        
        # Titulo y guardado del archivo
        plt.title("  Colonia bacteriana (5x5)   ")
        plt.tight_layout()
        plt.savefig(nombre_archivo)
        plt.close()
        self.nombre_ultima_imagen = nombre_archivo # así las imágenes se llaman paso1 paso2 etc

# CLASE Colonia

 # commit 9
class Colonia:
    def __init__(self, ambiente):
        self.ambiente = ambiente
        self.historial = []  # Guarda datos por paso
        # Lista de bacterias (para recorrerlas)
        self.bacterias = [
            self.ambiente.grilla[i, j]
            for i in range(5)
            for j in range(5)
            if self.ambiente.grilla[i, j] is not None
        ]

# commit 10
    def paso(self):
        self.ambiente.aplicar_ambiente()  # Actualiza y difunde nutrientes
        print("\n>>> Ejecutando paso de simulación")
        for i in range(5):
            for j in range(5):
                bacteria = self.ambiente.grilla[i, j]
                if bacteria and bacteria.get_estado() == "activa":
                    # Muestra información detallada de cada bacteria
                    print(f"[INFO] Bacteria ID: {bacteria._Bacteria__id} | Pos: ({i},{j}) | Raza: {bacteria._Bacteria__raza} | Energía: {bacteria.get_energia()} | Resistente: {bacteria.get_resistente()} | Estado: {bacteria.get_estado()}")

                    # 50% de probabilidad de morir si no es resistente (muerte por antibiótico)
                    if not bacteria.get_resistente() and random.random() < 0.5:
                        bacteria.morir()
                        print("  -> Murió por antibiótico (no era resistente)")
                        continue

                    # La bacteria consume nutrientes disponibles en su celda
                    consumido = bacteria.alimentar(self.ambiente.nutrientes[i, j])
                    self.ambiente.nutrientes[i, j] -= consumido
                    print(f"  -> Se alimentó con {consumido} nutrientes")

                    bacteria.mutar()  # Puede volverse resistente

                    # Si la energía es baja (< 20), la bacteria muere
                    if bacteria.get_energia() < 20:
                        bacteria.morir()
                        print("  -> Murió por baja energía")

                    # División bacteriana: crea hija si tiene suficiente energía
                    hija = bacteria.dividirse()
                    if hija:
                        # Busca un espacio vacío en las 4 celdas vecinas directas (arriba, abajo, izquierda, derecha)
                        for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nuevo_i, nuevo_j = i + x, j + y

                            # verificamos que la nueva posicion este en el rago de la grilla
                            if 0 <= nuevo_i < 5 and 0 <= nuevo_j < 5 and self.ambiente.grilla[nuevo_i, nuevo_j] is None: # si la celda está vacía
                                self.ambiente.grilla[nuevo_i, nuevo_j] = hija  # Coloca la hija en la grilla
                                self.bacterias.append(hija)  # Agrega la hija a la lista de bacterias
                                print(f"  -> Se dividió. Nueva hija ID: {hija._Bacteria__id} en ({nuevo_i},{nuevo_j})")
                                break

 # Guardar datos para gráficas
        activas = inactivas = resistentes = 0
        for i in range(5):
            for j in range(5):
                b = self.ambiente.grilla[i, j]
                if b:
                    if b.get_estado() == "activa":
                        activas += 1
                        if b.get_resistente():
                            resistentes += 1
                    else:
                        inactivas += 1
        self.historial.append({
            "paso": self.ambiente.contador_pasos,
            "activas": activas,
            "inactivas": inactivas,
            "resistentes": resistentes
        })

        self.ambiente.sincronizar_visual()  # Actualiza la grilla visual
        print("\n[VISUALIZACIÓN ACTUALIZADA]")

    def reporte_estado(self):
        # Muestra la grilla textual: primeras letras de los estados y 'R' si es resistente
        print("\n=== Grilla de Estados de Bacterias (Texto) ===")
        for i in range(5):
            for j in range(5):
                b = self.ambiente.grilla[i, j]
                estado = b.get_estado() if b else "None"
                res = "R" if (b and b.get_resistente()) else "-"
                print(f"{estado[:1]}{res}", end=" ")
            print()

        print("\n=== Grilla Visual (Números) ===")
        print(self.ambiente.grilla_visual.astype(int))  # Imprime los valores numéricos de la grilla visual

# CLASE Simulacion
class Simulacion:
    def __init__(self, colonia):
        self.colonia = colonia

# Grafica lineal
    def graficar_evolucion(self):
        historial = self.colonia.historial
        if not historial:
            print("No hay datos para graficar.")
            return

        pasos = [d["paso"] for d in historial]
        activas = [d["activas"] for d in historial]
        inactivas = [d["inactivas"] for d in historial]
        resistentes = [d["resistentes"] for d in historial]

        plt.figure(figsize=(8, 5))
        plt.plot(pasos, activas, label="Activas", color="green", marker="o")
        plt.plot(pasos, inactivas, label="Inactivas", color="red", marker="x")
        plt.plot(pasos, resistentes, label="Resistentes", color="blue", linestyle="--")
        plt.xlabel("Paso de simulación")
        plt.ylabel("Cantidad de bacterias")
        plt.title("Evolución de la colonia bacteriana")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("evolucion_colonia.png")
        plt.close()
        print("Gráfico de evolución guardado como 'evolucion_colonia.png'")

# Grafica circular (activas,inactivas,resistentes)
    def graficar_resistencias(self):
        ambiente = self.colonia.ambiente
        activas = inactivas = resistentes = 0
        for i in range(5):
            for j in range(5):
                b = ambiente.grilla[i, j]
                if b:
                    if b.get_estado() == "activa":
                        activas += 1
                        if b.get_resistente():
                            resistentes += 1
                    else:
                        inactivas += 1

        labels = ["Activas", "Inactivas", "Resistentes"]
        valores = [activas, inactivas, resistentes]
        colores = ["green", "red", "blue"]

        plt.figure(figsize=(6, 6))
        plt.pie(valores, labels=labels, colors=colores, autopct="%1.1f%%")
        plt.title("Distribución actual de bacterias")
        plt.tight_layout()
        plt.savefig("distribucion_colonia.png")
        plt.close()
        print("Gráfico de torta guardado como 'distribucion_colonia.png'")



# INTERFAZ GTK

class MiAplicacion(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.ejemplo.SimuladorColonia")
        self.ventana = None
        self.ambiente = Ambiente()  # instancia a Ambiente
        self.ambiente.grilla_objetos()  # Crea una bacteria inicial
        self.ambiente.sincronizar_visual()

        self.colonia = Colonia(self.ambiente)  # instancia a Colonia
        self.simulacion = Simulacion(self.colonia)  # instancia a Simulacion

        self.add_action(Gio.SimpleAction.new("exportar_csv", None))
        self.lookup_action("exportar_csv").connect("activate", self.on_exportar_csv)
        self.add_action(Gio.SimpleAction.new("graficar_evolucion", None))
        self.lookup_action("graficar_evolucion").connect("activate", self.on_graficar_evolucion)

# commit 3
    def do_activate(self):
        # Ventana principal
        self.ventana = Gtk.ApplicationWindow(application=self)
        self.ventana.set_title("Simulador de Colonia Bacteriana")
        self.ventana.set_default_size(800, 600)

# commit 4
        # HeaderBar con menú (el borde superior con un boton menú)
        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Simulador de Colonia Bacteriana"))
        header.set_show_title_buttons(True)

        # Menú desplegable con acciones
        menu = Gio.Menu()
        menu.append("Exportar CSV", "app.exportar_csv")
        menu.append("Graficar evolución", "app.graficar_evolucion")

        btn_menu = Gtk.MenuButton()
        btn_menu.set_icon_name("open-menu-symbolic")
        btn_menu.set_menu_model(menu)
        header.pack_end(btn_menu)

        self.ventana.set_titlebar(header)

        # Contenedor vertical para los botones y mensajes
        self.contenedor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin_top=10)
        self.ventana.set_child(self.contenedor)

        # Etiqueta de estado (información al usuario)
        self.label_estado = Gtk.Label(label="Simulación iniciada. Presione un botón para comenzar.")
        self.contenedor.append(self.label_estado)

        # Botón para ejecutar un paso de simulación
        boton_paso = Gtk.Button(label="Ejecutar un paso")
        boton_paso.connect("clicked", self.on_paso_click)
        self.contenedor.append(boton_paso)

        # Botón para graficar la grilla actual
        boton_graficar = Gtk.Button(label="Mostrar Grilla")
        boton_graficar.connect("clicked", self.on_graficar_click)
        self.contenedor.append(boton_graficar)

        # Botón para agregar una nueva bacteria
        boton_bacterias = Gtk.Button(label="Agregar Bacteria")
        boton_bacterias.connect("clicked", self.on_agregar_bacterias)
        self.contenedor.append(boton_bacterias)

        # Botón para aplicar antibiótico
        boton_antibiotico = Gtk.Button(label="Aplicar Antibiótico")
        boton_antibiotico.connect("clicked", self.on_aplicar_antibiotico)
        self.contenedor.append(boton_antibiotico)

        self.ventana.present()

    # métodos asociados a botones (lo que pasa cuando das click)
    def on_paso_click(self, button):
        # Ejecuta un paso de simulación cuando se hace clic
        self.colonia.paso()
        self.label_estado.set_text(f"Paso {self.ambiente.contador_pasos} de simulación ejecutado.")

    def on_graficar_click(self, button):
        # Muestra la grilla bacteriana en una ventana emergente
        self.ambiente.graficar_grilla()

        # Crea un widget Gtk.Image con la última imagen generada
        imagen = Gtk.Image.new_from_file(self.ambiente.nombre_ultima_imagen)
        imagen.set_hexpand(True)
        imagen.set_vexpand(True)

        # imprime en consola la grilla
        self.colonia.reporte_estado()

        # Scroll para visualizar imagen grande (sin scroll aparece una imagen minúscula)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(imagen)

        # Diálogo para visualizar la grilla
        dialogo = Gtk.Dialog(
            title="Grilla de Bacterias",
            transient_for=self.ventana,
            modal=True
        )
        dialogo.set_default_size(900, 900)
        dialogo.get_content_area().append(scroll)
        dialogo.add_button("Cerrar", Gtk.ResponseType.CLOSE)
        dialogo.connect("response", lambda d, r: d.destroy())
        dialogo.present()

    # Agregar bacteria (no paso)
    def on_agregar_bacterias(self, button):
        # Agrega una bacteria en una celda aleatoria libre
        self.ambiente.grilla_objetos()

        # Actualiza la grilla visual para reflejar la nueva bacteria
        self.ambiente.sincronizar_visual()

        self.label_estado.set_text("Bacteria creada.")

    # Aplicar antibiótico
    def on_aplicar_antibiotico(self, button):
        self.ambiente.aplicar_antibiotico()
        self.ambiente.sincronizar_visual()
        self.label_estado.set_text("Antibiótico aplicado a la colonia.")

    # Exportar csv
    def exportar_csv(self):
        datos = []
        for i in range(5):
            for j in range(5):
                b = self.ambiente.grilla[i, j]
                if b:
                    fila = {
                        "fila": i,
                        "columna": j,
                        "id": b._Bacteria__id,
                        "raza": b._Bacteria__raza,
                        "energia": b.get_energia(),
                        "resistente": b.get_resistente(),
                        "estado": b.get_estado()
                    }
                    datos.append(fila)

        df = pd.DataFrame(datos)
        df.to_csv("estado_colonia.csv", index=False)
        print("Archivo CSV exportado: estado_colonia.csv")
        self.label_estado.set_text("Archivo CSV exportado con éxito.")

    def on_exportar_csv(self, action, param):  # para conectar con menú (porque el boton está en el menú)
        self.exportar_csv()

    # Graficar Evolución
    def on_graficar_evolucion(self, action, param):
        self.simulacion.graficar_evolucion()
        self.simulacion.graficar_resistencias()

        # Crea imágenes Gtk a partir de los archivos generados
        imagen_crecimiento = Gtk.Image.new_from_file("evolucion_colonia.png")
        imagen_resistencia = Gtk.Image.new_from_file("distribucion_colonia.png")
        imagen_crecimiento.set_hexpand(True)
        imagen_crecimiento.set_vexpand(True)
        imagen_resistencia.set_hexpand(True)
        imagen_resistencia.set_vexpand(True)

        # Contenedor vertical para las imágenes
        box_imagenes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=10)
        box_imagenes.append(Gtk.Label(label="Gráfico: Evolución de bacterias activas"))
        box_imagenes.append(imagen_crecimiento)
        box_imagenes.append(Gtk.Label(label="Gráfico: Distribución actual de la colonia"))
        box_imagenes.append(imagen_resistencia)

        # Scroll único para ambas imágenes
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(box_imagenes)

        # Diálogo para mostrar ambas gráficas
        dialogo = Gtk.Dialog(
            title="Evolución de la colonia",
            transient_for=self.ventana,
            modal=True
        )
        dialogo.set_default_size(900, 1000)
        dialogo.get_content_area().append(scroll)
        dialogo.add_button("Cerrar", Gtk.ResponseType.CLOSE)
        dialogo.connect("response", lambda d, r: d.destroy())
        dialogo.present()

if __name__ == "__main__":
    app = MiAplicacion()
    app.run()
 

    