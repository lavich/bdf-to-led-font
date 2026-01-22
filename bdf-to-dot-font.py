#!/usr/bin/env python3
"""
Convert BDF bitmap font to dot-matrix TTF/WOFF2 font with LED effect.
Each pixel becomes a circle (dot).
"""

import sys
import os
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


def parse_bdf(filepath: str) -> dict:
    """Parse BDF font file and return glyph data."""
    glyphs = {}
    current_glyph = None
    in_bitmap = False
    bitmap_lines = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith('STARTCHAR'):
                current_glyph = {'name': line.split()[1]}
                bitmap_lines = []
                in_bitmap = False

            elif line.startswith('ENCODING'):
                if current_glyph:
                    current_glyph['encoding'] = int(line.split()[1])

            elif line.startswith('DWIDTH'):
                if current_glyph:
                    current_glyph['width'] = int(line.split()[1])

            elif line.startswith('BBX'):
                if current_glyph:
                    parts = line.split()
                    current_glyph['bbx'] = {
                        'width': int(parts[1]),
                        'height': int(parts[2]),
                        'x_offset': int(parts[3]),
                        'y_offset': int(parts[4]),
                    }

            elif line == 'BITMAP':
                in_bitmap = True

            elif line == 'ENDCHAR':
                if current_glyph and current_glyph.get('encoding', -1) >= 0:
                    current_glyph['bitmap'] = parse_bitmap(bitmap_lines, current_glyph.get('bbx', {}))
                    glyphs[current_glyph['encoding']] = current_glyph
                current_glyph = None
                in_bitmap = False

            elif in_bitmap and current_glyph:
                bitmap_lines.append(line)

    return glyphs


def parse_bitmap(lines: list, bbx: dict) -> list:
    """Convert hex bitmap lines to 2D array of pixels."""
    width = bbx.get('width', 8)
    bitmap = []

    for line in lines:
        row = []
        value = int(line, 16)
        bits = bin(value)[2:].zfill(len(line) * 4)

        for i in range(width):
            row.append(1 if i < len(bits) and bits[i] == '1' else 0)

        bitmap.append(row)

    return bitmap


def draw_circle(pen, cx, cy, r):
    """Draw a circle using quadratic Bezier curves with 12 points for smoother result."""
    import math
    cx, cy, r = int(cx), int(cy), int(r)

    # 12-point circle (every 30 degrees) for smoother appearance
    n_points = 12
    points = []
    for i in range(n_points):
        angle = 2 * math.pi * i / n_points
        x = cx + int(r * math.cos(angle))
        y = cy + int(r * math.sin(angle))
        points.append((x, y))

    # Calculate control points between each pair
    pen.moveTo(points[0])
    for i in range(n_points):
        p1 = points[i]
        p2 = points[(i + 1) % n_points]

        # Control point - offset outward for circular curve
        mid_angle = 2 * math.pi * (i + 0.5) / n_points
        # Factor for quadratic bezier to approximate circle arc
        ctrl_r = r / math.cos(math.pi / n_points)
        ctrl_x = cx + int(ctrl_r * math.cos(mid_angle))
        ctrl_y = cy + int(ctrl_r * math.sin(mid_angle))

        pen.qCurveTo((ctrl_x, ctrl_y), p2)

    pen.closePath()


def main():
    if len(sys.argv) < 2:
        print("Usage: python bdf-to-dot-font.py <input.bdf> [output-name]")
        sys.exit(1)

    bdf_path = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else "DotMatrix"

    print(f"Reading {bdf_path}...")
    bdf_glyphs = parse_bdf(bdf_path)
    print(f"Found {len(bdf_glyphs)} glyphs")

    # Font metrics
    EM = 1000
    BDF_HEIGHT = 11
    BDF_DESCENT = 4
    CELL = EM // BDF_HEIGHT  # 62
    RADIUS = int(CELL * 0.4)  # 24
    ASCENT = CELL * (BDF_HEIGHT - BDF_DESCENT)  # 750
    DESCENT = CELL * BDF_DESCENT  # 250

    # Build glyph order
    glyph_names = ['.notdef'] + [f'uni{cp:04X}' for cp in sorted(bdf_glyphs.keys())]

    # Character map
    cmap = {cp: f'uni{cp:04X}' for cp in bdf_glyphs.keys()}

    # Metrics
    metrics = {'.notdef': (CELL * 6, 0)}

    # Build glyphs
    glyph_table = {}

    # .notdef - empty
    pen = TTGlyphPen(None)
    glyph_table['.notdef'] = pen.glyph()

    # Process BDF glyphs
    total = len(bdf_glyphs)
    for i, (cp, gdata) in enumerate(sorted(bdf_glyphs.items())):
        if i % 500 == 0:
            print(f"  Processing glyph {i}/{total}...")

        glyph_name = f'uni{cp:04X}'
        bitmap = gdata.get('bitmap', [])
        width = gdata.get('width', 6)
        bbx = gdata.get('bbx', {})

        pen = TTGlyphPen(None)

        if bitmap:
            height = len(bitmap)
            x_offset = bbx.get('x_offset', 0)
            y_offset = bbx.get('y_offset', 0)

            for y, row in enumerate(bitmap):
                for x, bit in enumerate(row):
                    if bit:
                        cx = (x + x_offset) * CELL + CELL // 2
                        cy = (height - y - 1 + y_offset) * CELL + CELL // 2
                        draw_circle(pen, cx, cy, RADIUS)

        glyph_table[glyph_name] = pen.glyph()
        metrics[glyph_name] = (CELL * width, 0)

    print(f"Building font with {len(glyph_table)} glyphs...")

    # Create font
    fb = FontBuilder(EM, isTTF=True)
    fb.setupGlyphOrder(glyph_names)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyph_table)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=-DESCENT, lineGap=0)
    fb.setupHead(unitsPerEm=EM, created=0, modified=0)
    fb.setupOS2(sTypoAscender=ASCENT, sTypoDescender=-DESCENT,
                usWinAscent=ASCENT, usWinDescent=DESCENT)
    fb.setupPost()
    fb.setupNameTable({
        'familyName': output_name,
        'styleName': 'Regular',
    })

    # Save TTF
    ttf_path = f"{output_name}.ttf"
    print(f"Saving {ttf_path}...")
    fb.font.save(ttf_path)

    # Save WOFF2
    woff2_path = f"{output_name}.woff2"
    print(f"Saving {woff2_path}...")
    font = TTFont(ttf_path)
    font.flavor = 'woff2'
    font.save(woff2_path)

    # Print sizes
    ttf_size = os.path.getsize(ttf_path)
    woff2_size = os.path.getsize(woff2_path)

    print(f"\nResults:")
    print(f"  Glyphs: {len(glyph_table)}")
    print(f"  TTF:    {ttf_size / 1024 / 1024:.2f} MB")
    print(f"  WOFF2:  {woff2_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
