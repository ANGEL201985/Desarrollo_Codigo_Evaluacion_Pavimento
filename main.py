# ======================================================================
# ARCHIVO PRINCIPAL: main.py
# ORQUESTADOR DEL SISTEMA DE SIMULACIÓN NUMÉRICA (MDF)
# ======================================================================

import os
from comparacion import ComparativaPavimentos


def main():
    print("=" * 75)
    print("   SISTEMA DE SIMULACIÓN NUMÉRICA DE PAVIMENTOS RÍGIDOS (MDF)")
    print("   Resolución de la Ecuación de Kirchhoff-Love sobre Apoyo Winkler")
    print("=" * 75)

    # 1. Inicializar el módulo de comparación de estrategias elásticas
    analisis = ComparativaPavimentos()

    # 2. Ejecutar el solver y procesar los reportes en consola de forma limpia
    # 'original' y 'reparado' reciben las estructuras de datos con los resultados finales
    original, reparado = analisis.ejecutar_analisis()

    print("\n" + "=" * 75)
    print("   SIMULACIÓN CONCLUIDA EXITOSAMENTE: DATOS LISTOS PARA EL INFORME")
    print("=" * 75)


if __name__ == "__main__":
    main()