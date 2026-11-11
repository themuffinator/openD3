# openD3 UI Visual Design

Specification version 1.0, 11 November 2026. Status: implementation target; the
replacement has not shipped. openD3 runs the stock Doom 3 GUIs today, and launches
pin `ui_retained 0` because the retained interface has no Doom 3 documents yet
([rebase record](doom3-rebase.md)). This specification applies to every
player-facing GUI: menus, dialogs, the HUD, the PDA, gun-mounted displays, in-world
device screens, multiplayer overlays, loading screens and the console.

Version 1.0 records a survey of the effective retail GUI scripts, interface art,
fonts and materials, states the rules a vector replacement follows, and adds the
[modern interface direction](#12-modern-interface-direction): viewing profiles,
adaptive layout, controller and touch behaviour and an accessibility baseline. The
[Interface Atlas](#14-the-interface-atlas) draws the same vocabulary as
independently authored vector references, set in the
[reconstructed TrueType faces](ttf-font-system.md).
[Appendix D](#appendix-d-change-record) lists every change.

## Contents

1. [Purpose, authority and reference](#1-purpose-authority-and-reference)
2. [Visual identity](#2-visual-identity)
3. [Coordinates, density and aspect expansion](#3-coordinates-density-and-aspect-expansion)
4. [Colour, alpha and light](#4-colour-alpha-and-light)
5. [Typography and language](#5-typography-and-language)
6. [Framing and vector geometry](#6-framing-and-vector-geometry)
7. [Components and interaction states](#7-components-and-interaction-states)
8. [Motion, transitions and sound](#8-motion-transitions-and-sound)
9. [Screen composition](#9-screen-composition)
10. [HUD and in-game overlays](#10-hud-and-in-game-overlays)
11. [In-world device GUIs](#11-in-world-device-guis)
12. [Modern interface direction](#12-modern-interface-direction)
13. [Project branding](#13-project-branding)
14. [The Interface Atlas](#14-the-interface-atlas)

Appendices: [A. Survey method](#appendix-a-survey-method),
[B. Measured furniture](#appendix-b-measured-furniture),
[C. Observations recorded during the survey](#appendix-c-observations-recorded-during-the-survey),
[D. Change record](#appendix-d-change-record).

## 1. Purpose, authority and reference

Deliver a high-definition Doom 3 interface at every supported display density and
aspect ratio. Preserve the game's character as cold, self-lit UAC hardware in the
dark, together with its information hierarchy, interactions, motion and sound
vocabulary. Replace low-resolution interface furniture with authored vector
geometry and the bitmap fonts with the reconstructed TrueType faces. Every menu,
dialog, HUD element, PDA page, weapon display, device screen, loading screen and
multiplayer overlay is in scope.

The replacement is repository-authored content under `content/baseod3/pak0/`,
drawn from the measurements recorded here. It does not change the game's visual
identity and it does not bundle extracted retail art: stock bitmaps identify an
appearance, they are not implementation assets. Where the stock draws real imagery
(the planet, level shots, video, the logo) the replacement keeps reading it from the
player's own installation ([bitmap exceptions](#bitmap-exceptions)). The stock GUIs
remain available as the Classic interface and as the reference for every rule below.

Read this specification before composing a screen, component, icon or device. An
unstyled prototype cannot establish visual completion.

### Source hierarchy

1. The installed Doom 3 PK4s, with their actual filesystem precedence, establish
   stock visuals, animation, behaviour, fonts and sounds. Resurrection of Evil's
   archives establish the expansion's differences.
2. Repository `content/baseod3/` changes establish openD3's current features.
3. This specification establishes scalable geometry, density, layout, state and
   motion treatment while retaining both sets of behaviour.
4. Engine captures establish comparison views. Record the map, mode, state,
   language, renderer, resolution and capture command with each one.

The effective copy of a stock file is the one in the last archive in load order:
`guis/mainmenu.gui` exists in `pak000.pk4` and `pak007.pk4`, and the copy in
`pak007.pk4` wins; the 1.3 patch archives also replace the default face's 12 and
24 point pages and the console sheet. Survey the effective copy, never the first one
found.

Use `guis/mainmenu.gui`, `guis/msg.gui` and `guis/restart.gui` for the front-end
family, `guis/hud.gui` and `guis/cursor.gui` for the HUD, `guis/pda.gui` for the PDA,
and each device, weapon and loading GUI for its own family. Do not apply the steel
blue menu chrome to the HUD, the PDA or a device: each family has its own measured
palette and geometry inside the shared vocabulary of section 2.

### Measuring stock sources

Stock GUIs author every rectangle on a 640x480 virtual canvas. Record stock
measurements in source units (`u`) on that canvas and convert them last: at the
1280x720 dp reference, `1 u = 1.5 dp` on both axes, and the stock 4:3 canvas maps
to the central 960x720 dp (section 3).

- **Bitmaps are white.** Almost every furniture bitmap is pure white with its shape
  in the alpha channel; colour comes from the window's `matcolor` through a
  `colored` material stage. Record the shape from the alpha channel and the colour
  from the script, with the material's blend. An additive texture's black is
  transparent.
- **Bitmaps are stretched.** A texture is stretched non-uniformly into its window
  rectangle. Measure proportions in the texture (visible bounds, chamfer legs, line
  and glow widths) and scale them by the drawn rectangle. A proportion survives the
  stretch; a texel count does not.
- **Text.** A `textscale` of `s` draws an em of `48 s` u, which is `72 s` dp at the
  reference. The stock draws scales up to 0.30 from the 12 point atlas, up to 0.60
  from the 24 point atlas and larger text from the 48 point atlas, and the three
  atlases are not rescales of one another (section 5). Take cap and x-heights from
  glyph ink; the glyph rectangles in a `.dat` carry a border.
- **Time.** `onTime` keys are absolute milliseconds on the owning window's own
  timeline, and `resetTime` restarts it. `transition` takes a duration and optional
  acceleration and deceleration fractions of it, written here as `accel(a, d)`;
  omitted, the transition is linear. GUI expressions count `time` in milliseconds,
  material expressions in seconds. One pass through a material `table` takes one
  unit of its index.
- **Hidden work.** Several authored windows never show: their alpha is zero and
  nothing changes it, or their driver is commented out. Record what a player can
  see, and list the rest in Appendix C.
- Record numbers and descriptions only. Extracted art, fonts and captures stay
  outside tracked source. [Appendix A](#appendix-a-survey-method) describes the 1.0
  survey.

## 2. Visual identity

Doom 3's interface is UAC hardware. The menu is a console floating before Mars; the
HUD is the marine's suit; the PDA is a device he carries; every door panel, lift
control and terminal is a product bolted to a wall. All of it is cold, self-lit and
mostly transparent: thin steel-blue and pale cyan light over black space or a dark
scene, cut at 45 degrees, traced by glowing hairlines, set in heavy squared capitals
and engraver's small capitals. Warm colour belongs to the world behind it (the rust
planet, the bronze logo, hell and blood) and to danger. The interface tells the
player things by getting brighter, never by getting bigger or by moving.

Avoid rounded cards and pill buttons, drop shadows, large web headings, gradients
used as decoration, saturated accent colours, indiscriminate blur and blank spacer
areas. Do not obtain fidelity by putting a low-resolution screenshot into a vector
box, and do not tidy the stock's asymmetry into symmetry.

### Recognition traits

These measured traits make an interface read as Doom 3. A reconstruction of a stock
screen that drops one of them is not visually complete.

1. **Cold chrome, warm world.** Menu furniture stays between steel blue `#738CB2`,
   its lighter line colour `#8CA6BF` and blue slate `#2E4052`; text accents are pale
   cyan `#99FFFF` and `#99CCCC`. The only warm pixels in the front end are the planet,
   its halo, the bronze logo and amber user data. The HUD is grey-green and teal, the
   PDA white on near-black, and each device family has its own tint (section 4).
2. **Mostly transparency.** Idle furniture runs at 8 to 30% alpha; page plates at
   80%; the brightest idle element is a hairline at 50%. The same few colours are
   reused across a ladder of alphas instead of adding colours.
3. **Cut at 45 degrees.** Corners, steps and button ends are 45 degree chamfers: 5 u
   on small boxes, 19 to 22 u on buttons and dialogs, 32 u on page plates. Menu
   furniture has no radius at all. Buttons are parallelograms or boxes with one cut
   corner; plates are irregular polygons with notches and loose strokes.
4. **Glowing hairlines.** An edge is a 1 u line with a 4 u falloff either side
   (24, 18, 12 and 6%). Fills are faint or absent, and page plates carry no outline.
5. **A band, not a list.** Front-end navigation is three interlocking parallelograms
   in a band at 85 to 92% of the height, under a logo floating right of centre before
   a slowly turning planet. Sub-menus grow upward out of the band.
6. **Two corner plates on an empty screen.** The HUD is two slanted frames leaning
   25 degrees, in the bottom corners, holding bare sheared numerals. Everything else
   is transient. The weapon list is twelve pips, not a bar of icons.
7. **Type with strict jobs, at nearly one size.** Heavy squared capitals for actions
   and titles; Bank Gothic small capitals for labels and values; the narrow grotesque
   for dense reading; the heavy extended face for numerals, device labels and
   warnings. Most menu text is one size, 12 u. There are no text shadows in the menus.
8. **Built, then lit.** Every panel is born as a translucent white flash that settles
   to its tint within 50 ms plus 200 to 300 ms; pieces fire 50 ms apart; geometry
   decelerates into place from the control that opened it; text appears last in a
   single frame. The PDA boots; notices assemble themselves; LOADING types itself.
9. **Flash in, slow out.** Hover jumps brighter than its resting hover state and
   settles in 250 ms, and releases in 400 ms. A press is a flash or a 200 ms dip,
   never a held state. Nothing scales or moves under the pointer.
10. **Monitor artefacts.** Scan lines at 6 to 12%, a 15 u cyan grid at 2.5 to 5% that
    lights where the pointer crosses it, a flickering glow around the screen edge,
    furniture that breathes on a 400 ms flicker, and on device screens a stack of
    glass, dirt, static and bezel shadow, each almost too weak to see.
11. **Colour is state, tint is place.** On devices red is locked, green-cyan is open
    and amber wants attention, on the same white art; a wash of colour over the whole
    screen says where the device is. In the HUD a warning is a change of hue on the
    same shapes: amber, then red.
12. **Quiet.** Front-end menus make no sound on hover. A click up goes forward, a
    click down goes back, a chirp applies. Devices answer with one click or one error
    tone.

### Divergences to avoid

Do not introduce these, and do not carry them into the replacement:

- rounded rectangles, circles or pill shapes in menu, HUD or PDA furniture (devices
  have measured exceptions, section 11.3);
- an outline stroke on a page plate, or a closed outline around a field or a row;
- warm, red, green or yellow tints on menu chrome; amber is user data and warning,
  red is danger and a locked device;
- text shadows, outlines, glows, italics or letter-spacing in the menus;
- menu text above 0.35 scale (16.8 u) or below 0.20 (9.6 u);
- a control that scales, bounces or moves on hover, or a held pressed state;
- hover sounds in the front end and dialogs;
- an opaque backdrop behind a menu page: space and the planet show through page
  plates, and only dialogs are opaque, over a 50% dim;
- a symmetrical front end: the logo sits 20 u right of centre and the frame is
  heavier at the trailing side;
- drop-down lists, arrows, spinners and boxed value fields: a value is bare text that
  cycles on click, and a slider is a ticked ruler with a 4x8 u thumb;
- icons in the single-player menus;
- page text that fades in: content switches on in one frame after its plate has
  unfolded;
- the menu chrome applied to the HUD, the PDA or a device.

### Families

| Family | Identity | Required fidelity |
| --- | --- | --- |
| Front-end menus | Steel-blue transparency over Mars; parallelogram navigation band; chamfered plates | The backdrop stack, the band, interlocking ends, hairline glow, white-flash construction, both type voices |
| Dialogs | An opaque slate plate with four chamfers inside a glowing pale-blue octagon, over a dim | Plate and outline geometry, title rule, button order and default focus |
| Death screen | The menu pieces retinted warm over fire, blood and turning pentagrams | The retint, the flickering logo, options that type themselves |
| HUD | Two leaning corner frames, sheared numerals, twelve pips; everything else transient | Lean, stepped top edge, the warning ramp, pulses, the empty centre |
| Crosshair and focus cursor | Dot, ring, four arcs and a hairline circle; becomes the device cursor | Radii, the talk state, the hit flash |
| PDA | A full-screen opaque device: stepped bands, three tabs, a bracketed main frame | The boot sequence, staggered rows, white text on near-black, the info box |
| Weapon displays | Ice-blue digits on the gun, orange warnings | Legibility at view-model distance, per-weapon states |
| In-world devices | 457 screens in 18 families, each a UAC product | Each source's geometry, palette, timeline and sounds; the finishing stack; never the menu chrome |
| Multiplayer | Teal panels hung from a tab strip; slanted status plates; a scoreboard that snaps shut | Tab and panel recipe, player colours, the scoreboard's open sequence |
| Loading screens | A dark level picture under black bands with a 45 degree step; typed LOADING and an amber bar | Bands, the typing, bar geometry and completion, the text block |
| Console and engine text | Cyan fixed-cell text on black under a cyan rule | The 8x16 cell grid, colours, prompt and scroll marks |
| Intro and credits | Cyan crawl text; name and role pairs that flash, slide and fall | Reveal choreography and timings |

Family tokens extend the shared geometry, motion and interaction tokens. Their
colours and motifs are measured from their sources and recorded in sections 4 to 11.
An invented palette applied to all devices does not satisfy full GUI replacement.

## 3. Coordinates, density and aspect expansion

The replacement lays out in density-independent pixels and expands with the view; the
stock canvas remains the unit of record.

| Quantity | Value |
| --- | --- |
| Stock canvas | 640x480 `u`, origin at the top-leading corner |
| dp reference | 1280x720 dp; `1 u = 1.5 dp`; the canvas is the central 960x720 dp |
| Side fields at 16:9 | 160 dp (106.7 u) either side of the canvas |
| Portrait reference | 720x1280 dp; the canvas spans the width at `1 u = 1.125 dp` |
| Text em | `48 s` u = `72 s` dp for `textscale` `s` |
| Hairline | 1 u (1.5 dp), never thinner than one physical pixel |
| Hairline glow | 4 u (6 dp) either side, falling 24%, 18%, 12%, 6% of the line's alpha per u |
| Stock grid | 15 u (22.5 dp) pitch, accent lines every 75 u (112.5 dp) |
| Scan lines | 2 u (3 dp) pitch: 1 u dark, 1 u clear |

### Classic and Remastered

Every screen has two layouts built from the same components.

- **Classic** reproduces the stock composition: the 640x480 canvas is scaled
  uniformly to the view's height (to its width below 4:3) and centred, with every
  element at its stock position and size. Backdrops that are scenery (space, the
  loading picture, the death screen's fire) fill the view beyond the canvas; nothing
  else is added to the side fields.
- **Remastered** keeps every size, proportion, colour and timing and re-anchors the
  composition to the real view. Elements belong to an anchor (a corner, an edge or
  the centre) and keep their stock offset from it.

| Element | Remastered anchor |
| --- | --- |
| Menu backdrop: stars, planet, halo | View centre; stars and grid continue to the view's edges |
| Grid | Continues at its 15 u pitch from the canvas origin in every direction |
| Scan lines, edge glow | The whole view; the glow hugs the real edges |
| Top bar and flare; bottom strips | Leading parts to the leading edge, trailing parts to the trailing edge, their spans stretched between |
| Navigation band, logo, page plates, dialogs | The canvas, centred |
| Hint line | Bottom-leading corner of the canvas |
| HUD health and armour frame | Bottom-leading corner of the view, stock offsets |
| HUD ammunition frame, weapon pips | Bottom-trailing corner of the view, stock offsets |
| Crosshair, centre notices | View centre |
| PDA | Canvas centred; bands stretched to the view's edges |
| Loading picture and bands | The whole view; progress group top-leading, text block bottom-leading |
| Device screens | Their own canvas on their surface; no expansion |

Side-anchored elements stop moving outward at 21:9: on a wider view they keep the
position they have at 21:9, measured from the view centre. On a view narrower than
4:3 the canvas spans the width, top-anchored elements go to the top of the view and
bottom-anchored elements to the bottom, and the centre keeps the stock composition.

Essential content, text and targets stay inside the platform's safe area. Backdrops,
bands and scan lines extend full-bleed under display cutouts, rounded corners and
system bars.

### Density rules

- Geometry is authored in dp and rasterised at the display's density. A chamfer, a
  hairline and its glow keep their dp size at every resolution; nothing is a
  magnified bitmap.
- A hairline is centred on its edge and snapped so that its core covers whole
  physical pixels. Its glow is a linear falloff, not a blur of the scene.
- Scan lines and the grid are procedural. Snap their pitch to a whole number of
  physical pixels so they never beat against the display; where 3 dp is fewer than
  two physical pixels, omit the scan lines.
- Text is drawn from the TrueType faces at the size the display needs (section 5).
- An interface scale and a text scale (section 12) multiply dp sizes; they never
  change proportions inside a component.

## 4. Colour, alpha and light

Doom 3's interface art has almost no colour of its own. Furniture bitmaps are white
shapes, tinted where they are drawn, and most of what the player sees is a handful of
tints at a ladder of alphas over a dark scene. Colour is therefore specified as tokens:
a hue, an alpha and a blend, named by family and role. A token belongs to one family;
do not borrow a menu token for the HUD or a HUD token for a device.

### Principles

1. **Cold chrome, warm world.** Interface furniture is steel blue, slate, teal, pale
   cyan and white. Warm colour is the world (the planet, the logo, fire, hell), danger
   (the amber-to-red warning ramp, a locked device, an alarm) and the player's own data
   (a save name, an objective title).
2. **Alpha carries value.** A family uses a few hues and many alphas. Emphasis is a
   higher alpha of the same hue, not a new hue.
3. **Light is state.** Hover, focus, selection and pulses raise alpha or shift toward
   white. A warning changes hue on the same shape.
4. **Nothing persistent is opaque** except a dialog plate, the PDA and a device's black
   field. Space, the scene or the level picture shows through everything else.
5. **Tint is place.** A device's additive wash and the death screen's warm retint say
   where the player is; they never mark state.

### Families at a glance

| Family | Hues | Idle alpha range | Text | Defined in |
| --- | --- | --- | --- | --- |
| Front-end menus, dialogs | Steel blue `#738CB2`, line `#8CA6BF`, slate `#2E4052`, rule `#99CCFF` | 8 to 50%; page plate 80%; dialog plate 100% | White, `#99FFFF`, `#99CCCC` | This section |
| Death screen | The menu pieces retinted: `#FFFF99`, `#CCB280`, `#FFCC99` over an additive `#CC4C00` wash | as the menus | White at 50 to 100% | This section (`scene.death.*`) |
| HUD | Grey-green `#407366`, plate `#174242`, box `#4CCCB2`, pips `#009999` | 20 to 50% | Digits `#ABB2B2` and `#596B66` | Section 10.2 |
| HUD warnings | Amber `#FF9900`, then red `#FF1A00` and `#CC2600` | 15 to 100%, pulsing | The digits themselves | Section 10.2 |
| Notices | Label `#CCFFFF`, title `#FF9933`, body `#99CCCC` on a dark panel at 70% | n/a | as listed | Section 10.2 |
| PDA | Near-black `#000505`, chrome `#CCFFFF`, grid `#99FFFF` at 2% | Opaque field | White at 100, 80, 60 and 40% | Section 10.9 |
| Weapon displays | Ice blue `#99CCFF`; warnings `#FF8000` | n/a | Digits | Section 10.10 |
| Devices | State: red `#FF3300`, green-cyan `#33CC99`, amber `#FFB24C`; place tints additive | Black field 90%; slabs 30% | White at 40 to 80% | Section 11.4 |
| Multiplayer | Teal `#1A3333`, frame `#337366`, controls `#99FFFF` | 30 to 50% | White, `#99CCCC`, `#B2FFFF` | Sections 10.11 to 10.13 |
| Loading | Bands black 60% with a `#40586F` soft edge; bar amber `#FFC266` to `#995C00` | n/a | `#3399B2`, white at 90 and 40% | Section 10.14 |
| Console | Black field, cyan `#00FFFF` | Opaque | Cyan; white input | Section 10.15 |

### Menu tokens

| Token | Value | Role |
| --- | --- | --- |
| `text.active` | #FFFFFF at 100% | titles, row labels, body, hovered and selected labels |
| `text.action` | #99FFFF at 100% | idle label of anything that can be activated |
| `text.value` | #99CCCC at 100% (80% in the server browser) | values, column headers, secondary data |
| `text.caption` | #CCFFFF at 100% | list column caption, multiplayer page title |
| `text.dim` | #FFFFFF at 50% | disabled labels, group captions, nav labels while a page is open |
| `text.link`, `text.link.release` | #FFFFFF at 40%; release starts at #CCF2FF at 100% | idle footer links and the OPTIONS tab |
| `text.press` | #FFFFFF at 10% | low point of the press dip |
| `text.off` | #666666 at 100% | unselected item in an exclusive list |
| `text.hint` | #FFFFFF from 50% to 20% | hint line |
| `text.data`, `text.data.edit` | #FFBF66 at 100%; #FFCC66 at 80% (hover #FFFFCC at 80%) | the player's own data: a save name in a dialog, the server-name field |
| `text.credit.name`, `text.credit.role` | #99FFFF, #339999 | credits pairs |
| `chrome.line`, `chrome.line.hover`, `chrome.line.flash` | #8CA6BF at 50%; #8CA6BF at 100%; #CCE6FF at 100% | hairline outline: idle, hovered or focused, start of every hover-in |
| `chrome.fill`, `chrome.fill.hover`, `chrome.fill.open`, `chrome.fill.disabled` | #738CB2 at 30%; #8CA6BF at 50%; #738CB2 at 40%; #737373 at 30% | button and item plates: idle, hovered (and the nav hover plate), a tab grown into its sub-list, unusable |
| `chrome.tab` | #738CB2 at 20%; hover 35% | OPTIONS tab and its stub |
| `chrome.strip` | #738CB2 at 11% | bottom strips |
| `chrome.band` | #99D9CC at 8% | second band |
| `chrome.bar` | #7399B2 at 20% | top bar and flare |
| `chrome.glow`, `chrome.glow.hover`, `chrome.glow.disabled` | #80B2CC at 50%; #99CCE6 at 100%; #667399 at 50% | small glow button frame and fill |
| `chrome.header` | #4C8099 at 100% | browser column-header tab outlines |
| `chrome.radio.on`, `chrome.radio.off` | border #99FFFF at 80% with fill #99FFFF at 40%; border #80B2B2 at 80%, no fill | radio or check box |
| `plate.page` | #2E4052 at 80% | page plate |
| `plate.dialog` | #2E404C at 100% | dialog and message-box plate |
| `plate.bridge` | #336BAB at 15% | bridge from a plate to its nav button |
| `plate.flair` | #6699CC at 20% | flair strokes |
| `plate.sheen`, `plate.shade` | #FFFFFF at 18%; #00141A at 30% | corner light on plates; its mirrored shade on dialogs |
| `plate.outline` | #99CCFF hairline | dialog outline |
| `plate.dim` | #000000 at 50% (70% under engine message boxes) | modal dim |
| `rule.title` | #99CCFF at 20% | rule under every title |
| `rule.group`, `rule.group.header` | #99CCFF at 10%, 22% | group box body and header band |
| `rule.slider` | #99CCCC at 50% | slider ruler |
| `rule.shot` | #669999 at 100% | level-shot frame |
| `rule.hair` | #000000 at 100% | 1 u border of wells and swatches |
| `rule.entry` | #B2FFFF at 10% | entry-box frame in message boxes |
| `well.row` | #000000 at 60%; rim 73% and 87% | option row plate |
| `well.list` | #000000 at 60% | list wells, browser columns, name field |
| `well.inset` | #000000 at 50% | inset boxes, message-box edit well |
| `well.sorted` | #4C0000 at 60% | the sorted browser column |
| `well.select` | #4C8580 at 50%; browser #6699CC at 50%; map list #669999 at 50% | selected list row |
| `well.swatch.selected` | #FFFFFF at 100%, 1 u | selected skin swatch |
| `scene.space` | #000000 | behind everything |
| `scene.star` | grey points to #E2E2E2, additive | star layers |
| `scene.planet` | #865F48 median | planet surface |
| `scene.halo` | #EF8959 peak, additive | limb halo |
| `scene.logo` | #785632 median to #FFFBD8 | logo |
| `scene.grid`, `scene.grid.accent`, `scene.grid.lit` | #99FFFF at 2.5%, 5%, 15% | grid lines |
| `scene.scan` | #000000 at 6 to 12% | scan lines |
| `scene.edge` | #333B40 additive, 100 to 85% | edge glow |
| `scene.death.text`, `scene.death.frame`, `scene.death.caption` | #FFFF99; #CCB280 at 50%; #CCCC99 | death-screen button labels, button frames, column captions |
| `scene.death.rule`, `scene.death.select`, `scene.death.wash` | #FFCC99 at 20% (group 10%); #85661A at 50%; #CC4C00 additive | death-screen rule, list selection, colour wash |
| `flash.build`, `flash.tab` | #FFFFFF at 40%; #FFFFFF at 70% | birth of plates, bridges, strokes and dialogs; birth of nav tabs and sub-list items |
| `flash.press`, `flash.row` | #FFFFFF at 80% (60% closing; 100% on glow buttons); #FFFFFF at 15% | press; row flash on a category change |

### Opacity ladder

The menus reuse these steps; a new menu element takes the step of the role it plays.

| Alpha | Role |
| --- | --- |
| 2.5%, 5% | Grid lines and accent lines |
| 6 to 12% | Scan lines |
| 8%, 11% | Frame bands and strips |
| 10%, 20% | Group-box body; rules and header bands |
| 15%, 20% | Bridge and flair strokes |
| 18% | Plate sheen |
| 20%, 40% | Hint line at rest; idle footer links |
| 30%, 40% | Idle button plate; an opened tab |
| 40%, 70% | White construction flash |
| 50% | Idle hairline; disabled label; modal dim |
| 60% | Wells and row plates (black) |
| 80% | Page plate |
| 100% | Hovered hairline, labels, dialog plate |

### Light and composition modes

- **Straight alpha** is the default: every furniture piece, every text.
- **Additive** light is used for things that glow in the scene: the star layers and the
  planet's limb halo, the edge glow around the screen, the loading screen's text flare,
  the death screen's wash, and on devices the back glow, rim glow, top highlight and
  glass glare. An additive layer has no alpha of its own; its colour is its strength.
- **Masked** layers appear twice in the menus: stars that flare through a fixed mask,
  and interference bands that crawl inside the logo's silhouette.
- The stock never blurs the scene and never multiplies. A modal dims with flat black.
- A hairline's glow is part of the hairline (section 6.2), not a blur and not additive.

Composite in linear order back to front as the stock does. Where the replacement draws
an additive layer over HDR output, it adds at the stock's sRGB strength so the layer is
no brighter relative to the text beside it than it is in the stock.

### Contrast

- Menu body text is white or `#99CCCC` on a `#2E4052` plate at 80% over black space:
  a contrast ratio of at least 9:1 against the plate alone. Keep text on a plate or a
  well; never set reading text directly on the planet.
- The hint line rests at 20% by design. With a controller or keyboard it rests at 50%
  (section 12.4), and the text backing option applies to it.
- HUD digits are `#ABB2B2` over an arbitrary scene behind a 25% plate. The stock gives
  them a black copy offset by 1 and 2 u; the replacement keeps the copy and adds the
  optional backing of section 12.7.
- Do not raise an idle alpha to gain contrast. Raise text size, add the backing, or put
  the text on a well.

## 5. Typography and language

Doom 3 sets its whole interface in four faces and one console sheet. Each has a job,
sizes cluster tightly, and hierarchy comes from the face, the case, the colour and the
alpha rather than from size.

### Faces

Four proportional faces carry all GUI text; a fifth, fixed-cell sheet carries engine text. Fractions
are of the em, measured in the 48 px slot (BigChars: of its 16 texel cell). Ascenders reach the cap
height in every face.

| | Default | Bank | AN | Micro | BigChars |
| --- | --- | --- | --- | --- | --- |
| Stock `font` value | `fonts` (by omission) | `fonts/bank` | `fonts/an` | `fonts/micro` | `textures/bigchars` |
| Internal atlas name | `chrswfte` | `BNKGOTHM` | `ARIALN` | `M025096D` | - |
| Identification | Rounded-square techno sans; family undetermined | Bank Gothic Medium; high confidence (name and design) | Arial Narrow Regular; high confidence (name and design) | Microgramma / Eurostile Bold Extended; medium confidence (design; name unresolved) | Bold grotesque of the Arial Bold kind; inferred from design |
| Cap height | 0.646 | 0.521 | 0.708 | 0.667 | 0.688 |
| x-height | 0.479 | 0.417 (small caps) | 0.521 | 0.479 | 0.500 |
| Descent | 0.188 | 0 | 0.208 | 0.208 | 0.063 |
| Vertical stem | 0.125 | 0.104 | 0.083 | 0.208 (lower case 0.167) | 0.188 |
| Horizontal bar | 0.0625 | 0.083 | 0.0625 | 0.146 | 0.125 |
| Mean advance, a-z | 0.583 | 0.671 | 0.437 | 0.674 | 1 cell |
| Mean advance, A-Z | 0.667 | 0.780 | 0.579 | 0.921 | 1 cell |
| Mean advance, 0-9 | 0.648 | 0.796 | 0.485 | 0.919 | 1 cell |
| Space | 0.313 | 0.417 | 0.250 | 0.271 | 1 cell |
| Pitch | proportional; `1` half width | proportional; figures tabular | proportional; figures tabular | proportional; figures near tabular | fixed |
| Case | upper and lower | capitals and small capitals at 0.80 | upper and lower | upper and lower | upper and lower |
| Coverage | 33-126, 161-255 (Latin-1) | same | same | same | 33-255, plus drawing pieces in 0-31 |

Codes 0-31 and 127-159 of the GUI faces draw a hollow box; 32 and 160 are blank advances. None of
the faces carries the Windows-1252 additions (euro, curly quotes, dashes, ellipsis).

**Default.** A squared sans built from rounded rectangles: O, D, 0 and o are nearly the same shape,
terminals are cut flat, and there are no diagonal cuts. Its mark is contrast: vertical stems are
twice the weight of the horizontals, so a line reads as upright bars joined by hairlines. It is of
normal to wide width with a large x-height and short descenders. G is a C with a bar and no spur; a
is double-storey over a rectangular bowl; g is single-storey with a flat hook; 0 carries no slash;
1 is a stem with a small flag, half the width of the other figures. Spacing is tight.

**Bank.** Bank Gothic Medium: wide, square, nearly monoline capitals with flat terminals and slightly
softened outer corners. It has no lower case; lower-case codes draw small capitals at four fifths of
the cap height, and nothing descends. Its capitals are low for the em (0.52) and its spacing very
loose, so it reads small and airy for its scale. Figures sit in full-width cells.

**AN.** Arial Narrow: a light, condensed grotesque with low contrast, diagonal terminal cuts on C, S,
e and t, a spurred G, a double-storey a and a single-storey g. It is the narrowest face (a line is
about a quarter shorter than in Default) with the tallest capitals of the four. Capital I and
lower-case l are the same shape.

**Micro.** Microgramma or Eurostile Bold Extended: heavy, extended, superelliptical bowls with flat
horizontal and vertical terminals. Capitals advance 0.92 em on average, the widest of the four. It
has a true lower case with lighter stems. Figures are near tabular, 0 is a rounded rectangle and 1
has a long flag and no foot.

**BigChars.** A bold grotesque in fixed cells (section 10.15). Codes 0-31 hold drawing pieces: a dot,
a nine-piece filled panel and hollow frame, brackets, a capsule, a triangle and the two cursors.

**Atlas slots.** Each GUI face ships three hinted rasterisations, at 12, 24 and 48 px to the em. They
are not rescales of one another:

| Normalised to em, 12 / 24 / 48 | Default | Bank | AN | Micro |
| --- | --- | --- | --- | --- |
| Cap height | 0.667 / 0.625 / 0.646 | 0.500 / 0.500 / 0.521 | 0.750 / 0.708 / 0.708 | 0.667 / 0.667 / 0.667 |
| x-height | 0.500 / 0.458 / 0.479 | 0.417 / 0.417 / 0.417 | 0.500 / 0.500 / 0.521 | 0.500 / 0.458 / 0.479 |
| Vertical stem | 0.167 / 0.125 / 0.125 | 0.083 / 0.083 / 0.104 | 0.083 / 0.083 / 0.083 | 0.167 / 0.208 / 0.208 |
| Horizontal bar | 0.083 / 0.042 / 0.063 | 0.083 / 0.083 / 0.083 | 0.083 / 0.083 / 0.063 | 0.083 / 0.125 / 0.146 |
| Mean advance, a-z | 0.718 / 0.612 / 0.583 | 0.721 / 0.670 / 0.671 | 0.538 / 0.452 / 0.437 | 0.760 / 0.712 / 0.674 |
| Line width against the 48 px slot | +23% / +5% / 0 | +8% / -0.5% / 0 | +24% / +4% / 0 | +14% / +6% / 0 |
| Line box (u at textscale 1.0) | 52 / 46 / 45 | 56 / 52 / 50 | 56 / 48 / 48 | 60 / 52 / 51 |

Every stored advance is one texel wider than the outline's, which is 4 u at the 12 px slot, 2 u at
24 and 1 u at 48 for the same textscale; that and whole-texel hinting make small text wider. Text
therefore narrows when a textscale crosses a slot limit: Default at 0.30 sets a test line 412 u
wide, at 0.31 the same line is 362 u. Weight shifts too: Micro is lighter in the 12 px slot, Bank
lighter at 12 and 24, and Default's stem-to-bar contrast is 2:1 at 48, 3:1 at 24.

| Slot rule | 12 px | 24 px | 48 px |
| --- | --- | --- | --- |
| Stock | textscale up to 0.30 | up to 0.60 | above 0.60 |
| openD3 today | up to 0.10 | up to 0.60 | above 0.60 |

With openD3's present limit the 12 px slot is never chosen, which changes the width, weight and
line pitch of every text between 0.10 and 0.30: 21% of the stock's text windows. Stock sets the
first baseline one line box below the top of the text rect and advances lines by the line box plus
5 u; openD3 today rounds each advance up and uses 1.25 line boxes.

**Usage** across all 521 stock GUIs (25804 windows, 4025 of them with literal text):

| Face | Windows naming it | Text windows | Share of text | Commonest scales | Slot use (12 / 24 / 48) | Typical roles |
| --- | --- | --- | --- | --- | --- | --- |
| Micro | 1914 | 1914 | 48% | 0.40, 0.50, 1.0, 0.90, 0.31 | 3% / 50% / 47% | headings, numerals, warnings, device titles |
| Default | none (22632 windows name no face) | 1022 | 25% | 0.25, 0.40, 1.0, 0.70 | 25% / 25% / 51% | general text at every size from 0.12 to 7.8 |
| Bank | 1082 | 923 | 23% | 0.25 (55% of its windows), 0.35, 0.50 | 51% / 32% / 17% | labels, menu text, tables |
| AN | 176 | 166 | 4% | 0.25, 0.32, 0.38, 0.22 | 39% / 57% / 5% | running text, chat, briefings |

Micro is authored at 0.31 or larger, so it avoids its weak 12 px slot. No stock GUI names a face
that does not ship; an unknown name falls back to Default. A window does not inherit a face.

### The TrueType faces

openD3 ships each face as a TrueType reconstruction of the retail bitmaps, and the
engine draws GUI text from them by default (`r_useTrueTypeFonts 1`); the bitmap atlases
remain the fallback. The [font system record](ttf-font-system.md) describes how they
are traced, how closely they match and how the engine fits them to the stock layout.

| Family | File | Stock `font` value | Used for |
| --- | --- | --- | --- |
| openD3 Default | `fonts/english.ttf` | `fonts` | Actions, titles, general device text |
| openD3 Bank | `fonts/bank.ttf` | `fonts/bank` | Labels, values, body text, tables |
| openD3 AN | `fonts/an.ttf` | `fonts/an` | Dense reading: lists, mail, chat, briefings |
| openD3 Micro | `fonts/micro.ttf` | `fonts/micro` | Numerals, device labels, headings, warnings |
| openD3 BigChars | `fonts/bigchars.ttf` | `textures/bigchars` | Console and engine text, fixed cells |

Rules for the replacement:

1. Use only these five families. A new screen takes its faces from the family it joins.
2. Size text in `textscale` (an em of `48 s` u, `72 s` dp) and keep to the ramps in this
   document. Text scale settings multiply the ramp; they do not add sizes.
3. Text keeps the stock's advances. Up to scale 0.30 the stock draws from its 12 point
   atlas, whose letters stand 7 to 24% further apart than the 48 point design; the
   engine fits each TrueType slot to the retail advances so a line is as wide as the
   stock draws it. A replacement screen laid out against stock rectangles relies on
   that; a new screen may use the face's natural advances.
4. Bank's lower case is small capitals at four fifths of the cap height. Author Bank
   text in title case or sentence case and let the face draw it; do not upper-case it.
5. Micro is authored at 0.31 or larger in the stock, never in its 12 point slot. Keep
   Micro at 0.31 or above.
6. Do not synthesise bold, italic or condensed variants, and do not letter-space.

### Menu type ramp

| Role | Face | Scale | Em (u) | Em (dp) | Align | Case | Colour |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Page and dialog title | Default | 0.32 | 15.4 | 23 | leading | capitals | `text.active` |
| Multiplayer page title | Default | 0.35 | 16.8 | 25.2 | leading | capitals | `text.caption` |
| Primary nav, large buttons | Default | 0.26 | 12.5 | 18.7 | centre | capitals | `text.active` |
| Sub-menu items, glow buttons, dialog buttons, footer links | Default | 0.25 | 12 | 18 | leading or centre | capitals | `text.action`, `text.link` |
| Bind category tabs | Default | 0.24 | 11.5 | 17.3 | trailing | capitals | `text.action` |
| Row labels | Bank | 0.25 | 12 | 18 | trailing to a gutter | title case | `text.active` |
| Values, column headers | Bank | 0.25 | 12 | 18 | leading or centre | title case | `text.value` |
| Body, hint line | Bank | 0.25 | 12 | 18 | leading | sentence case | `text.active`, `text.hint` |
| Group captions | Bank | 0.25 | 12 | 18 | leading | title case | `text.dim` |
| Copyright | Bank | 0.20 | 9.6 | 14.4 | leading | sentence case | white at 30% |
| Save and mod list rows | AN | 0.25 | 12 | 18 | leading | data | `text.active` |
| Server and map list rows | Bank | 0.25 | 12 | 18 | leading | data | `text.value` |
| Credits names and roles | Bank | 0.35 | 16.8 | 25.2 | leading | mixed | `text.credit.name`, `text.credit.role` |
| Credits heading | Bank | 0.40 | 19.2 | 28.8 | leading | mixed | `text.active` |

Of 399 text windows in the stock menu, 323 are set at 0.24 to 0.26. Titles are one step larger and
nothing exceeds 0.35 outside the credits. No menu text has a shadow, an outline or a glow. Default
is used for 86 actions and titles and one value; Bank carries labels, values and body; AN appears
only in the save and mod lists; Micro appears only in two windows that never show.

The HUD's ramp is in section 10.3, the PDA's in section 10.9, the devices' in section
11.5, the multiplayer screens' in sections 10.11 to 10.13 and the loading screens' in
section 10.14.

### Case, alignment and shadow

| Habit | Where | Rule for the replacement |
| --- | --- | --- |
| Capitals for anything that acts or titles | Default in menus; Micro on devices | Author the string in capitals; never transform case in the renderer |
| Title case for labels, sentence case for body | Bank | Keep; Bank draws it as capitals and small capitals |
| Labels right-aligned to a gutter, values after it | Option rows | Keep the gutter; values are bare text |
| Text seated by negative offsets in 13 to 16 u cells | Menus | Centre text on its cell by cap height instead; the result matches |
| Centring by leading spaces in the string | Many menu buttons | Centre with alignment and strip the padding (Appendix C) |
| No shadow, outline or glow on text | Menus, PDA, devices | Never add one |
| A black copy offset by 1 to 2 u | HUD digits and notices | Keep as a drawn copy, not a blurred shadow |
| Sheared digits | HUD | Shear the text with its plate (section 10.3) |
| One size for nearly everything | Menus 12 u; PDA and HUD 12 u; device labels large | Do not introduce intermediate sizes |

### Language and coverage

The retail atlases cover Latin-1 only, and codes 127 to 159 draw a hollow box. The
TrueType faces add the Windows-1252 punctuation the stock lacked, Latin Extended-A and
B, Vietnamese, Greek, Cyrillic, Hebrew and Arabic forms, built from each face's own
parts where a letter can be composed and from a weight-matched donor otherwise. A
translated string may be longer than the stock's: a control grows along its middle
section and keeps its ends, and a label that cannot fit its row wraps to a second line
before it is ever scaled down.

## 6. Framing and vector geometry

The stock menu furniture is a small set of white bitmaps whose shape lives in the alpha channel and
whose colour comes entirely from the window that draws them. The replacement draws the same shapes
as paths. Every token named here is defined in section 4; every texel
measurement is collected in Appendix B.1.

Static axis-aligned edges snap to physical pixel centres. Diagonals are antialiased by coverage.
All sizes scale with density (`1 u = 1.5 dp`) except the hairline core, which has a one physical
pixel floor (6.2).

### 6.1 The chamfer system

Every corner, step and button end in the menus is a 45 degree cut. There is no radius anywhere in
the menu chrome. The cuts come in a fixed ladder of sizes, and the size says what kind of object
it belongs to.

| Leg (u) | Leg (dp) | Belongs to | Stock source |
| --- | --- | --- | --- |
| 2 | 3 | the clipped outer corner of a sub-list tab | `button_smallangle1` |
| 5 | 7.5 | small boxes: option rows, inset boxes, sub-menu items, small glow buttons | `select_angle`, `button_cornerangle`, `buttong_cornerangle2` |
| 7 | 10.5 | the top corner of a sub-list tab; flair stroke ends | `button_smallangle0`, `cframe_small` at 7 u |
| 16 | 24 | bridge ends | `cframe_small` at 16 u |
| 19 | 28.5 | the slanted ends of a primary nav button (the full height of its 21 u band, less antialiasing) | `button_edge` |
| 22 | 33 | dialog corners; the near corners of a page plate | `content_smallcorner` |
| 24 | 36 | the ends of the OPTIONS trapezoid and the steps of the frame bands | `button_largeangle0/1`, `borderb_angle` |
| 25 | 37.5 | the dialog outline | `boxframe` |
| 32 | 48 | the far corners of a page plate | `content_corner` |

Rules for the replacement:

1. Draw every cut at exactly 45 degrees on the 4:3 canvas. A cut never becomes an arc, and a
   rectangle that the stock chamfers never loses its chamfer.
2. Use only the legs in the table. A new piece takes the leg of the family it joins: 5 u for a
   control, 22 u for a shell, 32 u for a plate.
3. A box is chamfered on one corner only (top-trailing for controls). Plates and dialogs are the
   only objects cut on more than one corner.
4. The one curve in the stock chrome is the concave arc in the top-right flare (6.8). Keep it
   there and use it nowhere else.

### 6.2 The glowing hairline

A button edge is not a border: it is a 1 px line of light with a short falloff on both sides. It
is the brightest idle element in the menus and the element that carries hover.

| Part | Stock value | Replacement |
| --- | --- | --- |
| Core | 1 texel, drawn 1 u, at 100% of the line colour | 1.5 dp stroke, never less than one physical pixel, never more than 1.5 dp |
| Falloff | 24, 18, 12 and 6% at 1, 2, 3 and 4 u from the core, both sides, then nothing | a continuous ramp from 24% at the core edge to 0 at 6 dp (4 u) |
| Colour | `chrome.line` idle, `chrome.line.hover`, `chrome.line.flash` | same tokens; the falloff uses the core colour |
| Blend | straight alpha | straight alpha |

Rules for the replacement:

1. The core scales with density but stays one physical pixel wide on displays where 1.5 dp is
   less than a pixel. The falloff width scales with density without a floor.
2. Draw the falloff as a linear ramp through the four measured steps (24, 18, 12, 6%). Do not
   replace it with a blur wider than 4 u or a drop shadow.
3. The line follows the outside of the shape it outlines, mitred at 45 degree corners. The
   falloff is clipped by nothing: it may spill over neighbouring furniture.
4. The dialog outline (6.10) uses the same construction in its own colour (`plate.outline`).
   Page plates have no hairline.

### 6.3 Primary nav button

NEW GAME, LOAD GAME and MULTIPLAYER are parallelograms: both ends lean the same way, and
neighbouring buttons interlock. The same piece makes the two tabs of the multiplayer page and the
credits buttons. The apply bar under each options page uses the same parts with its leading cap
mirrored vertically, which makes it a trapezoid (6.9).

| Part | Stock source | Geometry |
| --- | --- | --- |
| Cell | `NewGameBtnLCorner` + `NewGameBtnMiddle` + `NewGameBtnRCorner` | 32 u tall; 214 u wide for NEW GAME (27, 410 to 241, 442) |
| Fill | `button_edge`, `button_middle` | a band 21 u tall, from 5 u to 26 u below the cell top (0.156 to 0.812 of the tile) |
| Leading end | `button_edge` | the edge runs from 7 u in at the band top to 26 u in at the band bottom: a 19 u run over 21 u |
| Trailing end | `button_edge` mirrored on both axes | the leading end rotated 180 degrees, so the two ends are parallel |
| Outline | `buttong_edge`, `buttong_middle` | hairline (6.2) on the band top, the slant and the band bottom; interior empty |
| Hover plate | a second, inset copy of the fill | rest rect inset 7, 3 in a 26 x 26 cap; 1, 3 in the middle; alpha 0 at rest (section 7) |
| Label | `NewGameBtnText` | 160 x 21 u box centred on the band; Default 0.26, centred |

Stock sizes and positions:

| Button | Cell (u) | Band corners, clockwise from top-leading (u, derived from the rects) |
| --- | --- | --- |
| NEW GAME (SAVE GAME in game) | 27, 410, 214, 32 | (34, 415) (215, 415) (234, 436) (53, 436) |
| LOAD GAME | 213, 410, 224, 32 | (220, 415) (411, 415) (430, 436) (239, 436) |
| MULTIPLAYER (QUIT CURRENT GAME in game) | 409, 410, 230, 32 | (416, 415) (613, 415) (632, 436) (435, 436) |

Cells overlap by 28 u so that the slants of neighbours run parallel about 5 u apart (derived).
Colours: fill `chrome.fill`, outline `chrome.line`, label `text.active`. A button that cannot be
used keeps its shape and takes `chrome.fill.disabled` with no outline.

Rules for the replacement:

1. Draw the band as one closed parallelogram and the outline as one open hairline path (top,
   slant, bottom). Do not draw the end caps as separate pieces.
2. Keep the 21 u band, the 19 u slant run and the 5 u gap between neighbours at every width. A
   longer label widens the middle; it never changes the slant.

### 6.4 Sub-menu item

The items that grow out of a nav button (the four options tabs, the four difficulties, the
multiplayer sub-list) and every dialog button are a low box with one chamfered corner, a faint
plate and a bracket of light.

| Part | Stock source | Geometry |
| --- | --- | --- |
| Plate | `OptionsBtn1Border` | rectangle 114 x 19 u in the open state |
| Plate end | `button_cornerangle` | a further 10 u, 19 u tall, with a 5 u chamfer on its top-trailing corner |
| Outline, leading | `buttong_cornersquare` | square bracket: vertical line 4 u in from the tile edge, horizontal lines top and bottom |
| Outline, middle | `buttong_middlesm` | two hairlines 18 u apart |
| Outline, trailing | `buttong_cornerangle` | top line, 5 u chamfer, vertical line, bottom line |
| Pitch | `OptionsBtn1` to `OptionsBtn4` | 20 u, so 19 u plates sit 1 u apart |
| Label | `ControlsBtnText` | 120 to 170 x 13 u, Default 0.25, left (centred in dialogs) |

Colours: plate `chrome.fill`, outline `chrome.line`, label `text.action`. Dialog buttons use the
same five parts in a 96 u wide cell with an 80 x 19 u label box.

Rules for the replacement:

1. Draw one plate path (a 19 u box with a 5 u top-trailing chamfer) and one closed hairline
   around it. The outline hugs the plate; there is no gap between them.
2. Stack items at a 20 u pitch. Do not add separators: the 1 u gap is the separator.

### 6.5 Small glow button

APPLY CHANGES, ADVANCED OPTIONS, LOAD GAME, DELETE, REFRESH and their kind are an outlined box
with a soft fill and no separate plate.

| Part | Stock source | Geometry |
| --- | --- | --- |
| Outline | `buttong_cornersquare2`, `buttong_middlesm2`, `buttong_cornerangle2` | hairlines 15 u apart; square leading end; 5 u chamfer top-trailing |
| Fill | the same tiles | 40% of the frame colour at the centre, rising to about 53% beside the lines |
| Height | `OSBtn1` | 16 u line to line, in a 28 u window |
| Width | `OSBtn1`, `LGCBtn1`, `MPPSBtn1` | 192 u (ADVANCED OPTIONS); 107 to 140 u elsewhere |
| Label | the window's own text | Default 0.25, seated 4 u down, left with leading spaces (Appendix C.2) |

Colours: frame and fill `chrome.glow`; label `text.action`. A three-line variant (`OSBtn1A`)
stacks the same section to 52 u tall.

Rules for the replacement:

1. Draw the fill as a vertical gradient: 53% at each line, 40% across the middle, in the frame
   colour, so the fill brightens and dims with the frame.
2. Centre the label with real centring. Do not reproduce the padding spaces.

### 6.6 Rows, wells, group boxes and rules

Settings sit on black plates, not in boxes. The plates darken the scene behind a line of text and
do nothing else: they have no hover and no selected state.

| Piece | Stock source | Stock size | Geometry | Colour |
| --- | --- | --- | --- | --- |
| Option row plate | `select_edge`, `select_border`, `select_angle` (`CM1`, `OG1`) | 320 x 16 u or 300 x 16 u; pitch 23 u (binds) or 25 u (options) | 60% fill; a 2 u rim at 73% then 87 to 100%; 5 u chamfer on the top-trailing corner | `well.row` |
| Inset box | `select_boxcorner`, `select_boxborderh`, `select_boxborderv`, `select_boxangle`, `select_boxcorner2` (`OS1`, `MPPSBParnt`) | 8 u edge pieces around a plain fill | the same rim; one 5 u chamfer | `well.inset` |
| List well | `LGCBG1`, `MMCBG1` | 410 x 240 u, 310 x 240 u | rectangle, 1 u border | `well.list`, border `rule.hair` |
| Browser column | `MPLanTab1` to `MPLanTab5` | 141 u tall, 2 u gaps | rectangle, 1 u border | `well.list`; the sorted column takes `well.sorted` |
| Group box | `OSBox1_1` to `OSBox1_5` | 350 x 167 u ("Video Settings") | L-shaped body, 16 u header band, bottom-trailing corner chamfered | `rule.group`, header `rule.group.header`, caption `text.dim` |
| Title rule | `OCTitleBar` | page width x 2 u, 23 u below the plate's content origin | rectangle | `rule.title` |
| Level-shot frame | `LGCLevelshot` | 105 x 79 u; 128 x 96 u in the browser | 1 u border | `rule.shot` |
| Radio or check box | `MPLANBtn02Border`, `CLPunkBusterBox` | 8 x 8 u | 1 u border; filled when set | `chrome.radio.on`, `chrome.radio.off` |
| Skin swatch | `MPPSSkin1` | 32 x 64 u | 1 u border; a second white border when selected | `rule.hair`, `well.swatch.selected` |

Rules for the replacement:

1. Draw a row plate as one path with a two-step inner shade (73% at 1 u, 60% beyond 2 u). The
   rim is darker than the body, never lighter.
2. A row plate carries one label and one value. Do not outline the value and do not add a
   hover band: the value text carries hover (section 7).
3. Wells and group boxes are flat fills with at most a 1 u border. They take no hairline glow.

### 6.7 Slider, values, lists and scroll bar

Values are bare text. The only drawn input control is the slider, and it is a ruler.

| Piece | Stock source | Geometry |
| --- | --- | --- |
| Slider ruler | `slider_bg` (`OG8SliderBG`) | 71 x 9 u. Eight major ticks every 10 u, 1 u wide, rising in height: 2, 3, 4, 5, 6, 7, 8, 9 u. Minor ticks at the 5 u midpoints, 2 to 3 u tall at about 30%. A baseline and a faint step line to each tick top at 7 to 20% |
| Slider thumb | `slider_bar` (`OG8Primary`) | 4 x 8 u box: 1 u solid outline, 40% centre, white |
| Choice | `choiceDef` (`OG1Primary`) | text only, Bank 0.25, centred in 50 to 100 u; a click steps to the next value; no arrows, no box |
| Bind | `bindDef` (`CM1Primary`) | text only, Bank 0.25, 195 u wide; a click waits for a key |
| Edit | `editDef` (`OG2Primary`, `SGC1Title`) | text only on the row plate; the save-name field sits in a `well.list` box with a `rule.hair` border |
| List | `listDef` (`LGCLoadList`, `LANServerlist`) | rows about 13 to 14 u tall (inferred from the atlas height); columns by tab stops; the selected row is a filled bar |
| Scroll bar | engine default (`scrollbarv`, `scrollbar_thumb`) | 16 u gutter at the trailing edge, flat white at 17%; a 12 x 12 u square thumb inset 2 u, grey-teal (#6E9499) |

Colours: ruler `rule.slider`; values `text.value`; list selection `well.select`.

Rules for the replacement:

1. Keep the ruler's rising ticks: the control shows magnitude by height as well as position.
   Scale the 71 u length with the row; keep eight major ticks.
2. Keep values as bare text. Never add drop-down arrows, steppers or field outlines to choices
   and binds.
3. The scroll bar is the plainest object on the screen. Draw a flat gutter and a square thumb;
   give it no chamfer and no glow.

### 6.8 Frame pieces

The title screen is framed by thin translucent bands, heavier at the top-trailing and
bottom-trailing corners. The bands are not symmetrical and are not meant to be.

| Piece | Stock source | Stock rect (u) | Geometry | Colour |
| --- | --- | --- | --- | --- |
| Top bar | `TopSmallBorder` | 0, -1, 542, 16 | 12 u band at 60% of the colour over a 4 u line at 100% | `chrome.bar` |
| Top flare | `TopLargeBorder` | 542, -1, 128, 128 | the bar continued, then a region that widens toward the trailing edge: its lower boundary leaves the bar 41% across the tile, follows a concave arc to (0.68, 0.22) and runs at 45 degrees to (0.98, 0.52); a brighter line follows the boundary. The tile hangs 30 u past the screen edge, so the flare is about 37 u deep at the edge | `chrome.bar` |
| Bottom strip, leading | `BottomSmallBorder` | 0, 468, 365, 12 | flat | `chrome.strip` |
| Bottom strip, step | `BottomRightAngleBorder` | 365, 448, 32, 32 | a 45 degree rise from the 12 u level to the 29 u level | `chrome.strip` |
| Bottom strip, trailing | `BottomTallBorder` | 397, 451, 243, 29 | flat | `chrome.strip` |
| Bottom chamfer | `BottomLeftAngleBorder` | 0, 436, 32, 32 | triangle under a 45 degree line from (0, 0.34) to (0.62, 1.0) | `chrome.strip` |
| Second band | `MiddleLeftAngle`, `MiddleTallBorder`, `MiddleSmallBorder` | 177, 432 to 640, 447 | 24 u tall from x 209 to 364, 7 u tall from 396 to 640, joined by 45 degree pieces | `chrome.band` |
| OPTIONS tab | `OptionsBtnLlCorner`, `OptionsBtnLBorder`, `OptionsBtnLrCorner` | 1, 440 to 197, 464 | trapezoid 24 u tall with 45 degree ends | `chrome.tab` |
| Options stub | `OptionsBtnMBorder`, `OptionsBtnMCorner`, `OptionsBtnTlCorner` | 2, 404 to 66, 440 | a small tab above the OPTIONS tab; it grows into the sub-list | `chrome.tab` |

Rules for the replacement:

1. Draw each band as one polygon in its own colour. Bands overlap and their alphas add; do not
   merge them into one shape.
2. Keep the asymmetry: the top bar ends in the flare at the trailing corner, the bottom strip is
   12 u at the leading side and 29 u at the trailing side.
3. The flare boundary line is the only stroked band edge. All other band edges are unstroked.

### 6.9 Page plate

A page (controls, game options, system, load, save, mods, player settings) sits on a slate plate
that is an irregular polygon with satellites. The plate has no outline.

| Part | Stock source | Open-state geometry (Controls) | Colour |
| --- | --- | --- | --- |
| Body | `OptionsBgMain1` to `OptionsBgMain13` | 467 x 341 u: x 161 to 628, y 46 to 387 | `plate.page` |
| Corner cuts | `content_smallcorner`, `content_corner` | 22 u cuts top-leading and bottom-trailing; 32 u cuts top-trailing and bottom-leading | `plate.page` |
| Notch | `content_angle` x 2 | between x 277 and 490 the bottom edge rises 15 u through two 45 degree steps | `plate.page` |
| Apply bar | `OptionsResetCorner`, `OptionsResetMiddle`, `OptionsResetRCorner` | a trapezoid in a 233 u cell (267, 369 to 500, 401) with corners (293, 375), (474, 375), (493, 396), (274, 396): the nav button's parts (6.3) with the leading cap mirrored vertically, so both ends lean outward and nest in the notch | `chrome.fill`, `chrome.line` |
| Bridge | `cframe_large`, `cframe_medium`, `cframe_small` (`OptionsBgBridge1` to `4`) | a slab with a 45 degree leading edge and a 12 u stem, an elbow and a 42 u strip, running from the plate's lower-leading corner toward the nav tab that opened it | `plate.bridge` |
| Flair | `cframe_small2`, `cframe_small` (`OptionsBgFlair1` to `5`) | two 7 u wide strokes with triangular ends: one vertical at x 152, y 208 to 271; one horizontal at y 389, x 257 to 276 | `plate.flair` |
| Sheen | `content_glow` (`OptionsBgMain14`) | a 340 x 279 u soft light at 164, 49: brightest in the top-leading corner, gone by half its size | `plate.sheen` |

Rules for the replacement:

1. Build the body as one polygon with the four corner cuts and the notch. Do not stroke it.
2. Draw the bridge and the flair strokes as separate polygons in their own colours. They are
   what ties a plate to the button that opened it; a plate without a bridge is a dialog.
3. Draw the sheen as a radial gradient anchored on the top-leading corner. It is the only
   gradient on a plate.
4. Each page has its own plate size and satellites (section 9). A new page takes a 22 u and a
   32 u corner, one notch for its apply bar, one bridge and one or two flair strokes.

### 6.10 Dialog shell

A dialog is the one opaque object in the menus: a slate octagon-cornered plate inside a separate
pale-blue outline of light, over a dimmed scene.

| Part | Stock source | Geometry (screen u) | Colour |
| --- | --- | --- | --- |
| Dim | `QuitToOS` | full screen | `plate.dim` |
| Plate | `QOSBgMain1` to `QOSBgMain7` | 364 x 144 u at 140, 130; all four corners cut 22 u | `plate.dialog` |
| Sheen | `QOSBgMain8` | 340 x 279 u at 143, 133, clipped by nothing | `plate.sheen` |
| Shade | `QOSBgMain81` | the sheen mirrored on both axes, toward the bottom-trailing corner | `plate.shade` |
| Outline | `boxframe` x 2 (`QOSGlowLeft`, `QOSGlowRight`) | a hairline (6.2) 5 u outside the plate: x 135 to 509, y 125 to 279, corners cut about 25 u | `plate.outline` |
| Title | `QOSTitleText` | plate + (20, 5), 320 x 20 u, Default 0.32 | `text.active` |
| Rule | `QOSTitleBar` | plate + (5, 23), 325 x 2 u | `rule.title` |
| Body | `QOSText` | plate + (30, 40), 300 x 100 u, Bank 0.25, wraps | `text.active` |
| Buttons | `QOSBtn1`, `QOSBtn2` | plate + (60, 100) and (210, 100); sub-menu items (6.4) 96 x 19 u | 6.4 |

Proportions: the plate is 57% of the canvas width and 30% of its height; the title band is 17% of
the plate height; the buttons take the bottom 22%, centred at 30% and 71% of the plate width. The
CD-key box is the same shell 204 u tall; the advanced server options shell is 440 x 320 u.

Rules for the replacement:

1. Draw the plate and the outline as two paths, 5 u apart on every side. The gap shows the dimmed
   scene.
2. Size the shell to its content by lengthening the straight runs. Corner cuts stay 22 u (plate)
   and 25 u (outline).
3. A dialog never has a bridge, a notch or flair strokes.

### 6.11 Pointer

The stock pointer is engine art (`guicursor_arrow`), not `guis/cursor.gui`: a left-leaning arrow
with a tail, 12 x 17 u in a 32 u tile, tip at the tile origin (the hot spot), shaded from mid grey
(#6B6B6B) to white, untinted, with a 1 u soft edge.

The replacement draws the arrow as a path at 18 x 25.5 dp with the same grey-to-white shading. It
does not tint the pointer with a chrome colour and does not change the pointer over controls.
`guis/cursor.gui` is the in-game crosshair and belongs to the HUD section.

### Bitmap exceptions

These stay raster or rendered in the replacement:

- The DOOM 3 logo (`DoomLogo`), with its interference overlay generated from the logo's alpha.
- The planet (`MarsRender`), a lit 3D model render, and its additive limb halo (`MarsHighlight`).
- Level shots in the load page and the server browser.
- Player skin swatches.
- Video: the id logo and the death screen's fire loop.
- The death screen's blood, face and pentagram layers.
- Game and anti-cheat icons in the server list.

## 7. Components and interaction states

State in the menus is light. A control at rest is dim and partly transparent; under the pointer its
outline flashes and settles brighter and its label turns white; a press is a flash that decays. No
control moves, grows or holds a pressed pose.

### 7.1 State table

| Family | Idle | Hover in | Hover out | Press | Selected or open | Disabled |
| --- | --- | --- | --- | --- | --- | --- |
| Primary nav button | label `text.active`; fill `chrome.fill`; outline `chrome.line` | outline `chrome.line.flash` to `chrome.line.hover`, 250 ms; hover plate from 0% to `chrome.fill.hover` in 200 ms while it shrinks from the full cell to its inset rect in 300 ms, accel(0, 0.9) | outline to `chrome.line`, 400 ms; hover plate to 0%, 400 ms | label 100% to `text.press`, 200 ms; sound | while a page is open the other nav buttons narrow, slide aside and drop to `text.dim` with no outline | `chrome.fill.disabled`, no outline |
| OPTIONS tab | label `text.link`; body `chrome.tab` | label to 100%, 100 ms; body to 35%, 300 ms | label to `text.link`, 200 ms; body to 20%, 300 ms | label 100% to `text.press`, 200 ms | body flashes `flash.tab` to `chrome.fill.open` and grows into the sub-list | none |
| Sub-menu item | label `text.action`; plate `chrome.fill`; outline `chrome.line` | label to `text.active`, 250 ms; outline flash to `chrome.line.hover`, 250 ms; plate to `chrome.fill.hover`, 200 ms | label 250 ms; outline and plate 400 ms | plate flashes `flash.press` (80% opening, 60% closing) and decays in 200 ms | label stays `text.active`; plate removed; outline idle | label `text.dim`; no hover change; error sound on click |
| Small glow button | label `text.action`; frame `chrome.glow` | label to `text.active`, 250 ms; frame `chrome.line.flash` to `chrome.glow.hover`, 250 ms | label 250 ms; frame to `chrome.glow`, 400 ms | frame flashes white 100% to idle, 400 ms | none | label `text.dim`; frame `chrome.glow.disabled`; no events |
| Dialog button | as sub-menu item | as sub-menu item | as sub-menu item | sound, then the action | default focus on the negative choice | none |
| Footer link | `text.link` | to 100%, 100 ms | from `text.link.release` to `text.link`, 200 ms | sound | none | none |
| Controls category tab | label `text.action`; no plate | label to `text.active` and a plate from 0% to `chrome.line` at 30%, 200 ms | label 200 ms; plate 400 ms | plate 20% to 0%, 400 ms; the rows flash (section 8) | label `text.active`; no events | none |
| Quality list item | `text.off` | to `text.active`, 200 ms | 200 ms | sound; a warning line appears | `text.value` after a 100 ms white flash; no events | none |
| Browser column header | `text.value` | to `text.active`, 100 ms | 100 ms | sound; its tab outline flashes white to `chrome.glow.hover`, 200 ms | header `text.active`; column well `well.sorted` | none |
| Radio toggle | label white 50%; box `chrome.radio.off` | label to 80%; box border to `chrome.radio.on`, 100 ms | 100 ms | fill flashes white 80% to the set fill, 250 ms | label 80%; box filled; no events | none |
| Choice, bind, list value | `text.value` | white at once (engine behaviour) | at once | none | list: selection bar | row at 40% when its parent option is off |
| Option row plate | `well.row` | none | none | none | none | none |
| Death screen option | white 50% | to 100% and its subtitle from 0% to 50%, 400 ms; sound | 400 ms | sound | none | none |

### 7.2 Recurring constants

| Constant | Stock value |
| --- | --- |
| Hover in | 250 ms for labels and outlines, 200 ms for fills; 100 ms for footer links, headers and toggles |
| Hover out | 400 ms for outlines and fills, 250 ms for labels: release is slower than arrival |
| Flash | the outline starts its hover transition at `chrome.line.flash`, brighter than the hovered state, and settles |
| Easing | linear for every colour change |
| Press | a 200 ms alpha dip or a white flash that decays; never a held pressed state |
| Geometry on hover | none, except the nav button's hover plate |
| Hint | every actionable control writes one line to the hint line on enter and clears it on exit |

### 7.3 Hint line

A single line of Bank 0.25 at 17, 470, 370 x 10 u (`ToolTip2`), under the nav band at the
bottom-leading corner, describes the control under the pointer.

| Phase | Stock behaviour |
| --- | --- |
| Show | the line's width wipes from 0 to 370 u in 150 ms while its colour runs from white 50% to white 20% in 250 ms (`text.hint`) |
| Rest | white 20%: the hint is the dimmest text on the screen |
| Hide | width to 0 and alpha from 30% to 0% in 50 ms |

A mirrored line at the top-leading corner (`ToolTip1`) is authored hidden.

### 7.4 Focus, selection and values

| Behaviour | Stock |
| --- | --- |
| Dialog default focus | the negative choice (NO, CANCEL) for quit, overwrite and delete; the affirmative for the reset-controls prompt |
| Dialog button order | affirmative leading, negative trailing |
| List selection | a filled bar in `well.select` behind the row; a 1 u outline of the same colour at 100% when the list has focus |
| List row hover | row text turns white |
| Value cycling | a click on a choice steps to the next value and wraps; 20 of the choices are a two-value No / Yes |
| Binding | a click on a bind shows a "press any key" prompt in white until a key arrives |
| Dependent options | a row whose parent option is off drops to 40% and ignores input |
| Buttons that need a selection | LOAD GAME, DELETE and LOAD MOD stay disabled until a list row is selected |
| Sorted column | the chosen header turns white and its column well turns `well.sorted` |

### 7.5 Rules for the replacement

1. **Focus is hover.** Keyboard and controller focus use the hover treatment of the control's
   family, with the same durations: arrival runs the hover-in transition, departure runs the
   hover-out transition. This is a replacement rule; the stock menus are pointer-driven and have
   no focus treatment outside lists and dialogs.
2. Pointer hover and focus never light two controls at once. Moving the pointer moves focus;
   moving focus leaves the pointer's last hover to finish its hover-out.
3. Keep the asymmetry: in 200 to 250 ms, out 400 ms. Do not shorten the release to match.
4. Keep the flash. The outline starts at `chrome.line.flash` on every arrival, including focus
   arrival.
5. Never scale, lift, shift or thicken a control for hover, focus or press. Never add a focus
   ring: the brightened hairline is the ring.
6. A press never latches. Controls that toggle show their state as light (filled box, white
   label), not as a depressed shape.
7. Every focusable control supplies a hint string. The hint line follows focus as it follows
   the pointer.
8. Disabled is dim, not absent: keep the shape, drop the label to `text.dim` and the frame to
   `chrome.glow.disabled`, and keep the hint so the reason can be read.
9. In a dialog, focus opens on the choice that changes nothing. Activating the affirmative
   choice plays its sound before the action runs.
10. Stock inconsistency: the OPTIONS tab's release starts from 30% although its hover reaches
    35%, and the footer link's release starts from `text.link.release` although its hover ends
    at white. The replacement releases from the current value.

## 8. Motion, transitions and sound

The menus behave like hardware switching on: panels unfold out of the nav band, each piece arrives
as a flash of white light and settles to its tint, and text appears only when its panel is built.
Nothing bounces and nothing overshoots.

### 8.1 Motion grammar

| Rule | Stock evidence (`guis/mainmenu.gui`: 3995 transitions) |
| --- | --- |
| Colour moves linearly | 3118 transitions carry no easing; they are the colour and alpha changes |
| Geometry decelerates | 457 rect transitions use accel(0.2, 0.8): plates, bridges, frame pieces |
| Slides ease both ways | 52 use accel(0.4, 0.6): nav buttons moving aside, whole pages panning |
| Camera moves settle long | accel(0, 0.9) and accel(0, 0.8) on the fly-in and the hover plate |
| Durations are quantised | 50 ms (597 uses), 200 (1104), 250 (458), 300 (540), 400 (815), 500 (98), 1000 (109); everything else is rare |
| Steps are 50 ms apart | pieces of one panel fire at 50 ms intervals; list rows at 20 ms |
| Text does not animate | a page's content window switches on in one frame when its plate has finished |

Rules for the replacement:

1. Use only the quanta 50, 100, 200, 250, 300, 400, 500 and 1000 ms for interface motion.
2. Colour and alpha are linear. Position and size use accel(0.2, 0.8); slides of whole groups
   use accel(0.4, 0.6). No spring, overshoot or elastic curve.
3. Reverse transitions are shorter and unstaggered: a panel closes as one object.
4. Input is locked while a screen change runs (the stock holds a click catcher for 350 to 800
   ms). The replacement queues one input rather than dropping it.

### 8.2 White-flash construction

Every plate, tab, bridge, stroke and dialog is born white.

| Step | Stock value |
| --- | --- |
| Birth | the piece appears at `flash.build` (white 40%); nav tabs at `flash.tab` (white 70%) |
| First settle | a 50 ms transition from white toward the piece's token |
| Second settle | the same transition restarted over 200 to 300 ms, so the piece lingers bright, then cools |
| Order | bridge at 0 ms, plate at 50, apply bar at 100, flair at 150; each sub-list item 50 ms after the last |
| Geometry | unfolds from the nav band toward the centre during the same 200 to 400 ms, accel(0.2, 0.8) |
| Content | switched on at the end, unanimated |

Rules for the replacement:

1. Keep the two-stage settle (50 ms, then 200 to 300 ms). A single fade from white reads as a
   fade-in, not as a device lighting up.
2. Flash in white, never in the piece's own tint and never in a warm colour.
3. Closing does not flash: pieces fade to 0% in 50 + 200 ms steps while the plate shrinks back
   toward the nav band in 400 ms.

### 8.3 Opening sequence

| Time (ms) | Event |
| --- | --- |
| 0 | pointer hidden; id logo video full screen with its sting (`guisounds_idlogo`) |
| 12400 | video removed |
| 13000 | pointer shown; menu timeline starts (times below are from this point) |
| +10 | menu music starts |
| +100 | planet turns from (-60, 60, 0) to rest over 12000 ms, accel(0, 0.9); the three star layers shrink from 1256 to 1024 u with parallax; light sweeps for 1000 ms |
| +500 | black fades out over 1000 ms: the frame and nav band are revealed already built |
| +1100 | camera travels to its resting offset over 9500 ms, accel(0, 0.9) |
| +4100 | light settles over 9000 ms, accel(0.1, 0.9) |
| +10700 | limb halo fades in over 2500 ms |
| +12650 | planet begins its endless rotation |
| +169000 | the music restarts (and every 169 s after) |

The menu is usable from +1500 while the planet is still arriving for another 11 s. With the intro
skipped the sequence starts at the 13000 mark. Opened from a game, the planet is already at rest,
the in-game music bed plays, and only the halo fades in (4500 ms, accel(0, 0.8)).

### 8.4 Screen-to-screen choreography

| Change | Stock controller | Length (ms) | Sequence |
| --- | --- | --- | --- |
| Main to options | `AnimMainToOptions` | 680 | 0, 20, 40: the three nav buttons slide aside and narrow (200 ms, accel(0.4, 0.6)), labels to `text.dim`, outlines out in 300 ms. 10: OPTIONS tab flashes. 80: the tab grows upward into a 132 x 89 u plate (200 ms, accel(0.2, 0.8)). 280 to 430: four items arrive 50 ms apart, each a flash settling in 50 + 200 ms |
| Options to main | `AnimOptionsToMain` | 380 | the reverse, unstaggered |
| Sub-list item to page | `AnimControlsUp`, `AnimGameUp`, `AnimSystemUp` | 400 | logo fades out (600 ms); top bar extends to full width (300 ms); plate grows from 258 x 138 u to full size (400 ms, accel(0.2, 0.8)); pieces flash in order (8.2); content on at 400 |
| Page to sub-list | `AnimControlsDown` | 400 | content off at 0; plate shrinks; logo returns (600 ms); top bar retracts |
| Page to page | `AnimControlsToGame` and five siblings | 300 | the plate morphs directly to the other page's size |
| Bind category | `ControlsFlash` | 470 | twelve rows flash `flash.row` to 0% (250 ms each), 20 ms apart, top to bottom |
| Main to new game | `AnimMainToNG` | 700 | as main to options; the stub above NEW GAME opens into the difficulty list |
| Main to load, save, mods | `AnimMainToLG`, `AnimMainToSG`, `AnimModsUp` | 400 | plate grows; logo and top bar as above |
| Main to multiplayer page | `AnimMPUp` | 2300 | the scene pans: menu up 480 u and multiplayer page in from below (1000 ms, accel(0.4, 0.6)); planet and halo leave upward (2000 ms, accel(0.1, 0.2)); stars shift 100 u (2300 ms); the page frame brightens at 1200 |
| Main to credits | `AnimCreditsUp` | 3000 | menu slides down, credits in from above (1000 ms); planet zooms to 1024 x 800 u (2000 ms); logo drifts to 370, 200 (3000 ms); letterbox bars close in (1800 to 2000 ms, accel(0, 0.8)) |
| Dialog open | `AnimQOSUp` and seven siblings | 460 | dim to 50% (200 ms); at 200 the plate and sheen flash and settle (50 + 200 ms); content and focus at 260 |
| Dialog close | `AnimQOSDown` | 200 | dim, plate and sheen fade together |
| Start game | `AnimNewGame` | 2400 | logo fades (1700 ms); menu slides down (1000 ms, accel(0.4, 0.6)); black from 1400 (1000 ms); the game starts at 2400 |
| Quit | `QOSYesBtnText` | 400 | sound, then exit after 400 ms |
| Logo | `LogoDown`, `LogoUp` | 600 | alpha only; the logo is hidden while any page plate is open |
| Top bar | `TopBarSlideOut`, `TopBarSlideIn` | 300 | 542 to 640 u; the flare leaves the screen |

### 8.5 Ambient loops

| Loop | Period | Amplitude |
| --- | --- | --- |
| Planet rotation | 500 s per turn | constant |
| Logo shimmer | 4 s | brightness 90 to 100% in 13 steps |
| Logo interference | continuous | two noise layers crawling at +0.07 and -0.12 logo heights per second, at 5% |
| Star twinkle | 10 s | 12 steps between 5% and 100% |
| Star drift | continuous | 0.002 and 0.01 tile widths per second |
| Scan lines | 500 ms (computed) | 6 to 12% black |
| Edge glow | 500 ms (computed) | 100 to 85% |
| Grid | none | static; responds to the pointer only |
| Music | 169 s | restart |

### 8.6 Death screen and credits

| Screen | Time (ms) | Event |
| --- | --- | --- |
| Death (`guis/restart.gui`) | 100 | black fades out over 1000 ms; a breathing loop starts as music |
| | 1500 | logo flickers on: five 50 ms steps through three damaged variants at 60, 40, 20, 40 and 60%, then 400 ms to full |
| | 1700, 1900, 2200 | the three options type themselves in, one character per 50 ms behind a bracket caret |
| | 3000 onward | logo breathes between 100 and 60% (1000 ms each way) and glitches every 8 s |
| | always | two additive pentagrams turn at about 50 and 5 degrees per second (inferred units); blood layers scroll |
| Credits | 0 | a white bar 300 u wide flashes and shrinks to 100 u (250 ms, accel(0.1, 0.8)); the name slides in 10 u (400 ms, accel(0, 0.5)) |
| | 250 | the role line repeats the entry |
| | 1000 | both lines fall to the bottom over 6000 ms, accel(0.6, 0), fading over 5500 ms |
| | 3000 | the next pair starts |

The death screen is the same furniture retinted warm (section 9.8) and the only menu with hover
sounds. Message boxes do not animate at all: they appear and vanish in one frame.

### 8.7 Sound vocabulary

| Shader | Event | Meaning | Uses |
| --- | --- | --- | --- |
| `guisounds_menuclickup` | action | forward, open, confirm: the default click | 65 |
| `guisounds_menuclickdown` | action | back, close, collapse | 14 |
| `guisounds_chirpconnect` | action | apply, reset, commit, toggle | 17 |
| `guisounds_menuerror` | action | a refused action in a dialog | 6 |
| `guisounds_error` | action | a locked item (NIGHTMARE) | 1 |
| `guisounds_click3` | list action | a list row selected | 3 |
| `guisounds_disconnect1` | action | disconnect from a server | 1 |
| `guisounds_idlogo` | intro time 0 | id logo sting | 1 |
| `guisounds_menu` (music) | menu start | front-end theme, restarted every 169 s | 1 |
| `guisounds_menuingame` (music) | menu start in game | looping pause bed | 1 |
| `guisounds_ping` | hover, death screen only | option under the pointer | 6 |
| `guisounds_ping2` | action, death screen only | option chosen | 4 |
| `guisounds_restartTest` (music) | death screen start | breathing loop | 1 |

Rules for the replacement:

1. No sound on hover or focus in the front end and in dialogs. None of the 154 hover handlers
   in the stock menu plays anything.
2. Use the up click for anything that goes deeper and the down click for anything that comes
   back. Use the chirp only where a value is committed.
3. Engine message boxes are silent in the stock. The replacement plays the up click on their
   buttons, as the in-menu dialogs do.
4. The death screen keeps its hover ping: it is a different device.

### Reduced motion

With reduced motion requested, the replacement keeps light and removes travel.

| Stock behaviour | Reduced motion |
| --- | --- |
| Opening fly-in (12 s camera, rotation and star zoom) | cut to the settled scene; black fades out in 500 ms |
| Planet rotation, star drift | kept: both are slower than 1 degree per second |
| Star twinkle, logo shimmer and interference, scan-line and edge-glow flicker | held at their mean value (scan lines 9%, edge glow 92%) |
| Plate unfold, nav slide, tab growth | cut to the final geometry; the white flash and its two-stage settle are kept |
| Sub-list and row staggers | all items at once |
| Multiplayer and credits scene pans, planet zoom | 250 ms cross-fade between the two compositions |
| Dialog open and close | dim and plate fade in 200 ms; no flash |
| Hover and focus transitions | kept as they are: they are colour only |
| Nav hover plate shrink; hint line wipe | removed: the plate and the hint fade in place |
| Death screen typewriter, logo flicker, pentagram rotation | options appear whole; logo fades in 400 ms; pentagrams hold still |
| Credits fall | names fade in and out in place |

## 9. Screen composition

The front end is one scene: a planet in space, a logo, and a band of three buttons along the
bottom. Pages grow out of that band and cover the middle of the scene with a translucent plate;
the scene is never replaced by an opaque background.

### 9.1 Backdrop layer stack

Back to front. All of it is in `guis/mainmenu.gui`.

| # | Layer | Stock window | Rect (u) | Blend | Colour | Motion |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Space | `Desktop` | 0, 0, 640, 480 | opaque | `scene.space` | none |
| 2 | Stars | `Stars` | -200, 0, 1024, 1024, tiled 4 x 4 | additive | `scene.star` at 70% | moves with page pans |
| 3 | Twinkle | `Stars1` | same, tiled 10 x 10 | additive | grey points | 10 s brightness table; slow drift |
| 4 | Flares | `Stars2` | same, tiled 4 x 4 | masked | white specks behind a star mask | drift |
| 5 | Planet | `MarsRender` | 0, 20, 640, 430 | lit render | `scene.planet` | 500 s rotation |
| 6 | Limb halo | `MarsHighlight` | 133, 57, 373, 373 | additive | `scene.halo` at 70% | fades in after the fly-in |
| 7 | Scan lines | `Scanlines2` | 0, 0, 640, 480 | straight alpha | `scene.scan`: 1 u black, 1 u clear | 6 to 12% flicker |
| 8 | Grid | `LineH1` to `LineH42`, `LineV1` to `LineV31` | 1 u lines every 15 u | straight alpha | `scene.grid`; every fifth line `scene.grid.accent` | a line crossed by the pointer flashes to `scene.grid.lit` and decays in 300 ms |
| 9 | Logo | `DoomLogo`, `DoomLogo2` | 212, 155, 256, 128 | straight alpha | `scene.logo` | shimmer; interference at 5% |
| 10 | Frame, nav, pages | `PrimaryMenuParent` | 0, 0, 640, 480 | straight alpha | chrome and plate tokens | section 8 |
| 11 | Dialogs | `QuitToOS` and seven siblings | full screen | straight alpha | `plate.dim`, `plate.dialog` | section 8 |
| 12 | Hint line | `ToolTip2` | 17, 470, 370, 10 | straight alpha | `text.hint` | 7.3 |
| 13 | Edge glow | `OuterGlowBar` | -30, -20, 700, 520 | additive | `scene.edge` | 100 to 85% flicker; drawn over everything, dialogs included |

The planet disc is about 360 u across, centred near (320, 243) (inferred from the halo). The
accent grid lines fall every 75 u: x = 15, 90, 165 ... 615 and y = 30, 105 ... 405. The grid
ignores the pointer in the bottom 80 u. The stock file also carries layers that never show (two
gradient washes, a scan pulse, a grid fade-in, an introduction caption); the replacement omits
them.

### 9.2 Title screen

| Element | Rect (u) | Notes |
| --- | --- | --- |
| Top bar and flare | 0, -1, 542, 16 and 542, -1, 128, 128 | 6.8 |
| Logo | 212, 155, 256, 128 | centre at (340, 219): 20 u toward the trailing side of the canvas centre |
| Nav band | y 410 to 442 | three parallelograms (6.3) at 85 to 92% of the height |
| OPTIONS tab | 1, 440 to 197, 464; label 10, 441, 175, 21 | below and leading of NEW GAME |
| Bottom strips, second band | y 432 to 480 | 6.8 |
| Footer links | y 454, 22 u tall | MODS x 384 w 50; UPDATES x 441 w 73; CREDITS x 522 w 65; EXIT x 594 w 40; Default 0.25 |
| Hint line | 17, 470, 370, 10 | 7.3 |
| Copyright (credits only) | 7, 452, 450, 40 | Bank 0.20 at 30% |

There is no title text, no version text and no vertical list. The upper 85% of the screen belongs
to the planet and the logo.

### 9.3 Options

| Element | Rect (u) | Notes |
| --- | --- | --- |
| Sub-list plate | 3, 351, 132, 89 | grown from the options stub |
| Sub-list items | y 346, 366, 386, 406; labels 5, 356 + 20 n, 120, 13 | CONTROLS, GAME OPTIONS, SYSTEM, DEFAULTS |
| Controls content | 165, 50, 450, 350 | plate x 161 to 628, y 46 to 387 |
| Game options content | 165, 70, 340, 330 | smaller plate, same parts |
| System content | 165, 30, 390, 370 | two group boxes: video 20, 36 to 370, 203; audio 20, 221 to 370, 328 |
| Page title | content + (20, 5) | Default 0.32 |
| Title rule | content + (5, 23), 2 u tall | 448, 325 or 375 u wide |
| Bind categories | content + (0, 50 + 20 n), 122 x 14 | four tabs, right-aligned to the row gutter |
| Bind rows | content + (130, 48 + 23 n), 320 x 16 | label 110 u, value 195 u from x 121; 10 to 12 rows |
| Option rows | content + (20, 72 + 25 n), 300 x 16 | label 180 u right-aligned; value at x 220; slider at x 210 |
| Quality list | four items 125 x 13 u, pitch 13 u | in an inset box |
| Apply bar | in the plate notch | trapezoid in a 233 u cell, ends leaning outward; label 180 x 20 u |

While any page is open the logo is hidden, the top bar runs the full width and the three nav
buttons sit narrowed at the trailing side of the band.

### 9.4 New game

The difficulty list rises out of a stub above NEW GAME: a caption (Bank 0.25, at 36, 319) and four
sub-menu items with plates at 34, 335 + 20 n, 161 x 19 u and labels at 46, 339 + 20 n, 170 x 13 u.
There is no plate and no page: the scene stays fully visible. The locked fourth item shows at
`text.dim`.

### 9.5 Load, save and mods

| Element | Load (content 53, 48, 540, 330) | Save (same content rect) | Mods (content 153, 48, 340, 330) |
| --- | --- | --- | --- |
| Title, rule | (20, 5); rule 510 u | (20, 5); rule 410 u | (20, 5); rule 310 u |
| Column captions | Name, Date, Time at x 7, 240, 322, y 38 | the same | none |
| List well | 5, 50, 410, 240 | 5, 50, 410, 240 | 5, 40, 310, 240 |
| List | 406 x 232 u, AN 0.25 | 406 x 232 u | 306 x 212 u |
| Detail | level shot 105 x 79 u at 422, 50; date and time below in a group box | name field 295 x 16 u at 8, 297 | none |
| Buttons | LOAD GAME 418, 244; DELETE 418, 266 (110 x 28 u) | SAVE GAME 303, 290 | LOAD MOD 70, 284; CANCEL 180, 284 |

### 9.6 Multiplayer

| Element | Rect (u) | Notes |
| --- | --- | --- |
| Sub-list | items at x 418, y 359, 379, 399 | find game, create server, settings; rises above MULTIPLAYER |
| Player settings content | 50, 122, 340, 270 | five 32 x 64 u skin swatches in an inset box |
| Multiplayer page | 0, 0, 640, 480 after the pan | its own frame: the title-screen bands mirrored to the top |
| Page title | 18, 14, 200, 22 | Default 0.35, `text.caption` |
| Page tabs | two nav parallelograms at y 36 to 69 | GAME BROWSER, CREATE SERVER |
| Page links | 390, 4 and 535, 4, 22 u tall | MAIN MENU, EXIT GAME, `text.link` |
| Browser panel | 5, 85, 630, 360 | six column wells 141 u tall; list 610 x 141 u, Bank 0.25 `text.value` at 80% |
| Create-server panel | 85, 85, 474, 362 | map shot 128 x 96 u, map list, option rows 16 u tall |

### 9.7 Credits

The credits page slides in from above while the planet zooms to 1024 x 800 u and the logo drifts
to 370, 200. Two black letterbox bars with slanted steel-blue edges close in from the top (200 u)
and the bottom (139 u). Name pairs appear at 30, 140 and 30, 160 in Bank 0.35 (`text.credit.name`,
`text.credit.role`) and fall away. A BACK TO MENU parallelogram sits at the bottom-trailing corner.
The standalone end credits (`guis/credits.gui`) use the same pairs on black with the logo as a
450 x 225 u watermark at 10%.

### 9.8 Death screen

`guis/restart.gui` is the menu's furniture in hell's colours.

| Element | Rect (u) | Notes |
| --- | --- | --- |
| Fire video, faces, blood, pentagrams | full screen; pentagrams 480 x 480 u | warm additive washes (`scene.death.wash`), scan lines, vignette and dirt on top |
| Logo | 207, 120, 256, 128 | flickers on, then breathes |
| Options | 120 x 20 u at x 252, y 260, 300, 340 | Bank, centred, white 50%; 40 u pitch |
| Option subtitles | 220 x 20 u, 18 u below each option | Bank 0.26, lower case, hidden until hover |
| Load panel | 53, 70, 540, 330 | the load page with `scene.death.*` tokens |

### 9.9 Message boxes

`guis/msg.gui` and `guis/netmenu.gui` draw the dialog shell of 6.10 at the same position (plate
140, 130, 364 x 144 u) with no open animation. The message box dims the scene to 70%, offers up to
three buttons at plate x 60, 135 and 210, y 110, and may hold a 258 x 31 u entry box with a 245 x
20 u black well. The wait box has a title and no buttons. The connecting box has one centred
CANCEL over opaque black.

### 9.10 Pause variants

Opened in a game the same screen changes as follows.

| Element | Front end | Single-player pause | Multiplayer pause |
| --- | --- | --- | --- |
| First nav button | NEW GAME | SAVE GAME | disabled (`chrome.fill.disabled`) |
| Second nav button | LOAD GAME | LOAD GAME | disabled |
| Third nav button | MULTIPLAYER | QUIT CURRENT GAME | MULTIPLAYER |
| Footer | MODS, UPDATES, CREDITS, EXIT | RETURN TO GAME (420, 454, 140 x 22 u), EXIT | RETURN TO GAME, EXIT |
| Opening | id logo, fly-in | planet at rest; halo fades in over 4500 ms | the same |
| Music | theme | looping pause bed | looping pause bed |

### 9.11 Classic and Remastered

| Element | Classic | Remastered |
| --- | --- | --- |
| Canvas | 640 x 480 u centred; black outside | the scene fills the view; controls keep their u sizes |
| Stars, scan lines | the canvas | the whole view; scan-line pitch stays 2 u |
| Grid | the canvas | continues at the 15 u pitch to every edge, aligned to the canvas origin; accents stay every 75 u |
| Planet, halo, logo | stock rects | stay on the centred 4:3 canvas; the planet is never stretched and never re-centred on a wide view |
| Top bar and flare | stock rects | the bar starts at the real leading edge; the flare anchors to the real top-trailing corner |
| Bottom strips, second band | stock rects | extend to both real edges; the step and the 45 degree joins keep their distance from the trailing edge |
| OPTIONS tab | stock rect | anchors to the real bottom-leading corner |
| Nav buttons | stock rects | keep their size and their 5 u gaps; the group stays centred on the canvas |
| Footer links | stock rects | anchor to the real bottom-trailing corner |
| Hint line | stock rect | anchors to the real bottom-leading corner |
| Page plates, sub-lists | stock rects | stay on the 4:3 canvas; the bridge still reaches its nav button |
| Dialogs, message boxes | stock rects | centred in the view; the dim covers the view |
| Edge glow | 30 and 20 u outside the canvas | hugs the real view edges with the same visible falloff, about 14 u at the sides and 12.5 u top and bottom (derived)  |
| Scene pans | 480 u | one view height |
| Tall views | letterboxed | the nav band anchors to the real bottom edge, the top bar to the real top edge; the canvas centre holds the planet |

Rules for both layouts:

1. Never place an opaque backdrop behind a page. Page plates stay at 80% so the planet shows
   through.
2. Keep the logo 20 u off centre and the frame heavier at the trailing side. Do not centre or
   mirror the composition.
3. Keep primary navigation in the bottom band. Sub-menus grow upward from the button that owns
   them.

## 10. HUD and in-game overlays

The Doom 3 HUD is two slanted corner plates on an otherwise empty screen. A hollow frame in the
bottom-leading corner carries health and armour as bare numbers; its mirror image in the
bottom-trailing corner carries the clip and the reserve. Nothing is labelled, nothing is opaque and
nothing sits at the top or in the centre except the crosshair. Every other element is a notice that
assembles itself, delivers one fact and leaves. Persistent furniture covers under 3% of the canvas.

The HUD is the marine's suit display. It is drawn as light on a visor: translucent grey-green
strokes that breathe on a 400 ms flicker, digits that lean with the plates, and warnings that change
the hue of the same art instead of adding a new element. The replacement keeps that restraint. It
redraws each piece as vector geometry, keeps every stock position, colour, threshold and duration
recorded here, and adds no furniture that the suit does not have.

### 10.1 Composition and order

The frame is built in this order, back to front. Later layers cover earlier ones.

| Order | Layer | Source | Notes |
| --- | --- | --- | --- |
| 1 | World view | engine | |
| 2 | Damage splats and blood spray | `PlayerView` | Under the HUD (section 10.8) |
| 3 | HUD | `guis/hud.gui` | Not drawn in cinematics, camera views or with the HUD switched off |
| 4 | Crosshair | `guis/cursor.gui` | Not drawn while a world GUI has focus or while the weapon rises, lowers or is holstered |
| 5 | Armour pulse, tunnel vision, berserk, BFG vision | `PlayerView` | Over the HUD |
| 6 | Double vision, berserk pass, screen fade | `PlayerView` | Re-draws the whole frame, HUD included |
| 7 | PDA | `guis/pda.gui` | Replaces layers 1 to 6 while open (section 10.9) |

Within the HUD, draw order is the order of the rows below. All rects are u on the 640x480 canvas.

**Bottom-leading group: health, armour, stamina.**

| Order | Element | Window | Rect (u) | Driven by |
| --- | --- | --- | --- | --- |
| 1 | Frame shadow | `ScanLineL` | 1, 417, 256, 64 | Always; the frame art offset +1, +1 |
| 2 | Stamina frame | `BorderBottom` | 4, 416, 270, 64; visible x 6–136, y 469–478 | Always |
| 3 | Plate frame | `Border` | 0, 416, 256, 64; visible x 6–149, y 438–467 | Health above 35 |
| 4 | Frame heat wash | `Border_2` | same | Alpha (85 − health)% |
| 5 | Frame, danger | `Border_1` | same | Health 35 or below |
| 6 | Stamina fill | `Stamina` / `StaminaImage` | visible x 9–133, y 471–476 | Stamina 0–100; clip width 1.33 u per percent |
| 7 | Hell stamina | `StaminaHell` | 5, 464, 133, 16 | Replaces 6 where stamina is disabled |
| 8 | Plate fill | `BgL` | visible x 10–144, y 442–463 | Always |
| 9 | Armour box | `Lines1`, `Lines1_1`, `ArmorFlash` | visible x 11–70, y 446–462 | Armour above zero / at zero / pickup pulse |
| 10 | Health box | `Lines2`, `Lines2_2`, `Lines2_1`, `HealthFlash` | visible x 68–143, y 443–462 | Health above 35 / wash / danger / pulse |
| 11 | Health digits | `MPHealthBlack`, `MPHealth`, `MPHealth2` | 90, 436, 39, 32 (shadow at 91, 438) | Health |
| 12 | Armour digits | `MPArmorBlack`, `MPArmor` | 28, 441, 34, 32 (shadow at 29, 442) | Armour |
| 13 | Death line | `DEAD` | 0, 395, 150, 50 | Health zero |
| 14 | Location caption | `LocationText` | 142, 460, 220, 20 | Current location name |

**Bottom-trailing group: ammunition and weapons.** The art is the leading group mirrored; a rect
of `384, 416, -256, 64` places texel x at screen x 640 − x.

| Order | Element | Window | Rect (u) | Driven by |
| --- | --- | --- | --- | --- |
| 1 | Frame shadow | `ScanLineLA`, `ScanLineLAG` | 385, 417, -256, 64 | Panel mode |
| 2 | Pip-row frame | `BorderLABottom`, `WeaponFlash`, `AmmoFlash1` | 399, 416, -241, 64; visible x 522–638, y 469–478 | Always; pulses |
| 3 | Plate frame | `BorderLA`, `BorderLA_1`, `BorderLA_2`, `AmmoFlash2` | visible x 511–634, y 438–467 | Normal / clip low / clip empty / pulse |
| 4 | Short frame | `BorderLAGrenades` | visible x 564–634 | Grenades |
| 5 | Plate fill | `BgLA` | mirrored `BgL`, 20 u shorter | Panel shown |
| 6 | Reserve box | `Lines1A` (`Lines1B` for grenades) | visible x 570–629, y 446–462 | Panel shown |
| 7 | Clip box | `Lines2A` | visible x 517–572, y 443–462 | Panel shown |
| 8 | Clip digits | `ammovalue2Black`, `ammovalue2` | 504, 436, 80, 32 | Rounds in the clip |
| 9 | Reserve digits | `ammovalue3Black`, `ammovalue3` | 559, 441, 80, 20 | Total minus clip |
| 10 | Weapon pips | `Weapon11`, `Weapon0` … `Weapon10` | 10x6 each at y 471; x 526, then 535 to 625 at 9 u pitch | Weapons owned; current weapon |
| 11 | Weapon name | `WeapName` | 295, 460, 220, 20, right-aligned | Weapon change |
| 12 | Weapon icon | `WeapIcon0` … `WeapIcon11` | 64x32 at 560, 405 or 410; 32x32 at 580, 405 or 410 | Weapon change |
| 13 | Soul cube ready | `CubePulseParent`, `CubePulse` | 64x64 at 453, 365; then 32x32 at 470, 437 | Cube fully charged |

**Leading-edge panels.** One parallelogram panel serves three uses and docks to the right of the
health plate on the same baseline.

| Element | Window | Rect (u) | Driven by |
| --- | --- | --- | --- |
| Oxygen | `AirWin` | 135, 435, 128, 64; visible x 149–256, y 438–467; bar x 156–244, y 454–461 | Player is in vacuum |
| Radio | `RadioWin` | 135, 435, 128, 64; moves to 146, 400 while oxygen shows | Radio transmission |
| Audio log | `AudioWin` | half-size panel 64x32 at 101, 402 | An audio log is playing |

**Transient notices.**

| Notice | Window | Rect (u) | Anchor | Trigger |
| --- | --- | --- | --- | --- |
| Pickup lines | `ItemPickup1` … `ItemPickup5` | 150x16 at x 10; y 310, 330, 350, 370, 390 | Bottom-leading | Any pickup |
| Inventory item | `InvItem` | -120, 205, 350, 115 | Leading, centre height | Inventory item taken |
| New objective | `ObjPopBox` | 356, 226, 300, up to 300 | Trailing, centre height | Objective given |
| Objective complete | `ObjPopBoxC` | 356, 183, 300, 20 and body | Trailing, above the previous | Objective completed |
| Tip | `TipPopBox` | 0, 60, 334, 150 | Top-leading | Game tip |
| PDA download | `PDABox1` … `PDABox5`, `PDAName1` … `PDAName3` | bar 140x10 at 250, 360 | Centre | PDA taken |
| Video download | `VidBox1` … `VidBox4`, `VidName1` | bar 140x10 at 250, 420 | Centre | Video disk taken |
| New e-mail | `PDABox1alt`, `PDANewMail` | bar 140x10 at 250, 360 | Centre | E-mail received |
| Reminders | `NewPDAVis`, `NewVidVis` | icon 32x32 at 10, 408; label at 37, 414 | Bottom-leading | After a download, until the PDA opens |
| New weapon | `WeapIcon1Large` … `WeapIcon10Large` | 128x64 at 256, 280 or 64x64 at 288, 280 | Centre | First pickup of a weapon |
| Talk prompt | `NPCName1`, `NPCName2` | text at 326, 220 and 326, 232 | Centre | Crosshair on a character who talks |
| Message | `message1` | 20, 260, 638, 10 | Leading, centre height | Game saved |

**Classic.** The 640x480 canvas is centred and scaled to the view height (to the width in views
narrower than 4:3). Every element keeps the stock rect above. Notices that the stock lets bleed past
the canvas edge (`ObjPopBox` ends at x 656) are clipped at the canvas edge exactly as in stock.

**Remastered.** The vocabulary and sizes are unchanged; only anchors move.

1. The health and armour plate, its stamina bar, the location caption, the leading-edge panels, the
   reminders and the pickup lines anchor to the bottom-leading corner of the real screen at their
   stock offsets from the canvas corner.
2. The ammunition plate, the pip row, the weapon name, the weapon icon and the soul cube anchor to
   the bottom-trailing corner at their stock offsets.
3. The crosshair, the talk prompt, the new-weapon notice and the download bars stay on the view
   centre at their stock offsets from the canvas centre. A download chip flies from the view centre
   to the reminder position in the bottom-leading corner.
4. Side notices anchor to their own edge at the stock offset: objective boxes to the trailing edge,
   the tip to the top-leading corner, the inventory notice and the message to the leading edge. On a
   wide view every unit of added width moves them out of the central 4:3 area. They never move
   inward of their stock position.
5. Nothing new occupies the central 4:3 area, and nothing is added along the top edge.

**Safe area.** Edge anchors measure from the platform safe-area rectangle, not from the physical
screen. The stock margins are the minimum: the plate frames stand 6 u (9 dp) from the side edge and
the stamina and pip frames end 2 u (3 dp) above the bottom edge. Where the platform reports a larger
inset, the stock offset is added to it. Panel art of a side notice may run past the safe area to the
physical edge, as `ObjPopBox` and `TipPopBox` do in stock; its text and icons stay inside.

### 10.2 Palette

Every HUD bitmap is white with its shape in alpha, so colour is a property of the element and not of
the art. One drawing serves as frame, shadow, warning copy and pulse. All blending is straight alpha
unless a row says otherwise. Alpha ranges are the limits of the idle flicker (section 10.4).

| Token | Value | Used for |
| --- | --- | --- |
| `hud.frame` | `#407366` at 41–50% | Plate frames, short grenade frame; side panels at 33–40% |
| `hud.frame.low` | `#337366` at 27–33% | Stamina frame, pip-row frame |
| `hud.plate` | `#174242` at 23–25% | Plate fill; side panels at 31–33% |
| `hud.box` | `#4CCCB2` at 20% | Readout boxes and their pictograms |
| `hud.shadow` | `#000000` at 30% | Frame shadow, offset +1, +1 u |
| `hud.digit` | `#ABB2B2` at 100% | Health and clip digits |
| `hud.digit.minor` | `#596B66` at 100% | Armour and reserve digits |
| `hud.digit.shadow` | `#000000` at 50% | Shadow copy of digits, offset +1, +2 u |
| `hud.caption` | `#406666` at 100% | Location caption, weapon name |
| `hud.pip` | `#009999` at 40% | Weapon owned |
| `hud.pip.current` | `#009999` at 90% | Weapon in hand |
| `hud.stamina` | `#B2804C` at 35% | Stamina fill |
| `hud.air` | `#338099` at 60% | Oxygen bar |
| `hud.air.text` | `#6699A6` at 100% | Oxygen label and value; radio captions use `#7399A6` |
| `hud.wave` | `#FF331A` at 100% (radio), 60% (audio log) | Waveform |
| `hud.flash` | `#FFFFFF` at 100% to 0% | Pulse copy; 60% and 50% on the ammunition side |
| `hud.icon` | `#B2FFFF` at 70% to `#4C9999` at 0% | Weapon-change icon |
| `hud.gain` | `#66BFB3` to `#4CA699`, 500 ms cycle | New-weapon icon tint |
| `hud.gain.name` | `#99FFE6` at 100% | New-weapon name |
| `hud.talk` | `#739980` at 100% | Character name; the hint under it is `#808080` |
| `hud.cube` | `#FFA633` at 80% to `#FF9966` at 20% | Soul cube ready |
| `hud.cross.dot` | `#B2FFCC` at 100% | Crosshair dot |
| `hud.cross` | `#73B2A6` at 50%, 20%, 10% | Crosshair ring, arcs, hairline circle |
| `hud.cross.talk` | `#1A8059` at 100% | Crosshair arcs in the talk state |
| `hud.cross.hit` | `#CC0000` at 100% and `#994C00` at 60% | Crosshair arcs and circle on a hit |

The persistent palette is one desaturated blue-green family, hue 165–180 degrees, with a grey-white
for digits. Nothing persistent is opaque; the brightest idle stroke peaks at 50%.

**Warning ramp.** Warning is a hue change on the same art: teal, then amber, then red. Amber
breathes slowly; red blinks at 500 ms. No warning adds an element.

| Token | Value | Used for |
| --- | --- | --- |
| `warn.amber.digit` | `#FF9900` at 100% | Clip digits, clip low |
| `warn.amber.frame` | `#995900` at 38–63%, 1000 ms cycle | Ammunition frame, clip low or no ammunition |
| `warn.amber.box` | `#FF8033` at 20% | Clip box, clip low |
| `warn.amber.armour` | `#FFA61A` at 18–30%, 2000 ms cycle | Armour box at zero armour |
| `warn.amber.dry` | `#806633` at 100% | Armour digits at zero |
| `warn.amber.wash` | `#CCB200` at (70 − health)% | Amber copy over the health digits |
| `warn.heat` | `#BF2A00` to `#731A00` (inferred from the expression) at (85 − value)% | Frame wash for health; bar wash for oxygen |
| `warn.red.digit` | `#FF1A00` at 100% | Health digits at 35 or below; oxygen text at 35 or below; death line |
| `warn.red.empty` | `#FF0000` at 100% (digits), 20% (boxes) | Empty clip; no ammunition |
| `warn.red.frame` | `#CC2600` at 15–50% (frame), 25–83% (box and ammunition frame), 500 ms cycle | Danger frame and box |

| Threshold | Switch |
| --- | --- |
| Health below 85 | `warn.heat` copy of the frame fades in, 0% at 85 to 85% at 0 |
| Health below 70 | `warn.amber.wash` over the digits and a `warn.red.frame` copy of the health box fade in, 0% at 70 to 34% at 36 |
| Health 35 or below | Hard switch: digits `warn.red.digit`, frame and box replaced by blinking `warn.red.frame`; amber copy removed |
| Health 0 | Death line fades in over 100 ms |
| Armour 0 | Armour box `warn.amber.armour`, digits `warn.amber.dry` |
| Clip at or below the weapon's low mark | `warn.amber.digit`, `warn.amber.box`, `warn.amber.frame` |
| Clip 0 | `warn.red.empty` digits and box, `warn.red.frame` ammunition frame |
| Total ammunition 0 | Both numbers and both boxes `warn.red.empty`; frame amber |
| Oxygen below 85, below 70, 35 or below | Bar wash; orange `#CC6600` copy of the text at (70 − air)%; text `warn.red.digit` |

Low marks per weapon: pistol 4, shotgun 2, machinegun 10, chaingun 10, plasma gun 10, rocket
launcher 1.

**Notice colours.**

| Token | Value | Used for |
| --- | --- | --- |
| `notice.label` | `#CCFFFF` at 100% (50% for reminders) | Notice label, chevrons |
| `notice.title` | `#FF9933` at 100% | Objective, item and tip titles |
| `notice.body` | `#99CCCC` at 100% (70% for pickup lines) | Body text |
| `notice.shadow` | `#000000` at 60% | Shadow copy of notice text, offset +1, +1 u |
| `notice.rule` | `#CCFFFF` at 10% | Title bar and lower rule |
| `notice.panel` | Panel art at 70% | Dark notice panel (black fill with a pale edge line) |
| `notice.pickup.in` | `#FFE666` at 40% | First frame of a pickup line |
| `notice.bar.fill` | `#6699B2` at 25%; video `#B29966` at 25% | Download bar fill |
| `notice.bar.line` | `#669999` at 100% | Download bar outline, screenshot border |
| `notice.bar.ring` | `#246361` at 50%, 30%, 15% | Three outer rings of the download bar |
| `notice.security` | `#CC9933` at 100% | Security clearance line |
| `notice.info.line` | `#8AEDFF` at 100% | Info box stroke |
| `notice.info.fill` | `#006BC5` at 30% | Info box fill |

Orange `notice.title` is the player's own data: it marks objective and item titles here and in the
PDA and nothing else.

### 10.3 Shape and type

The frame leans. Its outer edge slopes 25 degrees off vertical, its top edge steps up 2 u at 44% of
its width, and every persistent number is sheared to lean with it. Corners are cut, never rounded.

**Plate frame** (`Border`; visible bounds 143 x 29 u, drawn 1:1). One closed outline. Key points in
u from the top-left of the bounds, then as fractions of the bounds:

| Key point | Position (u) | Fraction (x, y) |
| --- | --- | --- |
| Top edge, raised trailing section | y 0, x 65 to 140 | 0.45–0.98, 0 |
| Step down to the leading section | at x 62–65; leading section at y 2, x 8 to 62 | 0.43–0.45; 0.07 of the height |
| Top-leading corner | 6–8, 2–4 | 0.05, 0.1 |
| Leading edge, leaning | 6, 4 down to 0, 18 | slope 0.43 (23 degrees) |
| Leading vertical stub | x 0, y 18 to 22 | |
| Bottom-leading chamfer | 0, 22 to 7, 28 | 7 x 6 u |
| Bottom edge | y 28–29, x 7 to 131 | |
| Trailing edge, leaning, top further out | 131, 28 up to 143, 3 | slope 0.46 (25 degrees) |

The stroke is 3 u on the leaning edges and 2 u on the horizontal edges, with a glow falloff of about
3 u to transparency. The ammunition frame is the same drawing mirrored and 20 u shorter (123 u
wide). The grenade frame is 70 u wide with a plain top edge. The plate fill is the same silhouette
inset 4 u, step included.

**Readout boxes.**

| Box | Bounds in the frame (u) | Shape |
| --- | --- | --- |
| Health / clip | 75 x 19 (clip 55 x 19) | 2 u outline; vertical leading edge with a cut top-leading corner 5 x 8 u; trailing edge leaning 8 u over the height; interior filled at 50% of the stroke |
| Armour / reserve | 59 x 16 | 1–2 u outline, no fill; leading edge leaning 5 u with a chamfer at the foot; trailing edge vertical with a 3 x 4 u cut at the top |
| Grenade reserve | 59 x 16 | As armour, trailing edge leaning 8 u |

The health box carries a ring about 14 u across holding a plus sign at its leading end; the armour
box carries a filled vest glyph about 10 x 8 u. These two pictograms are the only identification
the cluster has. The boxes abut at the frame's step: armour takes 0.03–0.45 of the frame width,
health 0.43–0.96.

**Bars, pips and panels.**

| Piece | Size (u) | Shape |
| --- | --- | --- |
| Stamina frame | 130 x 9 | Hollow slanted capsule, 2–3 u stroke; leading end pointed, trailing end leaning |
| Stamina fill | 124 x 5 | Solid bar with slanted ends, no segments |
| Oxygen bar | 88 x 7 | The stamina fill art |
| Weapon pip | 6.9 x 3.75 inside a 10 x 6 cell | Pill with 1 u corner radius |
| Side panel frame | 107 x 29 | Parallelogram, horizontal offset 11 u over the height (slope 0.39), 3 u stroke; plate inset 4–6 u |
| Notice panel | any | Black fill, 1–2 u pale edge line with a glow above it, outer corners cut 2 u |
| Info box | any | 4 u stroke, 45 degree corner chamfer about 4 u long, flat fill |
| Download bar | 140 x 10 | 1 u outline; rings at +2, +4 and +6 u |
| Title rule | 14 u tall; lower rule 7 u | Flat fill |

**Type.** One working size carries almost everything: 67 of the HUD's 84 text windows use scale
0.25. Hierarchy comes from face, colour and alpha.

| Role | Face | Scale | Em (u) | Align | Shear | Colour |
| --- | --- | --- | --- | --- | --- | --- |
| Health, clip | Micro | 0.38 | 18.2 | centre | 0, −0.33 leading; 0, 0.33 trailing | `hud.digit` |
| Armour, reserve | Micro | 0.25 | 12 | centre | 0, −0.3 leading; 0, 0.4 trailing | `hud.digit.minor` |
| Location, weapon name, reminders | Bank | 0.25 | 12 | left / right | 0, ∓0.35 | `hud.caption`, `notice.label` |
| Side-panel label | Bank | 0.23 | 11 | left | 0, −0.33 | `hud.air.text` |
| Notice label, chevrons | Micro | 0.25 | 12 | left | none | `notice.label` |
| Notice title, download text, talk prompt, new-weapon name | Bank | 0.25 | 12 | left / centre | none | `notice.title`, `notice.body`, `hud.talk`, `hud.gain.name` |
| Pickup line | Bank | 0.25 | 12 | right | none | `notice.body` |
| Notice body | AN | 0.22 | 10.6 | left, wrapped | none | `notice.body` |
| Message | AN | 0.25 | 12 | left | none | `#FFFFFF` |
| Death line | Bank | 0.2 | 9.6 | right | none | `warn.red.digit` |

A shear of `0, k` moves each row of the glyph horizontally by k times its distance below the window
top: −0.33 leans the digits forward by 18.3 degrees, 0.33 backward. Notices are upright. Bank
renders lower case as small capitals, so short lower-case labels appear as small caps.

Shadows are hand-placed copies, not an effect: a second copy of the text in black, at 50% and offset
+1, +2 u for the digits, at 60% and offset +1, +1 u for notices. The engine text shadow is used by
the tip alone.

**Replacement rules.**

1. Draw each frame, box, bar and pip as a vector path through the key points above, at the stock
   size: 1 u = 1.5 dp at the reference. Keep the lean, the 2 u step and the cut corners. Never round
   a corner other than the pip's.
2. Draw strokes as a hairline core with a soft falloff. The stock core is 2–3 u with about 3 u of
   glow; keep the visual weight at every density and never draw the frame as a hard opaque line.
3. Mirror the leading art for the trailing group; do not author a second drawing.
4. Keep the readout boxes' pictograms and add no text label, unit or maximum to the cluster.
5. Set digits in Micro and labels in Bank at the stock ems (18.2 u = 27.3 dp, 12 u = 18 dp), with
   the stock shear and the hand-placed shadow copy at the stock offset and alpha.
6. Colour comes only from tokens. A warning or pulse re-tints the same path.

### 10.4 Gauges and readouts

The gauges are numbers first. The only bars are two thin continuous ones, stamina and oxygen; there
is no health bar, no segmented bar and no radial gauge.

**Idle flicker.** Every stroke and plate breathes on a linear triangle wave. Nothing blinks hard.

| Wave | Range | Period (ms) | Applied to |
| --- | --- | --- | --- |
| Frame flicker | 100% to 82% of the token alpha | 400 | `hud.frame`, `hud.frame.low` |
| Plate flicker | 100% to 92% | 400 | `hud.plate` |
| Danger blink | 100% to 30% | 500 | `warn.red.frame` |
| Amber breath | 75%, 50%, 45% in turn | 1000 (clip low), 2000 (armour) | `warn.amber.frame`, `warn.amber.armour` |
| Heat | red channel 75%, 50%, 45% in turn | 500 | `warn.heat` |

| Readout | Behaviour |
| --- | --- |
| Health | Integer, no unit. States by the thresholds in section 10.2, re-evaluated every frame. A gain or a drain flashes the health box with `hud.flash` 100% to 0% in 400 ms, linear; regeneration repeats the flash every 333 ms |
| Armour | Integer. An armour pickup flashes the armour box, 400 ms. At zero the box and digits turn amber |
| Clip | Rounds in the clip, or two dashes for a weapon without a clip. States by the thresholds |
| Reserve | Total minus clip |
| Ammunition pulse | Pickup flashes the ammunition frame at 60% to 0%, or the pip-row frame at 50% to 0% when the panel is hidden, 400 ms |
| Weapon pulse | A weapon pickup flashes the pip-row frame at 50% to 0%, 400 ms |
| Stamina | Fill revealed from the leading end, 1.33 u per percent (133 u at full). No number. Replaced by a scrolling ember strip (flame layers scrolling over a `#531000` to `#FA3200` gradient) where stamina is disabled |
| Oxygen | Panel wipes open 0 to 128 u in 200 ms with a sound when the player enters vacuum and closes at once on leaving. Label and percentage; bar revealed 0.95 u per percent. The value falls one step per tick in vacuum and recovers at twice that rate |

**Ammunition panel modes.** The panel changes with the weapon in hand and switches at once, with no
slide or fade.

| Mode | Weapons | Drawn |
| --- | --- | --- |
| Full | Pistol, shotgun, rocket launcher | Frame, plate, clip box and digits, reserve box and digits |
| Hidden | Machinegun, chaingun, plasma gun, BFG; fists, flashlight, chainsaw, soul cube | Pip row and its frame only |
| Grenade | Hand grenades | Short frame, one box, the reserve number |

The four guns in the hidden mode carry their own ammunition display on the weapon (section 10.10).
The replacement keeps this: it does not show HUD ammunition for a gun that displays its own.

Observation: the leading frame is re-tinted every frame to `hud.frame.low` while the trailing frame
keeps `hud.frame`, so the two frames differ slightly in brightness. The replacement uses `hud.frame`
for both plate frames.

### 10.5 Weapon pips, weapon change and pickups

Twelve pips are the whole weapon inventory. There is no weapon bar, list or wheel in the stock HUD.

| Property | Value |
| --- | --- |
| Cell | 10 x 6 u at y 471, 9 u pitch; first cell at x 526, the rest from 535 to 625 |
| Order, leading to trailing | Flashlight, fists, pistol, shotgun, machinegun, chaingun, grenades, plasma gun, rocket launcher, BFG, soul cube, chainsaw |
| Not owned | No pip; the cell stays empty |
| Owned / in hand | `hud.pip` / `hud.pip.current`, switched at once |

**Weapon change.** The icon of the new weapon appears above the ammunition plate and its name at
295, 460, right-aligned to x 515. Both fade over 1000 ms with accel(1, 0): the icon from
`hud.icon` 70% to 0%, the name from `hud.caption` 100% to 0%.

**New weapon.** The icon appears below the crosshair with the name above it. At 0 ms it slides 3 u
toward the trailing side and fades in over 300 ms, accel(0, 1); at 1000 ms it slides 3 u further and
fades out over 300 ms. The game shows at most one per 1000 ms. The icon is tinted `hud.gain`.

**Pickup lines.** Five text lines stack downward from y 310 at 20 u pitch.

| Property | Value |
| --- | --- |
| Queue | One line every 400 ms into slots 1 to 5 in turn; after the fifth, the next waits until 2000 ms after the first; the slot counter resets after 2000 ms idle |
| Entry | Colour `notice.pickup.in` to `notice.body` at 70% and shadow 0% to 100% in 200 ms; the line slides in 8 u from the trailing side |
| Push | Lines still showing move down one row in 200 ms, accel(0, 0.4); the newest is always on top |
| Dwell and life | Fade out at 1500 ms over 200 ms; life 1700 ms |
| Content | Item name only, right-aligned in 142 u. No icon and no sound |

**Icon catalogue.** All icons are white line drawings in alpha, tinted by the element: a 1 px
outline, an interior at about 25% broken by horizontal scan lines, and a soft outer glow. None is a
solid silhouette. Sizes are the source tiles; the HUD draws them at half size above the plate.

| Icon | Tile | Shape |
| --- | --- | --- |
| Fists | 64x64 | Clenched fist seen from the front, cut off at the wrist |
| Pistol | 64x64 | Pistol facing left, grip at the lower right, boxy slide |
| Shotgun | 128x64 | Pump shotgun facing left, long and low |
| Machinegun | 128x64 | Bullpup facing left with a display block on top |
| Chaingun | 128x64 | Drum at the left, ribbed barrel cluster to the right, carry handle |
| Grenade | 64x64 | Grenade lying on its side, cap at the right |
| Plasma gun | 128x64 | Rifle facing right with a circular cell at its middle |
| Rocket launcher | 128x64 | Tube with a flared muzzle at the right, grip below |
| BFG | 128x64 | Large body facing left with a central lens |
| Chainsaw | 128x64 | Saw with the bar pointing right |
| Flashlight | 128x64 | Torch lying on its side, head at the right |
| Soul cube | 64x64 | Shield-like block with a horned face and tusks; a spiked halo ring rotates behind it when it charges |
| PDA | 32x32 | Upright handheld with a screen and buttons |
| Video disk | 32x32 | Disc with concentric rings in a square sleeve |
| Key card, panel, data linker, plasma conduit | 64x64 | Card with rings and a bar code; square monitor; two-part clamp; horizontal canister |
| Empty slot | 64x32, 32x32 | Box with both diagonals and hatching |

The replacement redraws each icon as line art in the same idiom and at the same bounds, in a single
white layer tinted by token. It never fills an icon solid and never colours parts of one.

### 10.6 Crosshair, focus cursor and hit feedback

The crosshair is a separate GUI drawn after the HUD. It is one design for every weapon: a dot, a
ring and four faint arcs inside a hairline circle, 32 u across and centred on 320, 240.

| Part | Window | Geometry (u from the centre) | Colour |
| --- | --- | --- | --- |
| Dot | `crosshairCenter` | 1–2 u across | `hud.cross.dot` |
| Ring | `crosshairCenter2` | radius 5.5, band 2 | `hud.cross` at 50% |
| Arcs | `crosshairLight` | radius 8.5, band 2; one arc of 55–60 degrees per diagonal quadrant, gaps of about 30 degrees at the four axes; arcs thicken at their ends | `hud.cross` at 20% |
| Circle | `crosshairFrame` | radius 11, hairline; a pair of short radial ticks at top and bottom, thickened spots at the sides | `hud.cross` at 10% |
| Side bars | `crosshairFrame2`, `crosshairFrame3` | 64 x 32 at +18 u; a bar 11 u tall with a slanted leading end, fading out toward the trailing side over about 50 u; the second copy is flipped vertically | `#1A8066` and `#1A8080`, talk state only |

| State | Change | Duration (ms) |
| --- | --- | --- |
| Talk on | Dot and ring hidden; arcs flash white at 60% and settle on `hud.cross.talk`; circle to 50%; side bars fade in to 50% and 25%; the crosshair moves 6 u to the leading side (a 4 u jump, then 2 u over the transition); the character's name and a talk hint slide in 9 u at 326, 220 | 150 |
| Talk off | Arcs from `#00FF80` at 50% back to idle; bars out; shift back; the name is removed at once | 140 |
| Hit | Dot white, arcs `#CC0000` at 100%, circle `#994C00` at 60%; shown, then removed with no fade | 200 |

**Device cursor rule.** When the player's aim lands on an interactive world GUI the crosshair is not
drawn. The device's own cursor is drawn on the surface instead, in the surface's space and at its
scale: an arrow about 13 x 19 px in a 32 px tile. A sound marks entering and another leaving. The
crosshair returns as soon as focus leaves the surface. The stock HUD has no separate "use" or hand
cursor of its own.

Replacement rules:

1. Draw the four parts as vector rings and arcs at the radii above. This is one of the two places
   where curves are stock; keep them.
2. Keep a single crosshair. Add no per-weapon shapes, no spread animation and no enemy tint.
3. Keep hit feedback to the 200 ms red set. Add no hit marker and no damage-direction indicator.

### 10.7 Notices, objectives, tips and downloads

A notice assembles itself. A dark panel opens, rules sweep in from one side, text arrives white and
settles to its token, and the whole thing reverses out. Every notice uses the notice panel and
`notice.*` colours of sections 10.2 and 10.3.

**Objective box** (`ObjPopBox`, with `animNewUp` and `animObjDown`).

| Time (ms) | Step |
| --- | --- |
| 0 | Sound. Header strip opens from 356, 236, 300, 0 to 356, 226, 300, 20 in 300 ms, accel(0.2, 0.8). Chevrons start blinking |
| 100 | Label fades in over 200 ms |
| 200 | Body opens in 100 ms; panel 0% to 70% in 400 ms; two title rules sweep in from the trailing side (x 311 to 9, width 0 to 302) in 400 ms; title white to `notice.title` in 200 ms while sliding 4 u; screenshot border fades in |
| 400 | Body text white to `notice.body` in 200 ms, sliding 4 u; the screenshot wipes in from a white flash over 200 ms |
| 800 | Ready |
| Close | Waits for the opening to finish; 400 ms later a sound, colours fade in 200 ms and the box collapses in 500 ms, accel(0.2, 0.8); hidden at 600 ms |

Contents: label at 28, 0; title at 11, 21; screenshot 90 x 75 u at 9, 44 with a 1 u border; body
text 168 x 90 u at 106, 41. The chevrons blink on a 1200 ms loop: 100% to 0% over 800 ms and back in
the last 200 ms, the inner chevron in opposite phase. The game closes the box when the player has
moved more than 64 world units or next fires. The objective-complete box (`ObjPopBoxC`) is the
header strip, one rule and the title, opening at 356, 183 by the same first three steps with its own
sound.

**Other notices.**

| Notice | Timeline |
| --- | --- |
| Tip (`TipPopBox`) | Sound; box from −10, 60, 334, 0 to 0, 60, 334, 150 in 200 ms, accel(0.2, 0.8); panel to 70% in 500 ms. At 500 ms title and text appear, rules flash 40% to 10% and text white to `notice.body` in 400 ms. Closes over 500 ms. Hides itself after 5000 ms, or when the player next fires. Title at 7, 9; text 250 x 90 u at 7, 29; an info box sits behind the panel |
| Inventory item (`InvItem`) | Panel height 0 to 115 in 400 ms, accel(0.2, 0.8); panel to 70% in 600 ms; title bar width 0 to 155. At 400 ms title white to `notice.title` in 200 ms. At 600 ms the 64 x 64 u icon fades in over 200 ms. At 3000 ms everything reverses in 200–400 ms; hidden at 3400 ms |
| PDA download (`animPDA`) | At 350, 400 and 450 ms the three rings fade in, 250 ms each. At 500 ms the outline, 250 ms. From 600 ms the fill grows 0 to 140 u in 2000 ms, linear. At 750 and 1000 ms two text lines fade from white, 250 ms. At 2500 ms the outline flashes white at 70% and the word for completion fades 80% to 0% in 400 ms. At 2600 ms the security line, if any. At 2900 ms the rings go and the bar shrinks to a 5 x 10 u chip that flies to x 23 (55 if a video reminder shows) in 400 ms, accel(0.2, 0.4). At 3300 ms the chip drops to y 425 in 200 ms, accel(0.2, 0.6), and fades. At 3500 ms the reminder icon appears. At 8500 ms the reminder label goes; the icon stays until the PDA opens |
| Video download (`animVid`) | The same sequence at y 420 with the video fill; ends at 7600 ms |
| New e-mail (`animNewMail`) | At 600 ms a sound, the bar flashes and its label fades 80% to 0% over 2000 ms. At 1000 ms shrink and fly, 400 ms. At 1400 ms drop, 200 ms |
| Security clearance (`SecOnly`) | Sound; `notice.security` line at 200, 335 fades in over 250 ms and out at 3000 ms |
| Reminder | Label blinks on a 1200 ms loop, `notice.label` to `notice.title` in 200 ms and back in 800 ms; icon 40% to 60% and back |
| Message (`message1`) | 100% to 0% over 5000 ms, accel(1, 0) |
| Soul cube ready | Three stacked 64 u icons flash in at 80%, 60% and 50% over 300 ms while rising 2 u; fade over 500 ms from 400 ms; the group drops 40 u in 400 ms, accel(1, 0); from 700 ms a 32 u icon pulses `hud.cube` 80% to 20% and back, 800 ms each way |
| Radio and audio captions | Marquee: two captions cross an 86 u window in a 20 000 ms loop; the audio-log caption crosses 140 u in 7500 ms. The waveform scrolls once per second and its amplitude wanders on a 1.67 s table |

The download bar's 2000 ms fill and its flight to the corner are the HUD's signature motion. The
replacement keeps the durations, the chip size and the destination. In Remastered the chip flies to
the reminder's anchored position.

### 10.8 Damage, vision and screen effects

Pain, blood and altered vision are not HUD elements. `PlayerView` draws them over or under the HUD
as full-screen engine effects. The stock HUD file contains no damage flash, no blood, no vignette
and no powerup tint.

| Effect | Drawn as | Colour and alpha | Timing |
| --- | --- | --- | --- |
| Damage splat | A material named by the damage: a generic darkening smear (multiplies the scene), left and right slashes, left and right smacks, a bite, a toxin splash. Typically 600 x 600 u at x ±100–140, y −100, with ±32 u position jitter and ±12.5% size jitter. Eight at most; the oldest is replaced | Alpha is the remaining fraction of its life | Linear fade over 300 ms (most damage) or 600 ms; a hit within 150 ms of the last adds none |
| Blood spray | A spray material, 600 x 480 u with the same jitter | Linear fade | Duration set by the caller |
| View kick | A view-angle offset | – | 400 ms typical; falls off with the square of the time left |
| Double vision | The frame rendered small and drawn twice, the copies offset sideways by up to half the width in a decaying oscillation | Second copy at 50%; red channel only under berserk | 100 ms per hit typical, accumulating, capped at 5000 ms |
| Armour pulse | A full-screen soft mask in pure red | 100% to 0% | 250 ms, linear, when armour absorbs a hit |
| Tunnel vision | A two-layer vignette that breathes in scale on a 1 s cycle and rotates slowly in both directions | Starts at (100 − health)% on a hit and loses 25 points per second; held at full strength when dead | Gone within 4 s of the last hit |
| Berserk | A rotating mask (3 turns per second) that reveals the previous frame at 97% scale | 100%, fading linearly over the last 10 000 ms | Powerup duration |
| BFG vision | Two layers of a tunnel image at 15% each, rotating in opposite directions at about 0.2 turns per second | Constant | While flagged |
| Screen fade and flash | A flat colour | Script colour, linear | Script duration |

The colours of the splat, spray, vignette and mask images were not sampled and are undetermined
here; the table records their materials' structure and timing.

Replacement rules:

1. Keep these as engine effects in their stock layers. Never move one into the HUD layer, and never
   draw a damage flash, vignette or tint as HUD furniture.
2. The HUD stays legible under them: double vision and the berserk pass distort the HUD with the
   scene, as in stock.
3. A reduced-flash option scales these and only these: the alpha of damage splats and blood spray,
   the alpha of the armour pulse, the sideways offset of double vision, the breathing amplitude of
   tunnel vision, the alpha of the berserk and BFG layers, and, in the HUD, the depth of the 400 ms
   pulse flashes and of the 500 ms danger blink. At the minimum setting the danger blink becomes a
   steady `warn.red.frame` at its peak alpha.
4. The option never changes a threshold, a hue, a duration of a notice, the tunnel vision's
   dependence on health, or whether a warning state is shown.

### 10.9 The PDA

The PDA is a full-screen, opaque device that replaces the view and the HUD while it is open. It
boots: chrome bands part from the middle of the screen, panels slide in from all four edges, fields
wipe in row by row and a fingerprint is scanned and judged. White text at stepped alphas sits on
near-black under a faint grid.

**Anatomy at rest** (u; positions after the opening sequence).

| Zone | Rect (u) | Content |
| --- | --- | --- |
| Top band | y 0–12 left of x 377; y 0–33 right of x 409; a 45 degree step between | Device title and ID, right-aligned at 405, −1 and 405, 12 |
| Tabs | 0, 31, 165, 82 | Three buttons at y 43, 65, 87; 16 u tall, 22 u pitch: user data, e-mail, video disks (the third only on the player's own PDA) |
| File header | 0, 119, 144, 32 | Caption box above the list |
| File list | 1, 155, 125, 223 | One row per collected PDA: the player's own first, then newest first; PDAs already read are greyed |
| Main frame | 145, 31, 416, 160; 505 wide on the e-mail tab | Frame with an L bracket; upper tab content |
| User data | 180, 46, 353, 132 | Fingerprint and retina block 128 x 128 u; five label and value rows at 26 u pitch, each indented 10 u further than the one above (labels at x 104, 115, 126, 134, 144; values at 110, 120, 130, 140, 150) |
| Lower panel | visible x 172–535, top edge at y 196 (its pieces' rects span x 160–547 from y 171, 150 or 256 tall) | Audio logs (another person's PDA) or mission objectives (the player's own) |
| E-mail | 174, 46, 450, 360 | Header bar 442 x 15; column headers at x 2, 125, 360 (120, 232, 84 wide, 15 tall); list 442 x 90, tab stops 2, 125, 362; reader below: title bar 445 x 22, body 445 x 170 |
| Video | 174, 46, 356, 132 | Header 354 x 15; list 350 x 106; player below: title 353 x 22, picture 210 x 170 at 32, 56, info text 135 x 140 at 244, 60, play at 250, 205 and stop at 318, 205 (64 x 16 each) |
| Audio | in the lower panel | Header naming the owner, list 348 x 40, play and stop at 35, 86 and 101, 86 |
| Bottom band | from y 412 (left of x 217) or 419 (right of x 249) to 480 | Captions at 2, 411; 239, 413; 566, 413 |
| Objectives strip | 0, 417, 234, 59 | Black plate at 50% with one 8 u corner cut; three lines at y 428, 443, 458; a 7 x 7 u outline checkbox per objective |
| Weapon strip | 253, 432, 296, 44 | Eleven slots, 80 x 40 and 40 x 40 at 83 and 43 u pitch; the first four slots (three large, one small) visible at rest; 8 u scroll buttons at x 243 and 551 |
| Item slot | 568, 432, 63, 44 | One 32 x 32 u icon; its name right-aligned at 400, 400 |
| Weapon info box | 229, 330, 408, 93 | Info box with a 128 x 64 u icon, a title, a description and a close tab |

Security clearance is the fifth row of the user-data block: the value comes from the PDA's own
clearance text, set in Bank like the other values.

**Palette.**

| Token | Value | Used for |
| --- | --- | --- |
| `pda.base` | `#000505` at 100% under a soft upward glow image at 30% | Screen base |
| `pda.grid` | `#99FFFF` at 2%; every fifth line at 6% | Grid lines every 15 u, both axes |
| `pda.logo` | `#FFFFFF` at 5% | Watermark, 512 x 512 u at 121, −15 |
| `pda.band` | `#CCFFFF` at 20% (fill), 50% (edge art), 15% (centre fill), 10% (slanted fills) | Top and bottom bands |
| `pda.frame` | `#B2FFFF` at 60% over a `#051015` backing at up to 70% | Main frame; the file header box uses `#99CCCC` at 100% |
| `pda.panel` | Notice panel art at 70% | Lower panel, readers |
| `pda.text` | `#FFFFFF` at 100% | Values, list text, titles |
| `pda.text.mid` | `#FFFFFF` at 80%, 60% | Descriptions; secondary values |
| `pda.text.low` | `#FFFFFF` at 40% | Field labels; 50% for video info |
| `pda.section` | `#CCFFFF` at 60% on `#CCF2FF` at 15%, border `#B2FFFF` at 20% | Section header bars |
| `pda.column` | `#4C666B` on `#000000` at 10%, border `#1A3340` | Column headers |
| `pda.rule` | `#666666`, `#4C4C4C` at 100% | Neutral box borders |
| `pda.select` | `#4C8580` at 50% (file list `#668C99` at 50%); 1 u outline at 100% when focused | Selected list row |
| `pda.tab` | `#99FFFF` at 100%; hover and active `#FFFFFF` | Tab labels; the active bar is tinted `#99B2B2` |
| `pda.button` | `#CCFFFF` at 60%; hover `#FFFFCC` at 100% | Buttons; label `#FFFFFF` at 70%, 100% on a click |
| `pda.objective` | Title `notice.title`, text `notice.body`, heading `#33CCCC` | Objectives |
| `pda.slot` | `#404C4C` at 100%; selected fill `#1A73CC` at 10%; empty glyph `#FFFFFF` at 5% | Weapon slots |
| `pda.mismatch` | `#FF3333` at 70% to 0% | Fingerprint mismatch |
| `pda.dim` | `#000000` at 70% (curtain), 90% (box) | Tutorial |

The screen also carries two additive sheen overlays (a pale cyan glow and a grey highlight) over
everything. The PDA is cooler and brighter than the HUD; orange appears only on objective titles.

**Type.** 61 of the PDA's 85 text windows use scale 0.25.

| Role | Face | Scale | Em (u) | Align | Colour |
| --- | --- | --- | --- | --- | --- |
| Opening title | Micro | 1.0 | 48 | centre | `pda.text` |
| Band and strip captions | Micro | 0.2–0.25 | 9.6–12 | left / right | `pda.text` at 100%, 60%, 30%, 25% |
| Tab labels | Micro | 0.2 | 9.6 | right | `pda.tab` |
| Scan status | Micro | 0.19 | 9.1 | left | `#CCFFFF`, `pda.mismatch` |
| Labels, values, headers, buttons, titles | Bank | 0.25 | 12 | left | `pda.text` family |
| Lists, e-mail body, objective text, video info | AN | 0.25 | 12 | left | `pda.text` |
| Weapon descriptions | AN | 0.22 | 10.6 | left, wrapped | `pda.text.mid` |
| Objectives strip | AN | 0.2 | 9.6 | left | `notice.body` at 80% |

**Furniture.**

| Piece | Geometry |
| --- | --- |
| L bracket (main frame) | A top bar 10 u thick and a leading bar 10 u thick meet at a corner cut about 5 x 5 u; the top bar carries a split inset tab; the leading bar thins to a hairline below about 97 u. The other three sides are hairlines with 3 u corner cuts; the bracket weight repeats at the bottom-trailing corner. Grey gradient stroke |
| Tab button | Bar 16 u tall: a 12 u body over a separate 3 u underline, trailing end cut 3 u |
| Active-tab bar | 12 u tall, fading in from its leading end over about 31 u, trailing end cut 2 u |
| Tab marker | 6 x 11 u block, `#CCFFFF` at 70% |
| Play, stop | 56 x 14 u capsule with 3 u corner cuts; glyph (triangle, square) at the leading end; label over it |
| Close | Slanted tab 42 x 13 u with its word in the art |
| Weapon slot | 1 px rectangle outline, 80 x 40 or 40 x 40 u |
| Scroll button | 8 x 44 u block at 50% with a 4 x 8 u triangle |
| Opening rings | A thick ring with four notches, in four sizes, turning at 0.2 and 0.25 turns per second in opposite directions |

**List rows and scroll bars.** Lists are engine lists. The row height is the face's tallest glyph;
text is inset 3 u. A selected row is a filled rect in `pda.select` with a 1 u outline at full alpha
when the list has focus. Selection does not animate. Hovering the file list plays the hover ping
only. The stock scroll-bar art could not be determined; the replacement draws a 16 u track at about
17% white with a square thumb in `#6E9499`, inset 2 u, and records this as inferred.

**Motion.**

| Behaviour | Timeline |
| --- | --- |
| Open | At 0 ms the bands, which start closed across the middle (top at y 178, bottom at y 262), part to y 0 and y 400 in 400 ms, accel(0, 0.6); the opening title fades out in 400 ms; four spinning rings contract to a 73 u spot, 400 ms each, accel(0.5, 0), staggered 40 ms, gone at 520 ms. At 250 ms every panel slides in from its own edge in 600 ms, accel(0.6, 0): file list and tabs from the leading side, main frame from the trailing side (x 640 to 145), strips from the bottom (y 480 to 432), objectives from the leading side; the watermark scales from 643 x 596 to 512 x 512 u, accel(0.2, 0.8). Captions fade in over 1500 ms. Settled at about 850 ms |
| Close | None. The device is switched off at once; the next opening replays the sequence |
| Tab change | The marker slides between y 14, 36 and 58 in 200 ms, accel(0, 0.8). The outgoing bar retracts 160 to 133 u and the incoming extends 134 to 160 u in 200 ms, accel(0, 1); the incoming label moves 34 u into the bar. The main frame widens 160 to 249 u for e-mail, 200 ms, accel(0, 0.8). Input is blocked for 250 ms |
| Content flash | A white rect at 10% grows from a point to 360 x 130 u (448 for e-mail) in 400 ms, accel(0, 1), fading to 0% |
| User-data reveal | From 300 ms the block widens 125 to 353 u in 350 ms. Rows start at 300, 380, 440, 500, 560 ms: a white bar at 50% wipes 0 to 202 u in 200 ms, accel(0.2, 0.8), and fades in 250 ms; each value fades in over 200 ms, 50 ms after its bar |
| Fingerprint scan | At 520 ms a sound; the print's glow fades over 1400 ms while two hairlines sweep it in 1100 ms; a scan bar sweeps 34 u in 800 ms and 44 u in 500 ms. A match plays a rising ping and shows its status line at 70% fading over 1200 ms; a mismatch (another person's PDA) plays a falling beep and turns the glow `pda.mismatch` |
| E-mail reveal | At 300 ms the header row opens 0 to 450 u in 100 ms; column headers flash white at 50% and settle in 300 ms, staggered 50 ms. At 400 ms the block grows 20 to 360 u in 500 ms. At 450 ms the reader opens 0 to 256 u in 400 ms, accel(0, 0.8). List at 600 ms |
| Video reveal | Width 0 to 356 u in 100 ms at 300 ms; height 20 to 132 u in 200 ms at 400 ms; player opens over 400 ms at 500 ms; list at 600 ms |
| Button | Hover `pda.button` to its hover value in 200 ms and back; a click flashes art and label white for 200 ms; play locks itself for 500 ms |
| Tab hover | Label to white in 200 ms; button art cool to warm white in 200 ms |
| Weapon slot | Hover shows the name at 80% dimming to 40% in 150 ms. A click opens the info box from 234, 330, 408, 55 to 229, 330, 408, 93 in 200 ms, accel(0, 0.7) |
| Strip scroll | Steps of 41–44 u with no tween |
| Tutorial | At 300 ms black curtains close from top and bottom to meet at y 170 over 1000 ms, accel(0.1, 0.8), to 70%. Box at 1200 ms, title at 1700 ms, text unrolls over 500 ms from 1900 ms. Dismissable from 10 000 ms; fades in 500 ms |

**Sounds.** The PDA is the one place in the game where hovering sounds: it is a device with keys.

| Sound | Event |
| --- | --- |
| `guisounds_ping` | Hover over a button, tab or the file list; closing or deselecting |
| `guisounds_ping2` | Click, select, confirm |
| `guisounds_clickstatic2` | Weapon strip already at its end |
| `guisounds_line2a` | Fingerprint sweep |
| `guisounds_pingup` | Fingerprint match (and the HUD tip opening) |
| `guisounds_beepdown3` | Fingerprint mismatch |

HUD sounds are `guisounds_objnew_up`, `guisounds_objdone_up` and `guisounds_obj_down` for objectives,
`guisounds_compup` for clearance and new e-mail, and `guisounds_air` for the oxygen panel. Downloads,
pickup lines, weapon changes and ammunition warnings are silent.

**Classic.** The PDA is the full 640x480 composition, opaque, centred and scaled to the view. The
area outside the 4:3 canvas is filled with `pda.base` and the grid continued at the same 15 u pitch.

**Remastered.** The top and bottom bands, the grid and the base extend to the screen edges. The
content column (tabs, lists, main frame, lower panel, strips) stays 4:3-wide and centred, at stock
positions inside it. Panels still slide in from the screen's real edges, so on a wide view they
travel further in the same 600 ms.

Replacement rules:

1. Keep the opening sequence and its durations. Do not add a closing animation.
2. Keep the diagonal 10 u stagger of the user-data rows and the row-by-row wipe.
3. Draw the L bracket, bands and buttons as vector paths with cut corners; the rings are the PDA's
   only curves.
4. Scrolling may be tweened for touch and controller input; with a mouse wheel keep the stock steps.

### 10.10 Weapon displays

Four guns carry their own ammunition display on the weapon model. Each is a 640x480 GUI on a small
surface, bluer and more saturated than the HUD, with digits many times the HUD's size. All four
share the clip, reserve, clip-low, clip-empty and no-ammunition states. Backgrounds are additive
line art whose brightness wanders on a 3.3 s table of twelve values between 50% and 100%.

| | Machinegun | Chaingun | Plasma gun | BFG |
| --- | --- | --- | --- | --- |
| Background | Teal line-art screen, additive | Curved bar, additive | Square screen, additive, with a 1000 ms 0% to 40% pulse layer | Screen at 80%, additive |
| Grid | Square grid in `#99CCFF` at 10%, drifting, masked to the screen | Curved-line grid at 5%, drifting | Square grid at 10% | Curved-line grid at 5% in a 353 x 169 u clip |
| Clip digits | Default, scale 3 (144 u em), right-aligned in 65, 160, 250, 220, `#99CCFF` at 90% | Default, 3.5 (168 u), right, 190, 123, 250, 220 | Bank, 6 (288 u), centre, 20, −20, 640, 220 | Micro, 3.1 (149 u), centre |
| Reserve digits | Default, 2 (96 u), left at 325, 200 | Default, 1.5 (72 u), right, `#99E6FF` | Bank, 3 (144 u), centre at y 250 | Micro, 1.1 (53 u), `#99F2FF` at 60% |
| Digit glow | Two 120 x 140 u glow tiles under the digits in `#B4DAFF`, brightening what is beneath, over a black copy at 55% | Tiles 140 x 150 u | Tiles 220 x 200 u | One 228 x 144 u tile |
| Gauges | – | Reserve: five slanted segments revealed 0.16 u per round; clip: four segments revealed 2.67 u per round; both `#99E6FF` at 30% | – | Charge: an additive half-disc rising 125 u with the charge level; a four-arc ring turning slowly in `#80B2FF` at 50% |
| Clip low | Digits `#FF8000`; amber warning strip blinking at 500 ms | Digits `#FF8000`; orange clip outline blinking | Digits `#FF8000` at 70%; a mirrored pair of warning strips | As plasma gun |
| Clip empty | Warning strip | Digits `#FF1A00` at 50%; red clip outline | Warning strips | Warning strips |
| No ammunition | Reserve digits `#FF8000` | Reserve `#FF8000` and an orange reserve outline; also whenever the reserve is 60 or less | Reserve `#FF8000` at 50%; strips top and bottom | As plasma gun |

The BFG adds a charge state. The charge fill is `#80B2FF` at 50% up to half charge, `#FF991A` at 50%
above it and `#FF1A1A` at 50% from 97%, where a warning word in Micro 0.85 and two red wedges blink
on a 550 ms loop (100% to 20% in 500 ms, back in 50 ms). At rest a two-part hint cross-fades on a
5000 ms loop of 1000 ms fades.

The replacement redraws each display as vector art on its own canvas, keeps the ice-blue
`#99CCFF` digits and the amber `#FF8000` warning, and never reuses HUD tokens here: the gun displays
are a separate product from the suit.

### 10.11 Multiplayer HUD

The multiplayer HUD is the marine's suit display cut down to what a match needs: two slanted plates
in the bottom corners, a timer and four score rows in the top-trailing corner, and plain text for
everything players say. It is Doom 3's because the plates lean in opposite directions with sheared
numerals to match, every outline flickers on a 400 ms wave, and danger changes the hue of the same
art instead of adding anything. Sources: `guis/mphud.gui`, `guis/chat.gui`, `guis/spectate.gui`,
`guis/mpmsgmode.gui`.

**Tokens.**

| Token | Value | Where it is used |
| --- | --- | --- |
| `mp.line` | #337366, alpha flickering 41-50% on plates, 33-40% on frames, 27-33% on the timer plate | every outline |
| `mp.line.shadow` | #000000 at 30% | a copy of the outline under it (status plate, score frame) |
| `mp.plate.fill` | #174242 at 23-25% | plate interiors |
| `mp.cell.line` | #4CCCB2 at 20% | health and armour cell outlines |
| `mp.digit.health` | #80B2B2 (#FFFFFF until the first update) | health numeral |
| `mp.digit.armor` | #4C6666 with armour, #669999 before the first update | armour numeral |
| `mp.digit.ammo` | #4C8080 (#99CCCC until the first update) | ammunition numeral |
| `mp.warn.low` | text #FF6600 at 80%, outline #994C00, fill #805200 | clip low |
| `mp.warn.crit` | text #FF0000 at 80% (health #FF1A00), outline #FF2600 (health #FF0000), fill #660D00, cell lines #CC2600 | clip empty, health 35 or less |
| `mp.warn.armor` | cell lines #FFA61A, text #998033 | armour 0 |
| `mp.score.row` | #000000 at 25%, 1 u border #1A3833 | score rows and their colour chips |
| `mp.score.self` | 1 u border #59736B | the local player's row |
| `mp.score.text` | #80B2B2 | scores |
| `mp.timer.text` | #809999 at 80% | timer |
| `mp.say.text` | #FFFFFF, stepping 100 / 87.5 / 75 / 62.5 / 50% | chat and event lines |
| `mp.vote.text` | #FFFFFF at 80% | vote line, spectator lines |
| `mp.warmup` | #CC1A1A | warm-up line |
| `mp.weapon.name` | #99CCBF | weapon name |
| `mp.pickup` | #FFCC33 | item pickup flash |
| `mp.lag` | #FF4C00 | connection-lost icon |
| `mp.player.0` .. `mp.player.4` | #404040, #FF0000, #00CC1A, #3380CC, #FFCC1A | player colour by skin: default, red, green, blue, yellow |

All plate and frame art is white shape tinted by the token, straight alpha. The only additive layer
is the scan-line overlay on the ammunition plate (white at 15%, masked to the plate).

**Stock layout.**

| Element | Rect (u) | Construction |
| --- | --- | --- |
| Status plate | ink 6, 448, 143, 29 (art rect 0, 426, 256, 64) | Outline `mp.line` over `mp.line.shadow`, fill `mp.plate.fill`, two cells: armour 11..70 x 456..471, health 68..143 x 453..471 in `mp.cell.line` |
| Health numeral | 90, 446, 39, 32 | Micro 0.38, centred, shadow 1, shear 0, -0.33 |
| Armour numeral | 28, 451, 34, 32 | Micro 0.25, centred, shadow 1, shear 0, -0.3 |
| Ammunition plate | ink 526, 448, 107, 28 (art rect 512, 416, 128, 64) | Outline, fill, scan lines; hidden for fists, chainsaw and flashlight |
| Ammunition numeral | 538, 449, 80, 20 | Micro 0.32, centred, shadow 1, shear 0, 0.33; reads clip/reserve |
| Timer plate | art rect 540, -44, 128, 64 | The ammunition plate's art pushed up so only its lower 19 u show |
| Timer | 570, 0, 100, 30 | Default 0.25, `mp.timer.text`, shadow 1; minutes:seconds, or a short state word |
| Score frame | corners at 574, 18 and 574, 84; open to the trailing edge | 8 u frame pieces in `mp.line` over `mp.line.shadow`, leading side only |
| Score rows | 581, 24 + 16 n, 58, 14 (n = 0..3) | `mp.score.row`; colour chip 14 x 14 at the leading end in the player colour at 40%; score in Default 0.25 at x 601, shadow 1; the local player's row takes `mp.score.self` |
| Weapon strip | selected icon 64 x 64 or 128 x 64 centred at x 320, y 390; neighbours 32 u high at y 416, 10 u gaps | Fades out after a change (below); the name above it at 55, 375, 540, 20 in Bank 0.25, centred, `mp.weapon.name` |
| Item text | 12, 429, 200, 15 | Bank 0.25 |
| Warm-up line | 0, 360, 640, 30 | Bank 0.35, centred, `mp.warmup`, shadow 1 |
| Vote line | 10, 235, 640, 30 | AN 0.33, left, `mp.vote.text`, shadow 1; the question with the yes and no counts |
| Aimed-at name | 200, 450, 238, 20 | AN 0.25, centred, shadow 1, on a bar of that player's colour at 25% |
| Lag icon | 5, 5, 32, 32 | A ring crossed by a diagonal bolt, `mp.lag` |
| Chat lines | 20, 275 + 13 n, 638, 10 (n = 0..4) | AN 0.25, left, `mp.say.text`, shadow 1 |
| Chat prompt | label 33, 250, 95, 20; field 130, 254, 272, 18 | Label Bank 0.25, right-aligned, white over a black copy offset 1 u; field #000000 at 60% with a 1 u #264040 border, AN 0.25 |
| Spectator lines | 0, 350, 640, 40 and 0, 400, 640, 40 | Bank 0.35, centred, white, no shadow |
| Lagometer | 10, 380, 64, 64 | A 64 x 44 cell graph, additive, unfiltered, clients only; one column per network update, scrolling toward the leading edge. Ahead of the server: a green #00FF00 bar rising from row 10, 2 rows a step, up to 5 steps. Behind: a yellow #FFFF00 bar falling from row 10, up to 10 steps. Duplicated commands: a bar from the bottom, 2 rows each up to 6, yellow up to 2, red #FF0000 beyond |

**Plate geometry** (key points in u; lines are 2-3 u wide with a 3 u soft edge):

| Plate | Outline |
| --- | --- |
| Status | Top edge at y 448 from x 69 to 148, stepping down 2 u to y 450 from x 14 to 68; leading edge from 12, 452 to 6, 466; cut corner 6, 470 to 13, 476; bottom edge y 476 from x 13 to 137; trailing edge from 149, 451 to 137, 476 |
| Ammunition | Top edge y 448 from x 526 to 622; leading edge from 526, 448 to 537, 476; trailing edge from 622, 448 to 633, 476; bottom edge y 476 |

Both are parallelograms about 21 degrees off vertical, mirrored: the status plate leans toward the
leading edge at its base, the ammunition plate toward the trailing edge. Fills sit 4 u inside the
outline. The numerals' shear of 0.33 (about 18 degrees) follows each plate's lean.

**States.** The art never changes; its tint does.

| Condition | Change |
| --- | --- |
| Health above 35 | Outline `mp.line`; health cell `mp.cell.line` plus #CC2600 at (70 - health)% |
| Health 35 or less | Outline #FF0000 pulsing 75 / 50 / 45% every 400 ms; cell lines #CC2600 pulsing 62 / 42 / 37% every 500 ms; numeral #FF1A00 |
| Armour 0 | Cell lines #FFA61A pulsing 30 / 20 / 18% every 2000 ms; numeral #998033 |
| Clip low | Outline #994C00 pulsing 62 / 42 / 37% every 1000 ms; fill #805200; numeral #FF6600 at 80% |
| Clip empty | Outline #FF2600 pulsing 75 / 50 / 45% every 500 ms; fill #660D00; numeral #FF0000 at 80% |
| Weapon in the strip | Not owned: tinted red, about #FF3333; owned: teal, #66BFB3 to #4DA699; both breathe every 500 ms |

**Timings.**

| Event | Timeline |
| --- | --- |
| Idle | Outlines flicker between 100% and 82% of their alpha, fills between 100% and 92%, on a 400 ms triangle wave |
| Weapon change | Icons snap to their slots; the selected icon starts at 100% and its neighbours at 80 / 60 / 40 / 20% by distance; all fade to 0 over 1500 ms, linear; the name fades over 1500 ms, accel(0.6, 0) |
| Item pickup | Item text white to `mp.pickup` in 200 ms; at 2000 ms it fades out over 1000 ms |
| Aimed-at name | Shown at once; after aim leaves, held 1500 ms, faded over 500 ms |
| Chat line | Arrives at 100%; after 1200 ms of silence it loses a step every 400 ms and is removed at about 2800 ms. Five lines, newest last |
| Spectator lines | 80% to 20% over 800 ms, cut at 500 ms by a 100 ms return to 80%; repeats every 900 ms |

**Replacement.**

1. Draw both plates as vector polygons from the key points, with the line as a 2 u core and its
   falloff, and keep the four layers (shadow, outline, fill, cell lines) separately tintable.
2. Keep every warning as a tint and pulse change on the same geometry. Never add an icon, a border
   or a size change for a warning.
3. Keep the 400 ms flicker on outlines and fills; reduced motion holds them at their mean alpha.
4. Numerals are Micro with the stock shear; keep tabular spacing so a changing count does not move.
5. **Classic** keeps the stock rects on the centred 4:3 canvas.
6. **Remastered** anchors by corner and keeps the stock insets: the status plate 6 u from the leading
   edge and 3 u from the bottom; the ammunition plate 7 u from the trailing edge and 4 u from the
   bottom; the score rows 1 u from the trailing edge and 24 u from the top, with the frame still
   open to that edge; the timer above them in the top-trailing corner; the lag icon 5 u from the
   top-leading corner.
7. In Remastered the chat lines stay on the leading edge at a 20 u inset with the last line 111 u
   above the status plate; the vote line sits 40 u above the first chat line; the lagometer keeps
   its 10 u inset and sits 4 u above the status plate.
8. Centred text (weapon strip and name, warm-up line, aimed-at name, spectator lines) stays centred
   on the view and keeps its stock distance from the bottom edge.
9. Omit the stock's never-shown item-pickup panel and its scripts for windows the file lacks.

### 10.12 Scoreboard

The scoreboard is a translucent table inside a flickering hairline frame, with scan lines and static
at the edge of visibility. Its signature is the way it arrives: the frame closes in on the table,
the fill flashes, and the cell borders land one column after another. Source: `guis/scoreboard.gui`.

**Tokens.**

| Token | Value | Where it is used |
| --- | --- | --- |
| `mp.board.fill` | #1A3333 at 50% settled (#334C4C at 20% before the first open) | table backing |
| `mp.board.border` | #1A4040, 1 u | backing border |
| `mp.board.cell` | #000000 at 35%, 1 u border #000000 | header and body cells |
| `mp.board.title` | #66B2B2 | title |
| `mp.board.head` | #99CCCC | column heads, footer text |
| `mp.board.row` | #FFFFFF at 80% | player rows |
| `mp.board.self` | 1 u border #809999 | the local player's row |
| `mp.board.foot` | #669999 at 10%, 1 u border #4C6666 | footer box |

**Stock layout.**

| Element | Rect (u) | Construction |
| --- | --- | --- |
| Frame | outer 67, 18, 494, 261 | 8 u frame pieces, `mp.line` flickering 33-40% |
| Backing | 75, 26, 477, 245 | `mp.board.fill`, `mp.board.border` |
| Scan lines | 77, 28, 473, 241 | Additive; one faint line in three at a 1.7 u period, adding about #060606; scrolls at about 1.4 u a second |
| Static | 77, 28, 473, 247 | Rotating noise at 3-4% alpha, pulsing every 1000 ms |
| Title | 120, 23, 385, 35 | Bank 0.40, centred, `mp.board.title`, shadow 1 |
| Header cells | y 53, h 19 | `mp.board.cell`; heads in Bank 0.25, `mp.board.head`, shadow 1 |
| Body cells | y 73, h 157 | `mp.board.cell`, one tall cell per column |
| Player rows | text rects 19 u high from y 79, pitch 40 | Bank 0.25, `mp.board.row`, shadow 1 |
| Colour band | 90, 84 + 40 n, 445, 16 | The player colour at 25% across the row; the local player's row adds `mp.board.self` at 88, 82 + 40 (rank - 1), 449, 20 |
| Footer | 82, 236, 462, 28 | `mp.board.foot`; game type left, limit centred, time limit right, Bank 0.23, shadow 1 |

| Column | x (u) | Width (u) | Alignment | Content |
| --- | --- | --- | --- | --- |
| Name | 82 | 186 | left, text from x 100 | player name |
| Score | 269 | 91 | centred | frags or lives; in team play the player's frags at 0.20 right-aligned, then the team total |
| Wins | 361 | 91 | centred | wins |
| Ping | 453 | 91 | centred | ping |

Columns are separated by 1 u gutters and total 462 u. A player's colour is the colour of the chosen
skin (`mp.player.0` .. `mp.player.4`); team games use the red and blue entries. Rows that are not
ranked (spectating, connecting, warming up) show a status word in the score column and no band.

**Open sequence.**

| t (ms) | Event |
| --- | --- |
| 0 | The eight frame pieces start 10 u outside their rest position and close in over 400 ms, accel(0, 0.8). The backing jumps to #FFFFFF at 20% and moves to #405959 at 40% in 70 ms |
| 70 | Backing to `mp.board.fill` over 300 ms |
| 100 | Name header border #FFFFFF at 20% to black over 300 ms |
| 150, 200, 250 | The next header and the previous column's body cell, each 300 ms |
| 300 | Last body cell |
| 600 | At rest |

Closing has no animation: the board disappears and the frame is reset to its outset.

**Observation.** The stock file declares four player rows. The game writes a line for every client
and clears only the first four, so a fifth player never appears.

**Replacement.**

1. Draw the frame from the frame-piece geometry in Appendix B.4. The corner is a quarter turn of
   about 3 u radius: one of the few stock curves, kept as measured.
2. Keep the open sequence with its times, the 70 ms flash and the 50 ms stagger. Reduced motion shows
   the board at rest.
3. Rows follow the client count. The name, score, wins and ping columns, the 40 u pitch, the colour
   band and the own-row outline are kept.
4. The body holds four rows at the stock pitch. With more clients than fit, the pitch compacts to
   20 u (the own-row outline's height), which holds seven rows in the 157 u body; past that the body
   scrolls with the local player's row kept in view. The header and footer never scroll.
5. **Classic** keeps the stock rects. **Remastered** centres the frame on the view and, when the view
   is taller than the canvas, lengthens the body by whole rows before it compacts.
6. Keep the scan lines and static at their stock strength. They are texture, not decoration: never
   raise them to where they compete with the text.

### 10.13 Multiplayer menu

The in-game multiplayer menu is a strip of tabs along the top edge with one panel hanging from the
current tab. The game stays visible behind it; nothing dims the scene. It is Doom 3's because the
chrome is a single teal hairline family, the panels are tied to their tabs by a cut trapezoid, and
the current tab is marked by darkening, not by a highlight. Source: `guis/mpmain.gui`.

**Tokens.**

| Token | Value | Where it is used |
| --- | --- | --- |
| `mp.menu.strip` | #336666 at 60% | tab strip body |
| `mp.menu.strip.glow` | #8CBFBF at 80% | the strip's edge line and halo |
| `mp.menu.tab` | text #B2FFFF | tab labels, text links |
| `mp.menu.tab.hover` | fill #73B2B2 at 50% | tab under the pointer |
| `mp.menu.tab.current` | fill #000D00 at 40% | current tab |
| `mp.panel.fill` | #1A3333 at 50% | panel backing |
| `mp.panel.border` | #1A4040, 1 u | panel backing border |
| `mp.panel.link` | #337366 at 30% | trapezoid joining a panel to its tab |
| `mp.button.fill` | #99FFFF at 30%, 1 u border #66B2B2, text #99FFFF | filled buttons |
| `mp.well.fill` | #000000 at 60%, 1 u border #264040 | text fields, lists |
| `mp.row.plate` | #000000 at 80% (player panel) or 100% (controls, options, system) | option row plates |
| `mp.text` | #FFFFFF | labels |
| `mp.text.value` | #99CCCC | values, bound keys |
| `mp.text.idle` | #FFFFFF at 60% | list rows at rest |
| `mp.text.disabled` | #FFFFFF at 40% (rows), #CCCCCC at 40% (list entries), #666666 (toggle borders, quality lines) | unavailable controls |
| `mp.select` | #99FFFF at 10% (list row), at 40% with an 80% border (toggle) | current choice |

**Tab strip.** The strip is drawn from y -6, so 6 u of it are above the screen.

| Part | Geometry (u) |
| --- | --- |
| Body | Rect 2, -6, 512, 27; the solid band covers 66% of the height, y -1.8 to 15.9 |
| Edge line | A bright line with a 4-step halo along y 15, in `mp.menu.strip.glow`; its twin on the upper edge is off screen |
| Trailing end | A straight diagonal cut from about x 531 at the top to x 519 at the bottom, about 35 degrees off vertical |
| Leading end | Off screen: the strip bleeds off the leading edge |
| Tabs | y -6, h 21; x and width: Main 0 / 48, New Vote 50 / 87, Multiplayer 139 / 105, Controls 246 / 82, Options 330 / 72, System 404 / 66, Exit 472 / 43; 2 u gaps; labels Bank 0.25, centred |

**Panel recipe.** Every panel is built the same way and hangs with its backing top at y 39.

| Layer | Construction |
| --- | --- |
| Backing | `mp.panel.fill` with `mp.panel.border` |
| Frame | 8 u frame pieces just outside the backing, `mp.line` flickering 33-40% |
| Link | A trapezoid 16 u high from y 17 to y 33: as wide as the tab at the top and spreading about 17 u to each side at its base, where it meets the frame line; `mp.panel.link` |

| Panel | Backing rect (u) | Content |
| --- | --- | --- |
| Main | 0, 39, 339, 178 (flush to the leading edge, no leading frame) | Status, join, team and vote rows; chat field |
| New Vote | 38, 39, 434, 178 | Vote type list, value control, call and cancel buttons |
| Multiplayer | 123, 39, 318, 178 | Rate, always run, name; skin pictures |
| Controls | 60, 39, 451, 295 | Four sub-tabs; twelve bind rows a page |
| Options | 195, 39, 315, 230 | Nine rows: seven two-state choices, two sliders |
| System | 140, 39, 370, 323 | Quality list, display rows, a modal confirmation |
| Exit | 378, 39, 132, 58 | Three text links |

The four trailing panels share a frame edge at x 510-518. A hint line sits at 12, 425, 256, 30 in
Bank 0.25, white, breathing between 100% and 40% over 2000 ms.

**Controls.**

| Control | Geometry (u) | Look |
| --- | --- | --- |
| Label and control row | Label right-aligned to x 120-125; control from x 129-134; row pitch 30-34 | Label Bank 0.25, `mp.text`, shadow 1 |
| Filled button | 128 x 16 (125 x 18 and 128 x 18 in the vote panel) | `mp.button.fill`, Bank 0.25 centred |
| Toggle | 8 x 8 box, caption 10 u to its trailing side | 1 u border; filled with `mp.select` when chosen |
| Text field | 200 x 18 | `mp.well.fill`; AN 0.25, white; 80 characters |
| List | 160 x 155 well; rows 154 x 18, pitch 19 | `mp.well.fill`; rows Bank 0.25, `mp.text.idle` |
| Map picture | 128 x 96 | 1 u border #669999 |
| Option row | 300 x 16 (320 x 16 in Controls and System), pitch 23-25 | `mp.row.plate` with a cut trailing corner; label right-aligned, value centred in `mp.text.value` |
| Skin pictures | 32 x 64, pitch 60 | 1 u black border; the chosen skin takes a 1 u white border |
| Text link | 127 x 17, pitch 18-19, right-aligned | `mp.menu.tab`, shadow 1 |
| Slider | Track 128 x 16 in #99CCCC at 50%; active length 71 x 8 | Thumb from the main menu's slider art |

**States.**

| Control | Hover | Press | Current | Unavailable |
| --- | --- | --- | --- | --- |
| Tab | Fill to `mp.menu.tab.hover` in 100 ms, back in 100 ms | Click sound | `mp.menu.tab.current`; ignores the pointer | - |
| Filled button | None in the stock | Click sound on press, action on release | - | The row is replaced by a dimmed copy without the button |
| Text link | Text to white in 50 ms | Click sound | - | - |
| List row | Text 60% to 100% in 50 ms | Click sound | `mp.select` fill | `mp.text.disabled`, ignores the pointer |
| Toggle | None | Click sound | `mp.select` | Border #666666 |
| Controls sub-tab | Text #99FFFF to white and fill #738CB2 at 0% to #8CA6BF at 30%, 200 ms; out 200 ms and 400 ms | Fill flash #8CA6BF at 20% to 0 over 400 ms | White; ignores the pointer | - |
| System header button | Text #99FFFF to white in 250 ms | Click sound | - | - |

All colour changes are linear. Panels switch at once: no slide, no fade.

**Type.**

| Role | Face and scale | Em (u) | Cap (u) |
| --- | --- | --- | --- |
| Tabs, labels, buttons, list rows, links | Bank 0.25 | 12 | 6.0 |
| Hint under a control | Bank 0.20 | 9.6 | 4.8 |
| Typed text | AN 0.25 | 12 | 9.0 |
| Controls sub-tabs | Default 0.24 | 11.5 | 7.7 |
| System header buttons | Default 0.25 | 12 | 8.0 |

Bank 0.25 carries about 93% of the menu's text. Nothing in the menu is larger.

**Sound.** One sound, `guisounds_menuclickup`, plays on every press. There is no hover sound and no
sound for opening, closing or changing panels.

**Replacement.**

1. Draw the strip, the links and the frames as vector geometry from the key points above; keep the
   strip bleeding off the top and leading edges.
2. Keep the panel recipe: translucent backing with its own dark border, the frame line outside it,
   and the trapezoid to the current tab. The link's sloped ends are 45 degrees.
3. Keep the current tab darkened and hover as a brightening wash. Never enlarge or move a tab.
4. Filled buttons gain the text links' hover (text to white in 50 ms) and a press flash on the fill;
   the stock gives them neither. Keep the single click sound and add no others.
5. Panels still switch at once.
6. Labels stay right-aligned to a gutter with the control beside it; keep Bank 0.25 as the only label
   size.
7. **Classic** keeps the stock rects. **Remastered** anchors the strip to the top-leading corner and
   hangs each panel from its tab at the stock offset; the hint line anchors 12 u from the leading
   edge and 55 u above the bottom edge.
8. The Controls, Options and System panels repeat the main menu's option furniture and follow its
   section; only their panel frame and sizes are particular to this menu.

### 10.14 Loading screens

A loading screen is a dark picture of the level under two black bands, with the word LOADING typed
out above an amber bar and the level's name and briefing below. It is Doom 3's because the picture
is nearly black, the bands are cut with a 45 degree step, and the only warm colour on the screen is
the bar. Sources: `guis/map/*.gui`.

**Selection and progress.**

| Step | Stock rule |
| --- | --- |
| Choice | The GUI named after the map file (`guis/map/<map>.gui`) if it exists, else `guis/map/loading.gui` |
| Intro | The engine runs the GUI for 1000 ms before loading starts, so the opening timeline always plays |
| Progress | At most every 100 ms: bytes read divided by the bytes expected for that map; not clamped |
| Finish | Progress is counted up by 0.05 a frame to 1.0; then a 1000 ms fade from black opens the level |

**Tokens.**

| Token | Value | Where it is used |
| --- | --- | --- |
| `load.word` | #3399B2 (typed in #FFFFFF) | the word LOADING |
| `load.word.hell` | #FF331A | the same word on the hell screen |
| `load.title` | #FFFFFF at 90% | level title |
| `load.subtitle` | #FFFFFF at 40% | subtitle |
| `load.body` | #FFFFFF | briefing paragraph |
| `load.titlebar` | #FFFFFF at 10% | bar behind the subtitle |
| `load.band` | #000000 at 60% | bands |
| `load.band.edge` | #40586F, 2% rising to 67% over 9 u | soft line along each band's inner edge |
| `load.bar.fill` | rows #FFC266, #FFC266, #FFD37C, #FFA319, #E68A00, #B86F00, #995C00, at 80% | progress fill |
| `load.bar.frame` | light #98C1C1 and #79AFAF over dark #002A2A and #003333, at 80% | progress frame |
| `load.flare` | #669999 at 50%, additive | flare on the newest typed letter |
| `load.status` | #00CFF0 | fallback screen text, start-up status line |

**Standard screen** (25 single-player levels), in draw order:

| Part | Rect (u) | Construction |
| --- | --- | --- |
| Picture | 0, 0, 640, 480 | A square picture of the level stretched to the canvas. Mean luma about 20 of 255; over half the pixels are below 32 |
| Scan lines | 0, 0, 640, 480 | Additive, every other 1 u line, adding about #050505; static |
| Top band | solid to y 34 leading of x 178, to y 21 trailing of x 190 | `load.band` with `load.band.edge`; a 13 u step through a 45 degree ramp |
| Bottom band | from y 331 leading of x 355, from y 344 trailing of x 367, to the bottom | The same pieces; darkens to solid black by about y 420 |
| Title bar | 0, 371, 512, 19 | `load.titlebar`, solid to 72% of its length, faded out by 92% |
| Briefing | 17, 394, 521, 81 | AN 0.25, `load.body`, wrapped, 19 u line pitch |
| Title | 16, 336, 610, 30 | Micro 0.40 capitals, `load.title` |
| Subtitle | 16, 367, 610, 30 | Default 0.40, `load.subtitle` |
| Progress fill | 6, 23, 168, 7, revealed from the leading end | `load.bar.fill`; highlight on the third row |
| Progress frame | 5, 22, 170, 9 | `load.bar.frame`: a two-line top and bottom edge and two-column ends, hollow |
| Word | 16, -6, 123, 30 | Micro 0.40, `load.word`; capitals at about y 1-14 |
| Flare | 54 x 21, riding the word | `load.flare` |
| Cover | 0, 0, 640, 480 | Black, fading out |

The step in the bottom band sits at x 347 on 23 screens and further along (377, 397) on two with long
titles. The fill is complete at a progress of 0.983.

**Timeline.**

| t (ms) | Event |
| --- | --- |
| 0 | Cover fades out over 400 ms. First letter; flare to 50% in 200 ms. Top band slides 20 u toward the trailing edge and the bottom band 30 u toward the leading edge, 400 ms, accel(0.2, 0.8) |
| 50, 100, 150, 250 | One more letter each; the flare jumps to the newest letter |
| 200 | Fifth letter. Title bar slides in 300 u from the leading edge; title and subtitle fade in; 400 ms, accel(0.2, 0.8) |
| 300 | Word complete; flare fades over 200 ms; the word turns from white to `load.word` in 200 ms; the frame fades in over 600 ms; the briefing fades in and slides 7 u, 400 ms, accel(0.2, 0.8) |
| 900 | At rest |

There is no closing animation in the GUI; the engine's fade from black covers the cut.

**Variants.**

| Screen | Difference |
| --- | --- |
| Multiplayer maps (`d3dm1`-`d3dm5`) | Bottom band from y 435; the title alone at 16, 447; no subtitle, briefing or title bar |
| Hell (`hell1`) | No bands; `load.word.hell`; frame tinted #FF0000; no level text |
| First level (`mars_city1`) | No picture: black, with the word centred at y 211 and the bar centred beneath it (frame 235, 242, 170, 9) |
| Fallback (`loading`) | The start-up picture full screen and one line of Default 0.40 in `load.status` at 5, 10; no bar, no animation |

**Replacement.**

1. Keep the composition: progress group top-leading, text block bottom-leading, the picture clear
   between them.
2. Type the word at one letter every 50 ms with the flare on the newest letter, then settle it to
   `load.word`. Reduced motion shows the word complete.
3. Draw the bar as a vector frame and a seven-step vertical gradient. Progress is clamped to 0..1 and
   the fill is complete at 1.0; it never runs past its frame, as the stock's unclamped value can.
4. Keep the bands at 60% so the picture shows faintly through them, with the soft edge line and the
   13 u, 45 degree step. Move the bottom step with the title's length, as the stock does by hand.
5. Keep pictures dark. A new picture is graded to the stock range (mean luma 8-48 of 255) so that
   the bar stays the brightest warm element.
6. Never add a percentage, a spinner or tips: the stock screen says where the player is going and
   nothing else.
7. **Classic** keeps the stock rects. **Remastered** extends the picture and both bands to the screen
   edges, lengthening only their straight spans; the progress group keeps its 5 u and 22 u insets
   from the top-leading corner; the text block keeps its 16 u inset from the leading edge and its
   stock distances from the bottom edge (title 144 u, subtitle 113 u, briefing 86 u).

### 10.15 Console and engine text

The console and the engine's status text are drawn from one fixed-cell character sheet, in cyan on
black. They are the plainest part of the interface and stay that way: a terminal, not a panel.

**Tokens.**

| Token | Value | Where it is used |
| --- | --- | --- |
| `console.text` | #00FFFF | default text, prompt, version, scroll marker |
| `console.back` | #000000, opaque (inferred from the material's image name) | background |
| `console.rule` | #00FFFF | 2 u rule under the console |
| `console.input` | #FFFFFF | typed line |
| `console.complete` | #CC3333 at 45% | highlight behind a completed command |
| `console.fps` | #FFFFFF | frame-rate counter and debug lines |

Colour escapes select red #FF0000, green #00FF00, yellow #FFFF00, blue #0000FF, cyan, magenta
#FF00FF, white, grey #808080 or black; the default escape returns to cyan.

**Console anatomy** (stock).

| Part | Geometry (u) | Notes |
| --- | --- | --- |
| Cell | 8 x 16 | 78 columns, starting at x 8 |
| Height | Half the screen; a fifth with Shift; full screen when forced | Slides at 3 screen-heights a second, linear: half height in 167 ms |
| Background | From the top to 2 u above the console's lower edge | Slides down with the console |
| Rule | 2 u high, full width | `console.rule` |
| Version | Right-aligned to x 640, 24 u above the lower edge | `console.text` |
| Text rows | From 48 u above the lower edge upward, 16 u pitch | Colour per character |
| Scroll marker | A caret at every fourth column on the lowest text row | Shown while scrolled back |
| Input line | 32 u above the lower edge: prompt `]` at x 8, text from x 16 | Prompt `console.text`, text `console.input` |
| Cursor | Baseline bar when inserting, solid block when overstriking | 16 ticks on, 16 off (about 267 ms each) |
| Notify lines | The last 4 lines for 3000 ms at the top-leading corner, 16 u pitch, no backing | Off in release builds |
| Frame-rate counter | Big cells (16 x 16 u), right-aligned to x 635 at y 2 | `console.fps`; the mean of the last four frames; debug lines stack beneath it in small cells at a 20 u pitch |

**Start-up screen.** A full-screen picture with one status line: BigChars small cells, centred, at
y 410, in `load.status`, upper case. The picture is letterboxed: black above 16% of its height, a
bright cyan rule (about #3988A8) at 16-17%, the image to 84%, a darker strip to 94% in which the
status line falls, then black. It shows Mars at the leading side under a teal hexagon grid, with the
id mark in a square block at 80-95% of the width and 70-94% of the height.

**BigChars cell metrics** (16 x 16 texel cell; a small cell draws it 8 x 16 u, a big cell 16 x 16 u):

| Metric | Texels | Small cell (u) | Big cell (u) |
| --- | --- | --- | --- |
| Baseline | row 14 | 14 | 14 |
| Cap height | 11 | 11 | 11 |
| x-height | 8 | 8 | 8 |
| Descender | 1 | 1 | 1 |
| Vertical stem | 3 | 1.5 | 3 |
| Horizontal bar | 2 | 2 | 2 |
| Ink width, i / n / o / H / W / M | 3 / 9 / 10 / 11 / 12 / 13 | half | same |

Glyphs are centred in their cells, so the pitch is fixed but the spacing is uneven. Small cells
squeeze the sheet 2:1 horizontally. The sheet has no baked shadow.

**Replacement.**

1. The console keeps its cell grid (8 x 16 u cells, 78 columns), its cyan-on-black scheme, the 2 u
   rule, the `]` prompt, the version line and the caret row.
2. Text is drawn from the BigChars TrueType face at display resolution, one glyph per cell, centred
   as in the sheet. Small cells keep the 2:1 condensed proportion; they are not re-spaced
   proportionally.
3. Keep the linear 167 ms drop. Never add a fade, blur or translucent backing: the console is
   opaque.
4. The cursor keeps its two shapes and its blink.
5. The start-up status line stays one centred line of small cells in `load.status` in the picture's
   lower strip.
6. The frame-rate counter stays white big cells in the top-trailing corner. In **Remastered** it and
   the debug lines anchor 5 u from the trailing edge; the console spans the full width of the view
   and keeps its 8 u text inset, with as many columns as fit.
7. The stock engine draws no screenshot flash, recording mark or network graph. The replacement adds
   none.

## 11. In-world device GUIs

Doom 3's signature interface is not a menu. It is 457 screens mapped onto surfaces in the levels:
door panels, keypads, lift controls, machine consoles, kiosks, status monitors, signs and video
walls. The player uses them by looking at them and firing; the crosshair becomes a cursor on the
glass. Retail maps place them 2,605 times, and 65% of those placements are loops nobody operates.

Each device is a UAC product. It has its own layout, colour and behaviour, and it is built from a
shared hardware vocabulary: a dark tube, a stack of monitor artefacts, a small set of frame kits and
one status language. The replacement keeps every device's identity and redraws only the shared
hardware. Classic and Remastered do not differ here: a device canvas is mapped to its surface, not
to the display, so both layouts show the same device. All 21,026 windows are plain windows: no
list, text field, slider, choice or scroll bar occurs on any device.

### 11.1 Families

Families group devices by function. Placements count the retail single-player maps.

| Family | Files | Placements | Function | Look | Representative |
|---|---|---|---|---|---|
| Door and lock panels | 48 | 263 | show lock state, sometimes one action | cog rings and crest behind slabs; red or green-cyan | `guis/doors/doorlock.gui`, `guis/doors/uac_general.gui` |
| Keypads | 8 | 51 | enter a three-digit code | door layout plus a ten-key pad | `guis/controlpanels/cabinet.gui` |
| Keycard scanners | 4 | 4 | scan a card | amber photographic plate, scan lines, card icon | `guis/doors/keycard.gui` |
| Security terminals | 10 | 12 | unlock or override an area | eight rings, one status word, outlined buttons | `guis/controlpanels/securitylock.gui` |
| Lifts | 32 | 115 | call and move lifts | brown or grey slab, arrows, large floor word | `guis/doors/elevatorcall.gui`, `guis/doors/elevator2floor.gui` |
| Transfer panels | 46 | 46 | leave or enter a level | thin rings in an L-bracket frame, teal | `guis/transfer/exit_admin.gui` |
| One-button utility | 26 | 32 | open a hatch, ladder, locker | one large outlined button, warning stripe | `guis/comm1/maintenance.gui` |
| Machinery | 62 | 77 | run a process | double-line frames, read-outs, long sequences | `guis/controlpanels/airlock_outer.gui` |
| Health station | 1 | 71 | administer health | red and pale-blue circles, clinical | `guis/controlpanels/healthstation.gui` |
| Kiosks and terminals | 54 | 107 | read, download to the PDA | title band, body copy, blue-cyan | `guis/marscity/uac_news.gui`, `guis/screens/laptop.gui` |
| Ambient loops | 81 | 1,177 | none (set dressing) | cyan tube, wordmark, charts, light sweep | `guis/screens/cpu_top.gui`, `guis/screens/scan4.gui` |
| Broken screens | 30 | 514 | none | red text, heavy static, cracks | `guis/screens/cpu_three.gui`, `guis/screens/malfunction.gui` |
| Video | 16 | 42 | play a cinematic | letterboxed footage, near-neutral tint | `guis/movies/mfs.gui` |
| Cameras | 8 | 8 | view and select remote cameras | amber frame bars, khaki captions | `guis/cameras/cam_on.gui`, `guis/cameras/camselect.gui` |
| Signs | 19 | 65 | name a place or direction | one large text line on a wide plate | `guis/doors/marquee.gui` |
| Hell | 6 | 15 | none | pentagram, faces, blood; no interface | `guis/demonic/hellface.gui` |
| Arcade | 2 | 2 | play a mini-game | photographic cabinet art, no monitor artefacts | `guis/marscity/sttp.gui` |
| Templates and tests | 4 | 4 | level-design helpers | not player-facing | `guis/templates/copy one click script.gui` |

221 of the 457 files are interactive. The most-placed interactive devices are
`guis/doors/uac_general.gui` (73), `guis/controlpanels/healthstation.gui` (71),
`guis/doors/elevatorcall.gui` (39) and `guis/controlpanels/cabinet.gui` (37). The most-placed device
of all is `guis/screens/cpu_top.gui` (263), a ten-window breathing wordmark.

- **Door and lock panels.** One layout serves both states. Four cog rings (820, 740, 640 and 580 u
  squares, alternately mirrored) turn behind a large crest inside a crop window 5, 79, 630, 358.
  Black bands above and below carry a title slab, a small outlined badge naming the controlling
  system, and a status slab. Locked is red; a game trigger converts the same panel to green-cyan.
- **Keypads.** The door layout with a pad. `guis/controlpanels/cabinet.gui` has ten keys of 96 x 64 u
  (two are 95 u wide, a stock inconsistency) in two rows at y 40 and 109 inside the `Keypad` frame
  5, 188, 628, 198, with 9 to 10 u gutters. Three digits are compared with three level parameters.
- **Lifts.** Two kits: an amber-brown slab (mean texel `#2E1D06`) and its grey twin (`#212121`), each
  drawn as two mirrored halves of 630 x 235 u, with 150 x 110 u arrows. Call panels are one
  full-canvas button. Floor panels light an amber plate under the chosen floor.
- **Transfer panels.** The most uniform family: five chromatic colours in 46 files. Four thin rings
  (709 x 645 down to 501 x 456 u) turn behind an L-bracket frame built from one corner piece mirrored
  four ways. The button is the label itself, 535 x 410 u.
- **Machinery.** The densest family (median 66 windows). Frames are the double-line kit or the caves
  kit; numbers use Default at 1.6, captions Micro at 0.57. A click starts a process of up to 33 timed
  steps over 6,000 ms (`Anim` in `guis/controlpanels/airlock_outer.gui`).
- **Health station.** The only clinical panel: a neutral additive tint (`#CCCCCC`), a pink back glow
  (`#FFCCCC` at 10%), two red circles of 590 x 440 and 538 x 401 u and a pale-blue spinning pair, a
  charge count in Micro at 2.0, and one near-full-canvas button (`ActionButton`, 630 x 470 u).
- **Kiosks and terminals.** A title band, body copy in AN at 0.65 inside 524 x 273 u, and a download
  strip 622 x 100 u across the top. `guis/screens/laptop.gui` (47 placements) is a wordmark, a locked
  notice in Bank at 1.1 and the owner's name.
- **Ambient loops.** A cyan-tinted tube face, a wordmark that breathes on a 1 s table, sub-windows
  that appear and disappear on a 3,900 to 13,000 ms timeline, a spike chart, a grid, one light sweep
  and a glare band. They carry no dirt, no scan lines and no bezel shadow.
- **Broken screens.** Failure text in Default at 2.0, `#FF3333`; a fast light bar; static at a constant
  40%; erratic flicker tables (11.7). `cracked*` devices are glass cracks and dirt over nothing.
- **Video.** The cinematic sits at 31, 24, 577, 428 on a black plate 10, 10, 618, 456. The tint is
  nearly neutral (`#0D1A1A`) so footage reads true. No cursor.
- **Cameras.** The remote view fills 10, 10, 620, 460 between amber frame bars 610 x 60 u (top) and
  610 x 72 u (bottom). The selector is six text rows of 500 x 50 u at a 52 to 54 u pitch.
- **Signs.** One text line from a level parameter, Default at 0.8 to 1.0, green or red, on a plate
  mirrored left and right. The marquee surface is 110.8 x 11.4 world units, so its canvas is stretched
  7.3 times wider than tall.
- **Hell.** No interface structure: a pentagram plate, three drifting face layers, scrolling blood,
  a 1,500 ms flash loop, strong static. `guis/admin/hell.gui` keeps an office door layout and corrupts
  it: name-plate text at 5% alpha, the title alternating with a threat, tint `#E60000`.
- **Arcade.** `guis/marscity/sttp.gui` is drawn as a different machine: photographic background, black
  bands at 60%, score in Micro at 0.31 and 0.47, one full-canvas button. It has no scan lines and no
  bezel shadow.

### 11.2 The finishing stack

Every device ends with the same run of full-canvas layers that turn a flat drawing into a lit,
dirty tube. The carrier material (`textures/common/entityGui` and its two siblings) has no stages:
it adds no bezel, glass or glow. Every artefact is a window inside the GUI, drawn over the content.
The physical bezel is the model around the surface.

The modal order, back to front: back glow, content, static, rim glow, bezel shadow, top highlight,
scan lines, alert rim (normally hidden), dirt, glare. 179 distinct orders exist; 42 files have no
finishing layer at all.

| # | Layer | Texture profile | Blend | Strength | Flicker | Files |
|---|---|---|---|---|---|---|
| 1 | Back glow | white radial: full in the central 14%, about 20% at edge midpoints, 2% at corners | alpha | 10% of the place glow colour | none | 285 |
| 2 | Static | tinted plate plus a noise plate scaled 2 x 2, jittered every 0.05 s, rotating 6 turns per second | alpha, noise through destination alpha | (20% to 30%) / N; N = 10, 8, 15, 6, 4 in that order of frequency | alpha 1 s linear; noise colour 25% at 0.5 s | 332 |
| 3 | Rim glow | white, 37% at the rim falling to 0 over 21% of each side | alpha | (85% to 100%) / 6, i.e. 14% to 17% | 15% at 0.4 s | 266 |
| 4 | Bezel shadow | black, 60%, 36%, 18%, 6% on four texels inside a clear border texel; 3.9% of each side | alpha | 100% (421 of 481) | none | 400 |
| 5 | Top highlight | flat across; 14.5% white at the top falling linearly to 0 at 69% of the height | additive | tint colour, alpha ignored | none | 373 |
| 6 | Scan lines | one lit row in three; 5.6 u pitch (7.5 u for the older texture) | additive | 2.5/255 per line (2/255 older) | scrolls 0.02 or 0.04 repeats per second | 356 |
| 7 | Scan pulse | a rolling sawtooth band in a 3,000 u tall window | alpha | 1% to 3% | scrolls 0.2 repeats per second | 48 |
| 8 | Alert rim | hairline frame 0.8% in from the edge with a glow 7% deep | additive | `#FF8080` at 100% when shown | flashed by error timelines | 73 |
| 9 | Dirt | black smudges, heaviest at the top and edges; coverage 26% to 52% | alpha | 50% (138), 20% (67), 100% (60), 30% (51), 80% (46) | none | 288 |
| 10 | Glare | white band: bright edge 9% from the top, gone by 34%, inset 5% each side; faint echo 8% above the bottom | alpha | 10% (97), 20% (70), 15% (62), 5% (34) | 8% at 0.33 s | 322 |
| 11 | Vignette | black radial, 78% at edge midpoints, 3% at the centre | alpha | 40% (45), 20% (38) | none | 117 |

Variants: a mottled dark rim on lift panels (24 files, 50%), scratches (34 files), glass cracks (14)
and blood (25) mark wear and damage. A second top highlight flipped up from the bottom, 280 u tall,
occurs 100 times. Static overscans the canvas by 10 u. 335 of 481 bezel shadows and 202 of 278 rim
glows are drawn mirrored.

Replacement rules:

1. Each layer becomes a procedural layer with the parameters in the table. The replacement draws
   no bitmap for layers 1, 3, 4, 5, 6, 7, 8, 10 and 11; they are gradients, bands and line patterns.
2. Dirt, scratches, cracks and blood are irregular. The replacement draws them from authored masks
   with the measured coverage and peak alpha; it does not synthesise them at run time.
3. Keep each device's own strengths and order. A device with static at /4 is noisier than one at
   /15 on purpose.
4. Strengths are near-subliminal. Scan lines add at most 2.5/255, static sits at 2% to 4% alpha on
   most devices, glare at 5% to 20%. Never raise them to make the effect "read". The look is the sum
   of the layers; remove one and almost nothing changes.
5. Scan lines keep their pitch in canvas units (5.6 u or 7.5 u). They are not drawn at the display's
   pixel pitch and do not thicken with resolution.
6. Dirt and glare stay non-blocking: 409 of 491 dirt layers ignore input.
7. The finishing stack never covers the cursor. The cursor is drawn after the desktop.
8. Ambient loops, video and the arcade keep their reduced stacks (11.1). Do not complete them.

### 11.3 Frame kits and shared furniture

Device frames are built from small white pieces, stretched and mirrored. A negative width or height
mirrors a piece; one corner makes four. Rounded corners do occur here, unlike the menus, and only
in the places this section names. Appendix B.3 gives texel-level measurements.

| Kit | Files | Top families |
|---|---|---|
| Button outline with fill | 119 | transfer 46, machinery 21, lifts 16, utility 14 |
| Title slab | 115 | transfer 46, doors 28, utility 14, lifts 12 |
| Tick-strip and square grids | 112, 115 | machinery, ambient, kiosks |
| UAC crest | 93 | doors 33, lifts 23, kiosks 15 |
| 1 px rounded outline | 73 | doors 28, kiosks 14, lifts 10 |
| L-bracket frame | 73 | transfer 46, doors 16 |
| Double-line ("scibox") frame | 64 | machinery 32, ambient 13 |
| Thin rings | 55 | transfer 46 |
| Caves kit | 46 | machinery 16, lifts 9 |
| Cog rings | 30 | doors 22, security terminals 7 |
| Warning stripe | 19 | machinery 7, utility 4 |

#### Title slab

A flat bar with one square end and one end whose outer corner is rounded. The bar fills 62.5% of
its rect height, centred. The rounded corner is a quarter ellipse over 5/16 of the cap piece.

| Use | Rect height | Slab thickness | Corner radius (cap 37 u wide) | Colour |
|---|---|---|---|---|
| Header rows (`bar1Mid`, `bar2Mid` in `guis/doors/doorlock.gui`) | 26 u | 16 u | about 11 u wide, 8 u tall | `device.locked.header` or `device.open.header` |
| Status slab (`Statusbar3Mid1`) | 52 u | 32 u | scales with the rect | `device.locked.slab` or `device.open.slab` |
| Keypad header (`bar1Mid` in `guis/controlpanels/cabinet.gui`) | 32 u | 20 u | scales | `#CCB2B2` at 30% |

Rules: exactly one corner of a slab is rounded. Flipping the cap moves the round corner between top
and bottom; header rows come in pairs with the round corners facing each other. The square end stays
square. Slabs are flat fills at 30% alpha with no outline and no glow.

#### 1 px rounded outline

A hairline box with four rounded corners, drawn from four mirrored corner pieces and four
straights. The line is one texel: 1.9 u thick on horizontals and 2.6 u on verticals at the badge
size, where corner pieces are 82 x 30 u and the corner arc is about 13 u wide and 9 u tall. Colour
`device.line` (white at 80%), or white at 50% around keypad and contents areas.
Rules: the replacement draws a 2 u line with a 9 u corner radius at the badge size and keeps the
radius when the box grows; the stock stretches the straights, not the corners. The outline has no
fill and no glow.

#### Button outline with fill

The same rounded box with a 2-texel outline, a 2-texel clear gap, then a fill at 47% of the outline's
alpha. Stock buttons range from the keypad key to 556 x 238 u (`TextTitle1` in
`guis/comm1/maintenance.gui`). The label is a separate text window that carries the events.
Rules: keep the gap between outline and fill; it is what distinguishes a button from a panel. The
outline is twice the hairline weight (about 4 u at the stock sizes). Hover and press change colour
and alpha only (11.6).

#### Double-line frame

Two bright hairlines two texels apart with a 73% fill between them, a 27% feather outside and a soft
two-texel tail. Corners are rounded over 4 to 5 texels; variants add a T-junction for a second rail
and a stepped tab. Capsule bars from the same kit (a solid bar 9/16 of its rect height with rounded
ends) serve as labels and level bars. A navy gradient plate (black to `#0D345C`) sits behind.
Rules: draw the frame as two parallel strokes with the fill between, not as one thick stroke. Keep
T-junctions and tabs where the source has them. This is the machinery frame; do not use it on doors.

#### L-bracket frame

One corner piece: a heavy bar along the top (about 3/16 of the piece's height) and a heavy bar down
one side (about 1/16 of its width), with a faint hairline closing the other two sides. Mirrored into
four quadrants of 626 x 276 u it frames transfer and office panels in `#99CCCC` at 100%.
Rules: corners are square. The four brackets meet at the centre lines; keep the stock asymmetry
between the heavy top/bottom bars and the lighter side bars.

#### Caves kit

Square-cornered green furniture: solid blocks with a 25% gutter, and corner, rail and title pieces
whose colour is baked into the art (mean `#5A735A`, peak `#96AF96`; title bar `#47744B`). Plates use
`device.caves.plate`. It is the only kit that is not white art.
Rules: no rounded corners anywhere in the caves kit. The replacement draws the pieces in their
measured colours and does not re-tint them.

#### Cog rings and thin rings

Rings are the slow machinery behind security devices. Cog rings are an octagonal toothed outline
filling 88% of a square; thin rings are plain circles. Alternate rings are mirrored so they appear to
counter-rotate. Periods are in 11.7.

| Device | Rings | Squares or rects (u) | Colour |
|---|---|---|---|
| Door panel (`Circle0`..`Circle3`) | 4 cog | 820, 740, 640, 580 | `device.locked.ring`; `device.open.ring` when open |
| Security terminal | 8 cog | 820 down to 340 | `#800000` at 50% outer four, `#801A1A` at 50% inner four |
| Transfer panel | 4 thin | 709 x 645, 640 x 582, 553 x 503, 501 x 456 | `#809999` at 50% |

Rules: rings are larger than the canvas and are cropped by black bands; never shrink them to fit.
Unlocking swaps the red set for the green set ring by ring at 0, 50, 100 and 300 ms.

#### UAC crest and wordmark

The crest is a white alpha-shaped emblem filling 97% of its square. It is drawn twice on door
panels: a watermark at 20, 20, 600, 440 at 30% to 60% alpha and a crisp copy of 204 x 155 u at the
upper middle at 60%. Lift panels use an additive copy of 390 x 265 u at `#261A0D`. The wordmark
(a lozenge above three letters, filled and outline versions) is used by ambient loops and laptops:
the filled copy breathes between 4% and 30% alpha under a steady outline at 60%.
Rules: the crest takes the panel's state colour (`#661A1A` locked, `#1A8066` open for the
watermark). It is never drawn at full opacity and never in a brand colour.

#### Status lights, bars, keypads, stripes

| Item | Anatomy | Stock values | Uses |
|---|---|---|---|
| Status pulse | a text or plate whose alpha or colour loops | 1,200 ms (`Text2` in `guis/controlpanels/securitylock.gui`); 1 s table loops on ambient screens | 1,035 looping timelines in 300 files |
| Level and progress bars | capsule bars; scrolling bar strips | ten bars on 400 to 2,400 ms loops (`Bar1`.. in `guis/screens/scan4.gui`) | charts and bars in 43 files |
| Keypad key | flat plate, centred digit in Micro 0.9 | 96 x 64 u; plate white at 10%, digit white at 40% | 8 keypad files |
| Warning stripe | a stripe pattern tiled 7 times across, scrolling 0.05 repeats per second, tinted by the device | 28 uses | 16 files |
| Moving arrows | a blurred chevron tiled 4 times, scrolling 2.5 repeats per second, alpha breathing on a 1 s table | 161 x 264 u on lift panels | 18 files |
| Tick strips | rows of evenly spaced marks, 8 texels tall | 192 uses of the commonest strip | 74 files |
| Hex and square grids | thin tiled lines; hex grid tiled 9 x 9 at 7% | coverage 17% and 23% | 30 and 115 files |

### 11.4 Palettes

Colour is state; tint is place. A device says its state with red, green-cyan or amber on the same
art, and says where it is with a faint additive wash over the whole tube. Art is white and is
tinted when drawn; alpha does most of the work. Text is white at partial alpha.

#### State and text tokens

| Token | Value | Used for |
|---|---|---|
| `device.panel` | `#000000` at 90% | the black field under every device (368 uses) |
| `device.text` | `#FFFFFF` at 60% | labels at rest |
| `device.text.dim` | `#FFFFFF` at 40% | secondary labels, button labels at rest |
| `device.text.strong` | `#FFFFFF` at 80% | location names, key values |
| `device.text.hover` | `#FFFFFF` at 100% | hovered label |
| `device.line` | `#FFFFFF` at 80% | 1 px outlines |
| `device.locked.ring` | `#800000` at 50% | rings, locked |
| `device.locked.header` | `#CC9980` at 30% | header slabs, locked |
| `device.locked.slab` | `#FF3300` at 30% | status slab, locked |
| `device.locked.text` | `#FF0303` at 70%; state line `#FF1A1A` at 90% | "LOCKED", "RESTRICTED ACCESS" |
| `device.open.ring` | `#33CC99` at 20% | rings, open |
| `device.open.header` | `#99CCD9` at 30% | header slabs, open |
| `device.open.slab` | `#99E6B2` at 30% | status slab, open |
| `device.open.text` | `#99FFCC` at 60%; state line at 90%; `#66FFCC` at 90% on terminals | "UNLOCKED", "GENERAL ACCESS" |
| `device.attention` | `#FFB24C` at 60% | small amber captions, amber read-outs |
| `device.button.line` | `#FFCC66` at 50%; 100% hovered | button outlines and fills on terminals |
| `device.hover.plate` | `#FFB233` at 30% | key and floor-button hover plate |
| `device.pressed` | `#99CCFF` at 40% | a keypad key already entered |
| `device.alarm` | `#FF0000` at 100% | error text, alarms |
| `device.hazard.line` | `#FF1A00` at 50%; `#FF0000` at 70% hovered | utility buttons that open hazards |
| `device.store.line` | `#80CCFF` at 30% to 40% | storage and vent outlines |

#### Place tints

The top highlight (11.2) carries the place tint. All are additive; alpha is ignored.

| Token | Value | Layers | Place |
|---|---|---|---|
| `device.tint.cool` | `#266680` | 64 | transfer, doors, signs, video idle: the standard teal |
| `device.tint.cool.low` | `#668080` | 51 | the second, bottom wash on transfer panels |
| `device.tint.security` | `#806626` | 45 | door locks, security terminals, keypads, keycards |
| `device.tint.lift` | `#99994C` | 35 | lifts |
| `device.tint.caves` | `#4CCCCC` | 35 | caves kit devices |
| `device.tint.machine` | `#669999`; `#99CCCC` | 34; 23 | utility and machinery |
| `device.tint.info` | `#66CCCC` | 23 | kiosks |
| `device.tint.ambient` | `#1A6666` | 19 | status monitors |
| `device.tint.video` | `#0D1A1A` | 8 | video |
| `device.tint.hell` | `#E60000`; `#CC6666` | 2; 2 | corrupted devices |

| Token | Value | Used for |
|---|---|---|
| `device.glow.cool` | `#66CCFF` at 10% | back glow, 112 layers |
| `device.glow.transfer` | `#80E699` at 10% | back glow, transfer panels, 46 layers |
| `device.glow.warm` | `#FF6633` at 10%; `#FF3300` and `#FF0000` on alarm and broken screens | back glow, warm devices |
| `device.tube` | `#99E6FF` at 80%; `#80FFE6` at 80% | tube face of ambient loops |
| `device.transfer.bar` | `#80FFE6` at 30%; `#99FFF2` at 50% hovered | transfer button bars |
| `device.transfer.frame` | `#99CCCC` at 100% | L-bracket frame |
| `device.caves.plate` | `#96AB96` at 100%; `#ADBF87` at 70% | caves plates |
| `device.camera.frame` | `#FF9933` at 100% | camera frame bars |
| `device.camera.text` | `#BAAB8A` at 100%; `#B29466` at 60%, 100% hovered | camera captions and rows |
| `device.health.charge` | `#B2E6FF` | charged state |
| `device.health.empty` | `#FF0000` at 42% and 62% | depleted circles |

Rules:

1. State changes hue on the same art. Locked and open devices share geometry.
2. "Open" is a green-leaning cyan. Pure green does not appear (1.3% of tints) and is never
   introduced.
3. Purple and magenta do not appear (0.1%) and are never introduced.
4. Amber is attention and hover; red is locked, failed or dangerous. Do not use red for hover.
5. Keep each family's palette. Transfer panels use five colours; machinery uses 132. Do not
   normalise one to the other.
6. Baked-colour art (lift slabs, caves pieces, camera plates, the pentagram) keeps its measured
   colours (Appendix B.3) and is not re-tinted by state tokens.

### 11.5 Type and language

Devices speak in capitals, large, in the Micro face. 2,989 text windows occur in 414 files; every
one sets its scale explicitly, and every face referenced ships.

| Face | Text windows | Share | Case | Alignment (left / centre / right) | Role (inferred) |
|---|---|---|---|---|---|
| **Micro** | 1,765 | 59% | 1,415 upper | 699 / 930 / 136 | headers, status words, captions, button labels |
| **Default** | 794 | 27% | mixed | 382 / 331 / 81 | location names, numbers, failure banners, signs |
| **Bank** | 336 | 11% | mixed | 153 / 180 / 3 | sub-captions, logs, name plates |
| **AN** | 94 | 3% | sentence | 82 / 12 / 0 | body copy on kiosks |

| Role | Stock scale | Em (u) | Em on the standard panel (world units) |
|---|---|---|---|
| Sign text | 1.3 median, up to 2.5 | 62 to 120 | n/a (wide surfaces) |
| Status word, button label | 1.0 to 1.2 | 48 to 58 | 1.4 to 1.6 |
| Interactive label, median | 0.8 to 0.95 | 38 to 46 | 1.1 to 1.3 |
| Header slab text | 0.64 to 0.78 | 31 to 37 | 0.9 to 1.1 |
| Read-outs, dense families | 0.43 to 0.5 | 21 to 24 | 0.6 to 0.7 |
| Small caption | 0.38 to 0.4 | 18 to 19 | 0.5 |
| Data dressing | 0.31 to 0.33 | 15 to 16 | 0.4 |

The standard panel is 13.6 world units tall, 0.0283 units per u vertically. The legibility floor for
anything the player must read to act is scale 0.5. Text below 0.33 is texture, not information; the
smallest in use is 0.1. The largest is a floor digit at 7.8.

Habits:

- 68% of static strings are all capitals. Security terminals reach 94%, keypads 87%. Keycard
  scanners are the exception at 5%; they use sentence case.
- Centre alignment (1,453 windows) is slightly more common than left (1,316); right is rare (220).
- Text shadow is almost absent: 22 of 2,989 windows.
- Button labels break into two or three short lines. Ladder panels stack a word one letter per line.
- 104 text windows show a level parameter directly (place names, counters).

Vocabulary. State is said three ways at once: a word, a colour and a change in the rings and bars.

| Phrase | Files | Use |
|---|---|---|
| "LOCKED" / "UNLOCKED" | 28 / 16 | status slab |
| "RESTRICTED ACCESS" / "GENERAL ACCESS" | 9 / 20 | state line under the location |
| "SECURITY DOOR", "LOCK" | 22, 24 | title slab and badge |
| "CLICK TO EXIT", other "CLICK ..." | 23, 39 in all | direct instruction on the button |
| "TRANSFER ..." | 81 | transfer panels |
| "WARNING", "CAUTION", "ERROR" | 31, 7, 23 | alarms |
| "ONLINE", "OFFLINE", "ACTIVE", "STANDBY" | 35, 28, 46, 12 | machine state |
| "UAC" | 42 | footer mark |

Busy-work data fills ambient screens: scrolling charts, tick strips, and one pasted column of
numbers that appears unchanged in 28 files. It is dressing and carries no state.

Rules:

1. Keep each window's face, scale, alignment and colour. The reconstructed faces replace the bitmap
   fonts one for one.
2. Never reduce an interactive label below scale 0.5, and never enlarge data dressing to make it
   readable.
3. Keep capitals where the stock has them and sentence case on keycard scanners.
4. Do not add text shadows or outlines.
5. Keep the pasted data and the busy-work loops; do not replace them with live values.

### 11.6 Interaction

The player aims and fires. There is no free pointer: the cursor sits where the view ray meets the
glass.

| Step | Stock behaviour |
|---|---|
| Focus | a trace of 80 world units along the view; an interactive device hit by it takes focus |
| Who takes focus | only devices with at least one click handler (221 files). Display-only devices never take focus: no cursor, no hover, weapon stays up |
| Cursor | moved to the hit point each frame; drawn 64 x 64 u, white, untinted, above the finishing stack |
| Cursor art | arrow, visible 26 x 38 u; hand over a clickable window, visible 28 x 34 u |
| Focus hold | 500 ms after the last hit |
| Enter and leave | the device runs its activate and deactivate scripts; the player hears an enter and an exit sound |
| Weapon and crosshair | the weapon lowers; the crosshair is not drawn |
| Click | fire sends button down and up to the device |
| Hidden cursor | 88 devices suppress the cursor outright |

Hover and press:

| Event | Handlers | What changes | Timing |
|---|---|---|---|
| Hover in | 286 | art colour 54%, text colour 50%, fill colour 23%; instant sets in 17% to 18% | 200 ms (614 transitions), 300 ms (335), 250 ms (53) |
| Hover out | 292 | art colour 69%, text colour 59% | 200 ms (701), 300 ms (320) |
| Press | 499 | sends a command 95%, starts a timeline 54%, locks the control 42%, flashes art 26% | 300 ms (542), 200 ms (156), 400 ms (95) |

- Hover brightens and never moves. No hover handler changes a rect. Typical steps: text 60% to 80%
  or 100%; outline 50% to 70% or 100%; white to amber.
- Hover in may be instant; hover out is eased. Keypad keys set `device.hover.plate` at once and fade
  back over 200 ms.
- A press plays a sound, sends the command, disables the control, flashes it to full alpha and fades
  it over 300 ms. A timeline then runs and re-enables input at its end (4,500 ms on the door lock's
  denial sequence).
- 134 of 221 interactive files define hover. Lift call panels and keycard scanners mostly have none.
- A second full-canvas click layer plays the error sound when the action is unavailable.

Button sizes: 73 click targets cover the whole canvas, in 55 files. The rest have a median of
254 x 110 u; heights run 59 u (first quartile), 86 u (median), 233 u (third quartile); the tenth
percentile by area is the 95 x 64 u keypad key. 281 of 499 click windows are the label itself.

Sounds are sent as commands to the game; hover is silent.

| Sound | Uses | Files | Role (inferred) |
|---|---|---|---|
| `guisounds_click` | 308 | 155 | standard press |
| `guisounds_error` | 106 | 61 | denied or unavailable |
| `guisounds_click3`, `guisounds_click1` | 45, 45 | 7, 6 | alternate presses |
| `guisounds_action` | 35 | 16 | process start |
| `guisounds_connect3`, `guisounds_connect2` | 35, 22 | 7, 17 | unlock, access granted |
| `guisounds_line` | 24 | 6 | a text line appears |
| `guisounds_close` | 19 | 11 | panel collapses |
| `guisounds_beep1` | 17 | 7 | machine beep |
| 22 others | 1 to 15 each | | errors, pings, disconnects, arcade |

Game-driven events and parameters:

| Hook | Count | Use |
|---|---|---|
| Trigger | 136 handlers, 126 files | the level flips the device's state (locked to open, alarm on) |
| Per-frame script | 100 files | copies level parameters into text, starts timelines |
| Activate / deactivate | 24 / 18 handlers | player focus gained and lost |
| Release | 20 handlers, 8 files | hold-to-move controls (cranes) |
| Commands to the game | `activate` 307, `changefloor` 53, `setkeyval` 56, `runscript` 16, `turkeyscore` 12, `addhealth` 2 | open, move, select, score, heal |
| Level parameters | slot 1 in 79 files, 2 in 59, 6 in 57, 3 in 42, 5 in 38, 4 in 36 | slots 1 to 5 are display strings; slot 6 names the level script to run; slot 7 gates an action (inferred) |

Replacement rules:

1. Keep the look-and-fire model, the 80-unit reach and the 500 ms hold.
2. Keep which devices take focus. A display-only device never shows a cursor.
3. Keep every hover and press treatment with its stock durations. Never add movement, scale or sound
   to hover.
4. Keep the lock-out during sequences. Input returns when the source timeline says so.
5. Keep whole-canvas targets whole. Do not shrink a full-panel button to its label.
6. The cursor keeps its drawn size of 64 u and is redrawn as vector art; it stays white and above
   the finishing stack.
7. Controller and touch: the cursor follows the view ray as on mouse. Cursor snapping to controls is
   not added. Two aids are allowed: a larger hit slop around partial buttons, and a focus highlight
   that uses the control's own hover treatment when the ray is within the slop.
8. Keep every sound and command at its stock point in the sequence.

### 11.7 Motion

Devices boot, breathe, sequence and loop. 9,533 timed handlers drive 1,576 windows in 351 files;
12,576 transitions run from them.

| Idiom | Pattern | Stock example |
|---|---|---|
| Status pulse | two or three steps that swap alpha or colour, then reset | `Text2`, `guis/controlpanels/securitylock.gui`, 1,200 ms |
| Hover pulse | the hovered plate is replaced by a copy on a 300 ms colour loop | `Background2a`, `guis/doors/doorlock.gui` |
| Response sequence | idle until a click resets it: lock input, expand a plate, stagger lines by 100 ms, hold, collapse, restore, unlock | `AccessDenied`, `guis/doors/doorlock.gui`, 4,500 ms |
| State conversion | started by a trigger: swap rings at 50 ms steps, cross-fade bars in 400 ms, replace the status word | `AccessGranted`, `guis/doors/doorlock.gui` |
| Process | 30 or more steps through read-outs, bars and messages | `Anim`, `guis/controlpanels/airlock_outer.gui`, 6,000 ms |
| Boot | staged lines revealed one by one, ending in a ready state | `guis/delta1/datalink.gui` (94 timed handlers) |
| Screen loop | one window cycling sub-windows | `Anim`, `guis/screens/cpu_top.gui`, 3,900 ms |
| Rolling text | a wide text window moved on a long loop | `TextScrollClip`, `guis/controlpanels/healthstation.gui`, 24,000 ms |

697 timeline windows are idle until a script resets them. 1,035 loops reset themselves, in 300
files.

| Transition duration | Count | | Loop period | Loops |
|---|---|---|---|---|
| under 50 ms | 6 | | under 300 ms | 42 |
| 50 to 150 ms | 964 | | 0.3 to 1.05 s | 439 |
| 150 to 250 ms | 2,303 | | 1.05 to 2.05 s | 321 |
| 250 to 350 ms | 2,744 | | 2 to 4 s | 117 |
| 350 to 550 ms | 4,300 | | 4 to 8 s | 40 |
| 0.55 to 1.05 s | 1,569 | | 8 to 16 s | 54 |
| 1.05 to 2.05 s | 368 | | over 16 s | 22 |
| over 2.05 s | 322 | | | |

The commonest durations are 500 ms (2,910), 300 ms (2,402), 200 ms (2,161), 400 ms (1,360),
1,000 ms (818) and 100 ms (761). The commonest loop is 1,000 ms (210). Transitions change art colour
(7,047), rects (2,499), text colour (2,335) and fill colour (616).

Easing: 86% of transitions (10,756) are linear. The rest use `accel(0.4, 0.6)` (288),
`accel(0, 0.8)` (266), `accel(0.5, 0.5)` (207), `accel(0, 0.6)` (140), `accel(1, 0)` (139) and
`accel(0.2, 0.8)` (105). Expanding plates decelerate (`accel(0, 0.9)` on the door lock's denial
plate, 300 ms); text that fades out and lingers accelerates (`accel(1, 0)`, 1,000 ms on the keypad).

Flicker separates healthy from broken:

| Table | Values | Period | Swing | Used by |
|---|---|---|---|---|
| glare shimmer | 1, 0.92 | 0.33 s | 8% | glass glare |
| rim flicker | 1, 0.85 | 0.4 s | 15% | rim glow; marquee text at 0.5 s |
| static fade | 0.3, 0.2 | 1 s | 33% | static alpha |
| noise flicker | 1, 0.75 | 0.5 s (0.17 to 0.25 s variants) | 25% | static noise colour, light sweeps |
| breathe | 0.75, 0.1 | 1 s (3.3 s on signs) | 87% | wordmarks, status lines, moving arrows |
| broken | 1, 0.2, 0.6, 0.1, 0.8, 0.4 | 2 s | erratic | broken screens |
| demonic | 12 values, 0.3 to 1 | 2 to 3.3 s | erratic | hell faces, corrupted text |

Healthy devices flicker 8% to 33% at 1 to 3 Hz on two-value tables. Broken and demonic devices use
the multi-value tables. That difference alone signals a screen that is wrong.

Rotation and scroll:

| Motion | Rate |
|---|---|
| Cog rings and thin rings 1 to 4 | 66.7, 50, 40 and 33.3 s per turn |
| Cog rings 5 to 8 | 28.6, 25, 22.2 and 20 s per turn |
| Health station circles | 20 s and 10 s per turn |
| Radar spin | 100 s per turn |
| Selector and data spinners | 2.0 s and 0.4 s per turn |
| Line charts | 2.5 s per repeat, leftward |
| Bar strips | 1.7 s and 2.0 s per repeat |
| Light sweeps | 3.3 s, 5.6 s and 0.6 s per repeat, downward |
| Text and hex scroll | 20 s and 10 s per repeat |

Rules:

1. Translate each timeline step for step. Keep durations, staggers, holds and easing fractions.
2. Keep flicker on its stock table and period. Never give a healthy device an erratic table.
3. Reduced motion: state changes, response sequences and process steps remain, because they are
   information. Rect transitions jump to their end values; colour and alpha transitions keep their
   durations.
4. Reduced motion: ring rotation, light sweeps, chart scroll, scan-line scroll, the scan pulse and
   static jitter stop. Flicker tables hold at their mean. Status pulses hold at their bright value.
5. Reduced motion: broken and demonic devices keep a static, visibly damaged frame; they do not
   become healthy.
6. Never add bounce, overshoot or scale. Movement on a device is a plate expanding, a line arriving
   or a mechanism turning.

### 11.8 Surface and legibility

A device canvas is 640 x 480 u, but it is almost never seen at 4:3. It is stretched to its surface,
and surfaces are small.

| Measure | min | 10% | 25% | median | 75% | 90% | max |
|---|---|---|---|---|---|---|---|
| Width (world units) | 2.8 | 8.0 | 10.0 | 14.1 | 20.6 | 30.0 | 305.0 |
| Height (world units) | 2.6 | 6.8 | 8.0 | 12.5 | 17.1 | 21.5 | 109.8 |
| Aspect, width / height | 0.2 | 0.8 | 1.0 | 1.2 | 1.5 | 2.1 | 9.7 |
| Canvas pixel aspect | 0.19 | 0.62 | 0.78 | 0.87 | 1.09 | 1.55 | 7.30 |

| Carrier | Placements | Device surface (world units) |
|---|---|---|
| Brush or patch built in the map | 1,436 | varies |
| Door-side panel model | 243 | 14.1 x 13.6 |
| Modular console | 173 | 25.1 x 17.2, plus two strips of 14.2 x 6.8 and 14.2 x 6.5 |
| Health station | 69 | 19.6 x 17.1 |
| Hanging monitor | 23 | 37.3 x 28.1 |
| Marquee | 24 | 110.8 x 11.4 |

A world unit is about one inch. The standard interactive panel is 14.1 x 13.6 units: the canvas is
squeezed to 78% of its width. Round art becomes a tall ellipse and type is condensed. Stock art is
authored for this. The commonest ambient surfaces are 10 x 8 and 14 x 7 units.

Devices are used within 80 units and read at about arm's length (inferred). Ambient screens are
read across a room or not at all. Device quads are not lit by world lights: a device shows its
authored colours in a dark room, as a dark field with thin bright content.

Legibility on the standard panel: a label at 0.9 is 1.2 units tall, about one eleventh of the panel;
the 0.5 floor is 0.7 units; data dressing at 0.31 is 0.4 units. A 1 px outline is 0.05 to 0.07 units.

Rules:

1. Judge every redraw on its real surface aspect, not on a 4:3 preview. The standard panel is the
   reference: 14.1 x 13.6 units.
2. Keep the stretch. Do not correct circles or type for the surface aspect; the squeeze is part of
   each device's look.
3. Draw the vector geometry at the density the surface has on screen. A panel that fills the view
   gets full-resolution lines; the stock softness of 8 to 128 texel art stretched over 640 u is not
   reproduced as blur.
4. A hairline never falls below one display pixel when the device is in use. At distance, hairlines
   and small type fade with coverage rather than alias; text hinting is off for device surfaces,
   which are seen at arbitrary angles and scales.
5. Keep devices unlit and at their authored brightness. Do not add bloom or exposure to make them
   glow; rim glow and back glow are already in the stack.
6. Never restyle a device to the menu vocabulary. Devices keep rounded slab corners, hairline boxes,
   rings and their own palettes.
7. Keep the carrier stage-free. Bezel, glass and glow stay inside the device.

### 11.9 Rules for device changes

A device translation is a redraw of one product, not an application of a theme.

Keep, per source GUI:

1. Geometry: every window's rect, mirroring and draw order, on the 640 x 480 canvas.
2. Palette: every tint and alpha, including the place tint and back glow of that device.
3. Finishing stack: the layers that device has, in its order, at its strengths.
4. Timelines: every step, duration, easing fraction, stagger, hold and loop period.
5. Sounds and commands: the same sound and the same game command at the same step.
6. Text: face, scale, case, alignment, line breaks and wording.
7. Hooks: trigger, activate, per-frame and release behaviour, and every level parameter slot.
8. Input shape: full-canvas targets, error-catch layers, lock-out windows.

Never:

1. Apply the menu chrome: no chamfered plates, no menu outlines, no menu palette on a device.
2. Add outlines, shadows or glows to text or art that has none.
3. Unify families. A lift is not a door; a caves panel is not a transfer panel.
4. Complete a reduced stack, or strengthen an artefact layer.
5. Add widgets the stock lacks: lists, text entry, sliders, scroll bars.
6. Add hover sounds, hover movement, or cursor snapping.
7. Replace busy-work data with real data, or remove it.
8. Repair a broken or demonic device.
9. Change which devices take focus, or show a cursor on a display-only device.

## 12. Modern interface direction

Sections 2 to 11 fix what must stay recognisably Doom 3. This section defines how the
replacement behaves as a current game interface on the devices the engine can reach:
desktop monitors, televisions, handheld PCs, and phones and tablets. Mouse and
keyboard, controller and touch are equal primary inputs. Everything added here that
the stock never had is drawn in the stock vocabulary, and the divergences listed in
section 2 apply to every new pattern. openD3 has been run on Windows x64 only; the
other platforms are the engine's, and the rules for them are targets.

### 12.1 Principles

1. **Stock identity, current behaviour.** Keep every recognition trait and add
   capability in the same vocabulary: a prompt is a small chamfered box in the hint
   line, a filter is a cycling value, a new panel is a plate that unfolds with a white
   flash.
2. **Every input is primary.** Each screen is complete with mouse and keyboard alone,
   a controller alone, or touch alone. A controller never steers a pointer through the
   menus, and touch never depends on hover.
3. **Focus is light.** While a controller or keyboard is in use, exactly one control
   holds focus, and it wears the hover treatment: the outline at full alpha, the label
   white. Focus never adds a ring, a scale or a new colour.
4. **Adapt, don't shrink.** Layout reflows by size class and viewing distance. A
   desktop composition is never scaled down to fit a phone.
5. **Immediate and interruptible.** Input changes the interface in the next presented
   frame. A construction sequence that is still running retargets or completes at once
   when the player acts; the stock's input locks become at most one frame.
6. **Nothing is lost.** Focus, scroll position, selection and unfinished edits survive
   navigation, device switches, resizing, suspension and resumption.
7. **Dark stays dark.** The interface never raises the scene's brightness to be read.
   Legibility comes from text size, contrast against its own plate and an optional
   backing, never from a brighter theme.
8. **Quiet at rest.** Light and motion mark change and focus. Flicker, scan lines and
   edge glow stay near the threshold of visibility and can be turned off.

### 12.2 Viewing profiles

A viewing profile sets the defaults for scale, target size and presentation. Players'
own interface and text scale choices always override the profile defaults.

| Profile | Devices | Viewing distance | Primary input | Interface / text scale | Minimum target |
| --- | --- | --- | --- | --- | --- |
| Desk | Monitors, laptops | 50 to 80 cm | Mouse and keyboard | 100% / 100% | 30 dp |
| Couch | Televisions | 2 to 3 m | Controller | 150% / 125% | Focus-driven; 40 dp rows |
| Handheld | Steam Deck and similar PCs | 30 to 40 cm | Controller, touch | 125% / 110% | 48 dp for touch |
| Phone | Phones in landscape or portrait | 25 to 35 cm | Touch, controller | 100% / 100% at native density | 48 dp |
| Tablet | Tablets and foldables | 35 to 50 cm | Touch, controller, keyboard | 100% / 100% at native density | 48 dp |

The stock menu sets nearly all of its text at 12 u, an 18 dp em at the reference: about
20 arc-minutes at a desk. The Couch and Handheld defaults bring the same text to 22 to
28 arc-minutes. Stock option rows are 16 u (24 dp) tall on a 23 to 25 u pitch; the
replacement keeps the drawn plate and grows its hit region to the profile's minimum
target, filling the pitch.

### 12.3 Size classes and adaptive structure

Size classes are evaluated on the safe area in dp after the interface scale.

| Class | Condition | Structure |
| --- | --- | --- |
| Compact height | Height below 600 dp, width at least 720 dp | The navigation band keeps its place at the bottom with its three buttons; page plates open above it at full canvas width; the logo yields to an open page as in the stock |
| Compact width | Width below 960 dp | One column. The navigation band's three buttons stack as three sub-menu items above the bottom strip; a page plate spans the width between 12 dp gutters; labels sit above their values |
| Regular | Width 960 to 1439 dp | The stock composition on the centred canvas |
| Expanded | Width 1440 dp and above | The stock composition; frame strips and backdrop reach the view's edges; a detail column may open on the trailing side of a page plate, joined by a bridge stroke |

Compact layouts keep the chamfer sizes, hairlines, type sizes and construction
choreography of the regular layout. They change where a component sits, never how it
is drawn.

### 12.4 Input model, prompts and details

**Modality.** The most recent input device sets the presentation: hover and the
pointer for a mouse, focus and glyph prompts for controller and keyboard, press
feedback and larger hit regions for touch. Switching is immediate and never moves focus
or drops an edit.

**Focus.** Initial focus goes to the screen's primary action, or to the control that
held focus when the screen was last left. Dialogs keep the stock's default: focus
starts on the negative answer. A dialog contains focus and returns it to its invoker.
Navigation is spatial, with authored overrides where the interlocking band or a
staggered list misleads. The navigation band and lists of up to seven items wrap;
scrolling lists do not.

**Hint line.** The stock's hint line (bottom-leading, Bank 0.25, resting at 20%
alpha) stays the one place that explains the control under the pointer or focus. With a
controller or keyboard it rests at 50% and carries the actions the focused control
accepts, each as a glyph and a verb, ahead of the description. It updates in the same
frame as focus and shows at most four actions.

**Values.** A value is still bare text. Left and right step a cycling value; Accept
opens the full list as a sub-menu stack when it has more than seven choices. A slider
steps along its ruler one minor tick at a time and one major tick with the triggers.
Binding capture starts on Accept, shows the stock waiting text and takes the next
input; holding Back for one second cancels, so Back itself can be bound.

**Details.** Every setting can explain itself in the hint line: its description, a
required restart, a performance cost, or why it is unavailable. Nothing is explained
only by a tooltip that needs hover.

### 12.5 Controller

| Control | Menu action |
| --- | --- |
| South face button | Accept |
| East face button | Back; closes dialogs and pages |
| West face button | Secondary: reset to default, delete, refresh |
| North face button | Tertiary: sort, filter, details |
| Bumpers | Previous and next page, tab or category |
| Triggers | Page up and down in lists; coarse slider steps |
| D-pad, left stick | Move focus; left and right change the focused value |
| Right stick | Scroll long text (PDA mail, credits) |
| Menu button | Pause from play; otherwise return to the game |
| View button | PDA in single player; scoreboard in multiplayer |

Glyphs are vector symbols in `text.action`, drawn at the cap height of the text beside
them; their shape and letter carry the identity, and they follow the controller the
platform reports. A keyboard key is a small box with one 5 u chamfered corner, the
sub-menu item at glyph size.

**In game.** The PDA opens on View and behaves as a menu: the bumpers change its tabs,
the D-pad moves through the file list, Accept plays an audio log or a video. At an
in-world device the crosshair stays the device cursor and Fire clicks, as in the stock;
the stick moves the view, not a cursor. The control under the cursor wears its hover
state, and an optional device assist slows the view while the cursor is over a control.
The cursor never snaps (section 11.6).

### 12.6 Touch

- Hit regions are at least 48 dp with 8 dp between neighbours. A drawn piece may be
  smaller; its hit region grows instead.
- Touch-down shows the hover treatment at once; release inside the region acts and
  plays the press flash. There is no hover-only information.
- Lists scroll by drag with the stock scroll bar as an indicator. Sliders drag along
  their ruler; a tap on the ruler steps toward the tap.
- A device screen is used by aiming the view at it and tapping the fire control; a
  direct tap on the device, when the device fills enough of the view to offer 48 dp
  targets, is an optional assist.
- The gameplay overlay's controls are drawn as HUD furniture: hairline outlines in
  `hud.frame`, no fills at rest, a 20% fill while held. It stays out of the bottom
  corners' status frames.

### 12.7 Accessibility baseline

| Need | Rule |
| --- | --- |
| Text size | A text scale of 100 to 200% applies to every family except device screens, which are part of the world. Rows grow with their text; nothing truncates silently |
| Contrast | An optional backing draws a black plate at a chosen opacity behind each text line. The engine's `gui_textBackground` already does this for the stock GUIs |
| Flicker and flashes | A reduce-flashing setting halves the amplitude of furniture flicker and scan-line pulsing, replaces the white construction flash with a fade from 20% and holds damage flashes to one 200 ms pulse. Full-screen changes never exceed three per second |
| Motion | A reduce-motion setting turns geometry transitions into cuts or 100 ms fades (sections 8 and 11.7 list them) and stops backdrop drift; state changes keep their colour transitions |
| Colour-independent state | Locked, open and warning states always differ in text or shape as well as hue. The stock already labels its device states; HUD warnings keep their threshold pulses |
| Subtitles | Caption text uses AN at a size the player sets, on a backing; it never covers the status frames |
| Remapping | Every action is rebindable on every device; the controls page shows conflicts and offers a swap |
| Pointer | The pointer scales with the interface scale; an optional high-contrast pointer adds a 1 dp black edge |

### 12.8 HUD presets

| Preset | Content |
| --- | --- |
| Classic | The stock HUD at stock positions on the centred canvas |
| Remastered | The same pieces anchored to the view's corners (section 10.1) |
| Minimal | Remastered with furniture alpha halved and the frames hidden until a value changes |
| Off | Crosshair and notices only |

Presets change position and visibility. They never change a piece's shape, palette or
type.

### 12.9 Performance and power

The interface is drawn by the retained vector path at display resolution. Idle frames
redraw only what moves: the flicker tables, scan-line pulse and planet. A mobile or
battery profile may drop the scan lines, static and edge glow and cap ambient loops at
30 Hz; it never changes layout or state feedback.

### 12.10 Patterns to avoid

- A pointer driven by a stick in menus.
- Focus rings, scaled focus, or a focus colour outside the family palette.
- Toasts, snack bars, cards or sheets from a platform toolkit.
- Icons standing in for the stock's text labels.
- A light theme, or a "high contrast" theme that recolours the chrome.
- Blur of the scene behind a plate. The stock dims; it never blurs.
- Smooth scaling of a whole stock screen into a small window.
- Hover sounds, haptics on focus movement, or sound on the hint line.

## 13. Project branding

The interface is Doom 3's; openD3 signs it in small type.

- **Name.** The project is written openD3: lower-case "open", upper-case "D3". It
  never borrows the game's logo, and the game's logo is never redrawn or recoloured.
- **Where it appears.** The console's version line (bottom-trailing, in the console's
  own text colour), the window title, and one line in the front end's copyright row
  (Bank 0.20 at 30%, the stock row's own style). It does not appear on the title
  screen's composition, in the HUD or on any device.
- **Engine pages.** Screens the stock never had (renderer settings, controller and
  accessibility pages, content checks) are ordinary menu pages in the menu vocabulary.
  They carry no openD3 badge; the hint line may say that a setting is an openD3
  addition.
- **Colour.** openD3 has no brand colour inside the game. Documentation and the atlas
  page use the menu palette.

## 14. The Interface Atlas

The [Interface Atlas](ui/atlas/opend3-interface-atlas.html) is a single HTML page that
draws this specification: every token, the type ramp, the furniture, the interaction
states, the construction choreography, the HUD, the PDA, the device vocabulary, the
multiplayer screens and the loading screen, each as vector artwork built from the
numbers here. It is the fastest way to check a component against the contract.

- **Independently authored.** Every figure in the atlas is drawn from measurements.
  The page contains no retail art, no captures and no retail font data. Where the
  stock shows real imagery (the planet, the logo, level pictures) the atlas draws a
  labelled stand-in.
- **The real faces.** Text in the atlas is set in openD3's TrueType faces, embedded in
  the page as subsets by `tools/assets/fonts/embed_atlas_fonts.py`. Rebuild the faces,
  run the script, and the atlas shows what the engine ships.
- **Units.** Figures are drawn on the 640x480 canvas at a stated scale; captions give
  values in u and dp with the token names used in this document.
- **Live states.** Controls in the atlas respond to pointer, keyboard focus and touch
  with the measured timings, and the page honours the reduced-motion preference in the
  way section 8 prescribes.
- **Keeping it current.** A change to a token, a size or a timing in this document
  changes the atlas in the same commit. The atlas's own change list names the
  specification version it draws.

## Appendix A. Survey method

Version 1.0 surveyed the effective retail files of the Steam release of Doom 3
(archives `pak000` to `pak008`), and the two interface files Resurrection of Evil's
patch archive replaces. The expansion's base archive was not available, so its own art
was not measured.

| Subject | Sources | Measured |
| --- | --- | --- |
| Front end | `guis/mainmenu.gui` (1,798 windows), `msg.gui`, `restart.gui`, `netmenu.gui`, `intro.gui`, `credits.gui`, `gameover.gui` | Composition, backdrop stack, palette and type census, furniture geometry, state changes, 3,995 transitions and 445 timeline keys, sounds |
| HUD and PDA | `guis/hud.gui`, `guis/cursor.gui`, `guis/pda.gui`, `guis/weapons/*.gui`, the weapon and item definitions, the game's HUD and view code | Element rectangles and drivers, palette, type, frame outlines, timings, overlays drawn outside the GUI |
| Devices | 457 GUIs under `guis/<level or family>/` and their 2,605 placements in the retail maps | Family census, the finishing stack, frame kits, palette and type census, interaction and motion statistics, panel sizes |
| Multiplayer, loading, console | `guis/mpmain.gui`, `mphud.gui`, `scoreboard.gui`, `chat.gui`, `guis/map/*.gui`, the console and session code | Composition, palette, type, open sequences, progress semantics, cell metrics |
| Fonts | The four faces under `fonts/english/` at 12, 24 and 48 point; `textures/bigchars.tga` | Coverage, metrics from glyph ink, the differences between the three sizes, usage across 521 GUIs |

Method:

- A parser for the GUI script language produced window trees with rectangles, colours,
  text and events, with `#include` files tokenised in place. Censuses of colours, fonts,
  scales, transitions and sounds were scripted over whole files and families.
- Material names were resolved against the `.mtr` declarations for blend, tint,
  scroll, rotation and table-driven flicker; an image named without a material is an
  alpha-blended, tinted, clamped stage.
- Textures were measured for visible bounds, per-row opaque spans, line and glow
  profiles and median and peak colour, and their proportions scaled by the drawn
  rectangle.
- Engine semantics (atlas selection, transition easing, table lookup, list and choice
  drawing, cursor size, focus tracing) were read from id Software's GPL source and from
  openD3's own.
- Nothing was measured from a running game. Values derived from engine semantics
  rather than read from a file are marked as inferred where they appear.

The extracted files, measurement scripts, contact sheets and findings are local working
material and are not tracked. The numbers in this document are the record.

## Appendix B. Measured furniture

Texel measurements of the stock furniture, collected in one place. Proportions are what
the replacement reproduces; a texel count applies only at the stock's drawn size.

### B.1 Menus

All tiles are white with the shape in alpha, drawn with straight alpha and tinted by the window,
except `boxframe` (pale blue) and `bg1` to `bg3` (steel-blue band). Geometry is in fractions of the
tile, x toward trailing, y down. "Drawn" gives one representative stock rect.

| Tile | Size | Drawn (u) | Measured geometry |
| --- | --- | --- | --- |
| `button_edge` | 32 x 32 | 27, 410, 32, 32 | opaque y 0.156 to 0.812; flush trailing; leading edge from (0.22, 0.156) to (0.81, 0.81) |
| `button_middle` | 8 x 32 | 59, 410, 150, 32 | opaque band y 0.156 to 0.812 |
| `buttong_edge` | 32 x 32 | as `button_edge` | 1 px line on the top (y 0.156), slant and bottom (y 0.78); falloff 24, 18, 12, 6% over 4 px each side |
| `buttong_middle` | 8 x 32 | as `button_middle` | lines at rows 5 and 25 with the same falloff |
| `buttong_edge2` | 32 x 32 | 0, 9, 32, 32 | the outline mirrored vertically with a 40% fill: browser header tabs |
| `button_cornerangle` | 16 x 32 | 117, 346, 16, 32 | opaque x 0 to 0.62, y 0.19 to 0.78; 5 px top-trailing chamfer |
| `button_corneranglesm` | 16 x 32 | one use | as above, slightly shorter (seen, not measured) |
| `buttong_cornersquare` | 16 x 32 | -1, 346, 16, 32 | vertical line at x 0.25; lines at rows 6 and 24; falloff outward |
| `buttong_middlesm` | 8 x 32 | 15, 346, 102, 32 | lines at rows 6 and 24 |
| `buttong_cornerangle` | 16 x 32 | 117, 346, 16, 32 | top line to x 0.31, chamfer to (0.59, 0.34), vertical at x 0.59, bottom line at row 24 |
| `buttong_cornersquare2`, `buttong_middlesm2`, `buttong_cornerangle2` | 16 x 32, 8 x 32, 16 x 32 | 0, 0, 16, 32; 16, 0, 160, 32; 176, 0, 16, 32 | lines at rows 7 and 22; interior 40% rising to 53% at the lines |
| `button_largeangle0`, `button_largeangle1` | 32 x 32 | 1, 440, 32, 32; 165, 440, 32, 32 | top 75% filled; one end cut by a diagonal from (0.06, 0.16) to (0.62, 0.72), mirrored for `1` |
| `button_smallangle0` | 16 x 16 | 14, 408, -16, 16 | filled; 7 px top-leading chamfer |
| `button_smallangle1` | 8 x 16 | 2, 408, -8, 16 | filled x 0 to 0.875; top corner clipped 2 px |
| `select_edge`, `select_border`, `select_angle` | 8 x 16 | 0, 0, 8, 16; 8, 0, 304, 16; 312, 0, 8, 16 | 60% fill; rim 73% then 87 to 100%; `select_angle` has a 5 px top-trailing chamfer |
| `select_boxcorner`, `select_boxborderh`, `select_boxborderv`, `select_boxangle`, `select_boxcorner2` | 8 x 8 | 8 u pieces | the same rim around a box; one 5 px chamfer; one inner diagonal |
| `slider_bg` | 128 x 16 | 210, 4, 128, 16 | only 71 x 9 px used: major ticks every 10 px, heights 2 to 9 px; minor ticks at 5 px, 30%; baseline 7 to 20% |
| `slider_bar` | 4 x 8 | at image size | 1 px solid outline, 40% centre |
| `border_small` | 16 x 16 | 0, -1, 542, 16 | rows 0 to 11 at 60%, rows 12 to 15 at 100% |
| `border_corner` | 128 x 128 | 542, -1, 128, 128 | top 12.5% full width; below, filled trailing of a boundary from (0.41, 0.125) by a concave arc to (0.68, 0.22), then 45 degrees to (0.98, 0.52); 60% fill, bright boundary line about 3 px (seen, not profiled) |
| `borderb_corner2` | 32 x 32 | 0, 436, 32, 32 | triangle under a line from (0, 0.34) to (0.62, 1.0) |
| `borderb_angle` | 32 x 32 | 365, 448, 32, 32 | full below y 0.625; above, filled trailing of a rise from (0.25, 0.56) to (0.72, 0.09) |
| `borderb_angle2` | 32 x 32 | 364, 432, 32, 32 | band y 0.25 to 0.47; below, filled leading of a line from (0.62, 0.5) to (0.12, 1.0) |
| `content_smallcorner` | 32 x 32 | 161, 185, -32, -32 | filled; one corner cut from (1.0, 0.31) to (0.31, 1.0): 22 px legs |
| `content_corner` | 32 x 32 | 387, 185, -32, -32 | filled on one side of the tile diagonal: 32 px legs |
| `content_angle` | 32 x 32 | 222, 355, 32, 32 | full above y 0.53; below, filled leading of a line from (0.69, 0.53) to (0.25, 1.0) |
| `cframe_small`, `cframe_small2` | 16 x 16 | 7 to 16 u | right triangles: upper-leading half, lower-trailing half |
| `cframe_medium` | 64 x 64 | 138, 359, 64, 64 | polygon (0, 0) (0.2, 0) (0.7, 0.5) (1, 0.5) (1, 0.7) (0, 0.7) |
| `cframe_large`, `cframe_large2` | 128 x 128 | 31, 231, 128, 128 | slab y 0.34 to 0.81 with a leading diagonal from (0.45, 0.34) to (0.01, 0.81) and a 12 px stem from x 0.84 to 0.93 down to the tile bottom; `2` mirrored |
| `content_glow`, `content_glow2` | 256 x 256 | 164, 187, 340, 279 | soft white light in the top-leading corner, gone by about half the tile (seen, not profiled) |
| `boxframe` | 256 x 256 | 66, 74, 256, 256 and mirrored at 322, 74 | #99CCFF 1 px line with falloff 24, 18, 12, 6%; vertical side at x 0.27 from y 0.31 to 0.70; 45 degree chamfers of about 25 px; horizontal runs at y 0.20 and 0.80 to the tile edge |
| `bg1`, `bg2`, `bg3` | 32 x 64 | credits bars | black with a steel-blue band and one 45 degree step |
| `outerglowbar` | 128 x 128 | -30, -20, 700, 520 | additive: 1 px white line 1 px inside each edge, then 8 px falloff (106, 90, 75, 61, 46, 30, 15, 5 of 255) |
| `guicursor_arrow` | 32 x 32 | at the pointer | arrow in the top-leading 12 x 17 px |
| `scrollbarv`, `scrollbar_thumb` (engine list default) | 16 x 16 | 16 u gutter | flat white 17%; 12 x 12 px opaque square inset 2 px, #6E9499 |

### B.2 HUD and PDA

Stock bitmaps are stretched to their rect without preserving aspect. Geometry is given in texels of
the tile, measured where alpha is at least half. HUD panel tiles are drawn 1:1.

| Piece | Stock art | Tile | Drawn rect (u) | Measured geometry |
| --- | --- | --- | --- | --- |
| Plate frame | `hud/mp/lborder1a` | 256x64 | 0, 416, 256, 64 | Bounds x 6–149, y 22–51. Top edge y 22 from x 71 to 146; step to y 24 at x 68–71; leading edge 12, 26 to 6, 40; chamfer 6, 44 to 13, 50; bottom y 50–51; trailing edge 137, 50 to 149, 25. Stroke 3 (sides), 2 (top, bottom); glow 3 |
| Ammunition frame | `hud/mp/lborder1a1` | 256x64 | 384, 416, −256, 64 | As above, bounds x 6–129 |
| Grenade frame | `hud/mp/lborder1c` | 256x64 | 384, 416, −256, 64 | Bounds x 6–76, y 25–50; plain top |
| Plate fill | `hud/mp/lbg1`, `lbg1a1` | 256x64 | as the frames | Bounds x 10–144 (124), y 26–47; step at x 72 |
| Health box | `hud/mp/llines21` | 256x64 | 0, 416, 256, 64 | Bounds x 68–143, y 27–46; corner cut 68, 35 to 73, 27; trailing edge 143, 27 to 135, 46; fill at half alpha; pictogram x 70–85, y 29–43 |
| Clip box | `hud/mp/llines2a1` | 256x64 | mirrored | Bounds x 68–123, y 27–46 |
| Armour box | `hud/mp/llines11` | 256x64 | 0, 416, 256, 64 | Bounds x 11–70, y 30–46; leading edge 17, 30 to 12, 41; pictogram x 18–28, y 34–41 |
| Reserve boxes | `hud/mp/llines1a1`, `llines1a2` | 256x64 | mirrored | As armour; grenade variant trailing edge 70, 30 to 62, 45 |
| Stamina / pip-row frame | `hud/mp/lborder1b` | 256x64 | 4, 416, 270, 64; 399, 416, −241, 64 | Bounds x 2–125, y 53–62; tip at 2, 57; trailing end 125, 55 to 121, 61 |
| Bar fill | `hud/mp/lstafill1` | 128x64 | 133 x 54 at 5, 425; 95 x 90 for oxygen | Bounds x 4–123, y 55–60; top row x 8–121, bottom row x 6–119 |
| Side panel | `hud/mp/rborder`, `rbg` | 128x64 | 0, 0, 128, −64 in the panel | Frame x 14–121, y 32–61: top x 14–110, bottom x 25–121; plate x 20–115, y 36–57 |
| Weapon pip | `hud/weapons` | 16x8 | 10 x 6 | Pill x 2–13, y 1–6 |
| Crosshair | `common/crosshaircenter`, `crosshaircenter2`, `crosshairlight`, `crosshairframe` | 32x32 | 32 x 32 at 304, 224 | Dot x 14–17; ring r 5.5; arcs r 8.5; circle r 11 |
| Crosshair side bar | `common/crosshairframe2` | 64x32 | 64 x 32 at +18 | Bounds x 2–57, y 16–27 |
| Notice panel | `pda/pb2_c`, `pb2_tb` | 32x128 | corner 14–32 wide, edge stretched | Fill below y 25; edge line y 22–25; corner cut 2 |
| Info box | `pda/ib_c2`, `ib_m`, `ib_s`, `ib_m2` | 32x32 | corner 32, edges stretched | Stroke 4 (top y 22–26, side x 4–8); chamfer x 25–29, y 22–27 |
| Main frame corner | `pda/pb1_tla` over `pb1_tlb` | 128x128 | 128 x 128 | Top bar y 5–14 from x 24; inset tab x 97–119; leading bar x 19–28 to y 97, hairline x 27–28 below; backing from x 28, y 14 |
| Main frame edges | `pda/pb1_ta`, `pb1_ba`, `pb1_bla` | 32x128, 32x32, 128x32 | stretched | Top line y 13; bottom line y 20–21; corner cut at 29–31, 18–20 |
| File header box | `pda/pb1_box1a`, `pb1_box2a` | 128x32, 16x32 | 144 x 32 at 0, 119 | Line y 4–5; lower band y 22–29 for x 0–61, hairline beyond |
| Top band | `pda/bordertop1`, `2`, `3` | 32x64 | 377, 32, 231 wide x 64 | Depth 12, diagonal x 10 at y 16 to x 26 at y 32, depth 33 |
| Bottom band | `pda/borderbtm1`, `2`, `3` | 32x64 | 217, 32, 391 wide x 64 | From y 12; step to y 19 across x 14–23; from y 19 |
| Tab button | `pda/nbutton` | 256x32 | 256 x 32 | Bar x 0–237, y 8–24; body y 8–20, underline y 21–24 |
| Active-tab bar | `pda/hlight` | 128x16 | 128 x 16 | y 2–14; alpha ramps x 14–45 |
| Play, stop | `pda/play`, `pda/stop` | 64x16 | 64 x 16 | Capsule x 1–57, y 1–15; glyph x 6–13 |
| Close | `pda/close` | 64x16 | 64 x 16 | Tab x 13–55, y 2–15 |
| Weapon slots | `hud/icons/weaplargeclip`, `weapsmallclip` | 128x64, 64x64 | 80 x 40, 40 x 40 | 1 px outline on the tile edge |
| Device cursor | `ui/assets/guicursor_arrow` | 32x32 | on the surface | Arrow x 0–13, y 0–19 |

### B.3 Devices

Bitmaps are stretched to their rects; read texel counts as fractions of the tile. All pieces are
white, alpha-shaped and drawn with straight alpha unless noted.

| Texture | Tile | Measured geometry | Where used |
|---|---|---|---|
| `guis/assets/common/outershadow` | 128 x 128 | black; clear border texel, then alpha 152, 93, 46, 16 inward; centre 118 texels clear | bezel shadow, 400 files |
| `guis/assets/common/outerglow` | 128 x 128 | clear border texel, then alpha 95 falling to 0 over 27 texels | rim glow, 266 files |
| `guis/assets/common/addhighlight` | 128 x 128 | additive; luminance 37 at the top falling to 0 at row 88; flat across | top highlight, 373 files |
| `guis/assets/common/outerglowbar` | 128 x 128 | additive; full-alpha hairline at texel 1, then 120 falling to 12 over 9 texels | alert rim, 73 files |
| `guis/assets/test/gui_scanlines5`, `gui_scanlines` | 128 x 128 | additive; every third row luminance 25 (2 in the older texture) | scan lines, 263 and 113 layers; tiled 2 times vertically in 182 layers, 1.5 times in 133 |
| `guis/assets/smdoor/reflect1` | 64 x 64 | alpha 3, 25, 73, 149 rising to 190 at rows 6 to 7, falling about 14 per row to 0 by row 22; faint band 26 to 39 at rows 58 to 60; 3-texel soft ends | glare, 298 layers |
| `guis/assets/test/mask` | 64 x 64 | black; alpha 200 at edge midpoints, 8 at the centre | vignette, 117 files |
| `guis/assets/cpuserver/bglow` | 64 x 64 | alpha 255 over the central 9 texels, 59 at an edge midpoint, 5 at corners | back glow, 285 files |
| `guis/assets/common/dirt4` (and 1, 2, 3, 5, 7) | 128 x 128 | black; coverage 46%, peak alpha 135; others peak 186 to 225, coverage 14% to 52% | dirt, 288 files |
| `guis/assets/common/titlebar_mid`, `_corner`, `_edge` | 16 x 16 | body: solid rows 3 to 12. Corner cap: the slab ending at column 12, top outer corner rounded over 5 texels, bottom square. Edge cap: the slab starting at column 3, square | title slab, 115 files |
| `guis/assets/common/1pxborder_vert`, `_horiz`, `_cornersm` | 32 x 16 | straights: one column at x = 2; one row at y = 12. Corner: column at x = 2 for 8 rows, quarter arc over 5 x 5 texels, row at y = 13 | hairline box, 73 files (corner 352 uses) |
| `guis/assets/common/btn_2pxborder_*` | 32 x 16 | outline 2 texels, clear gap 2 texels, fill at alpha 119 | button outline, 119 files |
| `guis/assets/common/scibox/g_horiz`, `g_vert`, `g_cornerround2` | 8 x 16, 16 x 8, 16 x 16 | straights: alpha 68, 255, 187, 187, 255, 68, then 51, 17. Corner: the same band through a corner of 4 to 5 texels | double-line frame, 64 files |
| `guis/assets/common/scibox/fillleft`, `fillcenter`, `fillright` | 8 x 16 | solid bar over rows 3 to 11 with a rounded end | capsule bars |
| `guis/assets/common/scibox/bg2` | 8 x 128 | gradient, black for rows 0 to 40 then to `#0D345C` | plate behind double-line frames |
| `guis/assets/common/glowborder_*` | 32 x 8, 8 x 32, 32 x 32 | two rails at 60% with a 40% fill, about 6 texels wide, soft feather | glow frame, 14 files |
| `guis/assets/doors/adminbg` | 256 x 128 | heavy bar across the top (about 3/16 of the height) and down one side (about 1/16 of the width); faint hairline on the other sides | L-bracket, 73 files |
| `guis/assets/caverns/boxc`, `boxh`, `boxv`; `corner`, `verta`, `tbarc` | 8 x 8; 16 x 16, 16 x 16, 16 x 32 | blocks: solid 6 x 6, 8 x 6, 6 x 8. Frame: baked colour, mean `#5A735A`, `#698269`, `#47744B`; peak `#96AF96` | caves kit, 46 files |
| `guis/assets/airlock/inbtn` | 256 x 64 | visible rows 4 to 37: one full row, then about half alpha; soft ends | pill bar, 31 files |
| `guis/assets/teleporter/button1`, `button2` | 64 x 32 | solid rounded rectangle with a 2-texel margin; its outline only | pill button, 27 files |
| `guis/assets/cpuserver/bgwhite4`, `bgwhitesmall` | 64 x 32, 16 x 8 | plain `#EEEEEE` rectangle with a soft 1 to 2 texel margin | flat plate; 386 uses in 113 files, 361 in 27 |
| `guis/assets/cpuserver/bg` | 64 x 64 | `#111111`, opaque, soft border texel | tube face |
| `guis/assets/common/securitybg` | 256 x 256 | toothed octagonal outline, visible from 15 to 241 | cog rings |
| `guis/assets/common/mlogo` | 128 x 128 | crest, visible 2, 3 to 126, 126; peak alpha 234 | 84 windows in 56 files |
| `guis/assets/elevator/callfloorbg`, `_g` | 128 x 64 | baked colour: mean `#2E1D06`, peak `#684006`; grey twin mean `#212121` | lift slabs, 31 files |
| `guis/assets/common/btn_yellow` | 64 x 64 | baked colour: mean `#FFA036`, peak alpha 214 | floor-button plate |
| `guis/assets/camera/bgc` | 128 x 128 | baked colour: mean `#431F12`, peak `#B7AF82` | camera and keycard plate |
| `guis/assets/common/pentagramfx` | 256 x 256 | baked colour: mean `#652100`, peak `#FFFF00` | hell devices |
| `ui/assets/guicursor_arrow`, `guicursor_hand` | 32 x 32 | visible 13 x 19 and 14 x 17 texels, anchored top-left | device cursor, drawn 64 x 64 u |

### B.4 Multiplayer and loading

All pieces are white with the shape in alpha, tinted and drawn with straight alpha, unless noted.
Coordinates are texels from the top-left corner of the tile.

| Texture | Tile | Drawn rect (u) | Measured geometry |
| --- | --- | --- | --- |
| `hud/mp/score_horiz` | 8 x 8 | 8 thick, any length | A horizontal line: rows 2-3 solid, rows 1 and 4 at 20%, rows 0 and 5 at 7%, rows 6-7 empty |
| `hud/mp/score_vert` | 8 x 8 | 8 thick, any length | The same line upright: columns 4-5 solid, 3 and 6 at 20%, 2 and 7 at 7% |
| `hud/mp/score_corner` | 8 x 8 | 8 x 8, mirrored for the other corners | Joins the horizontal run at rows 2-3 to the upright run at columns 4-5 through a quarter turn of about 3 texels radius |
| `hud/mp/lborder1a` | 256 x 64 | 0, 426, 256, 64 | Status plate outline, 2-3 texels wide, 3 texel soft edge; ink x 4-150, y 20-52 |
| `hud/mp/lbg1` | 256 x 64 | same | Status plate fill; x 10-144, y 26-46 |
| `hud/mp/llines11` | 256 x 64 | same | Armour cell outline, 1 texel; x 11-70, y 30-45 |
| `hud/mp/llines21` | 256 x 64 | same | Health cell outline, 1 texel, with tick marks at x 72-85; x 68-143, y 27-45 |
| `hud/mp/rborder` | 128 x 64 | 512, 416, 128, 64 | Ammunition plate outline: top y 32 from x 14 to 110; leading edge 14, 32 to 25, 60; trailing edge 110, 32 to 121, 60 |
| `hud/mp/rbg` | 128 x 64 | same | Ammunition plate fill; x 20-115, y 36-56 |
| `hud/mp/lag` | 32 x 32 | 5, 5, 32, 32 | A ring, ink 9-91% of the tile, crossed by a thick diagonal bolt |
| `mainmenu/button_middle` | 8 x 32 | strip body, 27 high | Solid on rows 5-25 |
| `mainmenu/button_edge` | 32 x 32 | 22 x 27 | The same band ending in a straight diagonal from x 7 on its top row to x 25 on its bottom row |
| `mainmenu/buttong_middle` (ends: `buttong_edge`, the same line on the diagonal) | 8 x 32 | strip body | Two 1 texel lines at rows 5 and 25, each with a 4 texel halo at 24 / 18 / 12 / 6% |
| `mainmenu/borderb_corner2` | 32 x 32 | 27 x 26 | A filled right triangle, hypotenuse from 0, 11 to 20, 31, with a 3 texel soft edge |
| `splash/loadborder` | 256 x 16 | 2, 18, 256, 16 | Hollow frame, ink x 3-172, y 4-12: light row over dark row at top and bottom, a dark and a teal column at each end |
| `splash/load` | 256 x 16 | same, clipped | Solid bar, ink x 4-171, y 5-11, uniform along its length, seven colour rows |
| `splash/titlebar` | 512 x 16 | 0, 371, 512, 19 | White; solid to x 370, faded out by x 473 |
| `mainmenu/bg1` | 32 x 64 | band, 64 high | Black from row 9; rows 0-8 #40586F rising from 2% to 67% |
| `mainmenu/bg3` | 32 x 64 | band, 64 high | As `bg1`, 13 rows lower |
| `mainmenu/bg2` | 32 x 64 | 32 x 64 | Joins `bg1` to `bg3` with a 45 degree ramp about 12 texels wide, starting a quarter of the way across |
| `mainmenu/bg4` | 16 x 128 | 0, 352, 642, 128 | Vertical alpha ramp, half strength at 39% of its height; tinted black |
| `mainmenu/textflare` | 16 x 16 | 54 x 21 | Soft grey blob, core 9 x 9, slightly above centre; additive |
| `splash/<map>` | 512 x 512, opaque | 0, 0, 640, 480 | Level pictures; mean luma 8-48 of 255 |

## Appendix C. Observations recorded during the survey

These are facts about the stock data that a translator will meet. Each says what the
replacement does about it. They are not rules.

### C.1 Exceptions to the identity rules

The rules of section 2 describe the stock closely, not perfectly. The stock's own
exceptions are kept where they are and extended nowhere.

- **Movement on hover.** The navigation button's inner plate shrinks from its cell to
  an inset rectangle over 300 ms on hover, and the other navigation buttons move and
  narrow when a page opens. These are the only geometric state changes in the menus.
- **A hover sound.** The death screen pings on hover. The front end and dialogs do not.
- **Curves.** The top bar's flare has one concave arc; device title slabs have one
  rounded corner and device outlines small radii; weapon pips have a 1 u radius; the
  crosshair and the PDA's rings are circles.
- **Warm chrome.** The server browser marks its sorted column with a dark red well.
- **No construction.** Engine message boxes appear in one frame and play no sound.
- **Text shadows.** 22 of 2,989 device text windows and five HUD windows use the
  engine's shadow; HUD digits otherwise use a hand-placed black copy.

### C.2 Front end

- **Centring by spaces.** Many button strings begin with 1 to 11 spaces, and the bind
  category strings end with three, in place of alignment. The replacement aligns the
  text and ignores leading and trailing spaces in those strings.
- **Layers that never show.** Two gradient washes, a scan pulse, the grid's fade-in and
  fade-out, an introduction caption with its flare, a second logo and a top hint line
  are authored and never visible. The replacement omits them.
- **Releases that start elsewhere.** Two hover-out transitions start from a value the
  hover never reached (the OPTIONS tab from 30% against 35%; footer links from
  `#CCF2FF`). The replacement releases from the current value.
- **Off centre by intent.** The logo sits 20 u right of the canvas centre. It stays.
- **Leftovers.** `guis/intro.gui` and `guis/gameover.gui` carry placeholder styling;
  whether the retail game reaches them was not determined.
- **Resurrection of Evil.** Its main menu is the base file plus a subtitle under the
  logo, a second logo video, a different halo, eight skin swatches at a 35 u pitch and
  two more dialogs of the standard shell. Chrome, palette, type and timings are
  unchanged. The expansion's own art was not available to measure.

### C.3 HUD and PDA

- **Unreachable work.** A HUD "twitch" animation, a reload prompt and an ammunition
  type icon are authored and never started. The replacement does not implement them.
- **Remnants.** The health script addresses windows of a heart-rate display that no
  longer exist; the game still sends a heart rate that nothing draws.
- **Icons that do not exist.** The weapon definitions name per-weapon HUD icons of
  which one exists, a boxed text placeholder. The HUD shows pips, not icons.
- **Clipped notice.** The objective box is authored 16 u wider than the canvas and is
  clipped at the trailing edge. Classic keeps the clip; Remastered anchors the box to
  the trailing edge whole.
- **No closing animation.** The PDA opens over about 850 ms and closes in one frame.
- **Not measured.** The colours of the damage, tunnel-vision, berserk and BFG overlay
  images, and which scroll-bar art the PDA's lists resolve to.

### C.4 Devices

- **Weak artefacts.** Scan lines add about 2.5 of 255 per line and static sits at 2 to
  4% alpha. The look is the sum of many faint layers; no one of them may be raised.
- **Mostly not interactive.** 65% of placements are display-only loops, and 87 of the
  221 interactive devices have no hover state.
- **A squeezed canvas.** The standard interactive panel is nearly square, so the 4:3
  canvas is seen at 78% of its width. Device art was drawn for that squeeze.
- **Uneven keys.** Two keys of one keypad are 95 u wide beside eight at 96 u. The
  replacement draws all ten at 96 u at the stock positions.
- **A one-texel step.** The straight outline piece sits one texel above the corner
  piece, and stock rectangles compensate. The replacement joins them exactly.
- **Formally interactive signs.** One sign carries an empty click handler. Signs are
  display-only.
- **Placeholders.** A developer signature at scale 0.1, placeholder text and
  level-designer help text remain in a few devices. They stay shown or hidden as the
  stock has them.
- **Strays.** 35 click windows have no area; 11 device files are placed by no retail
  map; one material names a device GUI that does not exist.

### C.5 Multiplayer, loading and console

- **Four rows.** The scoreboard GUI has four player rows; the game fills one per
  client. The replacement's rows follow the client count (section 10.12).
- **Dead references.** The multiplayer HUD declares a pickup panel that is never
  raised and addresses several windows it does not contain.
- **No hover on filled buttons.** The multiplayer menu's filled buttons have no hover
  or pressed look; one link piece is flipped on the wrong axis; the tab strip's leading
  end is drawn off screen.
- **Unshown text.** One loading screen declares a title, subtitle and briefing its
  timeline never shows; one carries another level's title.
- **Unclamped progress.** Loading progress is not clamped and the bar is full at 0.983.
  The replacement clamps to 0 and 1.
- **A cut-off fade.** The spectator line's 800 ms fade is interrupted at 500 ms.

### C.6 Fonts and text

- **Three designs per face.** The 12, 24 and 48 point atlases are separate hinted
  renders: small text is wider, lighter or heavier than a rescale of large text
  (section 5). The TrueType faces are traced from the 48 point atlases and fitted to
  each slot's line height, glyph tops and advances.
- **The small-slot limit.** The stock draws scales up to 0.30 from the 12 point atlas.
  openD3 inherited a limit of 0.10 from its upstream; version 1.0 of this document
  comes with the limit restored to 0.30.
- **Boxes.** Codes 127 to 159 of every GUI face draw the missing-glyph box, so a curly
  quote or an ellipsis in a string drew a box. The TrueType faces draw the characters.
- **The Default face** is identified in its atlas only by an internal name; the
  typeface behind it was not determined. Bank is Bank Gothic Medium and AN is Arial
  Narrow by name and design; Micro is of the Microgramma and Eurostile Bold Extended
  kind by design.

## Appendix D. Change record

### Version 1.0, 11 November 2026

First version. Records the survey of the retail front end, HUD, PDA, weapon displays,
457 device GUIs, multiplayer screens, loading screens, console and fonts; defines the
tokens, geometry, states, motion and sound of each family and the Classic and
Remastered layouts; adds the modern interface direction, the branding rules and the
Interface Atlas. Ships with the five reconstructed TrueType faces as the default text
path and with the 12 point slot limit restored to Doom 3's 0.30.
