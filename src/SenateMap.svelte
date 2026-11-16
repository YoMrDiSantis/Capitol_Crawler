<script lang="ts">
  import { onMount } from 'svelte';
  import type { Encounter } from './game';
  import Npc from './Npc.svelte';
  import Player from './Player.svelte';
  import { clampGridPosition } from './grid';

  let {
    encounters, completed, locked, held, playerSkinTone, playerPresentation, playerParty = 'D', playerX, playerY,
    onmove, oninteract, onrotunda, onarchive, onovertime, onprop, leadershipOfficeClosed = false
  }: {
    encounters: Encounter[];
    completed: string[];
    locked: string[];
    held: string[];
    playerSkinTone: string;
    playerPresentation: 'female' | 'male';
    playerParty?: 'D' | 'R';
    playerX: number;
    playerY: number;
    onmove: (x: number, y: number) => void;
    oninteract: (encounter: Encounter) => void;
    onrotunda: () => void;
    onarchive: () => void;
    onovertime: () => void;
    onprop: (id: string) => void;
    leadershipOfficeClosed?: boolean;
  } = $props();

  type LocalEncounter = Encounter & { source: Encounter };
  // Larger than the House chamber: a 100-seat Senate floor needs room to breathe.
  const mapWidth = 2400;
  const mapHeight = 1500;
  const tileSize = 100;
  const zones = [
    { id: 'archive', x: 200, y: 300, label: 'ARCHIVE BASEMENT' },
    { id: 'overtime', x: 2200, y: 300, label: 'CLOAKROOM / SUBWAY' },
    { id: 'leadership', x: 2100, y: 1200, label: 'LEADERSHIP CORRIDOR' },
    { id: 'rotunda', x: 1200, y: 1400, label: 'RETURN TO ROTUNDA' }
  ];
  const interactionProps = [
    { id: 'senate-clerk', x: 1200, y: 400, label: "CLERK'S TABLE" },
    { id: 'senate-papers', x: 500, y: 1000, label: 'FLOOR PAPERS' },
    { id: 'senate-ledger', x: 1900, y: 1000, label: 'VOTE LEDGER' },
    { id: 'senate-staff', x: 400, y: 500, label: 'FLOOR STAFF' },
    { id: 'senate-page', x: 2000, y: 500, label: 'PAGE DESK' }
    ,{ id: 'senate-board-west', x: 300, y: 900, label: 'WEST GALLERY MESSAGE BOARD' }
    ,{ id: 'senate-board-east', x: 2100, y: 900, label: 'EAST GALLERY MESSAGE BOARD' }
  ];
  const deskRows = Array.from({ length: 42 }, (_, index) => ({
    x: 400 + (index % 7) * 250,
    y: 700 + Math.floor(index / 7) * 100
  }));

  function localPosition(encounter: Encounter, index: number): LocalEncounter {
    const column = index % 5;
    const row = Math.floor(index / 5);
    return {
      ...encounter,
      source: encounter,
      x: 400 + column * 400,
      y: 800 + row * 200
    };
  }

  function normalize(valueX: number, valueY: number) {
    // Senate saves from the former wide map are projected into this local chamber.
    if (valueX > mapWidth || valueY > mapHeight) return { x: 1200, y: 1000 };
    return {
      x: clampGridPosition(valueX, 100, mapWidth - 100, tileSize),
      y: clampGridPosition(valueY, 200, mapHeight - 100, tileSize)
    };
  }

  let x = $state(1200);
  let y = $state(1000);
  let localEncounters = $derived(encounters.map(localPosition));
  let nearby = $derived(localEncounters.find((encounter) => Math.hypot(encounter.x - x, encounter.y - y) <= tileSize));
  let nearbyZone = $derived(zones.find((zone) => Math.hypot(zone.x - x, zone.y - y) <= tileSize * 1.5));
  let nearbyProp = $derived(interactionProps.find((prop) => Math.hypot(prop.x - x, prop.y - y) <= tileSize));

  $effect(() => {
    const position = normalize(playerX, playerY);
    x = position.x;
    y = position.y;
  });

  function nudge(horizontal: number, vertical: number) {
    const nextX = clampGridPosition(x + horizontal * tileSize, 100, mapWidth - 100, tileSize);
    const nextY = clampGridPosition(y + vertical * tileSize, 200, mapHeight - 100, tileSize);
    x = nextX;
    y = nextY;
    onmove(nextX, nextY);
  }

  function interact() {
    // Doors take priority over nearby senators so a leader standing close to a
    // doorway cannot swallow the Archive/Cloakroom interaction.
    if (nearbyZone) enterZone(nearbyZone.id);
    else if (nearby && !completed.includes(nearby.id) && !locked.includes(nearby.id)) oninteract(nearby.source);
    else if (nearbyProp) onprop(nearbyProp.id);
  }

  function enterZone(id: string) {
    if (id === 'archive') onarchive();
    else if (id === 'leadership' && !leadershipOfficeClosed) onprop('leadership-office');
    else if (id === 'leadership') onprop('leadership-office-locked');
    else if (id === 'overtime') onovertime();
    else onrotunda();
  }

  onMount(() => {
    const keydown = (event: KeyboardEvent) => {
      const tag = (event.target as HTMLElement | null)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      const directions: Record<string, [number, number]> = {
        ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1]
      };
      if (directions[event.key]) {
        event.preventDefault();
        const [horizontal, vertical] = directions[event.key];
        nudge(horizontal, vertical);
      } else if (event.key === 'e' || event.key === 'E' || event.key === 'Enter') {
        event.preventDefault();
        interact();
      }
    };
    window.addEventListener('keydown', keydown, true);
    return () => window.removeEventListener('keydown', keydown, true);
  });
  let viewport: HTMLDivElement;
  $effect(() => { if (viewport) viewport.scrollTo({ left: Math.max(0, x - viewport.clientWidth / 2), top: Math.max(0, y - viewport.clientHeight / 2), behavior: 'smooth' }); });
</script>

<main class="senate-play-map illustrated-senate">
  <header>
    <button onclick={onrotunda}>← ROTUNDA</button>
    <div><p>UNITED STATES SENATE</p><h1>SENATE <span>CHAMBER</span></h1></div>
    <b>Arrow keys to walk · E to interact</b>
  </header>

  <div class="senate-map-viewport" bind:this={viewport}><section class="senate-local-map grid-room" style={`--tile-size:${tileSize}px`} aria-label="Playable Senate chamber">
    <div class="senate-marble-border" aria-hidden="true"></div>
    <div class="senate-ink-lines" aria-hidden="true"></div>
    <div class="senate-gallery-label">UNITED STATES SENATE · FLOOR PLAN</div>
    <div class="senate-dais" aria-hidden="true"><div class="senate-rostrum"><span>THE</span>SENATE<br />ROSTRUM</div><div class="senate-dais-steps"></div></div>
    <button class="senate-prop senate-clerk-table" style="left:1200px;top:400px" onclick={() => onprop('senate-clerk')}><i></i><i></i><b>CLERK'S TABLE</b></button>
    <div class="senate-desk-field" aria-hidden="true">{#each deskRows as desk}<i style={`left:${desk.x}px;top:${desk.y}px`}></i>{/each}</div>
    <button class="senate-prop senate-side-table table-left" style="left:500px;top:1000px" onclick={() => onprop('senate-papers')}><i></i><i></i><b>FLOOR PAPERS</b></button>
    <button class="senate-prop senate-side-table table-right" style="left:1900px;top:1000px" onclick={() => onprop('senate-ledger')}><i></i><i></i><b>VOTE LEDGER</b></button>
    <button class="senate-prop senate-staffer-station staff-left" style="left:400px;top:500px" onclick={() => onprop('senate-staff')}><span></span><b>FLOOR STAFF</b></button>
    <button class="senate-prop senate-staffer-station staff-right" style="left:2000px;top:500px" onclick={() => onprop('senate-page')}><span></span><b>PAGE DESK</b></button>
    <button class="senate-message-board board-west" style="left:300px;top:900px" onclick={() => onprop('senate-board-west')}><b>WEST GALLERY</b><i></i><i></i></button><button class="senate-message-board board-east" style="left:2100px;top:900px" onclick={() => onprop('senate-board-east')}><b>EAST GALLERY</b><i></i><i></i></button>
    {#each zones as zone}
        <button class:closed={zone.id === 'leadership' && leadershipOfficeClosed} class:nearby-zone={nearbyZone?.id === zone.id} class={`senate-door senate-local-door ${zone.id}-door`} style={`left:${zone.x}px;top:${zone.y}px`} onpointerdown={(event) => { event.preventDefault(); event.stopPropagation(); enterZone(zone.id); }} onclick={(event) => { event.preventDefault(); event.stopPropagation(); enterZone(zone.id); }}>{zone.id === 'leadership' && leadershipOfficeClosed ? 'LEADERSHIP OFFICE · LOCKED' : zone.label}</button>
    {/each}
    {#each localEncounters as encounter (encounter.id)}
      <Npc encounter={encounter} completed={completed.includes(encounter.id)} locked={locked.includes(encounter.id)} onHold={held.includes(encounter.id)} nearby={nearby?.id === encounter.id} oninteract={() => oninteract(encounter.source)} />
    {/each}
    <Player {x} {y} skinTone={playerSkinTone} presentation={playerPresentation} party={playerParty} />
    {#if (nearbyZone || nearbyProp) && !nearby}<div class="senate-zone-prompt">E · {nearbyZone?.label ?? nearbyProp?.label}</div>{/if}
    <p class="senate-map-hint">Click a senator or chamber stop, or use arrows and E.</p>
  </section></div>

  <div class="senate-map-controls" aria-label="Senate map controls">
    <button aria-label="Walk left" onclick={() => nudge(-1, 0)}>◀</button><button aria-label="Walk up" onclick={() => nudge(0, -1)}>▲</button><button class="interact" onclick={interact}>E</button><button aria-label="Walk down" onclick={() => nudge(0, 1)}>▼</button><button aria-label="Walk right" onclick={() => nudge(1, 0)}>▶</button>
    <button class="reset" onclick={() => { x = 1200; y = 1000; onmove(x, y); }}>RESET</button>
    <button class="subway-direct" onclick={onovertime}>SUBWAY</button>
  </div>
</main>
