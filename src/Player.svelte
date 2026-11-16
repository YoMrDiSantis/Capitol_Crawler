<script lang="ts">
  let { x, y, skinTone = '#d8a57c', presentation = 'female', party = 'D' }: { x: number; y: number; skinTone?: string; presentation?: 'female' | 'male'; party?: 'D' | 'R' } = $props();
  const skinSprite: Record<string, string> = {
    '#f4d1b3': 'light', '#d8a57c': 'medium', '#ad7653': 'tan', '#754a35': 'brown', '#4c3029': 'dark'
  };
  let sprite = $derived(`${presentation === 'male' ? `male-congressman-${party === 'D' ? '1' : '2'}` : `female-congresswoman-${party === 'D' ? '1' : '2'}`}-${skinSprite[skinTone] ?? 'medium'}-walk.png`);
</script>

<div class="player" style={`left:${x}px;top:${y}px`} aria-label="Your character">
  <div class="player-sprite sprite-player" style={`--sprite-image:url('/assets/sprites/${sprite}')`}><i aria-hidden="true"></i></div>
</div>
