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
        .slice(0, 10); // Limitar a 10 sugestões
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

      // Adicionar às sugestões se não existir
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
        // Adicionar como nova skill
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
    // Delay para permitir clique na sugestão
    setTimeout(() => {
      showDropdown = false;
      highlightedIndex = -1;
    }, 200);
  }
</script>

<div class="skill-selector">
  <label for="skill-input-{label}">
    {label}
    <span class="count">{selected.length} selecionada(s)</span>
  </label>

  <div class="input-wrapper">
    <input
      id="skill-input-{label}"
      type="text"
      bind:value={inputValue}
      on:keydown={handleKeydown}
      on:focus={() => (showDropdown = inputValue.trim().length > 0)}
      on:blur={handleBlur}
      {placeholder}
      autocomplete="off"
    />

    {#if showDropdown && filteredSuggestions.length > 0}
      <div class="dropdown">
        {#each filteredSuggestions as suggestion, idx}
          <button
            type="button"
            class="dropdown-item"
            class:highlighted={idx === highlightedIndex}
            on:click={() => addSkill(suggestion)}
          >
            {suggestion}
          </button>
        {/each}
      </div>
    {/if}

    {#if showDropdown && inputValue.trim() && filteredSuggestions.length === 0}
      <div class="dropdown">
        <button
          type="button"
          class="dropdown-item new-skill"
          on:click={() => addSkill(inputValue)}
        >
          <span class="icon">+</span>
          Adicionar "{inputValue.toLowerCase()}"
        </button>
      </div>
    {/if}
  </div>

  {#if selected.length > 0}
    <div class="selected-skills">
      {#each selected as skill}
        <span class="skill-tag">
          {skill}
          <button
            type="button"
            class="remove-btn"
            on:click={() => removeSkill(skill)}>×</button
          >
        </span>
      {/each}
    </div>
  {/if}
</div>

<style>
  .skill-selector {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
  }

  .count {
    font-size: 0.75rem;
    color: #6b7280;
    font-weight: 400;
  }

  .input-wrapper {
    position: relative;
  }

  input {
    width: 100%;
    padding: 0.625rem 0.875rem;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    transition: all 0.2s;
  }

  input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .dropdown {
    position: absolute;
    top: calc(100% + 0.25rem);
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    max-height: 240px;
    overflow-y: auto;
    z-index: 50;
  }

  .dropdown-item {
    width: 100%;
    padding: 0.625rem 0.875rem;
    text-align: left;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 0.875rem;
    color: #374151;
    transition: background-color 0.15s;
  }

  .dropdown-item:hover,
  .dropdown-item.highlighted {
    background-color: #f3f4f6;
  }

  .dropdown-item.new-skill {
    color: #3b82f6;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .icon {
    font-size: 1.25rem;
    line-height: 1;
  }

  .selected-skills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .skill-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.625rem;
    background: #eff6ff;
    color: #1e40af;
    border-radius: 0.375rem;
    font-size: 0.813rem;
    font-weight: 500;
  }

  .remove-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1rem;
    height: 1rem;
    padding: 0;
    background: none;
    border: none;
    color: #3b82f6;
    cursor: pointer;
    font-size: 1.25rem;
    line-height: 1;
    transition: color 0.15s;
  }

  .remove-btn:hover {
    color: #1e40af;
  }
</style>
