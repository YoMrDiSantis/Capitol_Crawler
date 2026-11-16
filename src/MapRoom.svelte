<script lang="ts">
  import { onMount } from 'svelte';
  import { clampGridPosition } from './grid';
  import Player from './Player.svelte';

  type RoomId = 'west-cloakroom' | 'east-cloakroom' | 'west-caucus' | 'east-caucus';
  type StudyFind = { question: string; answer: string };
  let { roomId, title, description, source, discovered, scoutAvailable, scoutTargets, playerSkinTone, playerPresentation, playerParty, ondiscover, onnotebook, onscout, onreturn }: { roomId: RoomId; title: string; description: string; source: string; discovered: boolean; scoutAvailable: boolean; scoutTargets: readonly string[]; playerSkinTone: string; playerPresentation: 'female' | 'male'; playerParty: 'D' | 'R'; ondiscover: (source: string) => StudyFind | undefined; onnotebook: () => void; onscout: () => void; onreturn: () => void } = $props();
  const tileSize = 50;
  let x = $state(500);
  let y = $state(700);
  let staffOpen = $state(false);
  let scoutOpen = $state(false);
  let studyOpen = $state<StudyFind | null>(null);
  let staffVisits = $state(0);
  let nearbyFind = $derived(Math.max(Math.abs(x - 200), Math.abs(y - 300)) <= tileSize);
  let nearbyStaff = $derived(Math.max(Math.abs(x - 800), Math.abs(y - 300)) <= tileSize);
  let nearExit = $derived(y >= 700);
  let roomClass = $derived(`house-room-map ${roomId}`);
  let cameraY = $derived(Math.max(-180, Math.min(0, 360 - y)));
  let scoutLabel = $derived(roomId === 'west-caucus' ? 'CAUCUS RESEARCHER' : roomId === 'east-caucus' ? 'DISTRICT AIDE' : roomId === 'west-cloakroom' ? 'CLOAKROOM STAFFER' : 'MESSAGE BOARD INTERN');
  let staffCopy = $derived(roomId === 'west-caucus'
    ? '“I have watched Rep. Priya Anand and Rep. Diane Okafor. Priya wants proof the bill will work: mention evidence, repairs, and teacher training. Diane wants a plan people can count on after the cameras leave. Tell her exactly who will do the work and how it will be paid for. Use those ideas in their Rapport conversations.”'
    : roomId === 'east-caucus'
      ? '“I have a read on Rep. Selena Marsh and Rep. Robin Yates. Selena listens for teamwork: say you will listen to different groups and build common ground. Robin wants a practical reason to trust the bill: name one real result for schools, then explain the plan for making it happen. Use those ideas in their Rapport conversations.”'
      : roomId === 'west-cloakroom'
        ? '“Rep. Hank Delgado and Rep. Gus Whitfield are the people to watch. Hank wants to know if the bill will work on a busy Monday in a real school. Gus wants proof that equipment, repairs, and training are planned. Give each one a practical answer in their Rapport conversation.”'
        : '“I have notes on Rep. Naomi Cho and Rep. Cyrus Boone. Naomi wants a plain explanation that families can understand. Cyrus wants proof you did your homework and know the rules. Use those ideas in their Rapport conversations.”');
  let staffEasterEgg = $derived(roomId === 'east-caucus'
    ? 'The District Aide shuts the folder with a sigh. “Again? Please stop bothering me. If you need another voice from the past, people say Lincoln still listens at the Memorial after dark.”'
    : roomId === 'west-caucus'
      ? 'The Caucus Researcher rubs their temples. “That is six times. Please stop bothering me. Try the Monument at night instead. Some visitors swear Washington is still out there.”'
      : roomId === 'west-cloakroom'
        ? 'The Cloakroom Staffer straightens a coat tag. “You have asked enough. People whisper that Washington walks near the Monument after dark. Go ask a ghost, not me.”'
        : 'The intern points toward the exit. “You have asked enough questions for one day. I heard Lincoln’s ghost may be a better listener at the Memorial after dark.”');

  function nudge(horizontal: number, vertical: number) {
    x = clampGridPosition(x + horizontal * tileSize, 50, 950, tileSize);
    y = clampGridPosition(y + vertical * tileSize, 50, 750, tileSize);
  }
  function returnToHouse() {
    staffOpen = false;
    scoutOpen = false;
    (document.activeElement as HTMLElement | null)?.blur();
    onreturn();
  }
  function interact() {
    if (nearbyFind && !discovered) studyOpen = ondiscover(source) ?? null;
    else if (nearbyFind || nearbyStaff) { staffVisits += 1; staffOpen = true; }
    else if (nearExit) returnToHouse();
  }
  onMount(() => {
    const keydown = (event: KeyboardEvent) => {
      if ((event.target as HTMLElement)?.tagName === 'INPUT' || staffOpen) return;
      if (event.key === 'ArrowLeft') { event.preventDefault(); nudge(-1, 0); }
      else if (event.key === 'ArrowRight') { event.preventDefault(); nudge(1, 0); }
      else if (event.key === 'ArrowUp') { event.preventDefault(); nudge(0, -1); }
      else if (event.key === 'ArrowDown') { event.preventDefault(); nudge(0, 1); }
      else if (['e', 'E', 'Enter'].includes(event.key)) { event.preventDefault(); interact(); }
    };
    window.addEventListener('keydown', keydown, true);
    return () => window.removeEventListener('keydown', keydown, true);
  });
</script>

<div class="house-room-overlay">
<main class={roomClass}>
  <header><button onclick={returnToHouse}>← HOUSE FLOOR</button><div><p>HOUSE SIDE ROOM</p><h1>{title}</h1></div><b>Explore the room</b></header>
  <section class="house-room-playfield grid-room modern-interior-room" style={`--tile-size:${tileSize}px`}>
    <div class="room-camera" style={`transform:translateY(${cameraY}px)`}>
    <div class="room-bookshelf"><b>REFERENCE SHELF</b></div><div class="room-coat-rack"><b>COATS</b></div><div class="room-table-large"><b>{roomId.includes('caucus') ? 'CAUCUS TABLE' : 'WORK TABLE'}</b><i></i><i></i><i></i></div><div class="room-chairs"><i></i><i></i><i></i></div>
    {#if roomId.includes('caucus')}<div class="room-caucus-members" class:east-party={roomId === 'east-caucus'} aria-hidden="true"><i></i><i></i><i></i></div>{/if}
    <button class:found={discovered} class="room-study-find" onclick={() => { if (!discovered) studyOpen = ondiscover(source) ?? null; else staffOpen = true; }}><span>{discovered ? '✓' : '✦'}</span><b>{discovered ? 'STUDY FIND LOGGED' : 'REFERENCE MATERIAL'}</b></button>
    <button class="room-staffer" onclick={() => { staffVisits += 1; staffOpen = true; }}><i aria-hidden="true"></i><b>{scoutLabel}</b></button>
    <button class:scouted={scoutAvailable} class="room-scout" onclick={() => scoutOpen = true}><span>◎</span><b>{scoutAvailable ? 'SCOUT INTEL LOGGED' : scoutLabel}</b></button>
    <Player {x} {y} skinTone={playerSkinTone} presentation={playerPresentation} party={playerParty} />
    </div>
    {#if nearbyStaff}<div class="room-prompt">E · TALK TO {scoutLabel}</div>{:else if nearbyFind}<div class="room-prompt">E · {discovered ? 'ASK ABOUT REFERENCE MATERIAL' : 'SEARCH REFERENCE MATERIAL'}</div>{:else if nearExit}<div class="room-prompt">E · RETURN TO HOUSE FLOOR</div>{/if}
  </section>
  <div class="corner-map-controls"><button onclick={() => nudge(0,-1)}>▲</button><button onclick={() => nudge(-1,0)}>◀</button><button class="interact" onclick={interact}>E</button><button onclick={() => nudge(1,0)}>▶</button><button onclick={() => nudge(0,1)}>▼</button></div>
  <footer>{description}</footer>
</main>
</div>

  {#if staffOpen}<div class="modal-backdrop"><dialog class="house-room-dialog" open><button class="close" onclick={() => { staffOpen = false; (document.activeElement as HTMLElement | null)?.blur(); }}>×</button><header><i aria-hidden="true"></i><div><p>{scoutLabel}</p><h2>{staffVisits >= 6 ? 'ENOUGH QUESTIONS' : 'A QUICK WORD'}</h2></div></header><section class="room-dialogue"><p><b>{scoutLabel}:</b> {staffVisits >= 6 ? staffEasterEgg : staffCopy}</p></section><button class="primary" onclick={() => { staffOpen = false; (document.activeElement as HTMLElement | null)?.blur(); }}>{staffVisits >= 6 ? 'LEAVE THEM ALONE →' : 'THANKS, I WILL TRY THAT →'}</button></dialog></div>{/if}
  {#if studyOpen}<div class="modal-backdrop"><dialog class="house-room-dialog study-find-dialog" open><button class="close" aria-label="Close study find" onclick={() => studyOpen = null}>×</button><header><i aria-hidden="true"></i><div><p>REFERENCE SHELF</p><h2>NOTEBOOK UPDATED</h2></div></header><section class="room-dialogue"><p><b>Study sheet:</b> {studyOpen.question}</p><p class="accepted-answer"><b>Accepted answer:</b> {studyOpen.answer}</p><p>You earned 15 INF. This question and its answers are now saved in your Notebook.</p></section><button class="primary" onclick={() => { studyOpen = null; onnotebook(); }}>OPEN NOTEBOOK →</button><button class="text-button room-continue" onclick={() => studyOpen = null}>KEEP EXPLORING</button></dialog></div>{/if}
{#if scoutOpen}<div class="modal-backdrop"><dialog class="house-room-dialog" open><button class="close" onclick={() => scoutOpen = false}>×</button><p class="eyebrow">{scoutLabel}</p><h2>SCOUTING INTEL</h2><p>“I have watched the floor long enough to know that every Representative listens for something different. I can give you one useful read, but you still have to make the right case.”</p><p class="room-note">Use the clue in the leader’s Rapport conversation. Strong Rapport can make an encounter easier; scouting never supplies an answer.</p><button class="primary" onclick={() => { onscout(); scoutOpen = false; }}>LOG INTEL →</button></dialog></div>{/if}
