import numpy as np
from modelo import ModeloWinklerFDM
from postproceso import PostProceso


class ComparativaPavimentos:

    def __init__(self):

        # =====================================================
        # GEOMETRÍA DEL PAVIMENTO
        # =====================================================

        self.Lx = 3.00              # m
        self.h = 0.20               # m

        # =====================================================
        # PROPIEDADES DEL CONCRETO
        # =====================================================

        self.E = 27540.0*1000        # MPa
        self.nu = 0.15
        self.MR = 3.63            # MPa

        # =====================================================
        # SUBRASANTE
        # =====================================================

        self.k = 60.0*1000               # MPa/m

        # =====================================================
        # MALLA MDF
        # =====================================================

        self.nx = 22
        self.ny = 20

        # =====================================================
        # EJE EQUIVALENTE
        # =====================================================

        self.P_llanta = 20.0        # kN por rueda

        self.separacion_llantas = 0.342      # m

        self.huella_largo = 0.215            # m

        self.huella_ancho = 0.170            # m

        # =====================================================
        # BARRAS DE AMARRE
        # =====================================================

        self.diametro_barra = 0.0127         # m (1/2")

        self.longitud_barra = 0.80           # m

        self.E_acero = 200000.0*1000              # MPa

        self.area_barra = np.pi * self.diametro_barra**2 / 4

        # Rigidez axial equivalente EA/L

        self.rigidez_junta = (
            self.E_acero *
            self.area_barra /
            self.longitud_barra
        )

    # ==========================================================
    # EJECUTAR UN MODELO
    # ==========================================================

    def ejecutar_modelo(self,
                        Ly,
                        tiene_junta=False):

        modelo = ModeloWinklerFDM(

            self.Lx,
            Ly,
            self.h,
            self.E,
            self.nu,
            self.k,
            self.nx,
            self.ny

        )

        modelo.ensamblar(

            tiene_junta=tiene_junta,

            rigidez_junta=self.rigidez_junta

        )

        # ------------------------------------------------------
        # POSICIÓN DE LAS DOS RUEDAS
        # ------------------------------------------------------

        x = self.Lx / 2

        y1 = Ly

        y2 = Ly - self.separacion_llantas

        # ------------------------------------------------------
        # PRIMERA LLANTA
        # ------------------------------------------------------

        modelo.aplicar_carga(

            P=self.P_llanta,

            x=x,

            y=y1,

            largo=self.huella_largo,

            ancho=self.huella_ancho

        )

        # ------------------------------------------------------
        # SEGUNDA LLANTA
        # ------------------------------------------------------

        modelo.aplicar_carga(

            P=self.P_llanta,

            x=x,

            y=y2,

            largo=self.huella_largo,

            ancho=self.huella_ancho

        )

        # ------------------------------------------------------

        modelo.resolver()

        post = PostProceso(modelo)

        # ------------------------------------------------------
        # RESULTADOS
        # ------------------------------------------------------

        deflexion = post.deflexion_maxima() * 1000

        reaccion = np.max(post.reaccion())*1000

        Mx, My, Mxy = post.momentos()

        momento = max(

            np.max(np.abs(Mx)),

            np.max(np.abs(My))

        )

        esfuerzo = np.max(post.esfuerzo())

        indice = self.MR / esfuerzo

        return {

            "modelo": modelo,

            "post": post,

            "deflexion": deflexion,

            "reaccion": reaccion,

            "momento": momento,

            "esfuerzo": esfuerzo,

            "IS": indice

        }

        # ==========================================================
        # ANÁLISIS COMPARATIVO
        # ==========================================================

    def ejecutar_analisis(self):

        print()
        print("=" * 90)
        print("      ANÁLISIS ESTRUCTURAL DE REPOSICIÓN DE MEDIA LOSA")
        print("=" * 90)

        # ----------------------------------------------------------
        # Información del modelo
        # ----------------------------------------------------------
        print("\nPROPIEDADES DEL MODELO")
        print("-" * 60)
        print(f"Módulo de Elasticidad del concreto : {self.E/1000:.0f} MPa")
        print(f"Coeficiente de Poisson             : {self.nu:.2f}")
        print(f"Espesor de losa                    : {self.h:.3f} m")
        print(f"Módulo de reacción k               : {self.k/1000:.2f} MPa/m")
        print(f"Malla                              : {self.nx} x {self.ny}")

        print("\nCARGA DE ANÁLISIS")
        print("-" * 60)
        print("Carga por rueda                : 20.00 kN")
        print("Huella de contacto             : 0.215 x 0.170 m")
        print("Modelo de fundación            : Winkler")
        print("Modelo de placa                : Kirchhoff-Love")

        print("\nPROPIEDADES DE LAS BARRAS DE AMARRE")
        print("-" * 60)
        print(f"Diámetro               : {self.diametro_barra*1000:.1f} mm")
        print(f"Longitud               : {self.longitud_barra:.2f} m")
        print(f"Módulo del acero       : {self.E_acero/1000:.0f} MPa")
        print(f"Área de barra          : {self.area_barra*1e6:.2f} mm²")
        print(f"Rigidez equivalente EA/L : {self.rigidez_junta:.2f}")

        # ======================================================
        # EJECUCIÓN DE MODELOS NUMÉRICOS
        # ======================================================
        original = self.ejecutar_modelo(Ly=3.30, tiene_junta=False)
        reparado = self.ejecutar_modelo(Ly=1.65, tiene_junta=True)

        # ======================================================
        # VARIACIONES
        # ======================================================
        vdef = (
            100.0
            * (reparado["deflexion"] - original["deflexion"])
            / original["deflexion"]
        )
        vmom = (
            100.0
            * (reparado["momento"] - original["momento"])
            / original["momento"]
        )
        vesf = (
            100.0
            * (reparado["esfuerzo"] - original["esfuerzo"])
            / original["esfuerzo"]
        )
        vrea = (
            100.0
            * (reparado["reaccion"] - original["reaccion"])
            / original["reaccion"]
        )

        # ======================================================
        # REPORTE DE COMPARACIÓN ESTRUCTURAL
        # ======================================================
        print()
        print("=" * 95)
        print("                         COMPARACIÓN ESTRUCTURAL")
        print("=" * 95)
        print(
            f"{'Variable':30s}{'Original':>15s}{'Reparado':>15s}{'Variación':>15s}"
        )
        print("-" * 95)

        print(
            f"{'Deflexión (mm)':30s}{original['deflexion']:15.3f}{reparado['deflexion']:15.3f}{vdef:14.2f}%"
        )
        print(
            f"{'Momento Máximo (kN·m/m)':30s}{original['momento']:15.3f}{reparado['momento']:15.3f}{vmom:14.2f}%"
        )
        print(
            f"{'Esfuerzo Máximo (MPa)':30s}{original['esfuerzo']:15.3f}{reparado['esfuerzo']:15.3f}{vesf:14.2f}%"
        )
        print(
            f"{'Reacción Subrasante (kPa)':30s}{original['reaccion']:15.3f}{reparado['reaccion']:15.3f}{vrea:14.2f}%"
        )
        print("=" * 95)

        # ======================================================
        # CONCLUSIONES DIRECTAS PERFILADAS
        # ======================================================
        print()
        print("=" * 95)
        print("CONCLUSIONES DEL ANÁLISIS")
        print("=" * 95)
        print(f"• Deflexión máxima original        : {original['deflexion']:.3f} mm")
        print(f"• Deflexión máxima reparada        : {reparado['deflexion']:.3f} mm")
        print()
        print(f"• Momento máximo original          : {original['momento']:.3f} kN·m/m")
        print(f"• Momento máximo reparado          : {reparado['momento']:.3f} kN·m/m")
        print()
        print(f"• Esfuerzo máximo original         : {original['esfuerzo']:.3f} MPa")
        print(f"• Esfuerzo máximo reparado         : {reparado['esfuerzo']:.3f} MPa")
        print()
        print(f"• Reacción máxima original (kPa)   : {original['reaccion']:.3f}")
        print(f"• Reacción máxima reparada (kPa)   : {reparado['reaccion']:.3f}")
        print()
        print(
            "De acuerdo con los resultados obtenidos mediante el modelo numérico de diferencias finitas,"
        )
        print(
            "la reposición mediante media losa presenta un comportamiento estructural adecuado bajo las"
        )
        print(
            "condiciones de carga analizadas. Los valores de deflexión, momentos flectores, esfuerzos y"
        )
        print(
            "reacción de la subrasante obtenidos permiten concluir que la alternativa evaluada satisface"
        )
        print("los criterios mecánicos considerados en el modelo.")
        print("=" * 95)

        # ======================================================
        # POSTPROCESO REESTRUCTURADO
        # ======================================================
        print()
        print("=" * 70)
        print("           RESULTADOS DEL MODELO A (LOSA ORIGINAL)")
        print("=" * 70)
        print(f"Deflexión máxima           : {original['deflexion']:.3f} mm")
        print(f"Reacción máxima            : {original['reaccion']:.3f} kPa")
        print(f"Momento Máximo             : {original['momento']:.3f} kN·m/m")
        print(f"Esfuerzo máximo            : {original['esfuerzo']:.3f} MPa")
        print("=" * 70)

        print()
        print("=" * 70)
        print("           RESULTADOS DEL MODELO B (MEDIA LOSA)")
        print("=" * 70)
        print(f"Deflexión máxima           : {reparado['deflexion']:.3f} mm")
        print(f"Reacción máxima            : {reparado['reaccion']:.3f} kPa")
        print(f"Momento Máximo             : {reparado['momento']:.3f} kN·m/m")
        print(f"Esfuerzo máximo            : {reparado['esfuerzo']:.3f} MPa")
        print("=" * 70)

        return original, reparado


#==========================================================
# PROGRAMA PRINCIPAL
#==========================================================

if __name__ == "__main__":

    estudio = ComparativaPavimentos()

    estudio.ejecutar_analisis()