<script lang="ts">
  import UploadPanel from "$lib/components/UploadPanel.svelte";
  import CandidateCard from "$lib/components/CandidateCard.svelte";
  import ResultsTable from "$lib/components/ResultsTable.svelte";
  import EmptyState from "$lib/components/EmptyState.svelte";
  import { analyzeResumes } from "$lib/api";
  import type { CandidateResult, SortDirection, SortKey } from "$lib/types";

  let selectedFiles: File[] = [];
  let results: CandidateResult[] = [];
  let isUploading = false;
  let uploadProgress = 0;
  let statusMessage = "Envie currículos para começar.";
  let errorMessage: string | null = null;
  let sortKey: SortKey = "ranking_position";
  let sortDirection: SortDirection = "asc";
  let abortController: AbortController | null = null;

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
      const response = await analyzeResumes(
        selectedFiles,
        undefined,
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

<main class="mx-auto max-w-6xl space-y-10 px-6 py-10">
  <section
    class="rounded-4xl relative overflow-hidden bg-white/80 p-8 shadow-xl ring-1 ring-slate-100"
  >
    <div
      class="absolute inset-y-0 right-0 w-1/2 bg-linear-to-br from-primary-50 via-white to-slate-50 opacity-60 blur-3xl"
    ></div>
    <div
      class="relative flex flex-col gap-6 md:flex-row md:items-center md:justify-between"
    >
      <div class="space-y-3">
        <p
          class="text-sm font-semibold uppercase tracking-widest text-primary-500"
        >
          Sistema de apoio ao recrutamento
        </p>
        <h1 class="text-3xl font-bold text-slate-900">
          Análise inteligente de currículos
        </h1>
        <p class="max-w-2xl text-sm text-slate-500">
          Carregue currículos em PDF ou DOCX, envie para o backend e visualize o
          ranking com hard skills, soft skills e justificativas geradas pelo
          pipeline de IA.
        </p>
      </div>
      <div
        class="rounded-3xl border border-primary-100 bg-primary-50/60 px-6 py-4 text-sm text-primary-800"
      >
        <p class="font-semibold">Status</p>
        <p>{statusMessage}</p>
        {#if isUploading}
          <button
            class="mt-3 text-xs font-semibold text-primary-700 underline"
            on:click={cancelUpload}>Cancelar envio</button
          >
        {/if}
      </div>
    </div>
  </section>

  {#if errorMessage}
    <div
      class="rounded-2xl border border-red-100 bg-red-50/80 px-6 py-4 text-sm text-red-700"
      role="alert"
    >
      <p class="font-semibold">Algo deu errado</p>
      <p>{errorMessage}</p>
    </div>
  {/if}

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

      <div class="grid gap-6 md:grid-cols-2">
        {#each sortedResults as candidate (candidate.candidate_name)}
          <CandidateCard {candidate} />
        {/each}
      </div>
    </section>
  {/if}
</main>

<style lang="postcss">
  @reference "tailwindcss";
  .rounded-4xl {
    border-radius: 2.25rem;
  }
</style>
