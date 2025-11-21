<script lang="ts">
  import UploadPanel from "$lib/components/UploadPanel.svelte";
  import CandidateCard from "$lib/components/CandidateCard.svelte";
  import ResultsTable from "$lib/components/ResultsTable.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";
  import { analyzeResumes, checkHealth, getSkills } from "$lib/api";
  import type {
    CandidateResult,
    SortDirection,
    SortKey,
    StructuredJob,
  } from "$lib/types";
  import { onMount } from "svelte";

  let selectedFiles: File[] = [];
  let results: CandidateResult[] = [];
  let isUploading = false;
  let uploadProgress = 0;
  let statusMessage = "Checando backend...";
  let errorMessage: string | null = null;
  let sortKey: SortKey = "ranking_position";
  let sortDirection: SortDirection = "asc";
  let sortCriterion: "ranking" | "match" | "global" | "final" = "ranking";
  let abortController: AbortController | null = null;

  // Job (optional)
  let jobText: string = "";
  let jobFile: File | null = null;
  let mode: "upload" | "structured" = "upload";
  let hardSkillsSuggestions: string[] = [];
  let softSkillsSuggestions: string[] = [];

  onMount(async () => {
    // Health
    try {
      const ok = await checkHealth();
      statusMessage = ok ? "Backend online" : "Backend não respondeu";
    } catch {
      statusMessage = "Status do backend desconhecido";
    }

    // Skills
    try {
      const { hard_skills, soft_skills } = await getSkills();
      hardSkillsSuggestions = hard_skills;
      softSkillsSuggestions = soft_skills;
    } catch (e) {
      console.warn("Falha ao carregar skills", e);
    }
  });

  // Calcula final_score dinamicamente (não altera objeto original no array results)
  $: enrichedResults = results.map((r) => {
    const global = r.global_score ?? 0;
    const globalNormPct = Math.min(global / 10, 1) * 100; // assume escala 0-10
    const final = 0.6 * r.match_score + 0.4 * globalNormPct;
    return { ...r, final_score: final };
  });

  $: sortedResults = [...enrichedResults].sort((a, b) => {
    const multiplier = sortDirection === "asc" ? 1 : -1;
    let key: SortKey;
    if (sortCriterion === "ranking") key = "ranking_position";
    else if (sortCriterion === "match") key = "match_score";
    else if (sortCriterion === "global") key = "global_score";
    else key = "final_score";
    const av = (a as any)[key] ?? 0;
    const bv = (b as any)[key] ?? 0;
    return (av - bv) * multiplier;
  });

  function upsertFiles(newFiles: File[]) {
    const names = new Set(selectedFiles.map((file) => file.name));
    const merged = [...selectedFiles];
    newFiles.forEach((file) => {
      if (!names.has(file.name)) {
        merged.push(file);
        names.add(file.name);
      }
    });
    selectedFiles = merged;
  }

  function removeFile(index: number) {
    selectedFiles = selectedFiles.filter((_, i) => i !== index);
  }

  async function handleUpload(
    e:
      | CustomEvent<{
          structured?: {
            area: string;
            position: string;
            seniority: string;
            hardSkills: string[];
            softSkills: string[];
            additionalInfo: string;
          };
        }>
      | undefined,
  ) {
    if (!selectedFiles.length) {
      errorMessage = "Selecione pelo menos um currículo.";
      return;
    }

    errorMessage = null;
    statusMessage = "Enviando arquivos para análise...";
    isUploading = true;
    uploadProgress = 5;
    abortController = new AbortController();

    const progressTimer = setInterval(() => {
      uploadProgress = Math.min(uploadProgress + 5, 90);
    }, 300);

    try {
      let response;
      if (mode === "structured" && e?.detail?.structured) {
        const structured: StructuredJob = {
          area: e.detail.structured.area.trim(),
          position: e.detail.structured.position.trim(),
          seniority: e.detail.structured.seniority,
          hard_skills: e.detail.structured.hardSkills,
          soft_skills: e.detail.structured.softSkills,
          additional_info: e.detail.structured.additionalInfo?.trim() || "",
        };
        statusMessage = "Processando vaga estruturada...";
        response = await analyzeResumes(
          selectedFiles,
          { structuredJob: structured },
          abortController.signal,
        );
      } else {
        const options: { jobText?: string; jobFile?: File } = {};
        if (jobFile) options.jobFile = jobFile;
        if (jobText.trim()) options.jobText = jobText.trim();
        statusMessage = "Processando vaga textual...";
        response = await analyzeResumes(
          selectedFiles,
          Object.keys(options).length ? options : undefined,
          abortController.signal,
        );
      }
      results = response
        .map((item, index) => ({
          ...item,
          ranking_position: item.ranking_position ?? index + 1,
        }))
        .sort((a, b) => a.ranking_position - b.ranking_position);
      statusMessage = `Última atualização: ${new Date().toLocaleTimeString()}`;
      uploadProgress = 100;
    } catch (error) {
      console.error(error);
      const message =
        error instanceof Error ? error.message : "Erro desconhecido";
      errorMessage = message;
      statusMessage = "Não foi possível concluir a análise.";
    } finally {
      isUploading = false;
      clearInterval(progressTimer);
      abortController = null;
      setTimeout(() => (uploadProgress = 0), 800);
    }
  }

  function handleSort(key: SortKey) {
    if (sortKey === key) {
      sortDirection = sortDirection === "asc" ? "desc" : "asc";
    } else {
      sortKey = key;
      sortDirection = "asc";
    }
    if (key === "ranking_position") sortCriterion = "ranking";
    else if (key === "match_score") sortCriterion = "match";
    else if (key === "global_score") sortCriterion = "global";
    else if (key === "final_score") sortCriterion = "final";
  }

  function cancelUpload() {
    abortController?.abort();
    abortController = null;
    isUploading = false;
    statusMessage = "Envio cancelado pelo usuário.";
  }
</script>

<main class="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6 lg:px-8">
  <section
    class="relative overflow-hidden rounded-2xl bg-white dark:bg-neutral-800 p-6 shadow-sm ring-1 ring-neutral-200 dark:ring-neutral-700 sm:p-8"
  >
    <div
      class="absolute inset-0 bg-linear-to-br from-primary-50 via-white to-neutral-50 dark:from-neutral-800 dark:via-neutral-900 dark:to-neutral-800 opacity-40"
    ></div>
    <div
      class="relative flex flex-col gap-6 md:flex-row md:items-start md:justify-between"
    >
      <div class="space-y-2 flex-1">
        <p
          class="text-xs font-semibold uppercase tracking-wider text-primary-600 dark:text-primary-400"
        >
          Sistema de apoio ao recrutamento
        </p>
        <h1
          class="text-2xl font-bold text-neutral-900 dark:text-white sm:text-3xl"
        >
          Análise inteligente de currículos
        </h1>
        <p
          class="max-w-2xl text-sm text-neutral-600 dark:text-neutral-300 leading-relaxed"
        >
          Carregue currículos em PDF, DOCX ou TXT, envie para o backend e
          visualize o ranking com hard skills, soft skills e justificativas
          geradas pelo pipeline de IA.
        </p>
      </div>
      <div
        class="shrink-0 rounded-xl border border-primary-200 dark:border-primary-800 bg-primary-50 dark:bg-primary-900/30 px-4 py-3 text-sm"
      >
        <p class="font-semibold text-primary-900 dark:text-primary-200">
          Status
        </p>
        <p class="mt-1 text-primary-700 dark:text-primary-300">
          {statusMessage}
        </p>
        {#if isUploading}
          <button
            class="mt-2 text-xs font-medium text-primary-700 dark:text-primary-300 underline hover:text-primary-900 dark:hover:text-primary-100"
            on:click={cancelUpload}>Cancelar envio</button
          >
        {/if}
      </div>
    </div>
  </section>

  {#if errorMessage}
    <div
      class="rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/30 px-4 py-3 text-sm"
      role="alert"
    >
      <p class="font-semibold text-red-900 dark:text-red-200">Erro</p>
      <p class="mt-1 text-red-700 dark:text-red-300">{errorMessage}</p>
    </div>
  {/if}

  {#if mode === "upload"}
    <section
      class="rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 p-5 shadow-sm"
    >
      <p class="text-sm font-semibold text-neutral-900 dark:text-white">
        Vaga (texto ou arquivo)
      </p>
      <div class="mt-4 grid gap-4 md:grid-cols-2">
        <div>
          <label
            for="job-text"
            class="block text-xs font-medium text-neutral-700 dark:text-neutral-300"
            >Descrição da vaga (texto)</label
          >
          <textarea
            id="job-text"
            class="mt-2 w-full rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-2 text-sm text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800"
            rows="4"
            bind:value={jobText}
            placeholder="Cole aqui a descrição da vaga..."
          ></textarea>
        </div>
        <div>
          <label
            for="job-file"
            class="block text-xs font-medium text-neutral-700 dark:text-neutral-300"
            >Arquivo da vaga (.txt)</label
          >
          <input
            id="job-file"
            class="mt-2 w-full rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 text-sm text-neutral-900 dark:text-white file:mr-3 file:rounded-md file:border-0 file:bg-primary-600 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800"
            type="file"
            accept=".txt,text/plain"
            on:change={(e) => {
              const f = (e.target as HTMLInputElement).files?.[0] || null;
              jobFile = f;
            }}
          />
          {#if jobFile}
            <p class="mt-2 text-xs text-neutral-600 dark:text-neutral-400">
              📄 {jobFile.name}
            </p>
          {/if}
        </div>
      </div>
    </section>
  {/if}

  <UploadPanel
    bind:mode
    {isUploading}
    progress={uploadProgress}
    files={selectedFiles}
    {hardSkillsSuggestions}
    {softSkillsSuggestions}
    on:select={(event) => upsertFiles(event.detail as File[])}
    on:remove={(event) => removeFile(event.detail as number)}
    on:upload={handleUpload}
  />

  {#if !results.length}
    <EmptyState />
  {:else}
    <section class="space-y-6">
      <ResultsTable
        results={sortedResults}
        {sortKey}
        {sortDirection}
        on:sort={(event) => handleSort(event.detail as SortKey)}
      />

      <div class="grid gap-5 md:grid-cols-2">
        {#each sortedResults as candidate (candidate.candidate_name)}
          <CandidateCard {candidate} {sortCriterion} />
        {/each}
      </div>
    </section>
  {/if}
</main>
