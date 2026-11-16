# Capitol Hill Crawler Portrait Asset Checklist

Use this document as a build checklist for final portrait and sprite assets.

## Folder Audit (August 13, 2026)

- The files marked complete below are present in `public/assets/portraits/`.
- The current portrait files are `1024 x 1024` RGB PNGs. They are not yet transparent, pixel-sized exports, so the applicable export rules remain open.
- Visual requirements and the "no baked text" rule require a visual review and remain open.

## Export Rules

- [ ] Export every portrait as a transparent PNG.
- [ ] Use `48 x 48` pixels when possible.
- [ ] `96 x 96` pixels is acceptable if every expression for that character uses the same size.
- [x] Export one expression per file.
- [x] Use lowercase kebab-case filenames exactly as listed.
- [ ] Do not bake names or dialogue text into portrait images.

## President Anthony J. DiSantis

Visual requirements:

- [ ] Bald
- [ ] Black-framed glasses
- [ ] Neatly kept beard
- [ ] Navy suit
- [ ] Bright patterned tie
- [ ] Freemason lapel pin

Portrait files:

- [x] `president-disantis-neutral.png`
- [x] `president-disantis-pleased.png`
- [x] `president-disantis-thoughtful.png`
- [x] `president-disantis-concerned.png`
- [ ] `president-disantis-grin.png`

## Sutton DiSantis

Visual requirements:

- [ ] Brunette hair
- [ ] Girly, age-appropriate outfit
- [ ] Bow, headband, or another bright hair accessory

Portrait files:

- [x] `sutton-disantis-neutral.png`
- [x] `sutton-disantis-pleased.png`
- [x] `sutton-disantis-excited.png`
- [x] `sutton-disantis-concerned.png`

## Mr. Ben Venello

Visual requirements:

- [ ] Bald
- [ ] Beard
- [ ] No glasses
- [ ] Quieter professional suit than President DiSantis
- [ ] House staff or visitor lapel badge

Portrait files:

- [x] `ben-venello-welcoming.png`
- [x] `ben-venello-thoughtful.png`
- [x] `ben-venello-encouraging.png`
- [x] `ben-venello-concerned.png`

## Abner Mendoza, Press Secretary

Visual requirements:

- [ ] Distinct professional White House Press Secretary appearance
- [ ] Clearly different from Ben Venello and President DiSantis
- [ ] Optional press badge, briefing folder, or subtle earpiece

Portrait files:

- [x] `abner-mendoza-neutral.png`
- [x] `abner-mendoza-thoughtful.png`
- [x] `abner-mendoza-concerned.png`
- [x] `abner-mendoza-pleased.png`

## Priority House Leaders

### Wren Castellano

- [x] `wren-castellano-neutral.png`
- [x] `wren-castellano-pleased.png`
- [x] `wren-castellano-thoughtful.png`
- [x] `wren-castellano-concerned.png`

### Sarah Sterling

- [x] `sarah-sterling-neutral.png`
- [x] `sarah-sterling-pleased.png`
- [x] `sarah-sterling-thoughtful.png`
- [x] `sarah-sterling-concerned.png`

### Diane Okafor

- [x] `diane-okafor-neutral.png`
- [x] `diane-okafor-pleased.png`
- [x] `diane-okafor-thoughtful.png`
- [x] `diane-okafor-concerned.png`

### Tom Bracewell

- [x] `tom-bracewell-neutral.png`
- [x] `tom-bracewell-pleased.png`
- [x] `tom-bracewell-thoughtful.png`
- [x] `tom-bracewell-concerned.png`

### Marcus Vance

- [x] `marcus-vance-neutral.png`
- [x] `marcus-vance-pleased.png`
- [x] `marcus-vance-thoughtful.png`
- [x] `marcus-vance-concerned.png`

## Priority Senate Leaders

### Eleanor Vance

- [x] `eleanor-vance-neutral.png`
- [x] `eleanor-vance-pleased.png`
- [x] `eleanor-vance-thoughtful.png`
- [x] `eleanor-vance-concerned.png`

### Regina Alvarez

- [x] `regina-alvarez-neutral.png`
- [x] `regina-alvarez-pleased.png`
- [x] `regina-alvarez-thoughtful.png`
- [x] `regina-alvarez-concerned.png`

### Augustus "The Anchor" Kane

- [x] `augustus-kane-neutral.png`
- [x] `augustus-kane-pleased.png`
- [x] `augustus-kane-thoughtful.png`
- [x] `augustus-kane-concerned.png`
- [x] `augustus-kane-commanding.png`

### Lucia Marchetti

- [x] `lucia-marchetti-neutral.png`
- [x] `lucia-marchetti-pleased.png`
- [x] `lucia-marchetti-thoughtful.png`
- [x] `lucia-marchetti-concerned.png`
- [x] `lucia-marchetti-intense.png`

## Supporting Staff Portraits

- [x] `committee-clerk-hiroshi-tanaka-neutral.png`
- [x] `committee-clerk-hiroshi-tanaka-pleased.png`
- [x] `cloakroom-staffer-neutral.png`
- [x] `press-row-intern-neutral.png`
- [x] `west-wing-briefer-neutral.png`
- [x] `west-wing-operations-aide-neutral.png`

## Ghost Portraits

Visual requirements:

- [ ] Use pale, translucent blue-gray or warm-gold treatment.
- [ ] Keep faces and expressions readable.

Files:

- [x] `ghost-washington-neutral.png`
- [x] `ghost-washington-thoughtful.png`
- [x] `ghost-lincoln-neutral.png`
- [x] `ghost-lincoln-thoughtful.png`

## Optional Map Sprites

Use these for stationary overworld characters.

```text
48 x 48 PNG
Transparent background
Facing down or three-quarter front
```

- [ ] `wren-castellano-standing.png`
- [ ] `president-disantis-standing.png`
- [ ] `ben-venello-standing.png`
- [ ] `abner-mendoza-standing.png`
- [ ] `duncan-johnson-standing.png`

## Optional Walking Sprite Sheets

Use this format when creating a full walking animation:

```text
192 x 192 PNG
4 columns x 4 rows
48 x 48 pixels per frame
Row 1: down
Row 2: left
Row 3: right
Row 4: up
```

Suggested filenames:

- [ ] `player-representative-walk.png`
- [ ] `wren-castellano-walk.png`
- [ ] `ben-venello-walk.png`
- [ ] `duncan-johnson-walk.png`

## Upload Organization

Suggested folder structure:

```text
portraits/
  president-disantis/
  sutton-disantis/
  ben-venello/
  abner-mendoza/
  house/
  senate/
  staff/
  ghosts/

sprites/
  player/
  house/
  senate/
  tourists/
```

## Recommended Creation Order

1. [ ] President DiSantis portrait set
2. [ ] Sutton DiSantis portrait set
3. [ ] Ben Venello portrait set
4. [ ] Abner Mendoza portrait set
5. [ ] Wren, Sarah, Diane, Tom, and Marcus
6. [ ] Eleanor, Regina, Kane, and Lucia
7. [x] Staff and ghost portraits
8. [ ] Standing sprites
9. [ ] Walking sprite sheets
