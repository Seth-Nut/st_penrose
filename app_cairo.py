import math
import cmath
import cairocffi as cairo
import random
import re
import streamlit as st

color_map = {
        "random": lambda: [random.random() for _ in range(3)],
        "red": [0.8, 0.3, 0.3],
        "dark_red": [0.6, 0.1, 0.1],
        "orange": [0.9, 0.6, 0.3],
        "dark_orange": [0.8, 0.4, 0.1],
        "yellow": [0.6, 0.9, 0.3],
        "gold": [1.0, 0.84, 0.0],
        "green": [0.3, 0.9, 0.6],
        "dark_green": [0.1, 0.5, 0.2],
        "lime": [0.75, 1.0, 0.0],
        "blue": [0.3, 0.6, 0.9],
        "dark_blue": [0.1, 0.2, 0.5],
        "cyan": [0.0, 0.8, 0.8],
        "teal": [0.0, 0.5, 0.5],
        "purple": [0.8, 0.3, 0.6],
        "violet": [0.6, 0.4, 0.9],
        "pink": [1.0, 0.6, 0.8],
        "magenta": [1.0, 0.0, 1.0],
        "grey": [0.2, 0.2, 0.2],
        "dark_grey": [0.1, 0.1, 0.1],
        "light_grey": [0.7, 0.7, 0.7],
        "brown": [0.6, 0.3, 0.1],
        "tan": [0.82, 0.71, 0.55],
        "black": [0, 0, 0],
        "white": [1, 1, 1],
        "beige": [0.96, 0.96, 0.86],
        "turquoise": [0.25, 0.88, 0.82],
        "navy": [0.0, 0.0, 0.5],
        "olive": [0.5, 0.5, 0.0],
        "maroon": [0.5, 0.0, 0.0],
        "indigo": [0.29, 0.0, 0.51],
        "silver": [0.75, 0.75, 0.75],
        "goldenrod": [0.85, 0.65, 0.13],
        "peach": [1.0, 0.85, 0.73],
    }

def get_colors(color_names):
    """Convierte nombres de colores a valores RGB."""

    colors = []
    for name in color_names:
        if name in color_map:
            colors.append(color_map[name] if isinstance(color_map[name], list) else color_map[name]())
        else:
            try:
                color = [int(x, 16) / 256 for x in re.findall(r'[0-9a-fA-F]{2}', name)]
                if len(color) != 3:
                    raise ValueError
                colors.append(color)
            except ValueError:
                st.error(f"Invalid color: '{name}' is not supported.")
                st.stop()
    return colors


def setup_canvas(r1, r2, scale):
    """Configura el canvas para el dibujo."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, r1, r2)
    ctx = cairo.Context(surface)
    ctx.scale(max(r1, r2) / scale, max(r1, r2) / scale)
    ctx.translate(0.5 * scale, 0.5 * scale)  # Centra el dibujo
    return surface, ctx


def create_initial_triangles(base):
    """Crea la primera capa de triángulos."""
    triangles = []
    for i in range(base * 2):
        v2 = cmath.rect(1, (2 * i - 1) * math.pi / (base * 2))
        v3 = cmath.rect(1, (2 * i + 1) * math.pi / (base * 2))
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


def draw_triangles(ctx, triangles, colors, line_width):
    """Dibuja los triángulos en el canvas."""
    for shape, v1, v2, v3 in triangles:
        ctx.move_to(v1.real, v1.imag)
        ctx.line_to(v2.real, v2.imag)
        ctx.line_to(v3.real, v3.imag)
        ctx.close_path()
        if shape == "thin":
            ctx.set_source_rgb(*colors[0])
        else:
            ctx.set_source_rgb(*colors[1])
        ctx.fill()

    # Dibujar contornos
    ctx.set_source_rgb(*colors[2])
    ctx.set_line_width(line_width)
    for _, v1, v2, v3 in triangles:
        ctx.move_to(v2.real, v2.imag)
        ctx.line_to(v1.real, v1.imag)
        ctx.line_to(v3.real, v3.imag)
    ctx.stroke()


def main():
    st.title("Generador de Teselado de Penrose")
    
    # Entrada del usuario
    divisions = st.slider("Número de Capas/Subdivisiones de Teselado", min_value=2, max_value=10, value=5)
    
    # Botones para seleccionar el tipo de zoom
    st.markdown("<small>Selecciona el tipo de zoom</small>", unsafe_allow_html=True)
    zoom = "rectangular"  # Predeterminado a "rectangular"

    # Botones para seleccionar el tipo de zoom
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Rectangular"):
            zoom = "rectangular"
    with col2:
        if st.button("Geométrico"):
            zoom = "geometrico"

    # Escala basada en la selección
    scale = {"rectangular": 1, "geometrico": 2}[zoom]
   
   # Opciones disponibles
    color_options = list(color_map.keys())

    # Crear selectores para cada color
    color_triangulos_delgados = st.selectbox("Selecciona el color para triángulos delgados", color_options, index=color_options.index("red"))
    color_triangulos_gruesos = st.selectbox("Selecciona el color para triángulos gruesos", color_options, index=color_options.index("blue"))
    color_contorno = st.selectbox("Selecciona el color para el contorno", color_options, index=color_options.index("grey"))

    # Definir colors_input basado en las selecciones
    colors_input = [color_triangulos_delgados, color_triangulos_gruesos, color_contorno]

    # Parámetros fijos
    resolution = '2000 2000'
    filename = "example.png" 

    try:
        r1, r2 = map(int, resolution.split())
        colors = get_colors(colors_input)
        if not filename.endswith(".png"):
            st.error("Filename must end with '.png'")
            st.stop()
    except ValueError:
        st.error("Invalid resolution format or colors.")
        st.stop()

    # Generar imagen
    base = 5
    phi = (1 + 5**0.5) / 2  # Razón áurea
    surface, ctx = setup_canvas(r1, r2, scale)
    triangles = create_initial_triangles(base)
    triangles = subdivide_triangles(triangles, divisions, phi)

    line_width = divisions ** -3 if divisions > 3 else divisions ** -5
    draw_triangles(ctx, triangles, colors, line_width)

    # Guardar y mostrar
    surface.write_to_png(filename)
    #st.success(f"Image saved as {filename}")
    st.image(filename)


if __name__ == "__main__":
    main()
