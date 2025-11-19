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

<section class="space-y-3">
  <header>
    <p class="text-sm font-medium text-slate-600">
      Envie arquivos em PDF, DOCX ou TXT
    </p>
  </header>

  <div
    class={`flex flex-col items-center justify-center rounded-2xl border-2 border-dashed bg-white px-6 py-12 text-center transition-all ${
      dragActive
        ? "border-primary-400 bg-primary-50 shadow-md"
        : "border-slate-300"
    }`}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    on:drop={handleDrop}
    aria-label="Área para soltar arquivos"
    role="region"
  >
    <div class="rounded-full bg-primary-100 p-3 text-primary-600">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="2"
        stroke="currentColor"
        class="h-6 w-6"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
        />
      </svg>
    </div>
    <p class="mt-4 text-base font-semibold text-slate-900">
      Arraste e solte os currículos aqui
    </p>
    <p class="mt-1 text-sm text-slate-500">ou</p>
    <label
      class="mt-3 inline-flex cursor-pointer items-center gap-2 rounded-lg bg-primary-600 px-5 py-2.5 text-sm font-semibold text-black shadow-sm transition hover:bg-primary-700 focus-within:ring-2 focus-within:ring-primary-500 focus-within:ring-offset-2"
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
    <div
      class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
      transition:fade
    >
      <div class="flex items-center justify-between">
        <p class="text-sm font-medium text-slate-900">
          {files.length} arquivo{files.length !== 1 ? "s" : ""} selecionado{files.length !==
          1
            ? "s"
            : ""}
        </p>
        <button
          class="rounded-lg bg-primary-600 px-4 py-2 text-xs font-semibold text-black transition hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          on:click={() => dispatch("upload")}
          disabled={isUploading}
        >
          {isUploading ? "Enviando..." : "Enviar agora"}
        </button>
      </div>
      <ul class="mt-3 space-y-2">
        {#each files as file, index}
          <li
            class="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-4 py-3"
          >
            <div class="flex-1 min-w-0">
              <p class="truncate font-medium text-slate-900 text-sm">
                {file.name}
              </p>
              <p class="text-xs text-slate-500">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              class="ml-3 rounded-md p-1.5 text-slate-400 transition hover:bg-slate-200 hover:text-slate-700 disabled:opacity-50"
              on:click={() => dispatch("remove", index)}
              aria-label={`Remover ${file.name}`}
              disabled={isUploading}
            >
              <svg
                class="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </li>
        {/each}
      </ul>

      {#if isUploading}
        <div class="mt-4" aria-live="polite" transition:fade>
          <div
            class="flex items-center justify-between text-xs font-medium text-slate-600"
          >
            <span>Processando...</span>
            <span>{progress}%</span>
          </div>
          <div
            class="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-200"
          >
            <div
              class="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-300"
              style={`width:${progress}%`}
            ></div>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</section>
