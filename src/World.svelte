<script lang="ts">
  import { onMount } from 'svelte';
  import { worldHeight, worldWidth, type Encounter } from './game';
  import Npc from './Npc.svelte';
  import Player from './Player.svelte';
  import { clampGridPosition, snapToGrid } from './grid';
  import { defaultHouseLayout, housePropLabels, housePropTypes, isHouseLayout, type HouseLayout, type HouseProp, type HousePropType } from './house-layout';

  const tileSize = 48;
  // Desk banks fan out from the Speaker's rostrum, leaving a clear central aisle.
  const chamberDesks = [
    ...Array.from({ length: 8 }, (_, index) => ({ column: 13 + index, row: 0 })),
    ...Array.from({ length: 10 }, (_, index) => ({ column: 11 + index, row: 1 })),
    ...Array.from({ length: 12 }, (_, index) => ({ column: 9 + index, row: 2 })),
    ...Array.from({ length: 14 }, (_, index) => ({ column: 7 + index, row: 3 })),
    ...Array.from({ length: 16 }, (_, index) => ({ column: 5 + index, row: 4 })),
    ...Array.from({ length: 18 }, (_, index) => ({ column: 3 + index, row: 5 })),
    ...Array.from({ length: 20 }, (_, index) => ({ column: 1 + index, row: 6 })),
    ...Array.from({ length: 20 }, (_, index) => ({ column: 1 + index, row: 7 })),
    ...Array.from({ length: 20 }, (_, index) => ({ column: 1 + index, row: 8 })),
    ...Array.from({ length: 18 }, (_, index) => ({ column: 3 + index, row: 9 })),
    ...Array.from({ length: 16 }, (_, index) => ({ column: 5 + index, row: 10 })),
    ...Array.from({ length: 14 }, (_, index) => ({ column: 7 + index, row: 11 })),
  ];
  // Exact # runs from the playable E3:GK43 spreadsheet grid: [row, first column, last column].
  const houseWallRuns = [[0,1,188],[1,1,188],[2,1,36],[2,148,188],[3,1,36],[3,148,188],[4,20,23],[4,33,36],[4,148,150],[4,160,163],[4,184,188],[5,20,23],[5,33,36],[5,148,150],[5,160,163],[5,184,188],[6,20,23],[6,33,36],[6,148,150],[6,160,163],[6,184,188],[7,20,23],[7,33,36],[7,148,150],[7,160,163],[7,184,188],[8,20,23],[8,33,36],[8,148,150],[8,160,163],[8,184,188],[9,184,188],[10,184,188],[11,20,23],[11,33,36],[11,148,150],[11,160,163],[11,184,188],[12,20,23],[12,33,36],[12,148,150],[12,160,163],[12,184,188],[13,20,23],[13,33,36],[13,148,150],[13,160,163],[13,184,188],[14,1,23],[14,33,36],[14,148,150],[14,160,188],[15,1,23],[15,33,36],[15,148,150],[15,160,188],[16,1,23],[16,33,36],[16,148,150],[16,160,188],[17,1,23],[17,33,36],[17,148,150],[17,160,188],[18,1,23],[18,33,36],[18,148,150],[18,160,188],[19,1,23],[19,160,188],[20,1,23],[20,160,188],[21,1,23],[21,33,36],[21,148,150],[21,160,188],[22,1,23],[22,33,36],[22,148,150],[22,160,188],[23,1,23],[23,33,36],[23,148,150],[23,160,188],[24,1,23],[24,33,36],[24,148,150],[24,160,188],[25,1,23],[25,33,36],[25,148,150],[25,160,188],[26,1,23],[26,33,36],[26,148,150],[26,160,188],[27,1,86],[27,98,188],[28,1,86],[28,98,188],[29,1,86],[29,98,188],[30,1,86],[30,98,188],[31,1,86],[31,98,188],[32,1,67],[32,118,188],[33,1,67],[33,118,188],[34,1,67],[34,118,188],[35,1,90],[35,95,188],[36,1,7],[36,178,188],[37,1,7],[37,178,188],[38,1,91],[38,94,188],[39,0,188],[40,0,188]] as const;

  let {
    encounters,
    playerX,
    playerY,
    playerSkinTone = '#d8a57c',
    playerPresentation = 'female',
    playerParty = 'D',
    completed,
    locked,
    held = [],
    paused,
    interactionBlocked = false,
    houseLayout = defaultHouseLayout,
    builderRequested = false,
    onmove,
    oninteract,
    onzone,
    onbuilderclose,
    onlayoutchange
  }: {
    encounters: Encounter[];
    playerX: number;
    playerY: number;
    playerSkinTone?: string;
    playerPresentation?: 'female' | 'male';
    playerParty?: 'D' | 'R';
    completed: string[];
    locked: string[];
    held?: string[];
    paused: boolean;
    interactionBlocked?: boolean;
    houseLayout?: HouseLayout;
    builderRequested?: boolean;
    onmove: (x: number, y: number) => void;
    oninteract: (encounter: Encounter) => void;
    onzone?: (zone: string) => void;
    onbuilderclose?: () => void;
    onlayoutchange?: (layout: HouseLayout) => void;
  } = $props();

  let viewport: HTMLDivElement;
  let directionX = 0;
  let directionY = 0;
  let frame = 0;
  let lastGridStep = 0;
  let wasPaused = false;
  let builderUnlocked = $state(false);
  let builderPassword = $state('');
  let builderError = $state('');
  let selectedPropType = $state<HousePropType>('desk');
  let selectedPropId = $state<string | null>(null);
  let undoLayout = $state<HouseLayout | null>(null);
  let importInput = $state<HTMLInputElement>();
  let selectedProp = $derived(houseLayout.props.find((prop) => prop.id === selectedPropId));
  const roomAssignments: Record<string, { x: number; y: number }> = {
    'wren-castellano': { x: 4512, y: 912 }, 'alma-judd': { x: 3552, y: 720 },
    'dez-okonkwo': { x: 5472, y: 720 }, 'fritz-callahan': { x: 3072, y: 912 },
    'sarah-sterling': { x: 5952, y: 912 }, 'selena-marsh': { x: 8496, y: 528 },
    'priya-anand': { x: 720, y: 528 }, 'hank-delgado': { x: 1488, y: 1056 },
    'naomi-cho': { x: 7632, y: 1056 }, 'otis-reinholt': { x: 4032, y: 1104 },
    'robin-yates': { x: 8496, y: 624 }, 'marv-tillson': { x: 6432, y: 1104 },
    'gus-whitfield': { x: 1488, y: 816 }, 'cyrus-boone': { x: 7632, y: 816 },
    'marcus-vance': { x: 4992, y: 624 }, 'diane-okafor': { x: 816, y: 624 },
    'ines-falkenrath': { x: 2592, y: 1104 }, 'earl-pruitt': { x: 6912, y: 912 },
    'tom-bracewell': { x: 5952, y: 624 }, 'ada-boykin': { x: 1536, y: 1248 },
    'silas-kroft': { x: 7584, y: 1248 }, 'clem-osgood': { x: 6720, y: 1104 }
  };
  let gridEncounters = $derived(encounters.map((encounter) => ({
    ...encounter,
    x: roomAssignments[encounter.id]?.x ?? snapToGrid(encounter.x, tileSize),
    y: roomAssignments[encounter.id]?.y ?? snapToGrid(encounter.y, tileSize)
  })));
  let gridPlayerX = $derived(clampGridPosition(playerX, 80, worldWidth - 120, tileSize));
  let gridPlayerY = $derived(clampGridPosition(playerY, 160, worldHeight - 160, tileSize));
  let nearby = $derived(
    gridEncounters
      .map((encounter) => ({ encounter, distance: Math.hypot(encounter.x - gridPlayerX, encounter.y - gridPlayerY) }))
      .filter(({ distance }) => distance <= tileSize * 1.5)
      .sort((left, right) => left.distance - right.distance)[0]?.encounter
  );
  const mapZones = [
    { id: 'west-caucus', x: 1152, y: 528, label: 'ENTER WEST CAUCUS' },
    { id: 'east-caucus', x: 7968, y: 528, label: 'ENTER EAST CAUCUS' },
    { id: 'west-cloakroom', x: 1824, y: 528, label: 'ENTER WEST CLOAKROOM' },
    { id: 'east-cloakroom', x: 7296, y: 528, label: 'ENTER EAST CLOAKROOM' },
    { id: 'committee', x: 4608, y: 1584, label: 'ENTER COMMITTEE MARKUP' },
    { id: 'rotunda', x: 4608, y: 1776, label: 'ROTUNDA HALL' },
    { id: 'dc', x: 4608, y: 1872, label: 'EXIT TO D.C.' },
    { id: 'house-papers', x: 3024, y: 576, label: 'FLOOR PAPERS' },
    { id: 'house-ledger', x: 6240, y: 1056, label: 'VOTE LEDGER' },
    { id: 'house-briefing', x: 5760, y: 576, label: 'BRIEFING TABLE' },
    { id: 'house-board-west', x: 1488, y: 816, label: 'WEST CLOAKROOM MESSAGE BOARD' },
    { id: 'house-board-east', x: 7728, y: 816, label: 'EAST CLOAKROOM MESSAGE BOARD' },
    { id: 'house-board-south', x: 7008, y: 1776, label: 'HALLWAY MESSAGE BOARD' },
    { id: 'ben-venello', x: 4560, y: 480, label: 'MR. BEN VENELLO' }
  ];
  const backgroundWalkers = Array.from({ length: 34 }, (_, index) => ({
    // These are whole House-map tiles, not decorative pixel offsets.
    x: 2352 + (index % 11) * 432,
    y: 576 + Math.floor(index / 11) * 192,
    sprite: `${index % 3 === 0 ? 'female-congresswoman' : 'male-congressman'}-${index % 2 ? '1' : '2'}-walk.png`
  }));
  let gridZones = $derived(mapZones.map((zone) => ({
    ...zone,
    x: snapToGrid(zone.x, tileSize),
    y: snapToGrid(zone.y, tileSize)
  })));
  let nearbyZone = $derived(gridZones.find((zone) => Math.hypot(zone.x - gridPlayerX, zone.y - gridPlayerY) <= tileSize * 1.5));

  function isWalkable(x: number, y: number) {
    // These bounds match the visible spreadsheet-derived floor layers exactly.
    // Keeping collision and art on the same 48px grid prevents walking into walls.
    const inChamber = x >= 1776 && x <= 7152 && y >= 96 && y <= 1296;
    const inWestCaucus = x >= 48 && x <= 960 && y >= 192 && y <= 672;
    const inEastCaucus = x >= 7248 && x <= 8160 && y >= 192 && y <= 672;
    const inWestCloakroom = x >= 1152 && x <= 1584 && y >= 192 && y <= 1296;
    const inEastCloakroom = x >= 7248 && x <= 7680 && y >= 192 && y <= 1296;
    const inWestUpperDoor = x >= 1104 && x <= 1920 && y >= 480 && y <= 576;
    const inWestLowerDoor = x >= 1728 && x <= 1920 && y >= 960 && y <= 1056;
    const inEastUpperDoor = x >= 7248 && x <= 8016 && y >= 480 && y <= 576;
    const inEastLowerDoor = x >= 7248 && x <= 7392 && y >= 960 && y <= 1056;
    const inConnector = x >= 4176 && x <= 4704 && y >= 1344 && y <= 1584;
    const inCommittee = x >= 3264 && x <= 5664 && y >= 1584 && y <= 1728;
    const inHallwayEntrance = x >= 4560 && x <= 4752 && y >= 1728 && y <= 1776;
    const inHallway = x >= 432 && x <= 8688 && y >= 1776 && y <= 1872;
    const row = Math.round(y / tileSize);
    const column = Math.round(x / tileSize);
    const wallAtTile = houseWallRuns.some(([wallRow, start, end]) => wallRow === row && column >= start && column <= end);
    return !wallAtTile && (inChamber || inWestCaucus || inEastCaucus || inWestCloakroom || inEastCloakroom || inWestUpperDoor || inWestLowerDoor || inEastUpperDoor || inEastLowerDoor || inConnector || inCommittee || inHallwayEntrance || inHallway);
  }

  function move() {
    if ((directionX || directionY) && !paused && performance.now() - lastGridStep >= 130) {
      lastGridStep = performance.now();
      const nextX = clampGridPosition(playerX + directionX * tileSize, 80, worldWidth - 120, tileSize);
      const nextY = clampGridPosition(playerY + directionY * tileSize, 160, worldHeight - 160, tileSize);
      if (isWalkable(nextX, nextY)) onmove(nextX, nextY);
      else if (directionX && isWalkable(nextX, playerY)) onmove(nextX, playerY);
      else if (directionY && isWalkable(playerX, nextY)) onmove(playerX, nextY);
    }
    frame = requestAnimationFrame(move);
  }

  function setDirection(x: number, y: number) {
    directionX = x;
    directionY = y;
  }

  function nudge(x: number, y: number) {
    if (paused) return;
    lastGridStep = performance.now();
    const nextX = clampGridPosition(playerX + x * tileSize, 80, worldWidth - 120, tileSize);
    const nextY = clampGridPosition(playerY + y * tileSize, 160, worldHeight - 160, tileSize);
    if (isWalkable(nextX, nextY)) onmove(nextX, nextY);
  }

  function releaseDialogFocus() {
    requestAnimationFrame(() => (document.activeElement as HTMLElement | null)?.blur());
  }

  function copyLayout(layout: HouseLayout): HouseLayout {
    return { ...layout, props: layout.props.map((prop) => ({ ...prop })) };
  }

  function applyLayout(layout: HouseLayout) {
    onlayoutchange?.(layout);
  }

  function editLayout(change: (layout: HouseLayout) => HouseLayout) {
    undoLayout = copyLayout(houseLayout);
    applyLayout(change(copyLayout(houseLayout)));
  }

  function unlockBuilder() {
    if (builderPassword !== 'candy') { builderError = 'That password does not unlock Map Builder.'; return; }
    builderUnlocked = true;
    builderPassword = '';
    builderError = '';
  }

  function closeBuilder() {
    builderUnlocked = false;
    builderPassword = '';
    builderError = '';
    selectedPropId = null;
    onbuilderclose?.();
  }

  function placeProp() {
    const prop: HouseProp = {
      id: `house-prop-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      type: selectedPropType,
      x: gridPlayerX,
      y: gridPlayerY,
      width: 1,
      height: 1,
      rotation: 0,
      mirrored: false
    };
    editLayout((layout) => ({ ...layout, props: [...layout.props, prop] }));
    selectedPropId = prop.id;
  }

  function moveSelected(horizontal: number, vertical: number) {
    if (!selectedProp) return;
    editLayout((layout) => ({ ...layout, props: layout.props.map((prop) => prop.id === selectedProp.id ? { ...prop, x: Math.max(0, prop.x + horizontal * tileSize), y: Math.max(0, prop.y + vertical * tileSize) } : prop) }));
  }

  function resizeSelected(widthChange: number, heightChange: number) {
    if (!selectedProp) return;
    editLayout((layout) => ({ ...layout, props: layout.props.map((prop) => prop.id === selectedProp.id ? { ...prop, width: Math.max(1, Math.min(12, prop.width + widthChange)), height: Math.max(1, Math.min(12, prop.height + heightChange)) } : prop) }));
  }

  function rotateSelected() {
    if (!selectedProp) return;
    editLayout((layout) => ({ ...layout, props: layout.props.map((prop) => prop.id === selectedProp.id ? { ...prop, rotation: (prop.rotation + 90) % 360 } : prop) }));
  }

  function mirrorSelected() {
    if (!selectedProp) return;
    editLayout((layout) => ({ ...layout, props: layout.props.map((prop) => prop.id === selectedProp.id ? { ...prop, mirrored: !prop.mirrored } : prop) }));
  }

  function duplicateSelected() {
    if (!selectedProp) return;
    const duplicate = { ...selectedProp, id: `house-prop-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`, x: selectedProp.x + tileSize };
    editLayout((layout) => ({ ...layout, props: [...layout.props, duplicate] }));
    selectedPropId = duplicate.id;
  }

  function deleteSelected() {
    if (!selectedProp) return;
    editLayout((layout) => ({ ...layout, props: layout.props.filter((prop) => prop.id !== selectedProp.id) }));
    selectedPropId = null;
  }

  function undo() {
    if (!undoLayout) return;
    const current = copyLayout(houseLayout);
    applyLayout(undoLayout);
    undoLayout = current;
  }

  function exportLayout() {
    const file = new Blob([JSON.stringify(houseLayout, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(file);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'capitol-hill-crawler-house-layout.json';
    link.click();
    URL.revokeObjectURL(url);
  }

  function importLayout(event: Event) {
    const file = (event.currentTarget as HTMLInputElement).files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const layout = JSON.parse(String(reader.result));
        if (!isHouseLayout(layout)) throw new Error('Invalid layout');
        editLayout(() => layout);
        selectedPropId = null;
      } catch { builderError = 'That file is not a valid House layout export.'; }
      if (importInput) importInput.value = '';
    };
    reader.readAsText(file);
  }

  function interact() {
    if (paused || interactionBlocked) return;
    if (nearby && !completed.includes(nearby.id) && !locked.includes(nearby.id)) oninteract(nearby);
    else if (nearbyZone) onzone?.(nearbyZone.id);
  }

  function interactWith(encounter: Encounter) {
    if (!paused && !interactionBlocked && !completed.includes(encounter.id) && !locked.includes(encounter.id)) oninteract(encounter);
  }

  function beginDirection(event: PointerEvent, x: number, y: number) {
    if (paused) return;
    (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
    setDirection(x, y);
  }

  onMount(() => {
    const keydown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      // Dialog buttons can retain focus after closing. Only text-entry controls should
      // suppress map movement; buttons must not trap the player in place.
      if (target?.tagName === 'INPUT' || target?.tagName === 'TEXTAREA' || target?.tagName === 'SELECT') return;
      if (event.key === 'ArrowLeft') { event.preventDefault(); nudge(-1, 0); }
      if (event.key === 'ArrowRight') { event.preventDefault(); nudge(1, 0); }
      if (event.key === 'ArrowUp') { event.preventDefault(); nudge(0, -1); }
      if (event.key === 'ArrowDown') { event.preventDefault(); nudge(0, 1); }
      if (['e', 'E', 'Enter'].includes(event.key) && !paused) { event.preventDefault(); interact(); }
    };
    const keyup = (event: KeyboardEvent) => {
      // Always clear movement on release. A dialog input may have received keydown,
      // but focus can change before keyup when the dialog closes.
      if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) { event.preventDefault(); setDirection(0, 0); }
    };
    const clearDirection = () => setDirection(0, 0);
    // Capture keys before a previously focused dialog button can consume them.
    window.addEventListener('keydown', keydown, true);
    window.addEventListener('keyup', keyup, true);
    window.addEventListener('blur', clearDirection);
    document.addEventListener('visibilitychange', clearDirection);
    frame = requestAnimationFrame(move);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('keydown', keydown, true);
      window.removeEventListener('keyup', keyup, true);
      window.removeEventListener('blur', clearDirection);
      document.removeEventListener('visibilitychange', clearDirection);
    };
  });

  $effect(() => {
    if (playerX !== gridPlayerX || playerY !== gridPlayerY) onmove(gridPlayerX, gridPlayerY);
  });

  $effect(() => {
    if (paused) setDirection(0, 0);
    if (wasPaused && !paused) {
      requestAnimationFrame(() => {
        (document.activeElement as HTMLElement | null)?.blur();
        viewport?.focus({ preventScroll: true });
      });
    }
    wasPaused = paused;
  });

  $effect(() => {
    if (viewport) {
      viewport.scrollTo({ left: Math.max(0, playerX - viewport.clientWidth / 2), top: Math.max(0, playerY - viewport.clientHeight / 2), behavior: 'smooth' });
    }
  });
</script>

  <div class="viewport illustrated-house" bind:this={viewport} tabindex="-1">
    <div class="world grid-world house-spec-world" style={`width:${worldWidth}px;height:${worldHeight}px;--tile-size:${tileSize}px`}>
    <div class="house-spec-title" aria-hidden="true"><span>U.S. CAPITOL</span><b>HOUSE OF REPRESENTATIVES</b></div>
    <div class="house-sheet-floor floor-chamber" aria-hidden="true"></div><div class="house-sheet-floor floor-gallery" aria-hidden="true"></div><div class="house-sheet-floor floor-west-caucus" aria-hidden="true"></div><div class="house-sheet-floor floor-east-caucus" aria-hidden="true"></div><div class="house-sheet-floor floor-west-cloak" aria-hidden="true"></div><div class="house-sheet-floor floor-east-cloak" aria-hidden="true"></div><div class="house-sheet-floor floor-committee" aria-hidden="true"></div><div class="house-sheet-floor floor-connector" aria-hidden="true"></div><div class="house-sheet-floor floor-hall" aria-hidden="true"></div>
    <div class="house-spec-room west-caucus-spec"><b>WEST CAUCUS</b></div><div class="house-spec-room east-caucus-spec"><b>EAST CAUCUS</b></div>
    <div class="house-spec-room west-cloakroom-spec"><b>WEST CLOAKROOM</b></div><div class="house-spec-room east-cloakroom-spec"><b>EAST CLOAKROOM</b></div>
    <div class="house-floor-link house-link-west-upper" aria-hidden="true"></div><div class="house-floor-link house-link-west-lower" aria-hidden="true"></div><div class="house-floor-link house-link-east-upper" aria-hidden="true"></div><div class="house-floor-link house-link-east-lower" aria-hidden="true"></div>
    <div class="house-spec-door door-west-caucus">WEST CAUCUS</div><div class="house-spec-door door-east-caucus">EAST CAUCUS</div><div class="house-spec-door door-west-cloak">WEST CLOAKROOM</div><div class="house-spec-door door-east-cloak">EAST CLOAKROOM</div>
    <div class="house-spec-chamber"><div class="house-spec-gallery">PUBLIC GALLERY</div><div class="house-spec-rostrum">SPEAKER'S ROSTRUM</div>{#if !houseLayout.hideBuiltInDesks}<div class="house-spec-desks">{#each chamberDesks as desk}<i style={`--desk-column:${desk.column};--desk-row:${desk.row}`}></i>{/each}</div>{/if}</div>
    <div class="house-spec-connector"></div><div class="house-spec-committee">COMMITTEE MARKUP</div><div class="house-spec-hallway-entrance" aria-hidden="true"></div><div class="house-spec-hallway"><b>ROTUNDA HALLWAY</b><span>EXIT TO D.C. ↓</span></div>
    {#each houseWallRuns as [row, start, end]}<div class="house-wall-run" style={`left:${start * tileSize}px;top:${row * tileSize}px;width:${(end - start + 1) * tileSize}px`} aria-hidden="true"></div>{/each}
    <div class="house-spec-prop papers-prop">FLOOR PAPERS</div><div class="house-spec-prop ledger-prop">VOTE LEDGER</div><div class="house-spec-prop briefing-prop">BRIEFING TABLE</div>
    <div class="message-board house-board-west" aria-hidden="true"><b>STUDY BOARD</b><i></i><i></i></div><div class="message-board house-board-east" aria-hidden="true"><b>STUDY BOARD</b><i></i><i></i></div><div class="message-board house-board-south" aria-hidden="true"><b>FLOOR NOTES</b><i></i><i></i></div>
    <div class="house-ben" aria-hidden="true"><i></i><b>MR. BEN VENELLO</b></div>
    {#each houseLayout.props as prop}<button class:selected={selectedPropId === prop.id} class={`placed-house-prop prop-${prop.type}`} style={`left:${prop.x}px;top:${prop.y}px;--prop-width:${prop.width * tileSize}px;--prop-height:${prop.height * tileSize}px;--prop-rotation:${prop.rotation}deg;--prop-mirror:${prop.mirrored ? -1 : 1}`} onclick={() => { if (builderUnlocked) selectedPropId = prop.id; }} aria-label={builderUnlocked ? `Select ${housePropLabels[prop.type]}` : housePropLabels[prop.type]}></button>{/each}
    <div class="house-background-walkers" aria-hidden="true">{#each backgroundWalkers as walker}<i style={`left:${walker.x}px;top:${walker.y}px;--sprite-image:url('/assets/sprites/${walker.sprite}')`}></i>{/each}</div>
    {#each gridEncounters as encounter}
      <Npc {encounter} completed={completed.includes(encounter.id)} locked={locked.includes(encounter.id)} onHold={held.includes(encounter.id)} nearby={!interactionBlocked && nearby?.id === encounter.id} {paused} oninteract={interactWith} />
    {/each}
    <Player x={gridPlayerX} y={gridPlayerY} skinTone={playerSkinTone} presentation={playerPresentation} party={playerParty} />
    {#if nearbyZone && !nearby && !interactionBlocked}<div class="zone-prompt">E · {nearbyZone.label}</div>{/if}
  </div>
</div>

{#if builderRequested}<aside class="house-builder" aria-label="House Map Builder">
  {#if !builderUnlocked}
    <h2>MAP BUILDER</h2><p>Enter the builder password to edit the House layout.</p>
    <input type="password" bind:value={builderPassword} onkeydown={(event) => event.key === 'Enter' && unlockBuilder()} aria-label="Map Builder password" />
    {#if builderError}<p class="builder-error">{builderError}</p>{/if}
    <button class="builder-primary" onclick={unlockBuilder}>UNLOCK</button><button onclick={closeBuilder}>CANCEL</button>
  {:else}
    <header><div><p>MAP BUILDER</p><h2>HOUSE LAYOUT</h2></div><button onclick={closeBuilder}>LOCK</button></header>
    <label>PROP<select bind:value={selectedPropType}>{#each housePropTypes as type}<option value={type}>{housePropLabels[type]}</option>{/each}</select></label>
    <button class="builder-primary" onclick={placeProp}>PLACE AT CHARACTER</button>
    <label class="builder-toggle"><input type="checkbox" checked={houseLayout.hideBuiltInDesks} onchange={(event) => editLayout((layout) => ({ ...layout, hideBuiltInDesks: (event.currentTarget as HTMLInputElement).checked }))} /> HIDE BUILT-IN DESKS</label>
    <p class="builder-location">Character tile: {gridPlayerX / tileSize}, {gridPlayerY / tileSize}</p>
    {#if selectedProp}<section class="builder-selection"><p>SELECTED: {housePropLabels[selectedProp.type]}</p><div class="builder-grid"><button onclick={() => moveSelected(0, -1)}>UP</button><button onclick={() => moveSelected(-1, 0)}>LEFT</button><button onclick={() => moveSelected(1, 0)}>RIGHT</button><button onclick={() => moveSelected(0, 1)}>DOWN</button></div><div class="builder-actions"><button onclick={() => resizeSelected(-1, 0)}>WIDTH -</button><button onclick={() => resizeSelected(1, 0)}>WIDTH +</button><button onclick={() => resizeSelected(0, -1)}>HEIGHT -</button><button onclick={() => resizeSelected(0, 1)}>HEIGHT +</button><button onclick={rotateSelected}>ROTATE</button><button onclick={mirrorSelected}>MIRROR</button><button onclick={duplicateSelected}>DUPLICATE</button><button class="danger" onclick={deleteSelected}>DELETE</button></div><small>{selectedProp.width} x {selectedProp.height} tiles · {selectedProp.rotation} degrees · {selectedProp.mirrored ? 'mirrored' : 'normal'}</small></section>{:else}<p class="builder-location">Place a prop, then click it to move, resize, rotate, duplicate, or delete it.</p>{/if}
    <div class="builder-actions"><button disabled={!undoLayout} onclick={undo}>UNDO</button><button onclick={exportLayout}>EXPORT LAYOUT</button><button onclick={() => importInput?.click()}>IMPORT LAYOUT</button><button class="danger" onclick={() => { if (confirm('Clear all custom House props?')) { editLayout((layout) => ({ ...layout, props: [] })); selectedPropId = null; } }}>CLEAR PROPS</button></div>
    <input class="builder-file" bind:this={importInput} type="file" accept="application/json" onchange={importLayout} />
    {#if builderError}<p class="builder-error">{builderError}</p>{/if}
  {/if}
</aside>{/if}

<div class="map-accessibility-controls">
  <button onclick={() => { releaseDialogFocus(); onmove(4560, 1056); }}>RESET TO CHAMBER</button>
  <button disabled={interactionBlocked || (!nearby && !nearbyZone)} onclick={() => { releaseDialogFocus(); interact(); }}>{nearbyZone && !nearby ? `ENTER ${nearbyZone.label}` : 'INTERACT NEAREST'}</button>
  <button onclick={() => nudge(0, -1)}>UP</button><button onclick={() => nudge(0, 1)}>DOWN</button><button onclick={() => nudge(-1, 0)}>LEFT</button><button onclick={() => nudge(1, 0)}>RIGHT</button>
</div>

<div class="house-controls" aria-label="House map controls">
  <button onclick={() => nudge(-1, 0)}>◀</button><button onclick={() => nudge(0, -1)}>▲</button><button onclick={interact}>E</button><button onclick={() => nudge(0, 1)}>▼</button><button onclick={() => nudge(1, 0)}>▶</button>
</div>

<details class="leader-directory">
  <summary>HOUSE LEADER DIRECTORY</summary>
  <div>{#each encounters.filter((encounter) => !completed.includes(encounter.id) && !locked.includes(encounter.id)) as encounter}<button onclick={() => interactWith(encounter)}>{encounter.name}</button>{/each}</div>
</details>

<div class="mobile-controls" aria-label="Movement controls">
  <button aria-label="Walk left" onpointerdown={(event) => beginDirection(event, -1, 0)} onpointerup={() => setDirection(0, 0)} onpointercancel={() => setDirection(0, 0)} onlostpointercapture={() => setDirection(0, 0)}>◀</button>
  <button aria-label="Walk up" onpointerdown={(event) => beginDirection(event, 0, -1)} onpointerup={() => setDirection(0, 0)} onpointercancel={() => setDirection(0, 0)} onlostpointercapture={() => setDirection(0, 0)}>▲</button>
  <button class="talk" disabled={interactionBlocked || (!nearby && !nearbyZone) || completed.includes(nearby?.id ?? '') || locked.includes(nearby?.id ?? '')} onclick={interact}>{nearbyZone && !nearby ? 'ENTER' : 'TALK'}</button>
  <button aria-label="Walk down" onpointerdown={(event) => beginDirection(event, 0, 1)} onpointerup={() => setDirection(0, 0)} onpointercancel={() => setDirection(0, 0)} onlostpointercapture={() => setDirection(0, 0)}>▼</button>
  <button aria-label="Walk right" onpointerdown={(event) => beginDirection(event, 1, 0)} onpointerup={() => setDirection(0, 0)} onpointercancel={() => setDirection(0, 0)} onlostpointercapture={() => setDirection(0, 0)}>▶</button>
  <button class="unstick" onclick={() => onmove(4560, 1056)}>RESET</button>
</div>
