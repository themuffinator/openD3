# TrueType font system

openD3 draws GUI and console text from scalable TrueType faces reconstructed from
Doom 3's bitmap fonts. This document covers both halves: the generator that builds the
font files, and the engine path that draws with them.

This is the default path. `r_useTrueTypeFonts 0` returns to the retail bitmap atlases,
which are also the fallback whenever a `.ttf` is absent.

## Why

The retail fonts are fixed 12, 24 and 48 point atlases drawn onto a 640x480 virtual
canvas. Doom 3 draws nearly all of its menu, HUD and PDA text from the 12 point atlas,
so at 1440p that atlas is magnified twelve times. The TrueType path rasterises the same
letterforms at the resolution the display uses, so text stays sharp, and it draws the
characters the retail atlases never had.

## The font files

`content/baseod3/pak0/fonts/*.ttf`, one face per retail bitmap font:

| File | Family | Stock `font` value | Source | Notes |
| --- | --- | --- | --- | --- |
| `english.ttf` | openD3 Default | `fonts` (the default) | `fonts/english/fontImage_48.dat` | Wide squared sans; menus, actions, most device text |
| `bank.ttf` | openD3 Bank | `fonts/bank` | `fonts/english/bank/` | Engraver's capitals with small capitals for lower case |
| `an.ttf` | openD3 AN | `fonts/an` | `fonts/english/an/` | Narrow grotesque; lists, mail, chat |
| `micro.ttf` | openD3 Micro | `fonts/micro` | `fonts/english/micro/` | Heavy extended square face; numerals, device labels |
| `bigchars.ttf` | openD3 BigChars | `textures/bigchars` | `textures/bigchars.tga` | Console and engine text; monospaced, one em to a cell |

The engine resolves a GUI's `fonts` to `fonts/<language>` and `fonts/an` to
`fonts/<language>/an`, as Doom 3 does, then looks for the `.ttf` beside the language
folder: `fonts/english` finds `fonts/english.ttf`, `fonts/english/an` finds
`fonts/an.ttf`. The files are language independent.

Every face maps about 2,950 code points: ASCII, Latin-1, the Windows-1252 punctuation,
Latin Extended-A and B, Vietnamese, Greek, Cyrillic, Arabic (with the Presentation
Forms-B joined shapes), Hebrew, punctuation, currency, arrows and geometric shapes.

## Generator

`tools/assets/fonts/` rebuilds the whole set from an installed copy of the game. It
needs Python with NumPy, Pillow, fontTools, SciPy and contourpy.

```bash
python tools/assets/fonts/extract_source_fonts.py --install "C:/Program Files (x86)/Steam/steamapps/common/Doom 3" --output .tmp/fontsrc
```

```bash
python tools/assets/fonts/build_opend3_fonts.py --source .tmp/fontsrc --donors .tmp/fontdonors --output content/baseod3/pak0/fonts
```

The donor directory needs `NotoSans-var.ttf`, `NotoSansArabic-var.ttf` and
`NotoSansHebrew-var.ttf` from the Google Fonts repository, alongside their `OFL.txt`.
A full build takes ten to twenty minutes.

### What the source is

Doom 3's atlases are antialiased renders of four drawn typefaces. The `.dat` records
name the files they were rendered from: `ARIALN` (Arial Narrow) for `an`, `BNKGOTHM`
(Bank Gothic Medium) for `bank`, `M025096D` for `micro` (a heavy extended face of the
Microgramma kind) and `chrswfte` for the default face, which this project has not
identified. The 48 point atlas is the highest-fidelity source: capitals are 26 to 35
texels tall and stems about three texels wide. Every glyph rect carries a texel of
border, and the pen starts at the rect's edge: there is no separate side bearing.

DEL and the whole 0x80 to 0x9F band hold one missing-glyph box, 33 identical slots.
The builder recognises a drawing shared by that many slots as the box and leaves those
slots open for the later stages.

### Tracing

`d3font/curvefit.py` is the tracer. The tracer openQ4's faces were built with models a
glyph as stems, diagonals and simple arcs; on these drawn typefaces it facets the bowls
and leaves lumps at the joins. The curve-fitting tracer works in six steps, all in the
source atlas's texel space:

1. **Contour.** The coverage block is resampled bicubically to six times its size,
   lightly blurred and contoured at the 50% level. The result is a dense, smooth outline
   that is close to the drawn edge but not exact: interpolating area samples pulls an
   edge towards a saturated neighbour, rounds every corner over about a texel and thins
   a stroke narrower than a texel and a half.
2. **Refinement.** The dense outline is rasterised with exact area coverage, the way
   the retail glyph was made, and compared with the retail block. Each texel's residual
   is shared among the outline points near it, and the outline moves out where the
   render is short of ink and in where it has too much. After a few passes its render
   reproduces the retail coverage to about 0.1% of the block.
3. **Structure.** Corners are found from the turning angle over a window as wide as the
   rounding, and told from tight curves by what happens beyond it: a corner's edges run
   on straight, an arc keeps turning. Between corners, axis-parallel straight stretches
   become exact lines whose offsets are shared across the glyph, so both edges of a stem
   have one coordinate, and curves are cut at their horizontal and vertical extrema,
   where the tangent is known exactly.
4. **Short edges.** A stroke's end is an edge a few texels long with a corner at each
   end; almost nothing of it survives the rounding to fit a line to. Its two neighbours
   are long and well determined, so it has two unknowns, how far along each neighbour
   its corners lie, and they are found by matching the coverage of the quadrilateral
   they make to that of the refined outline.
5. **Fitting.** Each curved piece is fitted with cubic Beziers that share a tangent
   where they meet. Both ends and both end directions are fixed, which leaves the two
   handle lengths; they are optimised directly against the distance from the data to
   the curve. Pieces are cut into equal lengths until they fit within 0.075 of a texel.
   The cubics become the quadratics a TrueType outline holds.
6. **Corners.** A corner is rebuilt as the intersection of its two edges, checked
   against the retail coverage so that a shallow intersection cannot grow a spike, and
   then cut back by the area a perfectly sharp vertex gets wrong: flat across an acute
   corner (the apex of a W), with a curve at a right or obtuse one (the corners of a
   square bowl).

The console sheet is traced the same way with every distance scaled toward its 16 texel
cell. Its counters are under a texel wide: the eye of an `e` is a dip to two thirds
coverage, not a hole, so the 50% contour closes it. Those dips are picked up from a
higher contour and sized by the refinement.

### Building the rest

The steps after tracing are those of openQ4's generator:

- **Marks** are lifted out of the retail precomposed letters (the acute out of `Á`, the
  cedilla out of `Ç`), and caron, macron, dot-above and double-acute are derived from
  them. The breve and the ogonek come from the weight-matched donor.
- **Letters** such as dotless `ı`, `ł` and `đ` are built from the face's own letters.
- **Composition** builds Latin Extended and Vietnamese as base plus mark, so they are
  the face's own shapes.
- **Shape sharing** reuses the traced outline for Cyrillic and Greek letters identical
  to a Latin one.
- **Symbols** the retail atlases left blank or boxed, including the whole Windows-1252
  band, are built from the face's own glyphs.
- **Donors** supply what is left, from Noto instantiated at the weight and width whose
  stem-to-cap ratio matches the face. In Bank, whose lower-case slots are small
  capitals, a donor lower-case letter is the donor's capital at small-capital height.
- **The console cell.** BigChars is fitted last: every glyph is pressed into the cell
  the console clips to and given the cell as its advance.

### Fidelity

`tools/assets/fonts/audit_fonts.py` rasterises every traced glyph back into its atlas
slot and compares it with the retail coverage.

| Face | Traced glyphs | Mean overlap (IoU) | Lowest | Flagged |
| --- | --- | --- | --- | --- |
| Default | 189 | 99.2% | 93.0% | 1 |
| AN | 189 | 98.9% | 88.7% | 1 |
| Bank | 189 | 99.2% | 89.0% | 4 |
| Micro | 189 | 99.4% | 94.2% | 2 |
| BigChars | 217 | 97.0% | 89.2% | 0 |

The inherited tracer scored 96 to 98.6% on the four GUI faces and 90.6% on the console
sheet. The flagged glyphs are small symbols (the lowest are a few texels across) and
one capital whose retail art is cut off at its rect.

```bash
python tools/assets/fonts/audit_fonts.py --source .tmp/fontsrc --fonts content/baseod3/pak0/fonts --output .tmp/fontaudit --sheets
```

The retail atlases cannot ship, so `tools/tests/ttf_font_integrity.py` checks what the
font files alone can prove: coverage, no visible character drawn empty, no C1 control
mapped, no two accented letters with one drawing, and every BigChars glyph inside the
console cell.

### Retail quirks the builder handles

- **Boxes.** The 33 missing-glyph slots are not traced (above).
- **Bank's sharp s** is drawn `SS`, as small capitals write it; the face keeps that.
- **Bank has no lower case.** Its lower-case slots are small capitals at four fifths of
  the cap height, and nothing descends.

## Engine

- `src/renderer/TrueType.h/.cpp` is a self-contained TrueType reader and rasteriser
  with no third-party dependency.
- `src/renderer/tr_fontTTF.cpp` rasterises U+0020 to U+00FF into the 256 base glyph
  slots for each of the three point sizes, packs them into an atlas and fills the same
  `fontInfo_t` the bitmap loader produces. Code points above U+00FF go into a second
  atlas of sparse pages. The atlas is rasterised at the display's own upscale factor.
- `R_BuildConsoleFontAtlas` rebuilds the console's 16x16 grid at display resolution
  from `bigchars.ttf` and retargets the `textures/bigchars` material at it, so the
  console and loading text sharpen without any change to their draw paths.

### Fitting the three slots to the retail atlases

Doom 3's three atlases are not rescales of one another. Each was rendered separately,
hinted to its own pixel grid, and stored with a texel of space after every glyph.
Measured against the 48 point slot:

| Face | 12 point advance | 24 point advance | 12 point cap height |
| --- | --- | --- | --- |
| Default | +20% | +3% | +12% |
| AN | +19% | +4% | +14% |
| Bank | +7% | 0 | +8% |
| Micro | +11% | +4% | +9% |

The GUIs were laid out against those slots: buttons are centred with leading spaces,
rows are sized to their longest string. One outline rasterised uniformly at three sizes
would sit on a different baseline and run narrower. When the retail `.dat` files are
present, which they always are for a Doom 3 install, `R_TTFFitSlotsToRetail` fits each
slot to its retail counterpart:

- its line height becomes the retail one;
- its outline is stretched about the baseline so glyph tops land on the retail tops;
- every pen advance grows by a constant, the median over letters and digits of the
  retail advance minus the face's own. The retail advances themselves are whole texels
  chosen for hinted bitmaps; under unhinted outlines they leave uneven gaps, so the
  slot takes what they add on average and keeps the face's rhythm. A line comes out as
  wide as the stock's to within the rounding noise;
- a fitted slot is selected by authored text scale exactly as a retail atlas is.

### The 12 point threshold

Doom 3 draws text up to scale 0.30 from its 12 point atlas (`gui_smallFontLimit`). The
engine inherited a limit of 0.10, under which the 12 point slot was never chosen and
every line between 0.10 and 0.30, 21% of the stock's text windows and nearly all menu
text, was laid out with the 24 point metrics. The default is 0.30 again.

### Face names

`R_CanonicalFontName` folds the face names of other games that inherited engine code
still asks for (`chain`, `lowpixel`, `marine`, `profont`, `strogg`, `r_strogg`, `menu`,
`alien`) onto the default face. Doom 3 content names only `fonts`, `fonts/an`,
`fonts/bank` and `fonts/micro`.

### Cvars

| Cvar | Default | Meaning |
| --- | --- | --- |
| `r_useTrueTypeFonts` | `1` | Draw GUI and console text from the `.ttf` faces |
| `r_ttfFontResolution` | `1.0` | Multiplier on atlas rasterisation resolution |
| `r_ttfFontDebug` | `0` | Dump each atlas to `fs_savepath/ttfatlas` and log how each slot was fitted |
| `gui_smallFontLimit` | `0.30` | Largest text scale drawn from the 12 point slot |
| `gui_mediumFontLimit` | `0.60` | Largest text scale drawn from the 24 point slot |

## The Interface Atlas

`tools/assets/fonts/embed_atlas_fonts.py` subsets the five faces to the Latin range and
embeds them in `docs/dev/ui/atlas/opend3-interface-atlas.html`, so the atlas is set in
the faces the engine ships. Run it after rebuilding the faces.

## Known limitations

- The typeface behind the default face is not identified; the reconstruction is of its
  rendered shapes only.
- Glyphs with no retail source (Cyrillic and Greek letters without a Latin twin, Arabic,
  Hebrew, most symbols) are Noto's drawings matched for weight and width.
- The console sheet is a 16 texel source. Its trace is smooth and matches the retail
  coverage, but it cannot recover detail the sheet never held.
- Text input above ASCII, Arabic shaping and bidirectional text are not implemented.
- Atlases are rebuilt when fonts are registered; a resolution change wants a restart for
  text to be pixel-exact again.
