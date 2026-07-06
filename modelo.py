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

        # Rigidez a la flexión (Kirchhoff)
        self.D = E * (h**3) / (12 * (1 - nu**2))

        self.N = (nx + 1) * (ny + 1)
        self.K = lil_matrix((self.N, self.N))
        self.F = np.zeros(self.N)
        self.W = np.zeros(self.N)

    def numero(self, i, j):
        return j * (self.nx + 1) + i

    def ensamblar(self, tiene_junta=False, rigidez_junta=0.0):
        # Coeficientes del operador biarmónico para malla rectangular: d4w/dx4 + 2*d4w/(dx2*dy2) + d4w/dy4
        cx = self.D / (self.dx**4)
        cy = self.D / (self.dy**4)
        cxy = self.D / ((self.dx**2) * (self.dy**2))

        # Nodo central (i, j)
        w_central = 6 * cx + 6 * cy + 8 * cxy

        for j in range(self.ny + 1):
            for i in range(self.nx + 1):
                n = self.numero(i, j)
                
                # Contribución de la placa + el resorte de Winkler del suelo
                self.K[n, n] += w_central + self.k

                # Stencil de Diferencias Finitas discretizado para dx != dy
                vecinos = [
                    # Primer anillo (Inmediatos)
                    (-1,  0, -4 * cx - 4 * cxy), # (i-1, j)
                    ( 1,  0, -4 * cx - 4 * cxy), # (i+1, j)
                    ( 0, -1, -4 * cy - 4 * cxy), # (i, j-1)
                    ( 0,  1, -4 * cy - 4 * cxy), # (i, j+1)
                    # Segundo anillo (Salto doble)
                    (-2,  0, cx),                # (i-2, j)
                    ( 2,  0, cx),                # (i+2, j)
                    ( 0, -2, cy),                # (i, j-2)
                    ( 0,  2, cy),                # (i, j+2)
                    # Esquinas del término cruzado d4w/(dx2*dy2)
                    (-1, -1, 2 * cxy),           # (i-1, j-1)
                    ( 1, -1, 2 * cxy),           # (i+1, j-1)
                    (-1,  1, 2 * cxy),           # (i-1, j+1)
                    ( 1,  1, 2 * cxy)            # (i+1, j+1)
                ]

                for di, dj, val in vecinos:
                    ii = i + di
                    jj = j + dj

                    if 0 <= ii <= self.nx and 0 <= jj <= self.ny:
                        nv = self.numero(ii, jj)
                        self.K[n, nv] += val
                    else:
                        # Tratamiento cinemático de bordes libres (Reflexión de curvatura virtual)
                        # Esto simula los "ghost nodes" absorbiendo la rigidez simétricamente
                        ii_virtual = i - di if ii < 0 or ii > self.nx else i
                        jj_virtual = j - dj if jj < 0 or jj > self.ny else j
                        if 0 <= ii_virtual <= self.nx and 0 <= jj_virtual <= self.ny:
                            nv_virtual = self.numero(ii_virtual, jj_virtual)
                            self.K[n, nv_virtual] += val

        # Acoplamiento físico de las barras de amarre en la junta longitudinal (si aplica)
        if tiene_junta:
            # Asumimos la junta en el borde longitudinal superior (j = ny) para conectar con el medio paño
            for idx_x in range(self.nx + 1):
                n_junta = self.numero(idx_x, self.ny)
                self.K[n_junta, n_junta] += rigidez_junta

    def aplicar_carga(self, P, x, y):
        # Mapeo de coordenadas físicas a índices discretos de la malla
        ix = int(np.clip(round(x / self.dx), 0, self.nx))
        iy = int(np.clip(round(y / self.dy), 0, self.ny))
        
        n = self.numero(ix, iy)
        # Signo negativo indica carga vertical descendente
        self.F[n] = -P

    def resolver(self):
        # Resolver el sistema disperso eficiente utilizando CSR
        self.W = spsolve(self.K.tocsr(), self.F)
        return self.W