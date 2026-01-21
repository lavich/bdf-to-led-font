import fs from "fs-extra";
import opentype from "opentype.js";
import { $Font } from "bdfparser";
import getline from "readlineiter";

/**
 * Font configuration
 * BDF kirsch: 16px height, ascent 12, descent 4
 */
const EM = 1000;
const BDF_HEIGHT = 16;
const BDF_DESCENT = 4;
const CELL = Math.floor(EM / BDF_HEIGHT); // 62
const RADIUS = Math.floor(CELL * 0.4);    // ~25
const ASCENT = CELL * (BDF_HEIGHT - BDF_DESCENT); // 750
const DESCENT = CELL * BDF_DESCENT; // 250

/**
 * Add a circle to a path using cubic Bezier curves
 * All coordinates are rounded to integers for better WOFF2 compression
 */
function addCircle(path: opentype.Path, cx: number, cy: number, r: number) {
  const k = Math.round(r * 0.5522847498);
  cx = Math.round(cx);
  cy = Math.round(cy);
  r = Math.round(r);

  path.moveTo(cx + r, cy);
  path.curveTo(cx + r, cy + k, cx + k, cy + r, cx, cy + r);
  path.curveTo(cx - k, cy + r, cx - r, cy + k, cx - r, cy);
  path.curveTo(cx - r, cy - k, cx - k, cy - r, cx, cy - r);
  path.curveTo(cx + k, cy - r, cx + r, cy - k, cx + r, cy);
  path.closePath();
}

async function main() {
  const bdfPath = process.argv[2];
  const outputName = process.argv[3] || "DotMatrix";

  if (!bdfPath) {
    console.error("Usage: npx ts-node src/bdf-to-dot-otf.ts <path-to-bdf> [output-name]");
    process.exit(1);
  }

  console.log(`Reading ${bdfPath}...`);
  const bdf = await $Font(getline(bdfPath));

  // Create notdef glyph
  const notdefPath = new opentype.Path();
  const notdefGlyph = new opentype.Glyph({
    name: ".notdef",
    unicode: 0,
    advanceWidth: CELL * 6,
    path: notdefPath,
  });

  const glyphs: opentype.Glyph[] = [notdefGlyph];

  for (const cp of bdf.itercps()) {
    const g = bdf.glyphbycp(cp);
    if (!g || cp < 0) continue;

    const bitmap = g.draw();
    const data = bitmap.todata(2);
    const width = bitmap.width();
    const height = bitmap.height();

    const path = new opentype.Path();

    data.forEach((row, y) => {
      row.forEach((bit, x) => {
        if (!bit) return;

        const cx = x * CELL + CELL / 2;
        // Flip Y and adjust for descent (opentype.js uses bottom-up Y)
        const cy = (height - y - 1 - BDF_DESCENT) * CELL + CELL / 2;

        addCircle(path, cx, cy, RADIUS);
      });
    });

    const glyph = new opentype.Glyph({
      name: `uni${cp.toString(16).padStart(4, "0").toUpperCase()}`,
      unicode: cp,
      advanceWidth: CELL * width,
      path: path,
    });

    glyphs.push(glyph);
  }

  console.log(`Built ${glyphs.length} glyphs`);

  const font = new opentype.Font({
    familyName: outputName,
    styleName: "Regular",
    unitsPerEm: EM,
    ascender: ASCENT,
    descender: -DESCENT,
    glyphs: glyphs,
  });

  // Write TTF
  const ttfBuffer = Buffer.from(font.toArrayBuffer());
  fs.writeFileSync(`${outputName}.ttf`, ttfBuffer);
  const ttfSize = (ttfBuffer.length / 1024 / 1024).toFixed(2);
  console.log(`${outputName}.ttf: ${ttfSize} MB`);

  // Write WOFF2
  console.log("Generating WOFF2...");
  const { woff2 } = await import("fonteditor-core");
  await woff2.init();
  const woff2Buffer = woff2.encode(ttfBuffer);
  fs.writeFileSync(`${outputName}.woff2`, Buffer.from(woff2Buffer));
  const woff2Size = (woff2Buffer.length / 1024).toFixed(1);
  console.log(`${outputName}.woff2: ${woff2Size} KB`);
}

main().catch(console.error);
