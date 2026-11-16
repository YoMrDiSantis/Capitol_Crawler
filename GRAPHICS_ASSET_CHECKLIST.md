# Capitol Hill Crawler Graphics Checklist

This is the working asset list for replacing placeholder/CSS graphics with one
consistent top-down RPG art set. Complete the **core style rules** before making
individual assets so every new graphic fits the same grid.

## Core Style Rules

- [ ] Use a **top-down / three-quarter overhead RPG view**. The player is looking down into rooms, never at a front-facing wall.
- [ ] Export transparent PNGs unless the item is a room background or tile sheet.
- [ ] Do not include names, labels, dialogue, UI buttons, or other readable text in art files.
- [ ] Keep props centered within their usable grid footprint, with no extra empty margin.
- [ ] Use one consistent tile unit across the **entire game**: **48 x 48 pixel source tiles**. This includes the House, Senate, Rotunda, Caucus rooms, Cloakrooms, Committee, Subway, White House, and D.C. map props.
- [ ] Build every prop footprint as whole multiples of 48px. For example: 48 x 48 (one tile), 96 x 48 (two by one), 144 x 96 (three by two), and 288 x 144 (six by three).
- [ ] Do not create 40px, 50px, 80px, 100px, or arbitrary-size source tiles for new art. The code can be migrated to the shared 48px navigation grid once this art foundation is ready.
- [ ] Walking sheets: 4 columns x 4 rows, one direction per row: down, left, right, up.
- [ ] For the current game importer, export walk sheets at **1024 x 1024** with 256 x 256 source frames, or supply a 192 x 192 / 48 x 48 version and flag it so the importer can be updated.

## Highest Priority: House Side Rooms

The West/East Caucus and West/East Cloakroom need coherent overhead rooms. These are the most urgent graphics because the current rooms mix CSS placeholders with Modern Interiors.

### Caucus Room Tile Set

- [ ] `caucus-room-floor-tiles.png`

Prompt:
```text
Create a seamless top-down pixel-art interior tile set for a United States Capitol caucus room. Match the visual language of Modern InterAs able text, no front-facing perspective.
```

- [ ] `caucus-chair-topdown.png`

Prompt:
```text
Create a top-down pixel-art upholstered committee chair for an RPG interior. Match Modern Interiors style. The chair should occupy one 48 x 48 tile, seen from overhead, with a dark wood frame and muted teal upholstery. No person, no text, transparent background.
```

- [ ] `caucus-reference-shelf-topdown.png`

Prompt:
```text
Create a top-down pixel-art low reference shelf for a Capitol caucus room. Match Modern Interiors style. It should occupy 3 by 2 tiles and contain binders, folders, and a few books, with no readable text. It must look like a floor object viewed from above, not a front-facing bookcase. Transparent background.
```

### Cloakroom Tile Set

- [ ] `cloakroom-floor-tiles.png`

Prompt:
```text
Create a seamless top-down pixel-art tile set for a United States Capitol cloakroom. Match Modern Interiors RPG art: muted blue-green floor, warm wood, brass hardware, dark pixel outlines. Include floor tiles, wall trim, an overhead doorway threshold, and subtle coatroom details. No people, no labels, no readable text, no front-facing wall view. Use the Capitol Hill Crawler universal 48 x 48 pixel tile unit.
```

- [ ] `cloakroom-locker-bank-topdown.png`

Prompt:
```text
Create a top-down pixel-art cloakroom locker bank for an RPG interior. Match Modern Interiors style. It should occupy 4 by 2 tiles and show closed lockers, a bench, hanging coats, and a small umbrella stand from overhead. No person, no readable text, transparent background.
```

- [ ] `cloakroom-message-board-topdown.png`

Prompt:
```text
Create a top-down pixel-art Capitol cloakroom message board for an RPG. Match Modern Interiors style. The board is a 2 by 2 tile floor or wall-adjacent object with pinned notes, paper clips, and colored index cards, but no readable text. Leave its center visually clear enough to identify as an interactive study board. Transparent background.
```

## House Chamber Props

- [ ] `house-floor-desk-topdown.png`

Prompt:
```text
Create a top-down pixel-art U.S. House floor desk for an RPG chamber. Match Modern Interiors style. One desk should occupy 2 by 2 tiles and include a wood desktop, a small microphone, papers, and a chair. No people, no readable text, transparent background.
```

- [ ] `house-corridor-door-topdown.png`

Prompt:
```text
Create a top-down pixel-art Capitol office or side-room doorway threshold. Match Modern Interiors style. This must be viewed from above as a floor transition, not as a front-facing door. Occupy 4 by 1 tiles with brass trim, dark wood, and a clearly walkable center. No labels or text, transparent background around the threshold.
```

- [ ] `capitol-message-board-topdown.png`

Prompt:
```text
Create a top-down pixel-art Capitol hallway message board for an RPG. Match Modern Interiors style. Occupy 2 by 2 tiles. Include pinned paper shapes, colored notes, and brass corner hardware, but no readable text. Make it visually recognizable as an interactive study board. Transparent background.
```

## Character Walk Sheets

Create these only for named characters who appear on the map. The generic Democratic and Republican male/female sheets already cover background members.

Shared prompt prefix:
```text
Create a 4 by 4 top-down RPG walking sprite sheet for [CHARACTER]. Match the existing Capitol Hill Crawler / Modern Interiors pixel-art style. Direction rows must be: down, left, right, up. Keep the character centered in every frame with a transparent background. The character should be clearly readable at 48 x 48 pixels, wearing professional congressional clothing. No text, no nameplate, no backdrop.
```

- [ ] `priya-anand-walk.png`
  - Add: `South Asian woman, practical teal blazer, clipboard or folder detail, thoughtful policy professional.`
- [ ] `selena-marsh-walk.png`
  - Add: `Woman coalition builder, warm rust blazer, approachable but professional, carries a small notebook.`
- [ ] `robin-yates-walk.png`
  - Add: `Woman rural district representative, practical earth-tone jacket, sturdy shoes, calm skeptical expression.`
- [ ] `hank-delgado-walk.png`
  - Add: `Man small-business representative, rolled document folder, brown jacket, practical professional appearance.`
- [ ] `gus-whitfield-walk.png`
  - Add: `Man facilities expert, green tie, work-ready professional suit, small repair-plan folder.`
- [ ] `naomi-cho-walk.png`
  - Add: `East Asian woman communications representative, purple blazer, professional, carries a note card.`
- [ ] `cyrus-boone-walk.png`
  - Add: `Man committee rules representative, dark brown suit, folder of procedures, formal posture.`
- [ ] `alma-judd-walk.png`
  - Add: `Woman former debate coach, blue blazer, concise professional style, pencil or note card.`
- [ ] `dez-okonkwo-walk.png`
  - Add: `Black man youth arts organizer turned representative, bright but professional accent color, welcoming posture.`
- [ ] `fritz-callahan-walk.png`
  - Add: `Man former paramedic turned representative, practical navy suit, coffee cup or small briefing folder.`
- [ ] `otis-reinholt-walk.png`
  - Add: `Man budget-focused representative, slate suit, calculator or ledger detail.`
- [ ] `marv-tillson-walk.png`
  - Add: `Man former science teacher, neutral suit, mechanical pencil or paper detail.`
- [ ] `ines-falkenrath-walk.png`
  - Add: `Woman first-term idealist, plum blazer, hopeful professional style.`
- [ ] `ada-boykin-walk.png`
  - Add: `Woman determined committee challenger, red blazer, folder held firmly.`
- [ ] `silas-kroft-walk.png`
  - Add: `Man engineer representative, gray suit, precise formal posture.`
- [ ] `clem-osgood-walk.png`
  - Add: `Man public records representative, blue-gray suit, document folder.`
- [ ] `walt-iverson-walk.png`
  - Add: `Older man Senate institutionalist, navy suit, traditional formal style.`
- [ ] `bee-nakamura-walk.png`
  - Add: `Young East Asian woman Senate leader, bright professional blazer, clipboard.`
- [ ] `roland-fitch-walk.png`
  - Add: `Older man Senate veteran, reserved charcoal suit, direct posture.`
- [ ] `corinne-vasquez-walk.png`
  - Add: `Latina Senate negotiator, burgundy blazer, helpful but sharp professional style.`
- [ ] `del-ashworth-walk.png`
  - Add: `Man former civics teacher and Senator, tweed-like brown suit, textbook or notes detail.`
- [ ] `luciana-abbonizio-walk.png`
  - Add: `Woman Senate scheduler and leader, lavender suit, color-coded planner detail.`

## Portraits Still Needed

Create a transparent pixel-art dialogue portrait for each named Representative without a dedicated portrait. Use 96 x 96 or 128 x 128 pixels. Provide at least `neutral`, `thoughtful`, `pleased`, and `concerned` expressions. Do not include backgrounds, names, text, or flags.

Shared prompt prefix:
```text
Create four transparent pixel-art dialogue portraits of [CHARACTER] in the Capitol Hill Crawler / Modern Interiors style. Use a professional congressional appearance, head-and-shoulders framing, consistent lighting, dark pixel outlines, and no background. Export four separate expressions: neutral, thoughtful, pleased, concerned. No name, text, border, or UI.
```

- [ ] Priya Anand
- [ ] Selena Marsh
- [ ] Robin Yates
- [ ] Hank Delgado
- [ ] Gus Whitfield
- [ ] Naomi Cho
- [ ] Cyrus Boone
- [ ] Alma Judd
- [ ] Dez Okonkwo
- [ ] Fritz Callahan
- [ ] Otis Reinholt
- [ ] Marv Tillson
- [ ] Ines Falkenrath
- [ ] Ada Boykin
- [ ] Silas Kroft
- [ ] Clem Osgood
- [ ] Walt Iverson
- [ ] Bee Nakamura
- [ ] Roland Fitch
- [ ] Corinne Vasquez
- [ ] Del Ashworth
- [ ] Luciana Abbonizio

## Recommended Order

### Production 1: Shared Interior Foundation

Create these first. They are reusable across the Caucus rooms, Cloakrooms,
Committee room, Senate side rooms, Leadership Office, and future Capitol rooms.

| Checklist | Asset | Grid footprint | Reuse plan |
| --- | --- | --- | --- |
| [ ] | `capitol-floor-tiles.png` | 48 x 48 tiles | Use as the base floor for Caucus rooms, Cloakrooms, Committee rooms, offices, and study rooms. Make 4 to 6 matching tile variations so rooms do not look stamped. |
| [ ] | `capitol-wall-and-threshold-tiles.png` | 48 x 48 tiles | Use for every overhead doorway, room edge, doorway threshold, and hall transition in the House and Senate. |
| [ ] | `capitol-conference-table.png` | 6 x 3 tiles | Use in West Caucus, East Caucus, Committee markup, Leadership Office, and future briefing rooms. Change only papers/chairs in code. |
| [ ] | `capitol-chair.png` | 1 x 1 tile | Use around every conference table, committee table, staff desk, and waiting room. Rotate in CSS where needed. |
| [ ] | `capitol-reference-shelf.png` | 3 x 2 tiles | Use as the Reference Sheet find in every side room and as a non-interactive shelf elsewhere. |
| [ ] | `capitol-message-board.png` | 2 x 2 tiles | Use for all House, Senate, Cloakroom, Caucus, D.C. visitor, and future study-find boards. Change the source/question in code, not the art. |
| [ ] | `capitol-lockers-and-bench.png` | 4 x 2 tiles | Use in both Cloakrooms, Capitol Subway, staff hallways, and future storage rooms. |
| [ ] | `capitol-paper-stack.png` | 1 x 1 tile | Use on conference tables, desks, clerk tables, floor-paper finds, and vote-ledger areas. |
| [ ] | `capitol-folder.png` | 1 x 1 tile | Use on tables, in aide/scout scenes, and as a small study-find indicator. |
| [ ] | `capitol-flag-stand.png` | 1 x 2 tiles | Use in Caucuses, Committee room, Senate chamber, Rotunda, and White House rooms. |

Prompt for this production:
```text
Create a modular top-down pixel-art prop and tile set for a U.S. Capitol RPG.
Match the supplied Modern Interiors by LimeZu style and the Capitol Hill Crawler universal 48 x 48 pixel grid,
muted teal, warm walnut wood, aged brass, cream marble, dark clean outlines,
and readable overhead objects. Include seamless floor tiles, wall-edge and
door-threshold tiles, a conference table, chair, reference shelf, message
board, lockers with bench, paper stack, folder, and flag stand. Every prop
must be drawn from a top-down / three-quarter overhead view and fit an exact
48px tile footprint. No people, names, labels, readable text, or UI. Export
each prop separately on a transparent background and export tiles separately.
```

### Production 2: Side-Room Characters

These seven people are the first named side-room interactions and should have
both a map sprite and a dialogue portrait. They make the Caucus/Cloakroom
spaces feel intentional before adding more rooms.

| Checklist | Character | Room / use | Reuse plan |
| --- | --- | --- | --- |
| [ ] | Priya Anand | West Caucus target | Walk sheet for House floor and Caucus; portrait for dialogue, advice, and Committee scenes. |
| [ ] | Diane Okafor | West Caucus member | Existing custom walk sheet and portraits are available; reuse them in House, Caucus, Committee, and dialogue. |
| [ ] | Selena Marsh | East Caucus target | Walk sheet for House floor and Caucus; portrait for dialogue. |
| [ ] | Robin Yates | East Caucus member | Walk sheet for House floor and Caucus; portrait for dialogue. |
| [ ] | Hank Delgado | West Cloakroom target | Walk sheet for House floor and Cloakroom; portrait for dialogue. |
| [ ] | Gus Whitfield | West Cloakroom target | Walk sheet for House floor and Cloakroom; portrait for dialogue and Committee scenes. |
| [ ] | Naomi Cho | East Cloakroom target | Walk sheet for House floor and Cloakroom; portrait for dialogue. |
| [ ] | Cyrus Boone | East Cloakroom target | Walk sheet for House floor and Cloakroom; portrait for dialogue and Committee scenes. |

For each character, create:

- [ ] One `character-name-walk.png` 4 x 4 walking sheet
- [ ] `character-name-neutral.png`
- [ ] `character-name-thoughtful.png`
- [ ] `character-name-pleased.png`
- [ ] `character-name-concerned.png`

### Production 3: House Chamber Props

These turn the House into a coherent tiled map while reusing the Production 1
foundation instead of making one-off graphics.

| Checklist | Asset | Reuse plan |
| --- | --- | --- |
| [ ] | `house-floor-desk-topdown.png` | Repeat across the House and use a recolor in the Senate. |
| [ ] | `house-rostrum-topdown.png` | Use in House chamber, Committee presentation area, and tutorial cinematics. |
| [ ] | `house-vote-ledger.png` | Use as a House floor find, Senate ledger recolor, and Rotunda exhibit prop. |
| [ ] | `capitol-door-plate.png` | Use for Caucus, Cloakroom, Committee, office, Rotunda, Senate, and White House destination markers. The game supplies all labels. |
| [ ] | `capitol-stanchion-or-rail.png` | Use for visitor rails, gallery boundaries, Capitol tours, and security lines. |

### Production 4: Remaining House Members

Create only the map sprite and portraits for representatives who will recur in
dialogue or important rooms. Keep generic party sprites for background members
and low-priority one-off Representatives.

1. [ ] Alma Judd
2. [ ] Dez Okonkwo
3. [ ] Fritz Callahan
4. [ ] Otis Reinholt
5. [ ] Marv Tillson
6. [ ] Ines Falkenrath
7. [ ] Ada Boykin
8. [ ] Silas Kroft
9. [ ] Clem Osgood

### Production 5: Senate Members and Overtime Props

| Checklist | Asset | Reuse plan |
| --- | --- | --- |
| [ ] | Walt Iverson walk sheet + portraits | Senate floor, Senate Hold scenes, and dialogue. |
| [ ] | Bee Nakamura walk sheet + portraits | Senate floor and dialogue. |
| [ ] | Roland Fitch walk sheet + portraits | Senate floor and dialogue. |
| [ ] | Corinne Vasquez walk sheet + portraits | Senate Hold and dialogue. |
| [ ] | Del Ashworth walk sheet + portraits | Senate Hold and dialogue. |
| [ ] | Luciana Abbonizio walk sheet + portraits | Senate floor, office, briefcase route, and dialogue. |
| [ ] | `rogue-node-topdown.png` | Use for all ten Subway nodes; recolor cleared nodes in code. |
| [ ] | `subway-sign-and-bench.png` | Use in Capitol Subway, Cloakrooms, and Union Station / D.C. scenes. |

### Production 6: Optional World Detail Pack

Only start this once the interior foundation and core characters are complete.

- [ ] Rotunda museum display case
- [ ] Rotunda visitor information kiosk
- [ ] Rotunda study lectern
- [ ] D.C. park bench
- [ ] D.C. street lamp
- [ ] D.C. tree variations
- [ ] D.C. food cart
- [ ] D.C. museum sign
- [ ] Capitol visitor center desk

All of these should use the same universal 48px grid and can be reused in multiple D.C.
landmarks by changing position and surrounding terrain instead of creating a
separate asset for every location.
