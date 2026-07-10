import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection


def dibujar_configuracion_pavimento():
    # ------------------------------------------------------------------
    # LIENZO: figura grande + panel lateral FIJO para todo el texto.
    # Nada de texto queda "flotando" anclado a coordenadas 3D (eso es lo
    # que se cruzaba al rotar la vista); todo el texto vive en el margen
    # de la figura, que nunca rota ni cambia de posición.
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(17, 11))

    fondo = fig.add_axes([0, 0, 1, 1], zorder=-10)
    fondo.set_xticks([]); fondo.set_yticks([])
    for spine in fondo.spines.values():
        spine.set_visible(False)
    gradiente = np.linspace(0, 1, 256).reshape(-1, 1)
    fondo.imshow(gradiente, aspect='auto', cmap=plt.cm.colors.LinearSegmentedColormap.from_list(
        'fondo', ['#eef0f2', '#fbfbfa']), extent=[0, 1, 0, 1], origin='lower')
    fondo.set_xlim(0, 1); fondo.set_ylim(0, 1)

    # El eje 3D ocupa solo la parte izquierda del lienzo; el 30% derecho
    # queda libre para el panel de texto (leyenda + notas técnicas).
    ax = fig.add_axes([0.02, 0.03, 0.70, 0.86], projection='3d', computed_zorder=False)
    ax.set_facecolor('none')

    # ------------------------------------------------------------------
    # GEOMETRÍA REAL DEL PROYECTO (metros)
    # ------------------------------------------------------------------
    Lx = 3.00
    Ly_medio = 1.65
    Ly_berma = 1.70
    h = 0.20
    h_berma = 0.15
    ancho_total_y = (Ly_medio * 2) + Ly_berma

    # ------------------------------------------------------------------
    # PALETA: 3 materiales claramente diferenciados
    # ------------------------------------------------------------------
    color_antiguo_top   = '#b7b3aa'
    color_antiguo_side  = '#96928a'
    color_nuevo_top     = '#f0f2f3'
    color_nuevo_side    = '#d3d7da'
    color_berma_top     = '#dbc9a2'
    color_berma_side    = '#c2ac7c'

    def generar_prisma_3d(x1, y1, x2, y2, z1, z2):
        return np.array([
            [x1, y1, z1], [x2, y1, z1], [x2, y2, z1], [x1, y2, z1],
            [x1, y1, z2], [x2, y1, z2], [x2, y2, z2], [x1, y2, z2]
        ])

    def dibujar_bloque(x1, y1, x2, y2, z1, z2, color_top, color_side, edge, lbl, alpha=0.97, zorder=1):
        v = generar_prisma_3d(x1, y1, x2, y2, z1, z2)
        cara_inf = [v[0], v[1], v[2], v[3]]
        cara_sup = [v[4], v[5], v[6], v[7]]
        caras_lat = [
            [v[0], v[1], v[5], v[4]],
            [v[2], v[3], v[7], v[6]],
            [v[0], v[3], v[7], v[4]],
            [v[1], v[2], v[6], v[5]],
        ]
        top = Poly3DCollection([cara_sup], facecolors=color_top, edgecolors=edge,
                                linewidths=0.7, alpha=alpha, label=lbl)
        top.set_zorder(zorder + 0.2)
        lados = Poly3DCollection([cara_inf] + caras_lat, facecolors=color_side, edgecolors=edge,
                                  linewidths=0.5, alpha=alpha)
        lados.set_zorder(zorder)
        ax.add_collection3d(lados)
        ax.add_collection3d(top)
        return v

    # ------------------------------------------------------------------
    # 0. SOMBRA DE CONTACTO EN EL "SUELO"
    # ------------------------------------------------------------------
    z_suelo = -h_berma - 0.22
    margen_sombra = 0.28
    sombra = [[
        (-margen_sombra, -margen_sombra, z_suelo),
        (Lx + margen_sombra, -margen_sombra, z_suelo),
        (Lx + margen_sombra, ancho_total_y + margen_sombra, z_suelo),
        (-margen_sombra, ancho_total_y + margen_sombra, z_suelo)
    ]]
    ax.add_collection3d(Poly3DCollection(sombra, facecolors='#c9c9c4', alpha=0.35,
                                          edgecolors='none', zorder=0))

    # ------------------------------------------------------------------
    # 1. LOS TRES PAÑOS / MATERIALES
    # ------------------------------------------------------------------
    dibujar_bloque(0, 0, Lx, Ly_medio, -h, 0,
                    color_antiguo_top, color_antiguo_side, '#7d7a72',
                    'Paño Antiguo (1.65 m)', zorder=1)

    dibujar_bloque(0, Ly_medio, Lx, Ly_medio * 2, -h, 0,
                    color_nuevo_top, color_nuevo_side, '#aeb3b7',
                    'Paño Nuevo (1.65 m)', zorder=1)

    dibujar_bloque(0, Ly_medio * 2, Lx, Ly_medio * 2 + Ly_berma, -h_berma, 0,
                    color_berma_top, color_berma_side, '#a58f5f',
                    'Berma Lateral (1.70 m)', zorder=1)

    # ---- Textura sutil de "paño antiguo": microfisuras de desgaste ----
    rng = np.random.default_rng(7)
    lineas_desgaste = []
    for _ in range(16):
        xa, xb = sorted(rng.uniform(0.1, Lx - 0.1, 2))
        ya = rng.uniform(0.08, Ly_medio - 0.08)
        yb = np.clip(ya + rng.uniform(-0.15, 0.15), 0.05, Ly_medio - 0.05)
        lineas_desgaste.append([(xa, ya, 0.0011), (xb, yb, 0.0011)])
    grietas = Line3DCollection(lineas_desgaste, colors='#807c72', linewidths=0.6, alpha=0.5)
    grietas.set_zorder(1.5)
    ax.add_collection3d(grietas)

    # ---- Textura sutil de "berma": granulometría ----
    puntos_berma_x = rng.uniform(0.1, Lx - 0.1, 40)
    puntos_berma_y = rng.uniform(Ly_medio * 2 + 0.08, Ly_medio * 2 + Ly_berma - 0.08, 40)
    ax.scatter(puntos_berma_x, puntos_berma_y, np.full(40, 0.001),
               s=3.5, color='#8f7748', alpha=0.35, zorder=1.6, depthshade=False)

    # ------------------------------------------------------------------
    # 2. JUNTAS
    # ------------------------------------------------------------------
    ax.plot([0, Lx], [Ly_medio, Ly_medio], [0.0005, 0.0005],
            color='#d94801', linewidth=7.5, alpha=0.16, zorder=5.9)
    ax.plot([0, Lx], [Ly_medio, Ly_medio], [0.0035, 0.0035],
            color='#d94801', linewidth=3.3, linestyle='--',
            label='Nueva Junta Intervenida (crítica)', zorder=6)

    ax.plot([0, Lx], [Ly_medio * 2, Ly_medio * 2], [0.0015, 0.0015],
            color='#7d6a3f', linewidth=1.3, alpha=0.85, zorder=6)

    # ------------------------------------------------------------------
    # 3. REFUERZO DE ACERO EN JUNTAS: dowels (transversales) y
    #    barras de amarre (longitudinal)
    # ------------------------------------------------------------------
    color_dowel = '#aeb3b7'
    color_cap = '#e8940c'
    color_tie = '#5a4632'

    ancho_pavimento_y = Ly_medio * 2   # solo paños (antiguo+nuevo); la berma no lleva dowels

    # ---- DOWELS: juntas transversales en x=0 y x=Lx, cada 0.30 m, φ 1 1/4" ----
    espaciamiento_dowel = 0.30
    z_dowel = -h / 2
    emb_dowel = 0.14
    lib_dowel = 0.11
    grosor_dowel = 3.6

    ys_dowels = np.arange(espaciamiento_dowel / 2, ancho_pavimento_y, espaciamiento_dowel)
    for y_d in ys_dowels:
        for x_junta, signo in ((0.0, -1), (Lx, 1)):
            x0 = x_junta + signo * emb_dowel
            x1 = x_junta - signo * lib_dowel
            ax.plot([x0, x1], [y_d, y_d], [z_dowel, z_dowel],
                    color=color_dowel, linewidth=grosor_dowel, solid_capstyle='round',
                    zorder=7, alpha=0.97)
            ax.plot([x0, x1], [y_d, y_d], [z_dowel + 0.006, z_dowel + 0.006],
                    color='#ffffff', linewidth=0.7, alpha=0.5, zorder=7.05)
            ax.plot([x1], [y_d], [z_dowel], marker='o', markersize=5.5,
                    markerfacecolor=color_cap, markeredgecolor='#8a5a06', zorder=7.1)

    ax.plot([], [], [], color=color_dowel, linewidth=grosor_dowel, solid_capstyle='round',
            label='Dowel liso φ1 1/4" @ 0.30 m (junta transversal)')

    # ---- BARRAS DE AMARRE: junta longitudinal en y=Ly_medio, cada 1.30 m, φ 1/2" ----
    espaciamiento_tie = 1.30
    margen_tie = (Lx - 2 * espaciamiento_tie) / 2 if Lx > 2 * espaciamiento_tie else 0.15
    xs_ties = np.arange(margen_tie, Lx - margen_tie / 2, espaciamiento_tie)
    z_tie = -h / 2
    emb_tie = 0.16
    grosor_tie = 2.0

    for x_t in xs_ties:
        y0 = Ly_medio - emb_tie
        y1 = Ly_medio + emb_tie
        ax.plot([x_t, x_t], [y0, y1], [z_tie, z_tie],
                color=color_tie, linewidth=grosor_tie, solid_capstyle='round',
                zorder=7, alpha=0.97)
        for f in np.linspace(0.15, 0.85, 4):
            yf = y0 + f * (y1 - y0)
            ax.plot([x_t], [yf], [z_tie], marker='D', markersize=2.6,
                    color='#2c2015', zorder=7.15)

    ax.plot([], [], [], color=color_tie, linewidth=grosor_tie, solid_capstyle='round',
            label='Barra de amarre corrugada φ1/2" @ 1.30 m (junta longitudinal)')

    # ------------------------------------------------------------------
    # 4. NEUMÁTICOS 3D (carga dual crítica sobre la junta)
    # ------------------------------------------------------------------
    cx = Lx / 2
    cy_junta = Ly_medio
    separacion_dual = 0.342

    radio_neumatico = 0.15
    radio_rin = 0.086
    ancho_neumatico = 0.115
    epsilon_apoyo = 0.003
    n_seg = 44
    theta = np.linspace(0, 2 * np.pi, n_seg)

    ruedas_y = [cy_junta, cy_junta - separacion_dual]

    eje_y = [min(ruedas_y), max(ruedas_y)]
    ax.plot([cx, cx], eje_y, [radio_neumatico + epsilon_apoyo] * 2,
            color='#333333', linewidth=4.6, solid_capstyle='round', zorder=9,
            label='Eje de carga dual (camión de diseño)')

    for y_centro in ruedas_y:
        # Perfil circular en el plano X-Z: la llanta rueda paralela al eje X,
        # es decir, paralela a la junta longitudinal (como un camión real).
        xs_c = cx + radio_neumatico * np.cos(theta)
        zs_c = epsilon_apoyo + radio_neumatico + radio_neumatico * np.sin(theta)
        xs_rin = cx + radio_rin * np.cos(theta)
        zs_rin = epsilon_apoyo + radio_neumatico + radio_rin * np.sin(theta)

        y_atras = y_centro - ancho_neumatico / 2
        y_delante = y_centro + ancho_neumatico / 2

        caras_llanta, colores_llanta = [], []
        for t in range(n_seg - 1):
            caras_llanta.append([
                [xs_c[t], y_atras, zs_c[t]],
                [xs_c[t], y_delante, zs_c[t]],
                [xs_c[t + 1], y_delante, zs_c[t + 1]],
                [xs_c[t + 1], y_atras, zs_c[t + 1]],
            ])
            brillo = 0.16 + 0.11 * (np.sin(theta[t]) + 1)
            colores_llanta.append((0.09 + brillo * 0.35, 0.09 + brillo * 0.35, 0.10 + brillo * 0.35))
        llanta_mesh = Poly3DCollection(caras_llanta, facecolors=colores_llanta,
                                        edgecolors='#0d0d0d', linewidths=0.15, alpha=1.0)
        llanta_mesh.set_zorder(10)
        ax.add_collection3d(llanta_mesh)

        franjas = [[(xs_c[t], y_atras, zs_c[t]), (xs_c[t], y_delante, zs_c[t])]
                   for t in range(0, n_seg - 1, 3)]
        ax.add_collection3d(Line3DCollection(franjas, colors='#000000', linewidths=0.55, alpha=0.5, zorder=10.1))

        for y_lado in (y_atras, y_delante):
            cara = list(zip(xs_c, [y_lado] * n_seg, zs_c))
            costado = Poly3DCollection([cara], facecolors='#2b2b2b', edgecolors='#111111',
                                        linewidths=0.3, alpha=1.0)
            costado.set_zorder(10)
            ax.add_collection3d(costado)

        for y_lado in (y_atras + 0.007, y_delante - 0.007):
            cara_rin = list(zip(xs_rin, [y_lado] * n_seg, zs_rin))
            rin = Poly3DCollection([cara_rin], facecolors='#9fa5aa', edgecolors='#5b5f63',
                                    linewidths=0.3, alpha=1.0)
            rin.set_zorder(10.2)
            ax.add_collection3d(rin)
            ax.plot([cx], [y_lado], [epsilon_apoyo + radio_neumatico],
                    marker='o', markersize=3.2, color='#5b5f63', zorder=10.3)

        hx = [cx - 0.055, cx - 0.055, cx + 0.055, cx + 0.055]
        hy = [y_atras, y_delante, y_delante, y_atras]
        hz = [epsilon_apoyo] * 4
        huella = Poly3DCollection([list(zip(hx, hy, hz))], facecolors='#e31a1c',
                                   edgecolors='#99000d', linewidths=0.9, alpha=0.88)
        huella.set_zorder(11)
        ax.add_collection3d(huella)

        flecha = ax.quiver(cx, y_centro, radio_neumatico * 2.7, 0, 0, -radio_neumatico * 1.65,
                            color='#99000d', arrow_length_ratio=0.26, linewidth=2.8)
        flecha.set_zorder(12)

    # ------------------------------------------------------------------
    # 5. ENTORNO, ESCALA Y ESTÉTICA (SIN texto flotante anclado al 3D)
    # ------------------------------------------------------------------
    ax.set_xlim(-0.5, Lx + 0.5)
    ax.set_ylim(-0.3, ancho_total_y + 0.3)
    ax.set_zlim(-0.55, 0.75)

    ax.set_box_aspect((Lx * 1.15, ancho_total_y * 1.15, ancho_total_y * 0.42))

    ax.set_xlabel('Longitud (m)', fontsize=9, labelpad=8)
    ax.set_ylabel('Ancho calzada + berma (m)', fontsize=9, labelpad=10)
    ax.set_zlabel('Altura (m)', fontsize=9, labelpad=8)
    ax.tick_params(labelsize=7.5)

    ax.view_init(elev=26, azim=-50)
    ax.grid(True, linestyle=':', alpha=0.3)
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.set_facecolor((1, 1, 1, 0.0))
        pane.set_edgecolor('#d5d5d2')

    # Leyenda anclada a la FIGURA (transFigure), en la esquina superior
    # derecha del lienzo completo. Al usar coordenadas de figura (no de
    # los ejes 3D) queda siempre dentro del área visible, sin recortarse
    # ni desplazarse, sin importar la rotación del modelo.
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    leg = fig.legend(by_label.values(), by_label.keys(),
                      loc='upper right', bbox_to_anchor=(0.985, 0.93),
                      framealpha=0.95, fontsize=9, edgecolor='#c9c9c6',
                      borderpad=0.9, labelspacing=0.8, title='LEYENDA', title_fontsize=10)
    leg.get_frame().set_facecolor('#ffffff')

    # ------------------------------------------------------------------
    # 6. PANEL LATERAL FIJO (figura completa, no rota, no se superpone)
    # ------------------------------------------------------------------
    fig.suptitle(
        'MODELO GEOMÉTRICO CRÍTICO: REPOSICIÓN DE MEDIA LOSA',
        x=0.40, y=0.97, fontsize=14, fontweight='bold', color='#242424'
    )

    ruta_png = "geometria_critica_pavimento_3d.png"
    plt.savefig(ruta_png, dpi=320, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"\n[ÉXITO] Renderizado 3D guardado en la carpeta de trabajo como: {ruta_png}")

    return fig


if __name__ == "__main__":
    dibujar_configuracion_pavimento()
    plt.show()  # Abre la ventana interactiva de matplotlib (rotar, hacer zoom, etc.)