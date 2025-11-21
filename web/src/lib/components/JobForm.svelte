<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import SkillSelector from "./SkillSelector.svelte";

  export let hardSkillsSuggestions: string[] = [];
  export let softSkillsSuggestions: string[] = [];

  const dispatch = createEventDispatcher<{
    change: {
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

  // Emite evento de mudança contínuo para permitir análise externa com único botão
  $: dispatch("change", {
    area: area.trim(),
    position: position.trim(),
    seniority,
    hardSkills,
    softSkills,
    additionalInfo: additionalInfo.trim(),
  });
</script>

<div class="flex flex-col gap-6">
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

  <!-- Botão removido: análise unificada acionada externamente -->
</div>
