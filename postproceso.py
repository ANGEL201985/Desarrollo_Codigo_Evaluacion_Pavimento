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
        self.nu = modelo.nu

        self.W2 = self.W.reshape((self.ny + 1, self.nx + 1))

    # ==========================================================
    # DEFLEXIÓN
    # ==========================================================

    def deflexion_maxima(self):

        return np.max(np.abs(self.W2))

    # ==========================================================
    # REACCIÓN DE WINKLER
    # ==========================================================

    def reaccion(self):

        return np.abs(self.k * self.W2)

    # ==========================================================
    # MOMENTOS DE KIRCHHOFF
    # ==========================================================

    # ==========================================================
    # MOMENTOS DE KIRCHHOFF-LOVE
    # ==========================================================

    def momentos(self):

        #------------------------------------------------------
        # Primera derivada de la superficie de deflexión
        #------------------------------------------------------

        dw_dy, dw_dx = np.gradient(
            self.W2,
            self.dy,
            self.dx,
            edge_order=2
        )

        #------------------------------------------------------
        # Segundas derivadas
        #------------------------------------------------------

        d2w_dx2 = np.gradient(
            dw_dx,
            self.dx,
            axis=1,
            edge_order=2
        )

        d2w_dy2 = np.gradient(
            dw_dy,
            self.dy,
            axis=0,
            edge_order=2
        )

        #------------------------------------------------------
        # Derivada mixta
        # ∂²w/(∂x∂y)
        #------------------------------------------------------

        d2w_dxdy = np.gradient(
            dw_dx,
            self.dy,
            axis=0,
            edge_order=2
        )

        #------------------------------------------------------
        # Momentos de Kirchhoff-Love
        #------------------------------------------------------

        Mx = -self.D * (
            d2w_dx2 +
            self.nu * d2w_dy2
        )

        My = -self.D * (
            d2w_dy2 +
            self.nu * d2w_dx2
        )

        Mxy = -self.D * (
            1.0 - self.nu
        ) * d2w_dxdy

        return Mx, My, Mxy

    # ==========================================================
    # ESFUERZO PRINCIPAL MÁXIMO
    # ==========================================================

    def esfuerzo(self):

        Mx, My, Mxy = self.momentos()

        # Tensiones de flexión

        sigmax = 6 * Mx / (self.h ** 2)

        sigmay = 6 * My / (self.h ** 2)

        # Cortante equivalente

        tau = 6 * Mxy / (self.h ** 2)

        # Esfuerzo principal máximo

        sigma1 = (
            (sigmax + sigmay) / 2 +
            np.sqrt(
                ((sigmax - sigmay) / 2) ** 2 +
                tau ** 2
            )
        )

        return np.abs(sigma1)/1000

    # ==========================================================
    # REPORTE
    # ==========================================================

    def resumen(self):

        Mx, My, Mxy = self.momentos()

        sigma = self.esfuerzo()

        print()

        print("=" * 70)
        print(" REPORTE NUMÉRICO DEL POSTPROCESO ")
        print("=" * 70)

        print(f"Deflexión máxima           : {self.deflexion_maxima()*1000:.3f} mm")

        print(f"Reacción máxima            : {np.max(self.reaccion()):.3f} kPa")

        print(f"Momento Mx                 : {np.max(np.abs(Mx)):.3f} kN·m/m")

        print(f"Momento My                 : {np.max(np.abs(My)):.3f} kN·m/m")

        print(f"Momento torsional Mxy      : {np.max(np.abs(Mxy)):.3f} kN·m/m")

        print(f"Esfuerzo máximo            : {np.max(sigma):.3f} MPa")

        print("=" * 70)

    # ==========================================================
    # MAPA DE DEFLEXIONES
    # ==========================================================

    def mapa_deflexion(self):

        plt.figure(figsize=(7,5))

        plt.imshow(
            -1000*self.W2,
            origin="lower",
            cmap="jet",
            extent=[
                0,
                self.modelo.Lx,
                0,
                self.modelo.Ly
            ]
        )

        plt.colorbar(label="Deflexión (mm)")

        plt.xlabel("X (m)")
        plt.ylabel("Y (m)")

        plt.title("Mapa de Deflexiones")

        plt.tight_layout()

        plt.savefig(
            "Mapa_Deflexiones.png",
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()

    # ==========================================================
    # MAPA DE ESFUERZOS
    # ==========================================================

    def mapa_esfuerzo(self):

        sigma = self.esfuerzo()

        plt.figure(figsize=(7,5))

        plt.imshow(
            sigma,
            origin="lower",
            cmap="hot",
            extent=[
                0,
                self.modelo.Lx,
                0,
                self.modelo.Ly
            ]
        )

        plt.colorbar(label="MPa")

        plt.xlabel("X (m)")
        plt.ylabel("Y (m)")

        plt.title("Mapa de Esfuerzos")

        plt.tight_layout()

        plt.savefig(
            "Mapa_Esfuerzos.png",
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()

    # ==========================================================
    # DEFORMADA 3D
    # ==========================================================

    def deformada3D(self):

        X = np.linspace(
            0,
            self.modelo.Lx,
            self.nx + 1
        )

        Y = np.linspace(
            0,
            self.modelo.Ly,
            self.ny + 1
        )

        X, Y = np.meshgrid(X, Y)

        fig = plt.figure(figsize=(8,6))

        ax = fig.add_subplot(
            111,
            projection="3d"
        )

        superficie = ax.plot_surface(
            X,
            Y,
            -1000*self.W2,
            cmap="viridis",
            edgecolor="none"
        )

        fig.colorbar(
            superficie,
            shrink=0.6,
            label="mm"
        )

        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_zlabel("Deflexión (mm)")

        ax.set_title("Deformada 3D")

        plt.tight_layout()

        plt.savefig(
            "Deformada3D.png",
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()