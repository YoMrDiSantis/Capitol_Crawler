<script lang="ts">
  import { onMount } from 'svelte';
  import Player from './Player.svelte';
  import { dcMapRects, dcRiverTiles, dcRoadTiles } from './dc-overworld-layout';

  const tileSize = 48;
  const columns = 120;
  const rows = 80;
  type Point = { col: number; row: number };
  type Spot = Point & { id: string; label: string; district: string; width: number; height: number };
  type Building = { style: string; x: number; y: number; width: number; height: number };
  type CityProp = { style: string; col: number; row: number; width: number; height: number };
  type Tourist = { name: string; sprite: 'tourist-female' | 'tourist-male'; route: [number, number][] };

  function displayName(name: string) {
    return name.split(',')[0];
  }

  import { touristInteractionId } from './story-dialogue';
  let { minutes, whiteHouseOpen, notebookEntries = 0, touristClaims = [], washingtonGhostComplete, lincolnGhostComplete, playerSkinTone, playerPresentation, playerParty, onrotunda, onspot, ontourist, onwashington, onlincoln, onwait }: {
    minutes: number; whiteHouseOpen: boolean; notebookEntries?: number; touristClaims?: string[]; washingtonGhostComplete: boolean; lincolnGhostComplete: boolean; playerSkinTone: string; playerPresentation: 'female' | 'male'; playerParty: 'D' | 'R'; onrotunda: () => void; onspot: (id: string) => void; ontourist: (name: string) => void; onwashington: () => void; onlincoln: () => void; onwait: () => void;
  } = $props();

   let col = $state(99); let row = $state(58); let walkerStep = $state(0); let carStep = $state(0);
  let hour = $derived(Math.floor(minutes / 60) % 24); let night = $derived(hour >= 20 || hour < 6);
  let timeLabel = $derived(`${hour === 0 ? 12 : hour > 12 ? hour - 12 : hour}:00 ${hour >= 12 ? 'PM' : 'AM'}`);
   const landmarkDetails: Record<string, Omit<Spot, keyof Point | 'width' | 'height'>> = {
     CAP: { id: 'capitol', label: 'U.S. CAPITOL / ROTUNDA', district: 'CAPITOL HILL' }, WH: { id: 'white-house', label: 'WHITE HOUSE', district: 'PRESIDENTIAL DISTRICT' }, WM: { id: 'monument', label: 'WASHINGTON MONUMENT', district: 'NATIONAL MALL' }, RP: { id: 'reflecting', label: 'REFLECTING POOL', district: 'WEST MALL' }, LM: { id: 'lincoln', label: 'LINCOLN MEMORIAL', district: 'WEST MALL' }, SM: { id: 'smithsonian', label: 'SMITHSONIAN MUSEUMS', district: 'MUSEUM ROW' }, LC: { id: 'library', label: 'LIBRARY OF CONGRESS', district: 'CAPITOL HILL' }, SC: { id: 'court', label: 'SUPREME COURT', district: 'CAPITOL HILL' }, CF: { id: 'cafe', label: 'MALL CAFE & DINER', district: 'MUSEUM ROW' }, PR: { id: 'press', label: 'PRESS ROW', district: 'PENN QUARTER' }, DJ: { id: 'duncan', label: 'DUNCAN JOHNSON', district: 'WEST MALL' }, VC: { id: 'tourists', label: 'TOURISTS & LOCALS', district: 'CAPITOL HILL' }
   };
   const buildingCodes: Record<string, string> = { RH1: 'rowhouse1', RH2: 'rowhouse2', RH3: 'rowhouse3', RH4: 'rowhouse4', LR2: 'lowrise2', LR3: 'lowrise3', LR4: 'lowrise4', HR1: 'highrise1', HR2: 'highrise2', HTL: 'hotel', AN1: 'annex1', AN2: 'annex2' };
   const propCodes: Record<string, string> = { TR: 'tree-group', HD: 'hedge-row', FL: 'flower-bed', BN: 'park-bench', BR: 'bike-rack', HY: 'fire-hydrant', SL: 'streetlamp', TL: 'traffic-light', BuS: 'bus-stop' };
   const mapRects = dcMapRects.map((rect) => rect.code === 'RP' ? { ...rect, row: rect.row + 6 } : rect);
   const spots: Spot[] = mapRects.filter((rect) => landmarkDetails[rect.code]).map((rect) => ({ ...landmarkDetails[rect.code], col: rect.col, row: rect.row, width: rect.width, height: rect.height }));
   const roads = [
    { id: 'k', x: 0, y: 2, width: 120, height: 4, horizontal: true }, { id: 'h', x: 0, y: 18, width: 120, height: 4, horizontal: true }, { id: 'penn', x: 46, y: 32, width: 74, height: 4, horizontal: true }, { id: 'ind', x: 0, y: 69, width: 120, height: 4, horizontal: true }, { id: '23', x: 20, y: 0, width: 4, height: 22, horizontal: false }, { id: '17', x: 34, y: 0, width: 4, height: 22, horizontal: false }, { id: '15', x: 46, y: 0, width: 4, height: 36, horizontal: false }, { id: '12', x: 64, y: 0, width: 4, height: 36, horizontal: false }, { id: '7', x: 76, y: 0, width: 4, height: 80, horizontal: false }, { id: '3', x: 90, y: 0, width: 4, height: 80, horizontal: false }, { id: '1', x: 104, y: 0, width: 4, height: 80, horizontal: false }
   ];
   const roadTiles = dcRoadTiles;
   const riverTileKeys = new Set(dcRiverTiles.map(([riverCol, riverRow]) => `${riverCol},${riverRow}`));
  const intersections = roads.filter((road) => road.horizontal).flatMap((eastWest) => roads.filter((road) => !road.horizontal && road.x < eastWest.x + eastWest.width && road.x + road.width > eastWest.x && eastWest.y < road.y + road.height && eastWest.y + eastWest.height > road.y).map((northSouth) => ({ x: northSouth.x, y: eastWest.y, width: northSouth.width, height: eastWest.height })));
    const buildings: Building[] = mapRects.filter((rect) => buildingCodes[rect.code]).map((rect) => ({ style: buildingCodes[rect.code], x: rect.col, y: rect.row, width: rect.width, height: rect.height }));
    const cityProps: CityProp[] = mapRects.filter((rect) => propCodes[rect.code]).map((rect) => ({ style: propCodes[rect.code], col: rect.col, row: rect.row, width: rect.width, height: rect.height }));
  const parkedCars: Point[] = [[8,2],[15,2],[28,2],[42,2],[71,2],[84,2],[98,2],[112,2],[9,21],[27,21],[41,21],[55,21],[72,21],[85,21],[99,21],[113,21],[54,32],[71,32],[84,32],[97,32],[111,32],[24,72],[33,72],[62,72],[70,72],[98,72],[112,72],[76,10],[76,26],[76,65],[107,12],[107,27],[107,58]].map(([col, row]) => ({ col, row }));
  const walkerRoutes: [number, number][][] = [
    [[14,44],[15,44],[16,44],[17,44],[18,44],[19,44]],[[22,45],[23,45],[24,45],[25,45],[26,45],[27,45],[28,45]],[[35,44],[36,44],[37,44],[38,44],[39,44],[40,44]],[[52,43],[53,43],[54,43],[55,43],[56,43],[57,43],[58,43]],[[62,45],[63,45],[64,45],[65,45],[66,45],[67,45]],[[82,44],[83,44],[84,44],[85,44],[86,44],[87,44]],[[33,52],[33,53],[33,54],[33,55],[33,56],[33,57]],[[47,48],[47,49],[47,50],[47,51],[47,52],[47,53]],[[55,50],[55,51],[55,52],[55,53],[55,54],[55,55]],[[62,60],[63,60],[64,60],[65,60],[66,60],[67,60]],[[78,61],[79,61],[80,61],[81,61],[82,61]],[[95,60],[96,60],[97,60],[98,60],[99,60]],[[99,59],[99,60],[99,61]],[[108,52],[109,52],[110,52],[111,53],[112,53],[113,53]],[[108,43],[109,43],[110,43],[111,43],[112,43]],[[24,10],[24,11],[24,12],[24,13],[24,14],[24,15]],[[32,24],[32,25],[32,26],[32,27],[32,28],[32,29]],[[44,9],[45,9],[46,9],[47,9],[48,9],[49,9]],[[50,14],[51,14],[52,14],[53,14]],[[62,26],[62,27],[62,28],[62,29],[62,30]],[[68,16],[69,16],[70,16],[71,16],[72,16],[73,16]],[[74,24],[74,25],[74,26],[74,27],[74,28]],[[81,10],[81,11],[81,12],[81,13],[81,14],[81,15]],[[88,26],[88,27],[88,28],[88,29],[88,30]],[[94,22],[95,22],[96,22],[97,22],[98,22]],[[102,10],[102,11],[102,12],[102,13],[102,14]],[[108,24],[109,24],[110,24],[111,24],[112,24]],[[18,26],[19,26],[19,27],[19,28],[18,28]],[[39,38],[39,39],[39,40],[39,41],[39,42]],[[74,63],[75,63],[75,64],[75,65],[74,65]]
  ];
  const patrol = (points: [number, number][]) => [...points, ...points.slice(1, -1).reverse()];
  const tourists: Tourist[] = [
    { name: 'Alex, K Street visitor', sprite: 'tourist-female', route: patrol([[4,7],[8,7],[12,7],[16,7]]) },
    { name: 'Renee, Foggy Bottom visitor', sprite: 'tourist-male', route: patrol([[20,8],[20,12],[20,16]]) },
    { name: 'Malik, 17th Street visitor', sprite: 'tourist-male', route: patrol([[34,7],[34,11],[34,15]]) },
    { name: 'Dana, Downtown visitor', sprite: 'tourist-female', route: patrol([[39,17],[43,17],[47,17]]) },
    { name: 'Adam Gruff', sprite: 'tourist-male', route: patrol([[50,14],[51,14],[52,14],[53,14]]) },
    { name: 'Priya, White House visitor', sprite: 'tourist-female', route: patrol([[58,17],[62,17],[66,17]]) },
    { name: 'Patrick Bryan', sprite: 'tourist-male', route: patrol([[68,16],[69,16],[70,16],[71,16]]) },
    { name: 'Jordan, Embassy Row visitor', sprite: 'tourist-female', route: patrol([[76,8],[76,12],[76,16]]) },
    { name: 'Tessa, Upper Downtown visitor', sprite: 'tourist-female', route: patrol([[82,17],[86,17],[90,17]]) },
    { name: 'Wes, North Capitol visitor', sprite: 'tourist-male', route: patrol([[92,8],[92,12],[92,16]]) },
    { name: 'Morgan, NoMa visitor', sprite: 'tourist-female', route: patrol([[104,7],[108,7],[112,7]]) },
    { name: 'Seth, Union Station visitor', sprite: 'tourist-male', route: patrol([[106,18],[110,18],[114,18]]) },
    { name: 'Ari, 15th Street visitor', sprite: 'tourist-female', route: patrol([[46,23],[46,27],[46,31]]) },
    { name: 'Benjamin Swifeali', sprite: 'tourist-male', route: patrol([[62,26],[62,27],[62,28],[62,29]]) },
    { name: 'Carmen, Penn Quarter visitor', sprite: 'tourist-female', route: patrol([[70,31],[74,31],[78,31]]) },
    { name: 'Mason, Judiciary Square visitor', sprite: 'tourist-male', route: patrol([[84,31],[88,31],[92,31]]) },
    { name: 'Nia, East Capitol visitor', sprite: 'tourist-female', route: patrol([[100,34],[104,34],[108,34]]) },
    { name: 'Yuki Tanaka', sprite: 'tourist-female', route: patrol([[39,42],[39,41],[39,40],[39,39]]) },
    { name: 'Cadet Owusu', sprite: 'tourist-male', route: patrol([[47,43],[47,44],[47,45],[47,46]]) },
    { name: 'Big Country Merck', sprite: 'tourist-male', route: patrol([[62,45],[63,45],[64,45],[65,45]]) },
    { name: 'Deshawn Ottley', sprite: 'tourist-male', route: patrol([[68,41],[69,41],[70,41],[71,41]]) },
    { name: 'Roadmap Higgins', sprite: 'tourist-male', route: patrol([[74,42],[74,43],[74,44],[74,45]]) },
    { name: 'The Kowalski Twins', sprite: 'tourist-female', route: patrol([[78,44],[79,44],[80,44],[81,44]]) },
    { name: 'Sister Agnes Boyle', sprite: 'tourist-female', route: patrol([[108,43],[109,43],[110,43],[111,43]]) },
    { name: 'Jenna Browner', sprite: 'tourist-female', route: patrol([[112,44],[113,44],[114,44],[115,44]]) },
    { name: 'Ranger Ruth Ibarra', sprite: 'tourist-female', route: patrol([[12,53],[13,53],[14,53],[15,53]]) },
    { name: 'Frog Seibert', sprite: 'tourist-male', route: patrol([[20,54],[20,57],[20,60],[20,63]]) },
    { name: 'Ilse Draeger', sprite: 'tourist-female', route: patrol([[24,45],[25,45],[26,45],[27,45]]) },
    { name: 'The Brennan Family', sprite: 'tourist-male', route: patrol([[32,45],[33,45],[34,45],[35,45]]) },
    { name: 'Mr. Pete Hollinger', sprite: 'tourist-male', route: patrol([[48,61],[49,61],[50,61],[51,61]]) },
    { name: 'Benno the Vendor', sprite: 'tourist-male', route: patrol([[54,62],[55,62],[56,62],[57,62]]) },
    { name: 'Mina, Museum Row visitor', sprite: 'tourist-female', route: patrol([[60,60],[64,60],[68,60],[72,60]]) },
    { name: 'Adam Doorbell', sprite: 'tourist-male', route: patrol([[84,65],[85,65],[86,65],[87,65]]) },
    { name: 'James E Tollbooth', sprite: 'tourist-male', route: patrol([[91,66],[92,66],[93,66],[94,66]]) },
    { name: 'Pat Keller', sprite: 'tourist-female', route: patrol([[100,66],[100,67],[100,68],[100,69]]) },
    { name: 'Dolores Vance', sprite: 'tourist-female', route: patrol([[108,52],[109,52],[110,52],[111,53]]) },
    { name: 'Marguerite Ffolliott', sprite: 'tourist-female', route: patrol([[112,54],[113,54],[114,54],[115,54]]) },
    { name: 'Leo, Southwest visitor', sprite: 'tourist-male', route: patrol([[8,68],[12,68],[16,68]]) },
    { name: 'Amina, Wharf visitor', sprite: 'tourist-female', route: patrol([[24,68],[28,68],[32,68]]) },
    { name: 'Cory, L Enfant visitor', sprite: 'tourist-male', route: patrol([[40,68],[44,68],[48,68]]) },
    { name: 'Simone, Federal Center visitor', sprite: 'tourist-female', route: patrol([[58,68],[62,68],[66,68]]) },
    { name: 'Victor, Southeast visitor', sprite: 'tourist-male', route: patrol([[76,68],[80,68],[84,68]]) },
    { name: 'Paige, Capitol Riverfront visitor', sprite: 'tourist-female', route: patrol([[96,68],[100,68],[104,68]]) },
    { name: 'Derek, East Side visitor', sprite: 'tourist-male', route: patrol([[108,68],[112,68],[116,68]]) }
  ];
  const cityWalkers: Tourist[] = [
    { name: 'K Street pedestrian', sprite: 'tourist-male', route: patrol([[22,7],[26,7],[30,7]]) },
    { name: 'Downtown pedestrian', sprite: 'tourist-female', route: patrol([[46,17],[50,17],[54,17]]) },
    { name: 'White House pedestrian', sprite: 'tourist-male', route: patrol([[64,22],[64,25],[64,28]]) },
    { name: 'Penn Quarter pedestrian', sprite: 'tourist-female', route: patrol([[76,31],[80,31],[84,31]]) },
    { name: 'Monument pedestrian', sprite: 'tourist-male', route: patrol([[43,41],[43,42],[43,43]]) },
    { name: 'Mall pedestrian', sprite: 'tourist-female', route: patrol([[58,45],[62,45],[66,45]]) },
    { name: 'Capitol pedestrian', sprite: 'tourist-male', route: patrol([[94,65],[98,65],[102,65]]) },
    { name: 'Library pedestrian', sprite: 'tourist-female', route: patrol([[108,55],[112,55],[116,55]]) },
    { name: 'Southwest pedestrian', sprite: 'tourist-male', route: patrol([[32,68],[36,68],[40,68]]) },
    { name: 'Riverfront pedestrian', sprite: 'tourist-female', route: patrol([[88,68],[92,68],[96,68]]) }
  ];
  const carRoutes: [number, number][][] = [
    [[0,4],[119,4]],[[119,3],[0,3]],[[0,20],[119,20]],[[119,19],[0,19]],[[0,71],[119,71]],[[119,70],[0,70]],[[77,0],[77,79]],[[78,79],[78,0]],[[91,0],[91,79]],[[92,79],[92,0]],[[105,0],[105,79]],[[106,79],[106,0]],[[21,0],[21,20],[119,20]],[[119,19],[22,19],[22,0]],[[35,0],[35,19],[0,19]],[[0,20],[36,20],[36,0]],[[47,0],[47,34],[119,34]],[[119,33],[48,33],[48,0]],[[65,0],[65,34],[119,34]],[[119,33],[66,33],[66,0]]
  ];
  function expandRoute(points: [number, number][]) { const tiles: Point[] = []; for (let i = 0; i < points.length - 1; i += 1) { const [fromCol, fromRow] = points[i]; const [toCol, toRow] = points[i + 1]; const dx = Math.sign(toCol - fromCol); const dy = Math.sign(toRow - fromRow); let current = { col: fromCol, row: fromRow }; while (current.col !== toCol || current.row !== toRow) { tiles.push({ ...current }); current = { col: current.col + dx, row: current.row + dy }; } } const [col, row] = points.at(-1)!; return [...tiles, { col, row }]; }
  const carPaths = carRoutes.map(expandRoute);
   let nearbyTourist = $derived(tourists.find((tourist, index) => {
     const position = tourist.route[(walkerStep + index * 2) % tourist.route.length];
     return Math.max(Math.abs(position[0] - col), Math.abs(position[1] - row)) <= 1;
   }));
  let nearby = $derived(spots.find((spot) => spot.id !== 'white-house' || whiteHouseOpen ? Math.max(Math.abs(spot.col - col), Math.abs(spot.row - row)) <= 1 : Math.max(Math.abs(spot.col - col), Math.abs(spot.row - row)) <= 1));
  let washingtonReady = $derived(night && notebookEntries >= 100 && !washingtonGhostComplete); let lincolnReady = $derived(night && notebookEntries >= 127 && !lincolnGhostComplete);
  let nearWashingtonGhost = $derived(washingtonReady && Math.max(Math.abs(43 - col), Math.abs(40 - row)) <= 1); let nearLincolnGhost = $derived(lincolnReady && Math.max(Math.abs(12 - col), Math.abs(54 - row)) <= 1);
  function isBlocked(nextCol: number, nextRow: number) {
    const inBuilding = buildings.some((building) => nextCol >= building.x && nextCol < building.x + building.width && nextRow >= building.y && nextRow < building.y + building.height);
     const inLandmark = spots.some((spot) => nextCol >= spot.col && nextCol < spot.col + spot.width && nextRow >= spot.row && nextRow < spot.row + spot.height);
     const inParkedCar = parkedCars.some((car) => car.col === nextCol && car.row === nextRow);
     return inBuilding || inLandmark || inParkedCar || riverTileKeys.has(`${nextCol},${nextRow}`);
  }
  function nudge(horizontal: number, vertical: number) { const nextCol = Math.max(2, Math.min(columns - 3, col + horizontal)); const nextRow = Math.max(2, Math.min(rows - 3, row + vertical)); if (!isBlocked(nextCol, nextRow)) { col = nextCol; row = nextRow; } }
   function interact() { if (nearWashingtonGhost) onwashington(); else if (nearLincolnGhost) onlincoln(); else if (nearbyTourist) ontourist(nearbyTourist.name); else if (nearby) onspot(nearby.id); }
  onMount(() => { const keydown = (event: KeyboardEvent) => { if ((event.target as HTMLElement)?.tagName === 'INPUT') return; if (event.key === 'ArrowLeft') { event.preventDefault(); nudge(-1, 0); } else if (event.key === 'ArrowRight') { event.preventDefault(); nudge(1, 0); } else if (event.key === 'ArrowUp') { event.preventDefault(); nudge(0, -1); } else if (event.key === 'ArrowDown') { event.preventDefault(); nudge(0, 1); } else if (['e', 'E', 'Enter'].includes(event.key)) { event.preventDefault(); interact(); } }; const walkers = window.setInterval(() => walkerStep += 1, 3600); const cars = window.setInterval(() => carStep += 1, 260); window.addEventListener('keydown', keydown, true); return () => { window.clearInterval(walkers); window.clearInterval(cars); window.removeEventListener('keydown', keydown, true); }; });
</script>

<main class:night class="dc-overworld-large dc-grid-overworld">
  <header><button onclick={onrotunda}>← ROTUNDA</button><div><p>WASHINGTON, D.C.</p><h1>NATIONAL <span>MALL</span></h1></div><b>{night ? 'NIGHT' : 'DAY'} · {timeLabel}</b></header>
  <section class="dc-large-view" aria-label="Explorable Washington, D.C. city map"><div class="dc-map-title" aria-hidden="true"><span>THE PEOPLE'S MAP</span><b>EXPLORE WASHINGTON</b></div><div class="dc-large-world dc-grid-plan dc-v2-plan" style={`--tile-size:${tileSize}px;transform:translate(${Math.max(-4460, Math.min(0, 650 - col * tileSize))}px,${Math.max(-2790, Math.min(0, 450 - row * tileSize))}px)`}>
    <div class="dc-ground"></div><div class="dc-river-tiles"><i></i><i></i><i></i></div>{#each roadTiles as [roadCol, roadRow]}<div class="dc-road dc-road-tile" style={`left:${roadCol * tileSize}px;top:${roadRow * tileSize}px;width:${tileSize}px;height:${tileSize}px`}></div>{/each}
    {#each buildings as building}<div class={`dc-filler ${building.style}`} style={`left:${building.x * tileSize}px;top:${building.y * tileSize}px;--building-width:${building.width * tileSize}px;--building-height:${building.height * tileSize}px`}></div>{/each}
    {#each cityProps as prop}<i class={`dc-city-prop ${prop.style}`} style={`left:${prop.col * tileSize}px;top:${prop.row * tileSize}px;--prop-width:${prop.width * tileSize}px;--prop-height:${prop.height * tileSize}px`}></i>{/each}
    <div class="dc-white-house-fence"></div>{#each parkedCars as car, index}<i class={`dc-parked-car parked-${index % 3}`} style={`left:${car.col * tileSize}px;top:${car.row * tileSize}px`}></i>{/each}
    {#each spots as spot}<button class:locked={spot.id === 'white-house' && !whiteHouseOpen} class:nearby={nearby?.id === spot.id} class={`dc-site dc-${spot.id}`} style={`left:${spot.col * tileSize}px;top:${spot.row * tileSize}px;--footprint-width:${spot.width * tileSize}px;--footprint-height:${spot.height * tileSize}px`} onclick={interact} aria-label={`Visit ${spot.label}`}><i class="dc-pack-landmark"></i><b>{spot.label}</b><small>{spot.district}</small></button>{/each}
    {#each carPaths.slice(0, 14) as route, index}{@const position = route[(carStep + index * Math.floor(route.length / 14)) % route.length]}<i class={`dc-car car-${index % 3}`} style={`left:${position.col * tileSize}px;top:${position.row * tileSize}px`}></i>{/each}
    {#each tourists as tourist, index}{@const step = (walkerStep + index * 2) % tourist.route.length}{@const position = tourist.route[step]}{#if !riverTileKeys.has(`${position[0]},${position[1]}`)}<button class:claimed={touristClaims.includes(touristInteractionId(tourist.name))} class="dc-path-walker dc-sprite-front dc-interactive-tourist" style={`left:${position[0] * tileSize}px;top:${position[1] * tileSize}px;--walk-delay:-${(index % 4) * .16}s;--sprite-image:url('/assets/sprites/${tourist.sprite}-walk.png')`} onclick={() => ontourist(tourist.name)} aria-label={`Talk to ${tourist.name}`}><b class="tourist-name">{displayName(tourist.name)}</b>{#if !touristClaims.includes(touristInteractionId(tourist.name))}<i class="tourist-alert" aria-label="Study find available">!</i>{/if}</button>{/if}{/each}
    {#each cityWalkers as walker, index}{@const step = (walkerStep + index * 2) % walker.route.length}{@const position = walker.route[step]}{#if !riverTileKeys.has(`${position[0]},${position[1]}`)}<div class="dc-path-walker dc-sprite-front dc-background-local" style={`left:${position[0] * tileSize}px;top:${position[1] * tileSize}px;--sprite-image:url('/assets/sprites/${walker.sprite}-walk.png')`}></div>{/if}{/each}
    {#each walkerRoutes as route, index}{@const step = (walkerStep + index * 2) % route.length}{@const position = route[step]}{#if !riverTileKeys.has(`${position[0]},${position[1]}`)}<div class="dc-path-walker dc-sprite-front dc-background-local" style={`left:${position[0] * tileSize}px;top:${position[1] * tileSize}px;--walk-delay:-${(index % 4) * .16}s;--sprite-image:url('/assets/sprites/${index % 2 ? 'female-congresswoman-1' : 'male-congressman-1'}-walk.png')`}></div>{/if}{/each}
    {#if washingtonReady}<button class:nearby={nearWashingtonGhost} class="dc-washington-ghost" style="left:2064px;top:1920px" onclick={onwashington}><i></i><b>GEORGE WASHINGTON</b><span>THE MONUMENT CALLS</span></button>{/if}{#if lincolnReady}<button class:nearby={nearLincolnGhost} class="dc-lincoln-ghost" style="left:576px;top:2592px" onclick={onlincoln}><i></i><b>ABRAHAM LINCOLN</b><span>THE MEMORIAL CALLS</span></button>{/if}
    <Player x={col * tileSize} y={row * tileSize} skinTone={playerSkinTone} presentation={playerPresentation} party={playerParty} />
   </div>{#if nearWashingtonGhost}<div class="dc-large-prompt"><b>E</b><span>SPEAK TO GEORGE WASHINGTON</span><small>WASHINGTON MONUMENT · NIGHT</small></div>{:else if nearLincolnGhost}<div class="dc-large-prompt"><b>E</b><span>SPEAK TO ABRAHAM LINCOLN</span><small>LINCOLN MEMORIAL · NIGHT</small></div>{:else if nearbyTourist}<div class="dc-large-prompt"><b>E</b><span>TALK TO {nearbyTourist.name.toUpperCase()}</span><small>VISITOR CONVERSATION</small></div>{:else if nearby}<div class="dc-large-prompt"><b>E</b><span>{nearby.label}</span><small>{nearby.district}</small></div>{/if}</section>
  <div class="dc-map-bottom-bar"><div><span>NOTEBOOK</span><b>{notebookEntries} / 128 ENTRIES</b></div><p>Explore landmarks, meet people, and collect civics study material.</p><button onclick={onwait}>WAIT UNTIL {night ? 'DAY' : 'NIGHT'}</button></div><div class="corner-map-controls"><button onclick={() => nudge(0, -1)}>▲</button><button onclick={() => nudge(-1, 0)}>◀</button><button class="interact" onclick={interact}>E</button><button onclick={() => nudge(1, 0)}>▶</button><button onclick={() => nudge(0, 1)}>▼</button></div>
</main>
