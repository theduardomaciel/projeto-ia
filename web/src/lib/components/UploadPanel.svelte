<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { fade } from "svelte/transition";

  const allowedTypes = new Set([
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
  ]);

  export let files: File[] = [];
  export let isUploading = false;
  export let progress = 0;

  const dispatch = createEventDispatcher<{
    select: File[];
    remove: number;
    upload: void;
  }>();

  let dragActive = false;
  let errorMessage: string | null = null;

  function handleFileSelection(list: FileList | null) {
    if (!list?.length) return;

    const selected = Array.from(list);
    const invalid = selected.filter((file) => !allowedTypes.has(file.type));

    if (invalid.length) {
      errorMessage = `Arquivos inválidos: ${invalid.map((i) => i.name).join(", ")}`;
      return;
    }

    errorMessage = null;
    dispatch("select", selected);
  }

  function handleFileInput(event: Event) {
    const input = event.target as HTMLInputElement;
    handleFileSelection(input.files);
    input.value = "";
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    dragActive = false;
    handleFileSelection(event.dataTransfer?.files ?? null);
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    dragActive = true;
  }

  function handleDragLeave(event: DragEvent) {
    event.preventDefault();
    if (!event.currentTarget || event.relatedTarget) return;
    dragActive = false;
  }
</script>

<section class="space-y-4">
  <header>
    <p class="text-sm font-medium text-slate-500">
      Envie arquivos em PDF, DOCX ou TXT
    </p>
  </header>

  <div
    class={`flex flex-col items-center justify-center rounded-2xl border-2 border-dashed bg-white/70 px-6 py-10 text-center transition-all ${
      dragActive
        ? "border-primary-500 bg-primary-50 shadow-lg"
        : "border-slate-200"
    }`}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    on:drop={handleDrop}
    aria-label="Área para soltar arquivos"
    role="region"
  >
    <div class="rounded-full bg-primary-100 p-4 text-primary-600">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        class="h-8 w-8"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-15-9l6-6m0 0l6 6m-6-6V15"
        />
      </svg>
    </div>
    <p class="mt-4 text-lg font-semibold text-slate-800">
      Arraste e solte os currículos aqui
    </p>
    <p class="text-sm text-slate-500">ou</p>
    <label
      class="mt-3 inline-flex cursor-pointer items-center gap-2 rounded-full bg-primary-600 px-6 py-2 text-sm font-semibold text-white shadow-md transition hover:bg-primary-700 focus-within:ring-2 focus-within:ring-offset-2"
    >
      <input
        type="file"
        class="sr-only"
        multiple
        accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
        on:change={handleFileInput}
        aria-label="Selecionar arquivos"
      />
      Selecionar arquivos
    </label>
    {#if errorMessage}
      <p class="mt-4 text-sm text-red-500" transition:fade>{errorMessage}</p>
    {/if}
  </div>

  {#if files.length}
    <div class="rounded-2xl bg-white/80 p-4 shadow-sm" transition:fade>
      <div class="flex items-center justify-between">
        <p class="text-sm font-semibold text-slate-700">
          Arquivos prontos para envio
        </p>
        <button
          class="text-xs font-semibold uppercase tracking-wide text-primary-600 hover:text-primary-800 disabled:opacity-50"
          on:click={() => dispatch("upload")}
          disabled={isUploading}
        >
          {isUploading ? "Enviando..." : "Enviar agora"}
        </button>
      </div>
      <ul class="mt-3 space-y-2 text-sm text-slate-600">
        {#each files as file, index}
          <li
            class="flex items-center justify-between rounded-xl border border-slate-100 bg-white px-3 py-2"
          >
            <div>
              <p class="font-medium text-slate-800">{file.name}</p>
              <p class="text-xs text-slate-500">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              class="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
              on:click={() => dispatch("remove", index)}
              aria-label={`Remover ${file.name}`}
              disabled={isUploading}
            >
              ✕
            </button>
          </li>
        {/each}
      </ul>

      {#if isUploading}
        <div class="mt-4" aria-live="polite" transition:fade>
          <div
            class="flex items-center justify-between text-xs font-semibold text-slate-500"
          >
            <span>Upload em andamento</span>
            <span>{progress}%</span>
          </div>
          <div
            class="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-100"
          >
            <div
              class="h-full rounded-full bg-primary-500 transition-all"
              style={`width:${progress}%`}
            ></div>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</section>
