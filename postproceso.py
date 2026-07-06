import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class PostProceso:
    def __init__(self, modelo):
        self.modelo = modelo
        self.W = modelo.W
        self.nx = modelo.nx
        self.ny = modelo.ny
        self.dx = modelo.dx
        self.dy = modelo.dy
        self.D = modelo.D
        self.k = modelo.k
        self.h = modelo.h
        self.nu = modelo.nu  # Recuperamos Poisson para la ley constitutiva de la placa

        # Guardar en formato bidimensional (Matriz)
        self.W2 = self.W.reshape((self.ny + 1, self.nx + 1))

    #==========================================================
    # DEFLEXIÓN MÁXIMA
    #==========================================================
    def deflexion_maxima(self):
        # Usamos el valor absoluto porque la carga empuja hacia abajo (valores negativos)
        return np.max(np.abs(self.W2))

    #==========================================================
    # REACCIÓN DE WINKLER
    #==========================================================
    def reaccion(self):
        # k * w nos da la presión transmitida al suelo en kPa
        return np.abs(self.k * self.W2)

    #==========================================================
    # MOMENTOS FLECTORES (Ecuaciones de Kirchhoff Acopladas)
    #==========================================================
    def momentos(self):
        Mx = np.zeros_like(self.W2)
        My = np.zeros_like(self.W2)

        # 1. Calculamos las primeras derivadas por separado para cada eje
        # grad_y corresponde a las filas (eje 0), grad_x a las columnas (eje 1)
        grad_y, grad_x = np.gradient(self.W2)
        
        # 2. Volvemos a derivar respecto a sus propios ejes para obtener las segundas derivadas
        d2w_dy2 = np.gradient(grad_y, axis=0) # Segunda derivada respecto a Y
        d2w_dx2 = np.gradient(grad_x, axis=1) # Segunda derivada respecto a X

        # 3. Escalamos por los diferenciales de la malla (dx y dy)
        d2x = d2w_dx2 / (self.dx ** 2)
        d2y = d2w_dy2 / (self.dy ** 2)

        # 4. Aplicamos la ley constitutiva acoplada por el coeficiente de Poisson
        Mx = -self.D * (d2x + self.nu * d2y)
        My = -self.D * (d2y + self.nu * d2x)

        return Mx, My

    #==========================================================
    # ESFUERZO DE FLEXOTRACCIÓN
    #==========================================================
    def esfuerzo(self):
        Mx, My = self.momentos()
        
        # Ecuación clásica sigma = 6M / h^2
        sigmax = 6 * np.abs(Mx) / (self.h ** 2)
        sigmay = 6 * np.abs(My) / (self.h ** 2)

        # Devolvemos el esfuerzo envolvente más crítico para cada punto
        return np.maximum(sigmax, sigmay)

    #==========================================================
    # REPORTE INGENIERIL EN CONSOLA
    #==========================================================
    def resumen(self):
        Mx, My = self.momentos()
        esf_max = np.max(self.esfuerzo())
        
        print()
        print("=" * 70)
        print("     REPORTE NUMÉRICO COMPLETO: APARTADO DE POST-PROCESAMIENTO FDM")
        print("=" * 70)
        print(f"Deflexión Máxima Absoluta      : {self.deflexion_maxima() * 1000:.3f} mm")
        print(f"Reacción Máxima de Subrasante  : {np.max(self.reaccion()):.3f} kPa")
        print(f"Momento Flector Crítico Mx     : {np.max(np.abs(Mx)):.3f} kN·m/m")
        print(f"Momento Flector Crítico My     : {np.max(np.abs(My)):.3f} kN·m/m")
        print(f"Esfuerzo Máximo por Tensión    : {esf_max:.3f} MPa")
        print("=" * 70)

    #==========================================================
    # MAPA DE DEFLEXIONES
    #==========================================================
    def mapa_deflexion(self):
        plt.figure(figsize=(7, 5))
        # Multiplicamos por -1000 para graficar el asentamiento positivo hacia abajo de forma visual
        plt.imshow(
            self.W2 * -1000,
            origin="lower",
            cmap="jet",
            extent=[0, self.modelo.Lx, 0, self.modelo.Ly]
        )
        plt.colorbar(label="Deflexión hacia abajo (mm)")
        plt.xlabel("Eje X (m)")
        plt.ylabel("Eje Y (m)")
        plt.title("Mapa Térmico de Deflexiones Verticales")
        plt.tight_layout()
        plt.show()

    #==========================================================
    # MAPA DE ESFUERZOS
    #==========================================================
    def mapa_esfuerzo(self):
        sigma = self.esfuerzo()
        plt.figure(figsize=(7, 5))
        plt.imshow(
            sigma,
            origin="lower",
            cmap="hot",
            extent=[0, self.modelo.Lx, 0, self.modelo.Ly]
        )
        plt.colorbar(label="Esfuerzo de Tracción (MPa)")
        plt.xlabel("Eje X (m)")
        plt.ylabel("Eje Y (m)")
        plt.title("Distribución de Esfuerzos de Flexotracción")
        plt.tight_layout()
        plt.show()

    #==========================================================
    # DEFORMADA 3D
    #==========================================================
    def deformada3D(self):
        X = np.linspace(0, self.modelo.Lx, self.nx + 1)
        Y = np.linspace(0, self.modelo.Ly, self.ny + 1)
        X, Y = np.meshgrid(X, Y)

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="3d")

        # Multiplicamos por -1000 para que la deformada se hunda visualmente en el espacio Z
        surf = ax.plot_surface(
            X, Y, self.W2 * -1000,
            cmap="viridis",
            edgecolor='none'
        )
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label="mm")
        ax.set_xlabel("Eje X (m)")
        ax.set_ylabel("Eje Y (m)")
        ax.set_zlabel("Deflexión (mm)")
        ax.set_title("Deformada Tridimensional de la Losa de Pavimento")
        plt.show()