<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import SkillSelector from "./SkillSelector.svelte";

  export let hardSkillsSuggestions: string[] = [];
  export let softSkillsSuggestions: string[] = [];

  const dispatch = createEventDispatcher<{
    submit: {
      area: string;
      position: string;
      seniority: string;
      hardSkills: string[];
      softSkills: string[];
      additionalInfo: string;
    };
  }>();

  let area = "";
  let position = "";
  let seniority = "";
  let hardSkills: string[] = [];
  let softSkills: string[] = [];
  let additionalInfo = "";

  const seniorityOptions = [
    { value: "", label: "Selecione..." },
    { value: "estagio", label: "Estágio" },
    { value: "junior", label: "Júnior" },
    { value: "pleno", label: "Pleno" },
    { value: "senior", label: "Sênior" },
    { value: "especialista", label: "Especialista" },
    { value: "lideranca", label: "Liderança" },
  ];

  function handleSubmit() {
    // Validações básicas
    if (!area.trim() || !position.trim() || !seniority) {
      alert("Por favor, preencha área, cargo e senioridade.");
      return;
    }

    if (hardSkills.length === 0 && softSkills.length === 0) {
      alert("Por favor, adicione pelo menos uma skill (hard ou soft).");
      return;
    }

    dispatch("submit", {
      area: area.trim(),
      position: position.trim(),
      seniority,
      hardSkills,
      softSkills,
      additionalInfo: additionalInfo.trim(),
    });
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="flex flex-col gap-6">
  <div class="flex flex-col gap-1">
    <h3 class="text-lg font-semibold text-neutral-900 dark:text-white">
      Configuração Estruturada da Vaga
    </h3>
    <p class="text-sm text-neutral-600 dark:text-neutral-400">
      Defina diretamente os requisitos da vaga
    </p>
  </div>

  <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
    <div class="flex flex-col gap-2">
      <label
        for="area"
        class="text-sm font-medium text-neutral-700 dark:text-neutral-300"
        >Área *</label
      >
      <input
        id="area"
        type="text"
        bind:value={area}
        placeholder="Ex: Tecnologia, Marketing, Vendas..."
        required
        class="rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-2 text-sm outline-none text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800 transition"
      />
    </div>
    <div class="flex flex-col gap-2">
      <label
        for="position"
        class="text-sm font-medium text-neutral-700 dark:text-neutral-300"
        >Cargo *</label
      >
      <input
        id="position"
        type="text"
        bind:value={position}
        placeholder="Ex: Desenvolvedor Backend, Analista de Dados..."
        required
        class="rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-2 text-sm outline-none text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800 transition"
      />
    </div>
    <div class="flex flex-col gap-2">
      <label
        for="seniority"
        class="text-sm font-medium text-neutral-700 dark:text-neutral-300"
        >Senioridade *</label
      >
      <select
        id="seniority"
        bind:value={seniority}
        required
        class="rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-2 text-sm outline-none text-neutral-900 dark:text-white focus:border-primary-500 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800 transition"
      >
        {#each seniorityOptions as option}
          <option value={option.value}>{option.label}</option>
        {/each}
      </select>
    </div>
  </div>

  <SkillSelector
    label="Hard Skills *"
    bind:selected={hardSkills}
    suggestions={hardSkillsSuggestions}
    placeholder="Digite para buscar tecnologias, ferramentas..."
  />
  <SkillSelector
    label="Soft Skills"
    bind:selected={softSkills}
    suggestions={softSkillsSuggestions}
    placeholder="Digite para buscar competências comportamentais..."
  />

  <div class="flex flex-col gap-2">
    <label
      for="additional-info"
      class="text-sm font-medium text-neutral-700 dark:text-neutral-300"
    >
      Informações Adicionais <span
        class="font-normal text-neutral-400 dark:text-neutral-500"
        >(opcional)</span
      >
    </label>
    <textarea
      id="additional-info"
      bind:value={additionalInfo}
      placeholder="Ex: Cultura da empresa, benefícios oferecidos, diferenciais desejados..."
      rows="4"
      class="rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-900 px-3 py-2 text-sm outline-none text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 dark:focus:ring-primary-800 transition resize-y min-h-20"
    ></textarea>
  </div>

  <div class="flex justify-end pt-2">
    <button
      type="submit"
      class="relative inline-flex items-center justify-center rounded-lg bg-linear-to-r from-primary-500 to-primary-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:from-primary-600 hover:to-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-300 dark:focus:ring-primary-700"
    >
      Buscar Candidatos
    </button>
  </div>
</form>
