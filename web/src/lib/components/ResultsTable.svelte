<script lang="ts">
  import type { CandidateResult, SortDirection, SortKey } from "$lib/types";
  import { createEventDispatcher } from "svelte";

  export let results: CandidateResult[] = [];
  export let sortKey: SortKey = "ranking_position";
  export let sortDirection: SortDirection = "asc";

  const dispatch = createEventDispatcher<{ sort: SortKey }>();

  function toggleSort(key: SortKey) {
    dispatch("sort", key);
  }

  function iconFor(key: SortKey) {
    if (sortKey !== key) return "⇅";
    return sortDirection === "asc" ? "↑" : "↓";
  }
</script>

<div
  class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
>
  <div
    class="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-6 py-4"
  >
    <div>
      <p class="text-xs font-medium uppercase tracking-wide text-slate-500">
        Ranking
      </p>
      <p class="text-base font-semibold text-slate-900">
        Candidatos analisados
      </p>
    </div>
    <p class="text-xs text-slate-500">Clique no cabeçalho para ordenar</p>
  </div>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-slate-200 text-left text-sm">
      <thead class="bg-slate-50">
        <tr>
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-slate-600"
          >
            <button
              class="flex items-center gap-1.5 hover:text-slate-900"
              on:click={() => toggleSort("ranking_position")}
            >
              Posição <span class="text-xs">{iconFor("ranking_position")}</span>
            </button>
          </th>
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-slate-600"
          >
            <button
              class="flex items-center gap-1.5 hover:text-slate-900"
              on:click={() => toggleSort("candidate_name")}
            >
              Candidato <span class="text-xs">{iconFor("candidate_name")}</span>
            </button>
          </th>
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-slate-600"
          >
            <button
              class="flex items-center gap-1.5 hover:text-slate-900"
              on:click={() => toggleSort("match_score")}
            >
              Match <span class="text-xs">{iconFor("match_score")}</span>
            </button>
          </th>
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-slate-600"
            >Hard skills</th
          >
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-slate-600"
            >Soft skills</th
          >
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100 bg-white">
        {#each results as candidate}
          <tr class="transition hover:bg-slate-50">
            <td class="px-6 py-4 font-medium text-slate-700"
              >#{candidate.ranking_position}</td
            >
            <td class="px-6 py-4 font-medium text-slate-900"
              >{candidate.candidate_name}</td
            >
            <td class="px-6 py-4">
              <div class="flex items-center gap-3">
                <span
                  class="inline-flex rounded-lg bg-primary-50 px-2.5 py-1 text-xs font-semibold text-primary-700"
                >
                  {candidate.match_score.toFixed(0)}%
                </span>
                <div
                  class="h-1.5 w-20 overflow-hidden rounded-full bg-slate-200"
                >
                  <div
                    class="h-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all"
                    style={`width:${candidate.match_score}%`}
                  ></div>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-slate-600">
              {#if candidate.hard_skills.length}
                {candidate.hard_skills.slice(0, 3).join(", ")}
                {#if candidate.hard_skills.length > 3}
                  <span class="text-xs text-slate-400">
                    +{candidate.hard_skills.length - 3}</span
                  >
                {/if}
              {:else}
                —
              {/if}
            </td>
            <td class="px-6 py-3 text-slate-500">
              {#if candidate.soft_skills.length}
                {candidate.soft_skills.slice(0, 3).join(", ")}
                {#if candidate.soft_skills.length > 3}
                  <span class="text-xs text-slate-400">
                    +{candidate.soft_skills.length - 3}</span
                  >
                {/if}
              {:else}
                —
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
