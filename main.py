# ======================================================================
# ARCHIVO PRINCIPAL: main.py
# ORQUESTADOR DEL SISTEMA DE SIMULACIÓN NUMÉRICA (MDF)
# ======================================================================

import os
import matplotlib.pyplot as plt
from comparacion import ComparativaPavimentos

def main():
    print("="*75)
    print("   SISTEMA DE SIMULACIÓN NUMÉRICA DE PAVIMENTOS RÍGIDOS (MDF)")
    print("   Resolución de la Ecuación de Kirchhoff-Love sobre Apoyo Winkler")
    print("="*75)
    
    # 1. Inicializar el módulo de comparación de estrategias elásticas
    analisis = ComparativaPavimentos()
    
    # 2. Ejecutar el solver de diferencias finitas y extraer los post-procesadores
    post_A, post_B = analisis.ejecutar_analisis()
    
    print("\n[INFO] Generando representaciones gráficas y mapas de esfuerzos...")
    
    # 3. Renderizado de Gráficos para el Escenario A: Pavimento Original
    print("\n[PROCESO] Renderizando Escenario A (Losa Completa)...")
    # Descomenta las líneas según las gráficas que desees visualizar consecutivamente:
    # post_A.mapa_deflexion()
    # post_A.mapa_esfuerzo()
    # post_A.deformada3D()
    
    # 4. Renderizado de Gráficos para el Escenario B: Reposición de Media Losa
    print("[PROCESO] Renderizando Escenario B (Media Losa Intervenida)...")
    # post_B.mapa_deflexion()
    # post_B.mapa_esfuerzo()
    post_B.deformada3D() # Muestra la deformada tridimensional crítica por defecto
    
    print("\n" + "="*75)
    print("   SIMULACIÓN CONCLUIDA EXITOSAMENTE: DATOS LISTOS PARA EL INFORME")
    print("="*75)

if __name__ == "__main__":
    main()