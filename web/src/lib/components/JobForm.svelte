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

<form on:submit|preventDefault={handleSubmit} class="job-form">
  <div class="form-header">
    <h3>Configuração Estruturada da Vaga</h3>
    <p class="subtitle">Defina diretamente os requisitos da vaga</p>
  </div>

  <div class="form-grid">
    <!-- Área -->
    <div class="form-field">
      <label for="area">Área *</label>
      <input
        id="area"
        type="text"
        bind:value={area}
        placeholder="Ex: Tecnologia, Marketing, Vendas..."
        required
      />
    </div>

    <!-- Cargo -->
    <div class="form-field">
      <label for="position">Cargo *</label>
      <input
        id="position"
        type="text"
        bind:value={position}
        placeholder="Ex: Desenvolvedor Backend, Analista de Dados..."
        required
      />
    </div>

    <!-- Senioridade -->
    <div class="form-field">
      <label for="seniority">Senioridade *</label>
      <select id="seniority" bind:value={seniority} required>
        {#each seniorityOptions as option}
          <option value={option.value}>{option.label}</option>
        {/each}
      </select>
    </div>
  </div>

  <!-- Hard Skills -->
  <SkillSelector
    label="Hard Skills *"
    bind:selected={hardSkills}
    suggestions={hardSkillsSuggestions}
    placeholder="Digite para buscar tecnologias, ferramentas..."
  />

  <!-- Soft Skills -->
  <SkillSelector
    label="Soft Skills"
    bind:selected={softSkills}
    suggestions={softSkillsSuggestions}
    placeholder="Digite para buscar competências comportamentais..."
  />

  <!-- Informações Adicionais -->
  <div class="form-field">
    <label for="additional-info">
      Informações Adicionais
      <span class="optional">(opcional)</span>
    </label>
    <textarea
      id="additional-info"
      bind:value={additionalInfo}
      placeholder="Ex: Cultura da empresa, benefícios oferecidos, diferenciais desejados..."
      rows="4"
    ></textarea>
  </div>

  <div class="form-actions">
    <button type="submit" class="submit-btn">Buscar Candidatos</button>
  </div>
</form>

<style>
  .job-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .form-header {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  h3 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
  }

  .subtitle {
    margin: 0;
    font-size: 0.875rem;
    color: #6b7280;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .form-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
  }

  .optional {
    font-weight: 400;
    color: #9ca3af;
  }

  input,
  select,
  textarea {
    padding: 0.625rem 0.875rem;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-family: inherit;
    transition: all 0.2s;
  }

  input:focus,
  select:focus,
  textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  select {
    cursor: pointer;
    background-color: white;
  }

  textarea {
    resize: vertical;
    min-height: 80px;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    padding-top: 0.5rem;
  }

  .submit-btn {
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .submit-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }

  .submit-btn:active {
    transform: translateY(0);
  }
</style>
