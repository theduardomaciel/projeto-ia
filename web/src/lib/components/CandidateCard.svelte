<script lang="ts">
  import type { CandidateResult } from "$lib/types";
  import { fade } from "svelte/transition";

  export let candidate: CandidateResult;

  $: normalizedScore = Math.min(100, Math.max(0, candidate.match_score));
</script>

<article
  class="rounded-3xl border border-slate-100 bg-white/90 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
  transition:fade
>
  <header class="flex items-center justify-between">
    <div>
      <p class="text-xs uppercase tracking-widest text-slate-400">
        Posição #{candidate.ranking_position}
      </p>
      <h3 class="text-xl font-semibold text-slate-800">
        {candidate.candidate_name}
      </h3>
    </div>
    <div class="text-right">
      <p class="text-xs font-semibold text-slate-500">Match</p>
      <p class="text-3xl font-bold text-primary-600">
        {normalizedScore.toFixed(0)}<span class="text-base">%</span>
      </p>
    </div>
  </header>

  <div class="mt-4">
    <div
      class="flex items-center justify-between text-xs font-semibold text-slate-500"
    >
      <span>Compatibilidade com a vaga</span>
      <span>{normalizedScore.toFixed(0)}%</span>
    </div>
    <div class="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-100">
      <div
        class="h-full rounded-full bg-linear-to-r from-primary-400 via-primary-500 to-primary-600"
        style={`width:${normalizedScore}%`}
      ></div>
    </div>
  </div>

  <div class="mt-5 grid gap-4 md:grid-cols-2">
    <section>
      <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">
        Hard skills
      </p>
      <div class="mt-2 flex flex-wrap gap-2">
        {#if candidate.hard_skills.length}
          {#each candidate.hard_skills as skill}
            <span
              class="rounded-full bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700"
              >{skill}</span
            >
          {/each}
        {:else}
          <span class="text-sm text-slate-400">Nenhuma identificada</span>
        {/if}
      </div>
    </section>
    <section>
      <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">
        Soft skills
      </p>
      <div class="mt-2 flex flex-wrap gap-2">
        {#if candidate.soft_skills.length}
          {#each candidate.soft_skills as skill}
            <span
              class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700"
              >{skill}</span
            >
          {/each}
        {:else}
          <span class="text-sm text-slate-400">Nenhuma identificada</span>
        {/if}
      </div>
    </section>
  </div>

  <section class="mt-5 rounded-2xl bg-slate-50/80 p-4 text-sm text-slate-600">
    <p class="text-xs font-semibold uppercase tracking-wider text-slate-500">
      Justificativa
    </p>
    <p class="mt-2 leading-relaxed">{candidate.explanation}</p>
  </section>
</article>
