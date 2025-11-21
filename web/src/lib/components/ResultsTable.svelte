<script lang="ts">
  import type { CandidateResult, SortDirection, SortKey } from "$lib/types";
  import { createEventDispatcher } from "svelte";

  export let results: CandidateResult[] = [];
  export let sortKey: SortKey = "ranking_position";
  export let sortDirection: SortDirection = "asc";
  export let sortCriterion: "ranking" | "match" | "global" | "final" =
    "ranking";

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
  class="overflow-hidden rounded-2xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 shadow-sm"
>
  <div
    class="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900/50 px-6 py-4"
  >
    <div>
      <p
        class="text-xs font-medium uppercase tracking-wide text-neutral-500 dark:text-neutral-400"
      >
        Ranking
      </p>
      <p class="text-base font-semibold text-neutral-900 dark:text-white">
        Candidatos analisados
      </p>
    </div>
    <div class="flex items-center gap-3">
      <p class="text-xs text-neutral-500 dark:text-neutral-400">
        Clique no cabeçalho para ordenar
      </p>
      <div class="flex items-center gap-2">
        <select
          class="rounded-md border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-2 py-1 text-xs text-neutral-700 dark:text-neutral-200 focus:border-primary-500 focus:ring-1 focus:ring-primary-400"
          bind:value={sortCriterion}
          on:change={() => {
            if (sortCriterion === "ranking") toggleSort("ranking_position");
            else if (sortCriterion === "match") toggleSort("match_score");
            else if (sortCriterion === "global") toggleSort("global_score");
            else if (sortCriterion === "final") toggleSort("final_score");
          }}
        >
          <option value="ranking">Ranking</option>
          <option value="match">Match %</option>
          <option value="global">Score Global</option>
          <option value="final">Score Combinado</option>
        </select>
        <button
          class="text-xs font-medium text-neutral-500 dark:text-neutral-400 hover:text-neutral-800 dark:hover:text-neutral-200"
          on:click={() => {
            if (sortCriterion === "ranking") toggleSort("ranking_position");
            else if (sortCriterion === "match") toggleSort("match_score");
            else if (sortCriterion === "global") toggleSort("global_score");
            else toggleSort("final_score");
          }}
          aria-label="Alternar direção"
        >
          {iconFor(sortKey)}
        </button>
      </div>
    </div>
  </div>
  <div class="overflow-x-auto">
    <table
      class="min-w-full divide-y divide-neutral-200 dark:divide-neutral-700 text-left text-sm"
    >
      <thead class="bg-neutral-50 dark:bg-neutral-900/50">
        <tr>
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-neutral-600 dark:text-neutral-400"
          >
            <button
              class="flex items-center gap-1.5 hover:text-neutral-900 dark:hover:text-white"
              on:click={() => toggleSort("ranking_position")}
            >
              Posição <span class="text-xs">{iconFor("ranking_position")}</span>
            </button>
          </th>
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-neutral-600 dark:text-neutral-400"
          >
            <button
              class="flex items-center gap-1.5 hover:text-neutral-900 dark:hover:text-white"
              on:click={() => toggleSort("candidate_name")}
            >
              Candidato <span class="text-xs">{iconFor("candidate_name")}</span>
            </button>
          </th>
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-neutral-600 dark:text-neutral-400"
          >
            <button
              class="flex items-center gap-1.5 hover:text-neutral-900 dark:hover:text-white"
              on:click={() => {
                if (sortCriterion === "ranking") toggleSort("ranking_position");
                else if (sortCriterion === "match") toggleSort("match_score");
                else if (sortCriterion === "global") toggleSort("global_score");
                else toggleSort("final_score");
              }}
            >
              {sortCriterion === "ranking"
                ? "Ranking"
                : sortCriterion === "match"
                  ? "Match %"
                  : sortCriterion === "global"
                    ? "Score Global"
                    : "Score Combinado"}
              <span class="text-xs">{iconFor(sortKey)}</span>
            </button>
          </th>
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-neutral-600 dark:text-neutral-400"
            >Hard skills</th
          >
          <th
            class="px-6 py-3.5 text-xs font-medium uppercase tracking-wider text-neutral-600 dark:text-neutral-400"
            >Soft skills</th
          >
        </tr>
      </thead>
      <tbody
        class="divide-y divide-neutral-100 dark:divide-neutral-700 bg-white dark:bg-neutral-800"
      >
        {#each results as candidate}
          <tr
            class="transition hover:bg-neutral-50 dark:hover:bg-neutral-700/50"
          >
            <td
              class="px-6 py-4 font-medium text-neutral-700 dark:text-neutral-300"
              >#{candidate.ranking_position}</td
            >
            <td class="px-6 py-4 font-medium text-neutral-900 dark:text-white"
              >{candidate.candidate_name}</td
            >
            <td class="px-6 py-4">
              {#if sortCriterion === "match"}
                <div class="flex items-center gap-3">
                  <span
                    class="inline-flex rounded-lg bg-primary-50 dark:bg-primary-900/30 px-2.5 py-1 text-xs font-semibold text-primary-700 dark:text-primary-400"
                  >
                    {candidate.match_score.toFixed(0)}%
                  </span>
                  <div
                    class="h-1.5 w-20 overflow-hidden rounded-full bg-neutral-200 dark:bg-neutral-700"
                  >
                    <div
                      class="h-full bg-linear-to-r from-primary-500 to-primary-600 transition-all"
                      style={`width:${candidate.match_score}%`}
                    ></div>
                  </div>
                </div>
              {:else if sortCriterion === "global"}
                <span
                  class="inline-flex rounded-md bg-neutral-100 dark:bg-neutral-700/50 px-2 py-1 text-xs font-medium text-neutral-700 dark:text-neutral-200"
                >
                  {candidate.global_score?.toFixed(2) ?? "0.00"}
                </span>
              {:else if sortCriterion === "final"}
                <span
                  class="inline-flex rounded-md bg-primary-600/10 dark:bg-primary-500/20 px-2 py-1 text-xs font-semibold text-primary-700 dark:text-primary-300"
                >
                  {(candidate.final_score ?? 0).toFixed(1)}
                </span>
              {:else}
                <span
                  class="inline-flex rounded-md bg-neutral-100 dark:bg-neutral-700/50 px-2 py-1 text-xs font-medium text-neutral-700 dark:text-neutral-200"
                  >#{candidate.ranking_position}</span
                >
              {/if}
            </td>
            <td
              class="px-6 py-4 text-sm text-neutral-600 dark:text-neutral-300"
            >
              {#if candidate.hard_skills.length}
                {candidate.hard_skills.slice(0, 3).join(", ")}
                {#if candidate.hard_skills.length > 3}
                  <span class="text-xs text-neutral-400 dark:text-neutral-500">
                    +{candidate.hard_skills.length - 3}</span
                  >
                {/if}
              {:else}
                —
              {/if}
            </td>
            <td class="px-6 py-3 text-neutral-500 dark:text-neutral-300">
              {#if candidate.soft_skills.length}
                {candidate.soft_skills.slice(0, 3).join(", ")}
                {#if candidate.soft_skills.length > 3}
                  <span class="text-xs text-neutral-400 dark:text-neutral-500">
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
