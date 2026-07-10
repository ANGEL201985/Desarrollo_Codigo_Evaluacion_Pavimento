import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve


class ModeloWinklerFDM:

    def __init__(self, Lx, Ly, h, E, nu, k, nx, ny):
        self.Lx = Lx
        self.Ly = Ly

        self.h = h
        self.E = E
        self.nu = nu
        self.k = k

        self.nx = nx
        self.ny = ny

        self.dx = Lx / nx
        self.dy = Ly / ny

        # Rigidez a la flexión de la placa (kN·m)
        self.D = E * h**3 / (12 * (1 - nu**2))

        self.N = (nx + 1) * (ny + 1)
        self.K = lil_matrix((self.N, self.N))
        self.F = np.zeros(self.N)
        self.W = np.zeros(self.N)

    def numero(self, i, j):
        return j * (self.nx + 1) + i

    def ensamblar(self, tiene_junta=False, rigidez_junta=0.0):
        """Ensambla la matriz en formato de presión por unidad de área (kN/m²)."""
        self.K[:, :] = 0.0

        cx = self.D / (self.dx**4)
        cy = self.D / (self.dy**4)
        cxy = self.D / (self.dx**2 * self.dy**2)

        w_central = 6 * cx + 6 * cy + 8 * cxy

        vecinos = [
            (-1, 0, -4 * cx - 4 * cxy),
            (1, 0, -4 * cx - 4 * cxy),
            (0, -1, -4 * cy - 4 * cxy),
            (0, 1, -4 * cy - 4 * cxy),
            (-2, 0, cx),
            (2, 0, cx),
            (0, -2, cy),
            (0, 2, cy),
            (-1, -1, 2 * cxy),
            (1, -1, 2 * cxy),
            (-1, 1, 2 * cxy),
            (1, 1, 2 * cxy),
        ]

        for j in range(self.ny + 1):
            for i in range(self.nx + 1):
                n = self.numero(i, j)

                # En formulación por unidad de área, kw es directamente el módulo k
                kw = self.k

                self.K[n, n] += w_central + kw

                for di, dj, valor in vecinos:
                    ii = i + di
                    jj = j + dj

                    if 0 <= ii <= self.nx and 0 <= jj <= self.ny:
                        nv = self.numero(ii, jj)
                        self.K[n, nv] += valor
                    else:
                        ii_virtual = i - di if (ii < 0 or ii > self.nx) else ii
                        jj_virtual = j - dj if (jj < 0 or jj > self.ny) else jj

                        if (
                            0 <= ii_virtual <= self.nx
                            and 0 <= jj_virtual <= self.ny
                        ):
                            nv = self.numero(ii_virtual, jj_virtual)
                            self.K[n, nv] -= valor * 0.15

        # Restricción elástica perimetral de la junta (escalada a la dimensión del nodo)
        if tiene_junta:
            kspring = (rigidez_junta / (self.nx + 1)) / (self.dx * self.dy)
            for i in range(self.nx + 1):
                n = self.numero(i, self.ny)
                self.K[n, n] += kspring

    def aplicar_carga(self, P, x, y, largo=0.215, ancho=0.170):
        """Aplica la carga distribuyendo la PRESIÓN de contacto (kPa) en los nodos."""
        xmin = x - largo / 2
        xmax = x + largo / 2
        ymin = y - ancho / 2
        ymax = y + ancho / 2

        nodos = []
        for j in range(self.ny + 1):
            for i in range(self.nx + 1):
                xn = i * self.dx
                yn = j * self.dy
                if xmin <= xn <= xmax and ymin <= yn <= ymax:
                    nodos.append(self.numero(i, j))

        if len(nodos) == 0:
            distancias = []
            for j in range(self.ny + 1):
                for i in range(self.nx + 1):
                    xn = i * self.dx
                    yn = j * self.dy
                    d = np.sqrt((xn - x) ** 2 + (yn - y) ** 2)
                    distancias.append((d, self.numero(i, j)))
            distancias.sort()
            nodos = [distancias[0][1]]

        # CORRECCIÓN DE UNIDADES: q es Presión (kN/m²)
        area_huella = largo * ancho
        q = P / area_huella

        # Se aplica la presión directamente a los nodos afectados
        for nodo in nodos:
            self.F[nodo] -= q / len(nodos)

    def limpiar_cargas(self):
        self.F[:] = 0.0

    def limpiar_resultados(self):
        self.W[:] = 0.0

    def resolver(self):
        epsilon = 1e-10
        for i in range(self.N):
            self.K[i, i] += epsilon

        self.W = spsolve(self.K.tocsr(), self.F)
        return self.W