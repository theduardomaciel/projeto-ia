<script lang="ts">
  import type { CandidateResult } from "$lib/types";
  import { fade } from "svelte/transition";

  export let candidate: CandidateResult;

  $: normalizedScore = Math.min(100, Math.max(0, candidate.match_score));
</script>

<article
  class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6 shadow-sm transition hover:shadow-md"
  transition:fade
>
  <header class="flex items-start justify-between gap-4">
    <div class="flex-1">
      <p
        class="text-xs font-medium uppercase tracking-wider text-slate-400 dark:text-slate-500"
      >
        Posição #{candidate.ranking_position}
      </p>
      <h3 class="mt-1 text-lg font-semibold text-slate-900 dark:text-white">
        {candidate.candidate_name}
      </h3>
    </div>
    <div class="flex flex-col items-end">
      <p class="text-xs font-medium text-slate-500 dark:text-slate-400">
        Match
      </p>
      <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">
        {normalizedScore.toFixed(0)}<span class="text-sm">%</span>
      </p>
    </div>
  </header>

  <div class="mt-4">
    <div
      class="flex items-center justify-between text-xs font-medium text-slate-600 dark:text-slate-400"
    >
      <span>Compatibilidade</span>
      <span>{normalizedScore.toFixed(0)}%</span>
    </div>
    <div
      class="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700"
    >
      <div
        class="h-full rounded-full bg-linear-to-r from-slate-500 to-slate-600 transition-all"
        style={`width:${normalizedScore}%`}
      ></div>
    </div>
  </div>

  <div class="mt-6 grid gap-4 md:grid-cols-2">
    <section>
      <p
        class="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
      >
        Hard skills
      </p>
      <div class="mt-2 flex flex-wrap gap-1.5">
        {#if candidate.hard_skills.length}
          {#each candidate.hard_skills as skill}
            <span
              class="rounded-lg bg-primary-50 dark:bg-primary-900/30 px-2.5 py-1 text-xs font-medium text-primary-700 dark:text-primary-300"
              >{skill}</span
            >
          {/each}
        {:else}
          <span class="text-xs text-slate-400 dark:text-slate-500"
            >Nenhuma identificada</span
          >
        {/if}
      </div>
    </section>
    <section>
      <p
        class="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
      >
        Soft skills
      </p>
      <div class="mt-2 flex flex-wrap gap-1.5">
        {#if candidate.soft_skills.length}
          {#each candidate.soft_skills as skill}
            <span
              class="rounded-lg bg-emerald-50 dark:bg-emerald-900/30 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-300"
              >{skill}</span
            >
          {/each}
        {:else}
          <span class="text-xs text-slate-400 dark:text-slate-500"
            >Nenhuma identificada</span
          >
        {/if}
      </div>
    </section>
  </div>

  <section class="mt-6 rounded-xl bg-slate-50 dark:bg-slate-900/50 p-4">
    <p
      class="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
    >
      Justificativa
    </p>
    <p class="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
      {candidate.explanation}
    </p>
  </section>
</article>
