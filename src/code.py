import math
import cmath


def write_apollonian_gasket_svg(
    filename="images/apollonian_gasket.svg",
    width=1200,
    height=1200,
    max_depth=6,
    min_radius=2.0,
    bg_mode ='cool'
):
    def circle_radius(circle):
        b, _ = circle
        return abs(1.0 / b)

    def circle_svg_data(circle):
        b, z = circle
        return (z.real, z.imag, abs(1.0 / b))

    def other_descartes_circle(c1, c2, c3, c4):
        b1, z1 = c1
        b2, z2 = c2
        b3, z3 = c3
        b4, z4 = c4

        b_new = 2 * (b1 + b2 + b3) - b4
        bz_new = 2 * (b1 * z1 + b2 * z2 + b3 * z3) - b4 * z4
        z_new = bz_new / b_new
        return (b_new, z_new)

    def same_circle(ca, cb, tol=1e-8):
        ba, za = ca
        bb, zb = cb
        return abs(ba - bb) < tol and abs(za - zb) < tol

    r = 1.0
    z1 = complex(-1.0, 0.0)
    z2 = complex(1.0, 0.0)
    z3 = complex(0.0, math.sqrt(3.0))

    c1 = (1.0 / r, z1)
    c2 = (1.0 / r, z2)
    c3 = (1.0 / r, z3)

    outer_radius = 1.0 + 2.0 / math.sqrt(3.0)
    outer_center = complex(0.0, math.sqrt(3.0) / 3.0)
    c_outer = (-1.0 / outer_radius, outer_center)

    circles = [c_outer, c1, c2, c3]
    seen = {}

    def circle_key(circle, places=10):
        b, z = circle
        return (
            round(b.real, places),
            round(b.imag, places),
            round(z.real, places),
            round(z.imag, places),
        )

    for c in circles:
        seen[circle_key(c)] = c

    ox, oy, orad = circle_svg_data(c_outer)

    padding = 40
    scale = min(
        (width - 2 * padding) / (2 * orad),
        (height - 2 * padding) / (2 * orad),
    )

    def world_to_svg(x, y):
        sx = width / 2 + (x - ox) * scale
        sy = height / 2 - (y - oy) * scale
        return sx, sy

    def recurse(ca, cb, cc, known_fourth, depth):
        if depth <= 0:
            return

        candidate = other_descartes_circle(ca, cb, cc, known_fourth)

        rad = circle_radius(candidate)
        if rad < min_radius / scale:
            return

        key = circle_key(candidate)
        if key in seen:
            return

        seen[key] = candidate
        circles.append(candidate)

        recurse(candidate, ca, cb, cc, depth - 1)
        recurse(candidate, ca, cc, cb, depth - 1)
        recurse(candidate, cb, cc, ca, depth - 1)

    recurse(c1, c2, c3, c_outer, max_depth)
    recurse(c_outer, c1, c2, c3, max_depth)
    recurse(c_outer, c2, c3, c1, max_depth)
    recurse(c_outer, c1, c3, c2, max_depth)

    def color_for_circle(circle):
        _, z = circle
        angle = math.atan2(z.imag - oy, z.real - ox)
        hue = (angle * 180 / math.pi + 360) % 360
        sat = 70
        light = 72
        return f"hsl({hue:.1f}, {sat}%, {light}%)"

    drawable = []
    for c in circles:
        x, y, rr = circle_svg_data(c)
        sx, sy = world_to_svg(x, y)
        sr = rr * scale
        drawable.append((sr, sx, sy, c))

    drawable.sort(reverse=True, key=lambda item: item[0])

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )
    svg.append("<defs>")

    if bg_mode == 'cool':
        svg.append("""
        <radialGradient id="bgGradient" cx="35%" cy="30%" r="85%">
            <stop offset="0%"  stop-color="#1a2a6c"/>
            <stop offset="45%" stop-color="#6a11cb"/>
            <stop offset="75%" stop-color="#2575fc"/>
            <stop offset="100%" stop-color="#0b1020"/>
        </radialGradient>
        """)
    elif bg_mode == 'warm':
        svg.append("""
            <radialGradient id="bgGradient" cx="35%" cy="30%" r="85%">
            <stop offset="0%"   stop-color="#ff512f"/>
            <stop offset="40%"  stop-color="#dd2476"/>
            <stop offset="75%"  stop-color="#ff9a44"/>
            <stop offset="100%" stop-color="#220811"/>
        </radialGradient>
        """)

    svg.append("""
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>
    """)

    svg.append("""
    <radialGradient id="vignette" cx="50%" cy="50%" r="70%">
        <stop offset="60%" stop-color="rgba(0,0,0,0)" stop-opacity="0"/>
        <stop offset="100%" stop-color="#000000" stop-opacity="0.35"/>
    </radialGradient>
    """)

    svg.append("</defs>")
    svg.append(f'<rect width="{width}" height="{height}" fill="url(#bgGradient)"/>')

    for i in range(120):
        px = (i * 97) % width
        py = (i * 193) % height
        pr = 0.8 + (i % 3) * 0.35
        opacity = 0.14 + (i % 5) * 0.03
        svg.append(
            f'<circle cx="{px}" cy="{py}" r="{pr}" fill="white" opacity="{opacity:.2f}"/>'
        )

    for sr, sx, sy, c in drawable:
        b, _ = c

        if b.real < 0:
            svg.append(
                f'<circle cx="{sx:.3f}" cy="{sy:.3f}" r="{sr:.3f}" '
                f'fill="none" stroke="rgba(255,255,255,0.9)" stroke-width="3"/>'
            )
        else:
            fill = color_for_circle(c)
            svg.append(
                f'<circle cx="{sx:.3f}" cy="{sy:.3f}" r="{sr:.3f}" '
                f'fill="{fill}" fill-opacity="0.16" '
                f'stroke="white" stroke-opacity="0.8" stroke-width="1.15" '
                f'filter="url(#glow)"/>'
            )

    svg.append(f'<rect width="{width}" height="{height}" fill="url(#vignette)"/>')
    svg.append("</svg>")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))