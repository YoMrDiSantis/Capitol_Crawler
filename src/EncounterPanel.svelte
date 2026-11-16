<script lang="ts">
  import { onDestroy } from 'svelte';
  import { isCorrectCivicsAnswer } from './civics-validation';
  import { displayChoice, questionChoices, type Encounter } from './game';
  import { civicsConfirmation, civicsStudyNotes, type CivicsQuestion } from './civics-questions';
  import { officeholderDataLastVerified } from './officeholders';
  import type { Inventory, PowerUpId } from './RotundaShop.svelte';
  import { dialogueFor, traitCopy, type Trait } from './npc-dialogue';
  import Portrait from './Portrait.svelte';

  let {
    encounter,
    question,
    attempt,
    inventory,
    onuseitem,
    rapportBonus = 0,
    playerName,
    rapport = 50,
    onrapport,
    activeTrait,
    alternativeTrait,
    hasRapport = true,
    isExtreme = false,
    resolveDynamicAnswer,
    onskipdynamic,
    oncomplete,
    onclose
  }: {
    encounter: Encounter;
    question: CivicsQuestion;
    attempt: number;
    inventory: Inventory;
    onuseitem: (item: PowerUpId) => boolean;
    rapportBonus?: number;
    playerName: string;
    rapport?: number;
    onrapport: (choice: Trait | 'neutral') => { rapport: number; message: string };
    activeTrait: Trait;
    alternativeTrait: Trait;
    hasRapport?: boolean;
    isExtreme?: boolean;
    resolveDynamicAnswer: (question: CivicsQuestion, answer: string) => boolean | undefined;
    onskipdynamic: () => void;
    oncomplete: (correct: boolean) => void;
    onclose: () => void;
  } = $props();

  let stage = $state<'greeting' | 'background' | 'rapport' | 'question' | 'feedback'>('greeting');
  let answer = $state('');
  let correct = $state(false);
  let removedChoice = $state<string | null>(null);
  let hearingAidUsed = $state(false);
  let secondsRemaining = $state(30);
  let coffeePaused = $state(false);
  let timer: ReturnType<typeof setInterval> | undefined;
  let coffeeTimer: ReturnType<typeof setTimeout> | undefined;
  let dialogue = $derived(dialogueFor(encounter.id));
  let firstPersonBackground = $derived(
    dialogue.background
      .replace(new RegExp(`^${encounter.name.split(' ')[0]}\\b`), 'I')
      .replace(/^I ([a-z]+)ed\b/, 'I $1')
      .replace(/^I ([a-z]+)nt\b/, 'I $1')
      .replace(/^I was\b/, 'I am')
  );
  let rapportResult = $state('');

  function stopTimer() {
    if (timer) clearInterval(timer);
    timer = undefined;
  }

  // A single opening choice moves standard Rapport from 50 to either 65 or 35.
  // Those results must immediately affect this encounter rather than only a future visit.
  let encounterRapport = $state(50);
  $effect(() => { encounterRapport = rapport; });
  let rapportTier = $derived(encounterRapport >= 65 ? 'friendly' : encounterRapport <= 35 ? 'hostile' : 'neutral');
  let baseChoiceCount = $derived(encounter.mode === 'matrix' ? 12 : encounter.mode === 'multiple' ? (Math.abs(50 - encounter.polarization) <= 5 ? 3 : 4) : 0);
  let choiceCount = $derived(baseChoiceCount);
  let displayedPrompt = $derived(encounter.mode === 'mumbled'
    ? question.prompt.split(/(\s+)/).map((part, index) => index % (rapportTier === 'friendly' ? 5 : 3) === 0 && part.trim().length > 3 ? '...' : part).join('')
    : question.prompt);
  let isCurrentOfficeholderQuestion = $derived([23, 30, 38, 39, 57, 61].includes(question.id));

  function startTimer() {
    stopTimer();
    secondsRemaining = (encounter.mode === 'short' || encounter.mode === 'mumbled') ? (rapportTier === 'friendly' ? 75 : rapportTier === 'hostile' ? 45 : 60) : 30;
    timer = setInterval(() => {
      if (coffeePaused) return;
      secondsRemaining -= 1;
      if (secondsRemaining <= 0) {
        stopTimer();
        correct = false;
        stage = 'feedback';
      }
    }, 1000);
  }

  function submit(value = answer) {
    if (!value.trim()) return;
    const tolerance = rapportTier === 'friendly' ? 3 : rapportTier === 'hostile' ? 1 : 2;
    const isValid = isCorrectCivicsAnswer(question, value, encounter.mode === 'short' || encounter.mode === 'mumbled' ? tolerance : 0, resolveDynamicAnswer);
    if (isValid) { stopTimer(); correct = true; stage = 'feedback'; return; }
    stopTimer(); correct = false; stage = 'feedback';
  }

  function finish() {
    stopTimer();
    (document.activeElement as HTMLElement | null)?.blur();
    oncomplete(correct);
  }

  function useItem(item: PowerUpId) {
    if (onuseitem(item)) {
      if (item === 'memo') {
          const incorrect = questionChoices(question, choiceCount)
          .find((choice) => !question.acceptedAnswers.includes(choice));
        removedChoice = incorrect ?? null;
      }
      if (item === 'hearingAid') hearingAidUsed = true;
      if (item === 'coffee') {
        coffeePaused = true;
        if (coffeeTimer) clearTimeout(coffeeTimer);
        coffeeTimer = setTimeout(() => { coffeePaused = false; }, 15000);
      }
    }
  }

  onDestroy(() => {
    stopTimer();
    if (coffeeTimer) clearTimeout(coffeeTimer);
  });
</script>

<div class="modal-backdrop" role="presentation">
  <dialog class="dialog-panel" open aria-labelledby="speaker">
    <header class="speaker">
        <Portrait character="npc" name={encounter.name} initials={encounter.portrait} mood={stage === 'feedback' && correct ? 'pleased' : stage === 'greeting' ? 'thoughtful' : 'neutral'} />
      <div>
        <p>{encounter.affiliation}</p>
        <h2 id="speaker">REP. {encounter.name.toUpperCase()}</h2>
        <span>{encounter.votes} votes at stake{rapportBonus ? ` · +${rapportBonus} Rapport` : ''}</span>
      </div>
      <button class="close" aria-label="Leave conversation" onclick={() => { (document.activeElement as HTMLElement | null)?.blur(); onclose(); }}>×</button>
    </header>

    {#if stage === 'greeting'}
      <div class="dialog-copy conversation-copy">
        <div>
          <p class="speaker-line"><b>{encounter.name}:</b> {rapportBonus ? `Representative ${playerName}, ${encounter.greeting}` : `Representative ${playerName}, ${encounter.greeting}`}</p>
          <p class="player-line"><b>YOU:</b> I am here to build support for the Connected Schools Act.</p>
          {#if !isExtreme}
            <p class="trait-tell">{traitCopy[activeTrait]?.tell ?? 'They are listening carefully for the kind of case you make.'}</p>
          {:else}
            <p class="trait-tell">This leader gives no reliable tell. Optional scouting can reveal what they value.</p>
          {/if}
        </div>
      </div>
       <div class="dialog-actions"><button class="primary" onclick={() => stage = 'background'}>TELL ME ABOUT YOURSELF →</button><button class="text-button" onclick={() => { if (hasRapport) stage = 'rapport'; else { stage = 'question'; startTimer(); } }}>SKIP TO THE BILL</button></div>
    {:else if stage === 'background'}
      <div class="dialog-copy conversation-copy">
        <div>
          <p class="speaker-line"><b>{encounter.name}:</b> {firstPersonBackground}</p>
          <p class="player-line"><b>YOU:</b> Thanks for sharing that. I am ready to talk about the bill.</p>
        </div>
      </div>
      <button class="primary" onclick={() => { if (hasRapport) stage = 'rapport'; else { stage = 'question'; startTimer(); } }}>MAKE YOUR CASE →</button>
    {:else if stage === 'rapport'}
        <div class="dialog-copy rapport-copy"><span class="quote">“</span><div><p>{dialogue.prompt}</p><div class="rapport-options"><button onclick={() => { const result = onrapport(activeTrait); encounterRapport = result.rapport; rapportResult = result.message; stage = 'question'; startTimer(); }}>{traitCopy[activeTrait].response}</button><button onclick={() => { const result = onrapport(alternativeTrait); encounterRapport = result.rapport; rapportResult = result.message; stage = 'question'; startTimer(); }}>{traitCopy[alternativeTrait].response}</button><button onclick={() => { const result = onrapport('neutral'); encounterRapport = result.rapport; rapportResult = result.message; stage = 'question'; startTimer(); }}>{dialogue.neutral}</button></div><p class="rapport-status">Current Rapport: {encounterRapport} / 100</p></div></div>
    {:else if stage === 'question'}
        <div class="question-heading">
          <span>USCIS CIVICS · QUESTION {question.id} · ATTEMPT {attempt}</span>
        <strong>{encounter.mode === 'matrix' || encounter.mode === 'multiple' ? `${choiceCount}-CHOICE` : encounter.mode === 'mumbled' ? 'MUMBLED RESPONSE' : 'OPEN RESPONSE'} · {coffeePaused ? 'COFFEE BREAK' : `${secondsRemaining}s`}</strong>
      </div>
       <h3 class:mumbled-prompt={encounter.mode === 'mumbled'}>{displayedPrompt}</h3>
       {#if rapportResult}<p class="rapport-result">{rapportResult}</p>{/if}
       {#if isCurrentOfficeholderQuestion}<p class="hint"><strong>Current-official answer tip:</strong> A last name is usually enough. Include a first name only if more than one relevant official shares that last name. Last verified: {officeholderDataLastVerified}.</p>{/if}
      {#if question.id === 29}<button class="item-use" onclick={onskipdynamic}>FIND OR SKIP YOUR REPRESENTATIVE QUESTION</button>{/if}
        {#if rapportTier === 'friendly'}<p class="hint">Friendly Rapport: {encounter.hint ?? 'Look for the constitutional or civic principle at the heart of the question.'}{#if encounter.mode === 'short' || encounter.mode === 'mumbled'} You also have extra time.{/if}</p>{:else if encounter.mode === 'short' && rapportTier !== 'hostile'}<p class="hint">{encounter.hint ?? 'Context hint: identify the constitutional or civic principle at the heart of the question.'}</p>{:else if rapportTier === 'hostile'}<p class="hint">Hostile Rapport: this colleague is keeping the conversation brief. A precise answer can still win their support.</p>{/if}
      {#if hearingAidUsed}<p class="hint">Hearing Aid active: the question text is as clear as possible.</p>{/if}
       {#if inventory.memo > 0 && choiceCount > 0}<button class="item-use" onclick={() => useItem('memo')}>USE TALKING POINTS MEMO · {inventory.memo}</button>{/if}
       {#if inventory.hearingAid > 0 && encounter.mode === 'mumbled'}<button class="item-use" onclick={() => useItem('hearingAid')}>USE HEARING AID · {inventory.hearingAid}</button>{/if}
      {#if inventory.coffee > 0 && !coffeePaused}<button class="item-use" onclick={() => useItem('coffee')}>USE CAFETERIA COFFEE · {inventory.coffee}</button>{/if}

       {#if encounter.mode === 'short' || encounter.mode === 'mumbled'}
        <form onsubmit={(event) => { event.preventDefault(); submit(); }}>
          <label for="answer">Type your answer</label>
          <input id="answer" bind:value={answer} autocomplete="off" placeholder="Your answer..." />
          <button class="primary" type="submit" disabled={!answer.trim()}>SUBMIT ANSWER</button>
        </form>
      {:else}
        <div class:matrix={encounter.mode === 'matrix'} class="choices">
           {#each questionChoices(question, choiceCount).filter((choice) => choice !== removedChoice) as choice}
            <button onclick={() => submit(displayChoice(question, choice))}>{displayChoice(question, choice)}</button>
          {/each}
        </div>
      {/if}
    {:else}
      <div class:wrong={!correct} class="feedback">
  <span class="feedback-icon">{correct ? '✓' : '×'}</span>
        <h3>{correct ? 'SUPPORT SECURED' : 'NOT QUITE'}</h3>
        <p>{correct ? `${civicsConfirmation(question)} ${dialogue.success}` : `One accepted answer is “${question.acceptedAnswers[0]}.” ${attempt === 1 ? dialogue.firstMiss : dialogue.locked}`}</p>
        {#if !correct && civicsStudyNotes[question.id]}<p class="study-explanation"><strong>Study note:</strong> {civicsStudyNotes[question.id]}</p>{/if}
        {#if correct}<strong>+{encounter.votes} VOTES · +{encounter.mode === 'multiple' ? 15 : encounter.mode === 'short' ? 25 : 40} INF</strong>{/if}
      </div>
      <button class="primary" onclick={finish}>{correct ? 'RETURN TO THE FLOOR' : 'REVIEW & RETURN'}</button>
    {/if}
  </dialog>
</div>
