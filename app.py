import numpy as np
import random
import streamlit as st
import matplotlib.pyplot as plt

# Definición del mapa de colores
color_map = {
    "random": lambda: [random.random() for _ in range(3)],
    "red": [0.8, 0.3, 0.3],
    "blue": [0.3, 0.6, 0.9],
    "grey": [0.2, 0.2, 0.2],
    "yellow": [0.6, 0.9, 0.3],
    "green": [0.3, 0.9, 0.6],
    "black": [0, 0, 0],
    "white": [1, 1, 1],
}

def get_colors(color_names):
    """Convierte nombres de colores a valores RGB."""
    colors = []
    for name in color_names:
        if name in color_map:
            colors.append(color_map[name] if isinstance(color_map[name], list) else color_map[name]())
        else:
            st.error(f"Invalid color: '{name}' is not supported.")
            st.stop()
    return colors

def create_initial_triangles(base):
    """Crea la primera capa de triángulos."""
    angles = np.linspace(0, 2 * np.pi, base * 2, endpoint=False)
    vertices = np.exp(1j * angles)
    triangles = []
    for i in range(base * 2):
        v2 = vertices[i - 1]
        v3 = vertices[i]
        if i % 2 == 0:
            v2, v3 = v3, v2  # Invierte cada triángulo alterno
        triangles.append(("thin", 0, v2, v3))
    return triangles

def subdivide_triangles(triangles, divisions, phi):
    """Subdivide los triángulos iterativamente."""
    for _ in range(divisions):
        new_triangles = []
        for shape, v1, v2, v3 in triangles:
            if shape == "thin":
                p1 = v1 + (v2 - v1) / phi
                new_triangles += [("thin", v3, p1, v2), ("thicc", p1, v3, v1)]
            else:
                p2 = v2 + (v1 - v2) / phi
                p3 = v2 + (v3 - v2) / phi
                new_triangles += [("thicc", p3, v3, v1), ("thicc", p2, p3, v2), ("thin", p3, p2, v1)]
        triangles = new_triangles
    return triangles

def draw_triangles(ax, triangles, colors):
    """Dibuja los triángulos usando Matplotlib."""
    for shape, v1, v2, v3 in triangles:
        vertices = np.array([[v1.real, v1.imag], [v2.real, v2.imag], [v3.real, v3.imag]])
        color = colors[0] if shape == "thin" else colors[1]
        triangle = plt.Polygon(vertices, closed=True, color=color)
        ax.add_patch(triangle)

    # Contornos
    for _, v1, v2, v3 in triangles:
        vertices = np.array([[v1.real, v1.imag], [v2.real, v2.imag], [v3.real, v3.imag], [v1.real, v1.imag]])
        ax.plot(vertices[:, 0], vertices[:, 1], color=colors[2], linewidth=0.5)

def main():
    st.title("Generador de Teselado de Penrose con Matplotlib")

    # Entrada del usuario
    divisions = st.slider("Número de Capas/Subdivisiones de Teselado", min_value=2, max_value=8, value=5)

    # Escoge los colores
    color_options = list(color_map.keys())
    color_thin = st.selectbox("Selecciona el color para triángulos delgados", color_options, index=color_options.index("red"))
    color_thicc = st.selectbox("Selecciona el color para triángulos gruesos", color_options, index=color_options.index("blue"))
    color_outline = st.selectbox("Selecciona el color para el contorno", color_options, index=color_options.index("grey"))

    colors = get_colors([color_thin, color_thicc, color_outline])

    # Parámetros para el dibujo
    base = 5
    phi = (1 + np.sqrt(5)) / 2  # Razón áurea

    # Crear triángulos
    triangles = create_initial_triangles(base)
    triangles = subdivide_triangles(triangles, divisions, phi)

    # Configurar el gráfico
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")
    ax.axis("off")

    # Dibujar los triángulos
    draw_triangles(ax, triangles, colors)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

if __name__ == "__main__":
    main()
