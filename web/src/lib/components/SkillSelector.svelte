<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let label: string = "Skills";
  export let selected: string[] = [];
  export let suggestions: string[] = [];
  export let placeholder: string = "Digite para buscar ou adicionar...";

  const dispatch = createEventDispatcher<{ change: string[] }>();

  let inputValue = "";
  let showDropdown = false;
  let filteredSuggestions: string[] = [];
  let highlightedIndex = -1;

  $: {
    if (inputValue.trim()) {
      const searchTerm = inputValue.toLowerCase();
      filteredSuggestions = suggestions
        .filter((skill) => !selected.includes(skill))
        .filter((skill) => skill.toLowerCase().includes(searchTerm))
        .slice(0, 10);
      showDropdown = true;
    } else {
      filteredSuggestions = [];
      showDropdown = false;
    }
  }

  function addSkill(skill: string) {
    const normalized = skill.trim().toLowerCase();
    if (normalized && !selected.includes(normalized)) {
      selected = [...selected, normalized];
      dispatch("change", selected);
      if (!suggestions.includes(normalized)) {
        suggestions = [...suggestions, normalized];
      }
    }
    inputValue = "";
    showDropdown = false;
    highlightedIndex = -1;
  }

  function removeSkill(skill: string) {
    selected = selected.filter((s) => s !== skill);
    dispatch("change", selected);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Enter") {
      e.preventDefault();
      if (highlightedIndex >= 0 && filteredSuggestions[highlightedIndex]) {
        addSkill(filteredSuggestions[highlightedIndex]);
      } else if (inputValue.trim()) {
        addSkill(inputValue);
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      highlightedIndex = Math.min(
        highlightedIndex + 1,
        filteredSuggestions.length - 1,
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      highlightedIndex = Math.max(highlightedIndex - 1, -1);
    } else if (e.key === "Escape") {
      showDropdown = false;
      highlightedIndex = -1;
    }
  }

  function handleBlur() {
    setTimeout(() => {
      showDropdown = false;
      highlightedIndex = -1;
    }, 180);
  }
</script>

<div class="flex flex-col gap-2">
  <label
    for="skill-input-{label}"
    class="flex justify-between items-center text-sm font-medium text-neutral-700 dark:text-neutral-300"
  >
    {label}
    <span class="text-xs font-normal text-neutral-500 dark:text-neutral-400"
      >{selected.length} selecionada(s)</span
    >
  </label>

  <div class="relative">
    <input
      id="skill-input-{label}"
      type="text"
      bind:value={inputValue}
      on:keydown={handleKeydown}
      on:focus={() => (showDropdown = inputValue.trim().length > 0)}
      on:blur={handleBlur}
      {placeholder}
      autocomplete="off"
      class="w-full rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-2 text-sm text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800 transition"
    />

    {#if showDropdown && filteredSuggestions.length > 0}
      <div
        class="absolute z-50 mt-1 w-full rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 shadow-lg max-h-60 overflow-auto"
      >
        {#each filteredSuggestions as suggestion, idx}
          <button
            type="button"
            class="w-full text-left px-3 py-2 text-sm flex items-center gap-2 transition hover:bg-neutral-100 dark:hover:bg-neutral-700 focus:bg-neutral-100 dark:focus:bg-neutral-700 {idx ===
            highlightedIndex
              ? 'bg-neutral-100 dark:bg-neutral-700'
              : ''}"
            on:click={() => addSkill(suggestion)}
          >
            {suggestion}
          </button>
        {/each}
      </div>
    {/if}

    {#if showDropdown && inputValue.trim() && filteredSuggestions.length === 0}
      <div
        class="absolute z-50 mt-1 w-full rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 shadow-lg"
      >
        <button
          type="button"
          class="w-full flex items-center gap-2 px-3 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/30"
          on:click={() => addSkill(inputValue)}
        >
          <span class="text-lg leading-none">+</span>
          Adicionar "{inputValue.toLowerCase()}"
        </button>
      </div>
    {/if}
  </div>

  {#if selected.length > 0}
    <div class="flex flex-wrap gap-2 mt-1">
      {#each selected as skill}
        <span
          class="inline-flex items-center gap-1 rounded-md bg-primary-50 dark:bg-primary-900/30 px-2 py-1 text-xs font-medium text-primary-700 dark:text-primary-300"
        >
          {skill}
          <button
            type="button"
            class="ml-0.5 text-primary-500 dark:text-primary-300 hover:text-primary-700 dark:hover:text-primary-200"
            on:click={() => removeSkill(skill)}
          >
            ×
          </button>
        </span>
      {/each}
    </div>
  {/if}
</div>
}
