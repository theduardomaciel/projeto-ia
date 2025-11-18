# Mini-projeto

Considere os 4 projetos a seguir e faça a escolha de um deles para você (ou sua equipe) desenvolver completamente uma solução, usando um processo de desenvolvimento de software com a técnica de programação em pares, onde o outro par é um LLM (de sua livre escolha), gerando sistemas de software que funcionem.

No desenvolvimento de cada projeto escolhido, realize o seguinte:

---

### (i)  
Elabore e implemente uma solução via software para o problema (projeto) escolhido, tendo a assistência de um LLM (ChatGPT, Gemini, GitHub Copilot, Claude, DeepSeek, Qwen, …). Espera-se a entrega de um protótipo funcional do sistema.

---

### (ii)  
Descreva no relatório técnico a ser entregue — além da arquitetura e exemplos de diálogos — **como foi cada interação feita com o LLM usado**, destacando pergunta e resposta/sugestão obtida. Discuta o nível de assistência oferecido.

---

### (iii)  
Inclua no relatório:

- Comparações feitas entre LLMs utilizados (se houver mais de um);  
- Documentação de todas as interações e análise das sugestões;  
- Itens adicionais que você considerar relevantes;  
- Coletas e impressão de telas consideradas importantes durante a programação.

O código deve ser entregue como parte do relatório.

---

### (iv)  
No relatório, discutam:

- Que tipo de ajuda o LLM ofereceu;  
- Quais LLMs foram melhores (se utilizaram mais de um);  
- Se houve alguma ajuda muito boa e inesperada;  
- Se houve sugestões erradas — caso sim, apresentá-las.

---

## Critérios de avaliação (80% da nota total)

- **Relatório final**, incluindo o que foi pedido em (ii), (iii) e (iv): **40%**  
- **Nível de funcionalidade do protótipo entregue**: **30%**  
- **Apresentação oral**: **30%**

---

# Mini-projetos

## **Mini-projeto 1: Sistema de recomendação de vinho a partir de escolha de prato de jantar**

Desenvolver um sistema de recomendação inteligente capaz de sugerir o vinho apropriado para acompanhar um prato de jantar indicado pelo usuário, contendo os ingredientes do jantar dentre opções disponíveis.

O sistema deve considerar características do prato (ex.: ingredientes principais, tipo de carne ou vegetariano, tempero, acidez, intensidade do sabor) e sugerir o tipo de vinho (tinto, branco, seco, doce etc.) que harmonize bem.

### **Requisitos Técnicos**
- Base de dados de vinhos e pratos (JSON ou CSV)  
- Algoritmo de recomendação (baseado em regras ou similaridade)  
- Integração com LLM via API para processamento de texto e justificativas  
- Interface simples (CLI ou web)

---

## **Mini-projeto 2: Sistema baseado em lógica fuzzy (ou Redes Bayesianas) para gestão de riscos**

Elabore e implemente uma solução de software baseada em regras fuzzy para avaliar o nível de risco de um projeto de software (saída) utilizando **pelo menos 10 variáveis principais de entrada**.

Descreva cada variável utilizada e apresente seus valores fuzzy. Estruture o trabalho conforme solicitado na lista 2 da AB1.

**Alternativa:** substituir lógica fuzzy por uma abordagem com Redes Bayesianas.

### **Observações**
Variáveis de entrada representam fatores que influenciam o risco do projeto.  
Cada variável deve ter valores fuzzy (conceitos linguísticos) para capturar incertezas. Exemplos de variáveis:  
- experiência da equipe,  
- entrosamento,  
- rotatividade,  
- clareza dos requisitos,  
- estabilidade dos requisitos,  
- porte/complexidade, entre outros.

---

## **Mini-projeto 3: Sistema Tutor Inteligente (STI)**

Criar um sistema tutor inteligente para algum domínio (Matemática, Lógica, Programação ou Educação Ambiental).

O STI deve:
- propor problemas;  
- avaliar soluções/respostas dos estudantes;  
- fornecer feedback adaptativo;  
- manter um modelo de perfis dos estudantes (iniciante, intermediário, avançado).

---

## **Mini-projeto 4: Sistema de Apoio ao Recrutamento – Analisador de Currículos com IA**

Suponha que um gerente de RH contrate você para desenvolver um sistema de IA que auxilie na seleção de candidatos para um cargo de desenvolvedor de software.

O sistema deve:
- analisar currículos;  
- identificar hard skills e soft skills;  
- avaliar a compatibilidade com uma vaga específica;  
- gerar um ranking de candidatos;  
- justificar (explicar) cada decisão.