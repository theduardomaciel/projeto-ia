<script lang="ts">
  import UploadPanel from "$lib/components/UploadPanel.svelte";
  import CandidateCard from "$lib/components/CandidateCard.svelte";
  import ResultsTable from "$lib/components/ResultsTable.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";
  import { analyzeResumes, checkHealth } from "$lib/api";
  import type { CandidateResult, SortDirection, SortKey } from "$lib/types";
  import { onMount } from "svelte";

  let selectedFiles: File[] = [];
  let results: CandidateResult[] = [];
  let isUploading = false;
  let uploadProgress = 0;
  let statusMessage = "Checando backend...";
  let errorMessage: string | null = null;
  let sortKey: SortKey = "ranking_position";
  let sortDirection: SortDirection = "asc";
  let abortController: AbortController | null = null;

  // Job (optional)
  let jobText: string = "";
  let jobFile: File | null = null;

  onMount(async () => {
    try {
      const ok = await checkHealth();
      statusMessage = ok ? "Backend online" : "Backend não respondeu";
    } catch {
      statusMessage = "Status do backend desconhecido";
    }
  });

  $: sortedResults = [...results].sort((a, b) => {
    const multiplier = sortDirection === "asc" ? 1 : -1;
    if (sortKey === "candidate_name") {
      return a.candidate_name.localeCompare(b.candidate_name) * multiplier;
    }
    return (a[sortKey] - b[sortKey]) * multiplier;
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

  async function handleUpload() {
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
      const options: { jobText?: string; jobFile?: File } = {};
      if (jobFile) options.jobFile = jobFile;
      if (jobText.trim()) options.jobText = jobText.trim();

      const response = await analyzeResumes(
        selectedFiles,
        Object.keys(options).length ? options : undefined,
        abortController.signal,
      );
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
      sortDirection = key === "candidate_name" ? "asc" : "asc";
    }
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
    class="relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 sm:p-8"
  >
    <div
      class="absolute inset-0 bg-linear-to-br from-primary-50 via-white to-slate-50 opacity-40"
    ></div>
    <div
      class="relative flex flex-col gap-6 md:flex-row md:items-start md:justify-between"
    >
      <div class="space-y-2 flex-1">
        <p
          class="text-xs font-semibold uppercase tracking-wider text-primary-600"
        >
          Sistema de apoio ao recrutamento
        </p>
        <h1 class="text-2xl font-bold text-slate-900 sm:text-3xl">
          Análise inteligente de currículos
        </h1>
        <p class="max-w-2xl text-sm text-slate-600 leading-relaxed">
          Carregue currículos em PDF, DOCX ou TXT, envie para o backend e
          visualize o ranking com hard skills, soft skills e justificativas
          geradas pelo pipeline de IA.
        </p>
      </div>
      <div
        class="shrink-0 rounded-xl border border-primary-200 bg-primary-50 px-4 py-3 text-sm"
      >
        <p class="font-semibold text-primary-900">Status</p>
        <p class="mt-1 text-primary-700">{statusMessage}</p>
        {#if isUploading}
          <button
            class="mt-2 text-xs font-medium text-primary-700 underline hover:text-primary-900"
            on:click={cancelUpload}>Cancelar envio</button
          >
        {/if}
      </div>
    </div>
  </section>

  {#if errorMessage}
    <div
      class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm"
      role="alert"
    >
      <p class="font-semibold text-red-900">Erro</p>
      <p class="mt-1 text-red-700">{errorMessage}</p>
    </div>
  {/if}

  <section class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <p class="text-sm font-semibold text-slate-900">Vaga (opcional)</p>
    <div class="mt-4 grid gap-4 md:grid-cols-2">
      <div>
        <label for="job-text" class="block text-xs font-medium text-slate-700"
          >Descrição da vaga (texto)</label
        >
        <textarea
          id="job-text"
          class="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-200"
          rows="4"
          bind:value={jobText}
          placeholder="Cole aqui a descrição da vaga..."
        ></textarea>
      </div>
      <div>
        <label for="job-file" class="block text-xs font-medium text-slate-700"
          >Arquivo da vaga (.txt)</label
        >
        <input
          id="job-file"
          class="mt-2 w-full rounded-lg border border-slate-300 bg-white text-sm text-slate-900 file:mr-3 file:rounded-md file:border-0 file:bg-primary-600 file:px-4 file:py-2 file:text-sm file:font-medium file:text-black hover:file:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-200"
          type="file"
          accept=".txt,text/plain"
          on:change={(e) => {
            const f = (e.target as HTMLInputElement).files?.[0] || null;
            jobFile = f;
          }}
        />
        {#if jobFile}
          <p class="mt-2 text-xs text-slate-600">📄 {jobFile.name}</p>
        {/if}
      </div>
    </div>
  </section>

  <UploadPanel
    {isUploading}
    progress={uploadProgress}
    files={selectedFiles}
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
          <CandidateCard {candidate} />
        {/each}
      </div>
    </section>
  {/if}
</main>
