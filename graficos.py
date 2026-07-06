# ======================================================================
# ARCHIVO: graficos.py (GEOMETRÍA EXACTA DE AUDITORÍA Y NEUMÁTICOS 3D)
# ======================================================================

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def dibujar_configuracion_pavimento():
    fig = plt.figure(figsize=(12, 9))
    # FIX 1: computed_zorder=False -> le decimos a matplotlib que respete
    # el ORDEN EN QUE DIBUJAMOS los objetos (como en 2D), en vez de intentar
    # adivinar la profundidad con el centroide de cada colección (lo cual
    # falla con geometrías grandes y planas como la losa, y hacía que el
    # neumático se viera "metido" dentro del concreto).
    ax = fig.add_subplot(111, projection='3d', computed_zorder=False)
    
    # Geometría real del proyecto (metros)
    Lx = 3.00         # Largo de las losas
    Ly_medio = 1.65   # Ancho de cada medio paño
    Ly_berma = 1.70   # Ancho de la berma lateral
    h = 0.20          # Espesor del pavimento (20 cm)
    h_berma = 0.15    # Espesor de la berma (15 cm, asumido estructural)
    
    # ------------------------------------------------------------------
    # 1. DEFINICIÓN DE CAPAS Y ELEMENTOS DEL PAVIMENTO (SE DIBUJAN PRIMERO,
    #    ES DECIR, QUEDAN "ABAJO" EN EL ORDEN DE RENDERIZADO)
    # ------------------------------------------------------------------
    # Paleta unificada: mismos tonos de concreto (gris-azulado) para que las
    # losas se vean como UNA SOLA SUPERFICIE CONTINUA, diferenciadas solo por
    # una variación sutil de tono (no por colores fuertes/contrastantes).
    # La berma usa un tono ligeramente más cálido/claro para distinguir el
    # cambio de material sin romper la continuidad visual del conjunto.
    color_concreto_antiguo = '#c9ccd1'   # gris-azulado neutro
    color_concreto_nuevo   = '#d5d8dc'   # mismo tono, apenas más claro
    color_berma            = '#e4e0d8'   # gris-beige, distinto material

    # Arreglo: [x1, y1, x2, y2, z_inf, z_sup, color, etiqueta]
    elementos = [
        # Medio Paño Existente/Antiguo (Lado interior del carril)
        [0, 0, Lx, Ly_medio, -h, 0, color_concreto_antiguo, 'Medio Paño Antiguo (1.65 m)'],
        # Medio Paño Nuevo (Reposición intervenida)
        [0, Ly_medio, Lx, Ly_medio*2, -h, 0, color_concreto_nuevo, 'Medio Paño Nuevo (1.65 m)'],
        # Berma Lateral Adyacente
        [0, Ly_medio*2, Lx, (Ly_medio*2) + Ly_berma, -h_berma, 0, color_berma, 'Berma Lateral (1.70 m)']
    ]
    
    def generar_prisma_3d(x1, y1, x2, y2, z1, z2):
        return np.array([
            [x1, y1, z1], [x2, y1, z1], [x2, y2, z1], [x1, y2, z1],
            [x1, y1, z2], [x2, y1, z2], [x2, y2, z2], [x1, y2, z2]
        ])

    # Renderizar los bloques de concreto y berma
    for idx, (x1, y1, x2, y2, z1, z2, color, lbl) in enumerate(elementos):
        vertices = generar_prisma_3d(x1, y1, x2, y2, z1, z2)
        caras = [
            [vertices[0], vertices[1], vertices[2], vertices[3]], # Inf
            [vertices[4], vertices[5], vertices[6], vertices[7]], # Sup
            [vertices[0], vertices[1], vertices[5], vertices[4]], # Lat 1
            [vertices[2], vertices[3], vertices[7], vertices[6]], # Lat 2
            [vertices[0], vertices[3], vertices[7], vertices[4]], # Frontal
            [vertices[1], vertices[2], vertices[6], vertices[5]]  # Post
        ]
        # Bordes finos y de bajo contraste (en vez de gris oscuro grueso) para
        # que las losas se lean como una sola superficie continua y no como
        # bloques recortados/discontinuos.
        poligonos = Poly3DCollection(caras, facecolors=color, linewidths=0.4, edgecolors='#9a9a9a', alpha=0.92, label=lbl)
        # FIX 2: zorder explícito y bajo para el pavimento (se dibuja primero/abajo)
        poligonos.set_zorder(1)
        ax.add_collection3d(poligonos)

    # ------------------------------------------------------------------
    # 2. DIBUJAR LA NUEVA JUNTA LONGITUDINAL INTERVENIDA (Marcador visual)
    # ------------------------------------------------------------------
    # Línea que divide el paño antiguo del nuevo en Y = 1.65 m
    linea_junta, = ax.plot([0, Lx], [Ly_medio, Ly_medio], [0.002, 0.002], color='#d94801', linewidth=3.0, linestyle='--', label='Nueva Junta Intervenida')
    linea_junta.set_zorder(2)

    # Línea sutil (gris, no punteada) en el límite losa/berma, para marcar el
    # cambio de material sin introducir un color fuerte que "corte" la vista.
    linea_berma, = ax.plot([0, Lx], [Ly_medio * 2, Ly_medio * 2], [0.001, 0.001], color='#9a9a9a', linewidth=1.2, alpha=0.8)
    linea_berma.set_zorder(2)

    # ------------------------------------------------------------------
    # 3. CONSTRUCCIÓN DE NEUMÁTICOS 3D REALISTAS (Carga en Junta)
    #    Se dibujan AL FINAL para que, con computed_zorder=False, queden
    #    siempre por ENCIMA de la losa y de la junta.
    # ------------------------------------------------------------------
    cx = Lx / 2               # Coordenada X central exacta (1.50 m)
    cy_junta = Ly_medio       # Coordenada Y sobre la junta longitudinal (1.65 m)
    separacion_dual = 0.342   # Distancia entre centros de rueda (0.342 m)
    
    # Dimensiones visuales calibradas para la perspectiva 3D
    # (reducidas para que la rueda se vea proporcional a una losa de 3.0 m,
    # en vez de dominar visualmente la escena)
    radio_neumatico = 0.13    # Radio del neumático (antes 0.22)
    ancho_neumatico = 0.10    # Ancho visual de la banda de rodadura (antes 0.16)

    # FIX 3: pequeño colchón (epsilon) para que la base del neumático quede
    # ligeramente POR ENCIMA de z=0 (cara superior de la losa) y no exactamente
    # coplanar con ella. Esto evita el "z-fighting" (parpadeo/recorte) que
    # ocurre cuando dos superficies están exactamente a la misma altura.
    epsilon_apoyo = 0.003
    
    ruedas_y = [cy_junta, cy_junta - separacion_dual]
    
    for i, y_centro in enumerate(ruedas_y):
        # Para que el neumático apunte hacia adelante (eje X), variamos Y y Z con funciones circulares
        theta = np.linspace(0, 2*np.pi, 24)
        
        # El contorno circular se genera en los ejes Y y Z (perpendicular al avance del vehículo)
        # Se suma el radio en Z para que la parte inferior quede apoyada justo
        # sobre la superficie de la losa (Z = 0 + epsilon_apoyo)
        ys_circulo = y_centro + radio_neumatico * np.cos(theta)
        zs_circulo = epsilon_apoyo + radio_neumatico + radio_neumatico * np.sin(theta)
        
        # El ancho del neumático se extiende a lo largo del eje longitudinal X (centrado en cx)
        x_borde_atras = cx - ancho_neumatico / 2
        x_borde_adelante = cx + ancho_neumatico / 2
        
        # 1. Renderizado de la banda de rodadura (Cuerpo cilíndrico)
        for t in range(len(theta)-1):
            cara_cilindro = [
                [x_borde_atras, ys_circulo[t], zs_circulo[t]],
                [x_borde_adelante, ys_circulo[t], zs_circulo[t]],
                [x_borde_adelante, ys_circulo[t+1], zs_circulo[t+1]],
                [x_borde_atras, ys_circulo[t+1], zs_circulo[t+1]]
            ]
            llanta_mesh = Poly3DCollection([cara_cilindro], facecolors='#252525', edgecolors='#111111', linewidths=0.2, alpha=1.0)
            llanta_mesh.set_zorder(10)  # FIX: siempre encima del pavimento
            ax.add_collection3d(llanta_mesh)
            
        # 2. Tapas laterales del neumático (Rines/Costados en las caras X)
        cara_lateral_atras = list(zip([x_borde_atras]*len(theta), ys_circulo, zs_circulo))
        cara_lateral_adelante = list(zip([x_borde_adelante]*len(theta), ys_circulo, zs_circulo))
        
        tapa_atras = Poly3DCollection([cara_lateral_atras], facecolors='#434343', alpha=1.0)
        tapa_adelante = Poly3DCollection([cara_lateral_adelante], facecolors='#434343', alpha=1.0)
        tapa_atras.set_zorder(10)
        tapa_adelante.set_zorder(10)
        ax.add_collection3d(tapa_atras)
        ax.add_collection3d(tapa_adelante)

        # 3. Huella de contacto crítica (Rectángulo rojo justo sobre la losa)
        hx = [x_borde_atras, x_borde_adelante, x_borde_adelante, x_borde_atras]
        hy = [y_centro - 0.05, y_centro - 0.05, y_centro + 0.05, y_centro + 0.05]
        hz = [epsilon_apoyo, epsilon_apoyo, epsilon_apoyo, epsilon_apoyo]
        huella = Poly3DCollection([list(zip(hx, hy, hz))], facecolors='#e31a1c', edgecolors='#99000d', alpha=0.8)
        huella.set_zorder(11)  # por encima incluso del cuerpo del neumático
        ax.add_collection3d(huella)

        # 4. Flecha indicadora de carga vertical (Nace arriba del neumático y baja al centro de la huella)
        flecha = ax.quiver(cx, y_centro, radio_neumatico * 2.5, 0, 0, -radio_neumatico * 1.5, color='#99000d', arrow_length_ratio=0.3, linewidth=3.0)
        flecha.set_zorder(12)

    # ------------------------------------------------------------------
    # 4. CONFIGURACIÓN DEL ENTORNO E INGENIERÍA VISUAL
    # ------------------------------------------------------------------
    ax.set_xlim(-0.5, Lx + 0.5)
    ax.set_ylim(-0.5, (Ly_medio * 2) + Ly_berma + 0.5)
    ax.set_zlim(-0.4, 0.8)

    # Proporción real de escala: el largo (Lx=3.0 m) y el ancho total
    # (1.65+1.65+1.70=5.0 m) mantienen su relación real 3:5, en vez de que
    # matplotlib fuerce un cubo. El eje Z se exagera un poco (factor propio)
    # solo para que espesores/neumático sigan siendo visibles, ya que a
    # escala real (cm) serían casi imperceptibles.
    ancho_total_y = (Ly_medio * 2) + Ly_berma
    ax.set_box_aspect((Lx, ancho_total_y, ancho_total_y * 0.35))
    
    ax.set_xlabel('Eje X: Longitud del Paño (m)', fontsize=10, labelpad=10)
    ax.set_ylabel('Eje Y: Ancho de Calzada y Berma (m)', fontsize=10, labelpad=15)
    ax.set_zlabel('Eje Z: Alturas y Espesores (m)', fontsize=10, labelpad=10)
    
    ax.set_title('MODELO GEOMÉTRICO CRÍTICO: REPOSICIÓN DE MEDIA LOSA\nEvaluación por Diferencias Finitas (MDF) - Carga de Borde en Nueva Junta', fontsize=11, pad=15, fontweight='bold')
    
    # Ajustar vista en perspectiva limpia para el informe
    ax.view_init(elev=24, azim=-45)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Manejo correcto de la leyenda sin duplicados de parches volumétricos
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', framealpha=0.9)
    
    # Guardado directo en alta definición
    ruta_png = "geometria_critica_pavimento_3d.png"
    plt.savefig(ruta_png, dpi=300, bbox_inches='tight')
    print(f"\n[ÉXITO] Renderizado 3D guardado en la carpeta de trabajo como: {ruta_png}")
    
    plt.show()

if __name__ == "__main__":
    dibujar_configuracion_pavimento()