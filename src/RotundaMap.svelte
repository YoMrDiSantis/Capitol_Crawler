<script lang="ts">
  import { onMount } from 'svelte';
  import { clampGridPosition } from './grid';

  type RotundaPoint = { id: string; label: string; x: number; y: number; run: () => void; locked?: boolean };
  let { housePassed, tutorialComplete, playerName, playerPresentation, playerSkinTone, playerParty, onhouse, onsenate, onshop, onbill, onnotebook, onguide, onprofile, ondc, ondiscover, ontutorial }: { housePassed: boolean; tutorialComplete: boolean; playerName: string; playerPresentation: 'female' | 'male'; playerSkinTone: string; playerParty: 'D' | 'R'; onhouse: () => void; onsenate: () => void; onshop: () => void; onbill: () => void; onnotebook: () => void; onguide: () => void; onprofile: () => void; ondc: () => void; ondiscover: () => void; ontutorial: () => void } = $props();
  const tileSize = 50;
  // The spreadsheet defines a 40 x 28 map using 50 px tiles.
  const mapWidth = 2000;
  const mapHeight = 1400;
  const skinSprite: Record<string, string> = {
    '#f4d1b3': 'light', '#d8a57c': 'medium', '#ad7653': 'tan', '#754a35': 'brown', '#4c3029': 'dark'
  };
  let playerSprite = $derived(`${playerPresentation === 'male' ? `male-congressman-${playerParty === 'D' ? '1' : '2'}` : `female-congresswoman-${playerParty === 'D' ? '1' : '2'}`}-${skinSprite[playerSkinTone] ?? 'medium'}-walk.png`);
  let x = $state(1000); let y = $state(1250);
  let playfield: HTMLElement;
  let viewWidth = $state(1000);
  let viewHeight = $state(720);
  let touristStep = $state(0);
  let stepsTaken = $state(0);
  let introStage = $state<'none' | 'house-doors' | 'approaching' | 'ready' | 'departing'>('none');
  let benStep = $state(0);
  let notice = $state<'exhibit' | 'visitor' | null>(null);
  // Coordinates below are the 0-indexed cells marked in rotunda-grid-map.xlsx.
  const stations = $derived<RotundaPoint[]>([{ id:'house', label:'HOUSE FLOOR', x:100,y:700,run:onhouse },{ id:'senate',label:housePassed?'SENATE DOORS':'SENATE LOCKED',x:1900,y:700,run:onsenate,locked:!housePassed},{id:'shop',label:'ROTUNDA SHOP',x:850,y:650,run:onshop},{id:'bill',label:'BILL SCROLL',x:1150,y:750,run:onbill},{id:'guide',label:'VOCABULARY GUIDE',x:950,y:150,run:onguide},{id:'dc',label:'D.C. ENTRANCE',x:1000,y:1300,run:ondc}]);
  const points = $derived<RotundaPoint[]>([...stations, { id: 'exhibit', label: 'CIVICS EXHIBIT', x: 400, y: 650, run: () => { ondiscover(); notice = 'exhibit'; } }, { id: 'visitor', label: 'VISITOR INFO', x: 1550, y: 700, run: () => notice = 'visitor' }]);
  // A destination owns one cell and can be used from any touching cell.
  let nearby = $derived(points.find((point) => Math.max(Math.abs(point.x - x), Math.abs(point.y - y)) <= tileSize));
  let benStart = $derived({ x: 350, y: 650 });
  let benTarget = $derived({ x, y: Math.min(1250, y + 100) });
  let benPosition = $derived({
    x: Math.round(((introStage === 'departing' ? benTarget.x : benStart.x) + ((introStage === 'departing' ? benStart.x : benTarget.x) - (introStage === 'departing' ? benTarget.x : benStart.x)) * Math.min(1, benStep / 9)) / tileSize) * tileSize,
    y: Math.round(((introStage === 'departing' ? benTarget.y : benStart.y) + ((introStage === 'departing' ? benStart.y : benTarget.y) - (introStage === 'departing' ? benTarget.y : benStart.y)) * Math.min(1, benStep / 9)) / tileSize) * tileSize
  });
  let cameraFocus = $derived(introStage === 'house-doors' ? benStart : introStage === 'approaching' ? benPosition : { x, y });
  let cameraX = $derived(Math.max(viewWidth - mapWidth, Math.min(0, viewWidth / 2 - cameraFocus.x)));
  let cameraY = $derived(Math.max(viewHeight - mapHeight, Math.min(0, viewHeight / 2 - cameraFocus.y)));
  const visitorRoute = [{ x: 250, y: 650 }, { x: 300, y: 650 }, { x: 350, y: 650 }, { x: 400, y: 700 }, { x: 400, y: 750 }, { x: 350, y: 800 }, { x: 300, y: 800 }, { x: 250, y: 750 }, { x: 250, y: 700 }];
  const stafferRoute = [{ x: 850, y: 650 }, { x: 900, y: 650 }, { x: 950, y: 700 }, { x: 950, y: 750 }, { x: 900, y: 800 }, { x: 850, y: 800 }, { x: 800, y: 750 }, { x: 800, y: 700 }];
  let visitorPosition = $derived(visitorRoute[touristStep % visitorRoute.length]);
  let stafferPosition = $derived(stafferRoute[touristStep % stafferRoute.length]);
  function beginIntro() {
    introStage = 'house-doors';
    window.setTimeout(() => {
      introStage = 'approaching';
      const benWalk = window.setInterval(() => {
        benStep += 1;
        if (benStep >= 9) {
          window.clearInterval(benWalk);
          introStage = 'ready';
        }
      }, 420);
    }, 850);
  }
  function sendBenToHouse() {
    introStage = 'departing';
    benStep = 0;
    const benWalk = window.setInterval(() => {
      benStep += 1;
      if (benStep >= 9) {
        window.clearInterval(benWalk);
        introStage = 'none';
      }
    }, 360);
  }
  $effect(() => {
    if (tutorialComplete && introStage === 'ready') sendBenToHouse();
  });
  function nudge(horizontal:number,vertical:number){
    if (introStage !== 'none') return;
    const nx=clampGridPosition(x+horizontal*tileSize,50,mapWidth-50,tileSize);const ny=clampGridPosition(y+vertical*tileSize,50,mapHeight-50,tileSize);
    if(isWalkable(nx, ny) && (nx !== x || ny !== y)) {
      x=nx;y=ny;
      if (!tutorialComplete) { stepsTaken += 1; if (stepsTaken === 5) beginIntro(); }
    }
  }
  function isWalkable(px: number, py: number) {
    const col = Math.round(px / tileSize);
    const row = Math.round(py / tileSize);
    const bounds = row >= 7 && row <= 20
      ? Math.abs(col - 20) <= (row <= 13 ? row - 5 : 22 - row)
      : false;
    const inRotunda = bounds;
    const inLibrary = px >= 700 && px <= 1300 && py >= 50 && py <= 450 && (py <= 300 || (px >= 950 && px <= 1050));
    const inPortico = px >= 800 && px <= 1200 && py >= 1000 && py <= 1350;
    const inWestWing = px >= 50 && px <= 650 && py >= 550 && py <= 850 && (px <= 500 || (py >= 650 && py <= 750));
    const inEastWing = px >= 1350 && px <= 1950 && py >= 550 && py <= 850 && (px >= 1500 || (py >= 650 && py <= 750));
    return inRotunda || inLibrary || inPortico || inWestWing || inEastWing;
  }
  function interact(){if(introStage === 'ready')ontutorial();else if(introStage === 'none'&&nearby&&!nearby.locked)nearby.run()}
  onMount(()=>{const updateViewport=()=>{viewWidth=playfield?.clientWidth??1000;viewHeight=playfield?.clientHeight??720};const down=(e:KeyboardEvent)=>{if((e.target as HTMLElement)?.tagName==='INPUT')return;if(e.key==='ArrowLeft'){e.preventDefault();nudge(-1,0)}if(e.key==='ArrowRight'){e.preventDefault();nudge(1,0)}if(e.key==='ArrowUp'){e.preventDefault();nudge(0,-1)}if(e.key==='ArrowDown'){e.preventDefault();nudge(0,1)}if(['e','E','Enter'].includes(e.key)){e.preventDefault();interact()}};const touristWalk=window.setInterval(()=>touristStep+=1,900);updateViewport();window.addEventListener('resize',updateViewport);window.addEventListener('keydown',down);return()=>{window.clearInterval(touristWalk);window.removeEventListener('resize',updateViewport);window.removeEventListener('keydown',down)}})
</script>

<main class="rotunda-play-map illustrated-rotunda">
  <header><p>CAPITOL ROTUNDA</p><h1>THE <span>ROTUNDA</span></h1><b>Walk to a place and press E</b></header>
  <section class="rotunda-playfield" bind:this={playfield} aria-label="Capitol Rotunda map">
    <div class="rotunda-camera grid-room" style={`--tile-size:${tileSize}px;transform:translate(${cameraX}px,${cameraY}px)`}>
       <div class="rotunda-floor rotunda-west-wing"><b>HOUSE CORRIDOR</b><span>HOUSE FLOOR</span></div><div class="rotunda-floor rotunda-east-wing"><b>SENATE CORRIDOR</b><span>SENATE FLOOR</span></div><div class="rotunda-floor rotunda-library"><b>CONGRESSIONAL LIBRARY</b><span>STUDY NOOK</span></div><div class="rotunda-floor rotunda-portico"><b>D.C. PORTICO</b><span>START HERE</span></div><div class="portal-wall west-portal-wall-top" aria-hidden="true"></div><div class="portal-wall west-portal-wall-bottom" aria-hidden="true"></div><div class="portal-wall east-portal-wall-top" aria-hidden="true"></div><div class="portal-wall east-portal-wall-bottom" aria-hidden="true"></div><div class="rotunda-marble"></div><div class="rotunda-ink-lines" aria-hidden="true"></div><div class="rotunda-rings"></div>
      <div class="rotunda-center"><small>THE PEOPLE'S</small>CAPITOL<br/><em>ROTUNDA</em></div><div class="dome-light"></div>
       <div class="rotunda-dome-skylight" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
       <div class="arch arch-north"></div><div class="arch arch-south"></div><div class="arch arch-west"></div><div class="arch arch-east"></div>
       <div class="rotunda-prop portico-steps" aria-hidden="true"></div><div class="rotunda-prop portico-arch" aria-hidden="true"></div>
       <div class="rotunda-prop statue statue-one" aria-hidden="true"></div><div class="rotunda-prop statue statue-two" aria-hidden="true"></div><div class="rotunda-prop statue statue-three" aria-hidden="true"></div><div class="rotunda-prop statue statue-four" aria-hidden="true"></div><div class="rotunda-prop statue statue-five" aria-hidden="true"></div><div class="rotunda-prop statue statue-six" aria-hidden="true"></div><div class="rotunda-prop statue statue-seven" aria-hidden="true"></div>
       <div class="rotunda-prop wing-bench bench-west" aria-hidden="true"></div><div class="rotunda-prop wing-bench bench-east" aria-hidden="true"></div><div class="rotunda-prop wing-plaque plaque-west" aria-hidden="true"></div><div class="rotunda-prop wing-plaque plaque-east" aria-hidden="true"></div>
       <button class="shopfront" class:nearby={nearby?.id === 'shop'} onclick={onshop}><b>ROTUNDA<br/>SHOP</b><span>TOOLS · STUDY</span><i></i><i></i></button>
      <button class:nearby={nearby?.id === 'exhibit'} class="rotunda-display display-one" onclick={() => { ondiscover(); notice = 'exhibit'; }}><span>CIVICS</span><b>EXHIBIT</b><small>STUDY FIND</small></button>
      <button class:nearby={nearby?.id === 'visitor'} class="rotunda-display display-two" onclick={() => notice = 'visitor'}><span>VISITOR</span><b>INFO</b><small>PLAN YOUR VISIT</small></button>
      {#each stations as s}
        <div class:locked={s.locked} class:nearby={nearby?.id===s.id} class={`rotunda-station station-${s.id}`} style={`left:${s.x}px;top:${s.y}px`}><i aria-hidden="true"></i><b>{s.label}</b>{#if s.locked}<span>218 VOTES REQUIRED</span>{/if}</div>
      {/each}
      <div class="rotunda-tourist tourist-a" style={`left:${visitorPosition.x}px;top:${visitorPosition.y}px`}><i aria-hidden="true"></i></div><div class="rotunda-tourist tourist-b" style={`left:${stafferPosition.x}px;top:${stafferPosition.y}px`}><i aria-hidden="true"></i></div>
      {#if introStage !== 'none'}<div class:departing={introStage === 'departing'} class="ben-rotunda" style={`left:${benPosition.x}px;top:${benPosition.y}px`}><i aria-hidden="true"></i><b>MR. BEN VENELLO</b></div>{/if}
      <div class="rotunda-player" style={`left:${x}px;top:${y}px;--sprite-image:url('/assets/sprites/${playerSprite}')`}><i aria-hidden="true"></i><b>REP. {playerName}</b></div>
    </div>
    {#if introStage === 'ready'}<div class="rotunda-prompt ben-prompt"><b>E</b> · TALK TO MR. BEN VENELLO</div>{:else if introStage === 'none'&&nearby}<div class="rotunda-prompt">{nearby.locked?'218 HOUSE VOTES REQUIRED':`E · ${nearby.label}`}</div>{/if}
  </section>
  <p class="rotunda-asset-note">Character and interior art: Modern Interiors by LimeZu.</p>
  <div class="corner-map-controls"><button aria-label="Move up" onclick={() => nudge(0,-1)}>▲</button><button aria-label="Move left" onclick={() => nudge(-1,0)}>◀</button><button class="interact" onclick={interact}>E</button><button aria-label="Move right" onclick={() => nudge(1,0)}>▶</button><button aria-label="Move down" onclick={() => nudge(0,1)}>▼</button></div>
  <div class="rotunda-station-list"><button onclick={onnotebook}>NOTEBOOK</button><button onclick={onprofile}>PROFILE</button>{#each stations as s}<button class:locked={s.locked} disabled={s.locked} onclick={() => !s.locked && s.run()}>{s.label}{#if s.locked}<span>218 VOTES REQUIRED</span>{/if}</button>{/each}</div>
  {#if notice}
    <div class="modal-backdrop"><dialog class="rotunda-notice" open aria-labelledby="rotunda-notice-title">
      <button class="close" aria-label="Close" onclick={() => notice = null}>×</button>
      {#if notice === 'exhibit'}
        <p class="eyebrow">ROTUNDA CIVICS EXHIBIT</p><h2 id="rotunda-notice-title">YOUR NOTEBOOK GREW</h2>
        <p>A curator's study card has been added to your Notebook. Throughout the Capitol and D.C., look for documents, displays, and conversations like this one to build your study collection.</p>
        <a href="https://www.uscis.gov/citizenship/find-study-materials-and-resources/study-for-the-test" target="_blank" rel="noreferrer">OPEN THE OFFICIAL USCIS STUDY MATERIALS ↗</a>
      {:else}
        <p class="eyebrow">VISITOR INFORMATION</p><h2 id="rotunda-notice-title">WELCOME TO THE CAPITOL</h2>
        <p>Explore the Rotunda for study tools, your Living Bill Scroll, and routes to the House, Senate, and D.C. Follow the plaques at each archway to continue your legislative journey.</p>
        <p class="rotunda-tip">Tip: use the Notebook between conversations to review questions and accepted answers.</p>
      {/if}
      <button class="primary" onclick={() => notice = null}>RETURN TO ROTUNDA</button>
    </dialog></div>
  {/if}
</main>
