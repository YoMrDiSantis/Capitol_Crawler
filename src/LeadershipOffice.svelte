<script lang="ts">
  import { onMount } from 'svelte';

  let { recovered, onrecover, onreturn }: { recovered: boolean; onrecover: () => void; onreturn: () => void } = $props();
  let room = $state<'waiting' | 'office'>('waiting');
  let secretaryGreetingOpen = $state(false);

  onMount(() => { secretaryGreetingOpen = !recovered; });

  function enterOffice() {
    secretaryGreetingOpen = false;
    room = 'office';
  }

  function recoverBriefcase() {
    onrecover();
  }
</script>

<main class="abbonizio-office">
  <header>
    <button onclick={onreturn}>← SENATE</button>
    <div><p>SENATE LEADERSHIP CORRIDOR</p><h1>SEN. ABBONIZIO'S <span>OFFICE</span></h1></div>
    <b>{recovered ? 'DELIVERY COMPLETE' : 'BRIEFCASE RECOVERY'}</b>
  </header>

  {#if room === 'waiting'}
    <section class="abbonizio-room waiting-room" aria-label="Senator Luciana Abbonizio's waiting room">
      <img src="/assets/luciana-disantis-office-waiting-room.png" alt="Senator Luciana Abbonizio's waiting room" />
      <button class="office-screen" onclick={enterOffice} aria-label="Enter Senator Abbonizio's office"><span>ENTER OFFICE</span></button>
      <button class="room-return" onclick={onreturn}>RETURN TO SENATE CORRIDOR</button>
    </section>
  {:else}
    <section class="abbonizio-room inner-office" aria-label="Senator Luciana Abbonizio's office">
      <img src="/assets/luciana-disantis-office.png" alt="Senator Luciana Abbonizio's office" />
      {#if !recovered}
        <button class="office-briefcase" onclick={recoverBriefcase} aria-label="Pick up Luciana Abbonizio's briefcase">
          <img src="/assets/luciana-disantis-briefcase.png" alt="" />
          <span>PICK UP BRIEFCASE</span>
        </button>
      {:else}
        <p class="briefcase-recovered">BRIEFCASE SECURED</p>
      {/if}
      <button class="room-return" onclick={() => room = 'waiting'}>RETURN TO WAITING ROOM</button>
    </section>
  {/if}

  {#if secretaryGreetingOpen}
    <div class="modal-backdrop"><dialog class="office-secretary-dialogue" open aria-labelledby="secretary-title">
      <p class="eyebrow">OFFICE SECRETARY</p><h2 id="secretary-title">WELCOME TO SEN. ABBONIZIO'S OFFICE</h2>
      <p>Oh - new face! You must be one of ours. This is Senator Abbonizio's office, but she's already headed to the floor - in a rush, as usual, which means she forgot her briefcase again.</p>
      <p>She needs it before the vote starts. The screen will let you into her office. Find the briefcase and get moving, would you? She's not going to be happy waiting.</p>
      <p>Corridor's back that way when you're ready. Don't get lost - this place eats freshmen alive.</p>
      <button class="primary" onclick={() => secretaryGreetingOpen = false}>I'LL GET IT →</button>
    </dialog></div>
  {/if}
</main>
