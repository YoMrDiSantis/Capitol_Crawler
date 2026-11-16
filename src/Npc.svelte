<script lang="ts">
  import type { Encounter } from './game';

  let { encounter, completed, locked, onHold = false, nearby, paused = false, oninteract }: { encounter: Encounter; completed: boolean; locked: boolean; onHold?: boolean; nearby: boolean; paused?: boolean; oninteract: (encounter: Encounter) => void } = $props();
  const specificSprites: Record<string, string> = {
    'wren-castellano': 'wren-castellano-walk.png',
    'sarah-sterling': 'sarah-sterling-walk.png',
    'diane-okafor': 'diane-okafor-walk.png',
    'eleanor-vance': 'eleanor-vance-walk.png',
    'regina-alvarez': 'regina-alvarez-walk.png',
    'lucia-marchetti': 'lucia-marchetti-walk.png',
    'augustus-kane': 'augustus-kane-walk.png',
    'tom-bracewell': 'tom-bracewell-walk.png',
    'marcus-vance': 'marcus-vance-walk.png'
  };
  const femaleLeaders = ['wren-castellano', 'sarah-sterling', 'diane-okafor', 'eleanor-vance', 'regina-alvarez', 'lucia-marchetti', 'priya-okafor-lin', 'selena-marsh', 'alma-judd', 'naomi-cho', 'robin-yates', 'ines-falkenrath', 'ada-boykin', 'corinne-vasquez', 'bee-nakamura'];
  let partySprite = $derived(encounter.polarization <= 50 ? '1' : '2');
  let sprite = $derived(`/assets/sprites/${specificSprites[encounter.id] ?? `${femaleLeaders.includes(encounter.id) ? 'female-congresswoman' : 'male-congressman'}-${partySprite}-walk.png`}`);
</script>

<button class:nearby class:completed class="npc" style={`left:${encounter.x}px;top:${encounter.y}px;--vote-marker-size:${Math.min(46, 22 + Math.ceil(encounter.votes / 5) * 3)}px`} disabled={completed || locked || paused} onclick={() => oninteract(encounter)} aria-label={`Talk to ${encounter.name}`}>
  {#if completed}<div class="check" aria-label="Support secured">✓</div>{:else if locked}<div class="locked" aria-label="No further meeting">×</div>{:else if onHold}<div class="hold" aria-label="Hold active">H</div>{:else}<div class="available" aria-label="Available to talk">!</div>{/if}
  <div class="npc-sprite senate-token sprite-npc" style={`--npc-color:${encounter.color}`} aria-hidden="true"><img class="npc-sprite-image" src={sprite} alt="" /><span>{encounter.portrait}</span></div>
  <div class="nameplate">
    <strong>{encounter.name}</strong>
  </div>
  {#if nearby && !completed && !locked}<div class="talk-prompt">E · TALK</div>{/if}
</button>
