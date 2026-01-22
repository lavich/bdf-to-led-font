# BDF to Dot-Matrix Font Converter

Convert BDF (Bitmap Distribution Format) bitmap fonts to modern TTF/WOFF2 fonts with a distinctive LED dot-matrix effect. Each pixel becomes a circular dot, creating an authentic retro display appearance.

## Features

- **BDF to Vector**: Converts bitmap fonts to scalable vector formats (TTF/WOFF2)
- **LED Dot Effect**: Each pixel rendered as a circular dot for authentic LED/dot-matrix display look
- **High Quality**: Produces clean, scalable fonts suitable for web and desktop use
- **Compression**: WOFF2 output is highly compressed (e.g., 15MB TTF → 166KB WOFF2)
- **Unicode Support**: Preserves full Unicode character coverage from source BDF

## Demo

[View Live Demo](https://lavich.github.io/bdt-to-otf/)

## Installation

### Requirements

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bdt-to-otf.git
cd bdt-to-otf
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Conversion

```bash
python3 bdf-to-dot-font.py input.bdf
```

This will generate:
- `DotMatrix.ttf` - TrueType font file
- `DotMatrix.woff2` - Web font file (compressed)

### Example

```bash
# Convert the included Kirsch font
python3 bdf-to-dot-font.py kirsch.bdf
```

Output:
```
Reading kirsch.bdf...
Found 8153 glyphs
  Processing glyph 0/8153...
  ...
Building font with 8154 glyphs...
Saving DotMatrix.ttf...
Saving DotMatrix.woff2...

Results:
  Glyphs: 8154
  TTF:    15.16 MB
  WOFF2:  166.5 KB
```

## How It Works

The converter:

1. **Parses BDF**: Reads bitmap font data including glyph metrics and pixel data
2. **Vectorizes**: Converts each pixel to a circular path using TrueType curves
3. **Optimizes**: Creates efficient glyph outlines with proper metrics
4. **Exports**: Generates TTF and compressed WOFF2 formats

### Font Metrics

- Default EM size: 1000 units
- Configurable dot size and spacing
- Preserves original character widths and spacing
- Maintains Unicode code points

## Web Usage

### CSS

```css
@font-face {
  font-family: 'DotMatrix';
  src: url('DotMatrix.woff2') format('woff2');
  font-weight: normal;
  font-style: normal;
}

.led-display {
  font-family: 'DotMatrix', monospace;
  font-size: 32px;
  color: #0f0;
  text-shadow: 0 0 10px #0f0, 0 0 20px #0f0;
}
```

### HTML

```html
<div class="led-display">
  HELLO WORLD
</div>
```

## Dependencies

- [fontTools](https://github.com/fonttools/fonttools) - Font manipulation library
- [Brotli](https://github.com/google/brotli) - Compression for WOFF2 format

See [requirements.txt](requirements.txt) for exact versions.

## File Structure

```
bdt-to-otf/
├── bdf-to-dot-font.py    # Main converter script
├── kirsch.bdf            # Example BDF font (8154 glyphs)
├── DotMatrix.ttf         # Generated TTF font
├── DotMatrix.woff2       # Generated WOFF2 font
├── index.html            # Demo page
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Technical Details

### BDF Format

BDF (Bitmap Distribution Format) is a bitmap font format originally created by Adobe. It stores glyphs as hexadecimal bitmap data with metadata about character dimensions and spacing.

### Conversion Process

1. Each pixel in the bitmap is identified by its coordinates
2. A circular bezier curve path is generated for each pixel
3. Paths are combined to form complete glyph outlines
4. Font metrics (ascent, descent, width) are calculated
5. TrueType tables are generated with proper encoding

### Output Quality

The dot-matrix effect creates:
- Authentic retro aesthetic
- Scalable to any size without pixelation
- Clean circles with smooth anti-aliasing
- Consistent dot size across all glyphs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Example font: [Kirsch](https://github.com/molarmanful/kirsch) by molarmanful
- Built with [fontTools](https://github.com/fonttools/fonttools)

## Related Projects

- [BDF Format Specification](https://www.adobe.com/content/dam/acom/en/devnet/font/pdfs/5005.BDF_Spec.pdf)
- [fontTools Documentation](https://fonttools.readthedocs.io/)

---

Made with Python and fontTools
