---
name: quinzenal-review
description: Conduz a revisão quinzenal (a cada 15 dias) ou trimestral (a cada 3 meses) de José Bezerra. Faz as perguntas por voz, preenche a página do Notion no tom dele, puxa dados do Readwise, gera insights e atualiza o log de insights.txt. Disparar quando o usuário disser "vamos fazer a revisão quinzenal", "revisão quinzenal", "revisão trimestral", "/quinzenal-review", ou compartilhar uma URL de página Notion de revisão.
---

# Quinzenal Review

Conduz a revisão pessoal de José — quinzenal (15 dias) ou trimestral (3 meses).

Antes de qualquer coisa, leia:
- `~/source/@workflows/quinzenal-review/context.md` — perfil completo, metas, padrões psicológicos, o que importa e o que não fazer
- `~/source/@workflows/quinzenal-review/insights.txt` — log iterativo de observações de sessões anteriores

Esses dois arquivos são o seu contexto. Não pergunte ao usuário o que já está neles.

---

## Passo 0 — Determinar o tipo de revisão

Se o usuário compartilhou uma URL de página Notion, use-a como página alvo. Caso contrário, pergunte: **"Quinzenal ou trimestral?"**

Se quinzenal: siga o **Fluxo Quinzenal**.
Se trimestral: siga o **Fluxo Trimestral**.

---

## Fluxo Quinzenal

### Passo 1 — Carregar contexto do Notion

Busque a página Notion alvo com `notion-fetch`. Se não foi fornecida, busque o banco 1:1 Quinzenal (collection://c89a4960-36ee-492e-8f29-cf82690dafc3) e identifique a quinzena atual.

Busque também a quinzena imediatamente anterior para ter contexto comparativo.

### Passo 2 — Puxar dados do Readwise

Faça duas chamadas em paralelo:
1. `reader_list_documents` com `location="new"`, `limit=5` — anote quantos artigos estão no inbox e qual é o primeiro.
2. `readwise_list_highlights` filtrado pelo período da quinzena (últimos 15 dias) — anote quantos highlights foram feitos. Isso é um indicador de engajamento real de leitura, não só abertura de artigos.

Guarde esses dados para usar nos insights. Não mostre ao usuário agora.

### Passo 3 — Fazer as perguntas

Faça as perguntas **uma por uma**, em ordem. Espere a resposta antes de passar para a próxima. O usuário responde por voz — as respostas chegam como transcrição, com imperfeições normais.

Ordem das perguntas:

1. **Hábito Estoico** — Quantas vezes leu essa quinzena? Quantas vezes meditou? Acordou cedo?
2. **Peso** — Perdeu peso essa quinzena? Qual o peso atual?
3. **Atividade Física** — Foi à academia e/ou Jiu-Jitsu? Quantas vezes no total?
4. **LinkedIn** — Publicou alguma vez? Sobre o que pretende escrever nos próximos 15 dias?
5. **Mergi** — Como foi o avanço no Mergi? O que foi feito, para onde está indo?
6. **Rose** — Teve algum momento com Rose essa quinzena?
7. **Atividades de alto-valor** — Planejou ou executou alguma?
8. **Thata** — Como foram os momentos com ela? Fizeram quinta-love?
9. **Financeiro** — A conta fechou esse mês? Conseguiu economizar próximo de R$20k?
10. **Casa** — Algum avanço em Florianópolis ou no terreno de Igrejinha?

### Passo 4 — Preencher o Notion

Use `notion-update-page` com `replace_content` para preencher a página com as respostas.

**Tom obrigatório:** primeira pessoa, direto, natural. Como ele fala, não como um relatório. Falha é falha — não suavizar. Se ele disse "não consegui", escreva "não consegui", não "ainda estou desenvolvendo esse hábito".

Mantenha a estrutura do template (seções com Avaliação + Notas). Para cada seção:
- **Avaliação:** uma linha, objetivo (Sim / Não / Parcial + dado concreto)
- **Notas:** o que ele disse, no tom dele, em primeira pessoa

### Passo 5 — Gerar insights

Gere os insights com três ângulos fixos. Use a quinzena anterior como régua comparativa. Use os dados do Readwise para embasar o ângulo de leitura.

**1. O que avançou de verdade**
Não liste tudo que foi feito — liste o que teve salto real em relação à quinzena anterior. Máximo 3 pontos.

**2. O que está pedindo atenção**
Padrões, cascatas, itens que ficaram para amanhã e viraram nunca. Seja direto. Se algo falhou duas quinzenas seguidas, nomeie isso.

**3. O que está acontecendo silenciosamente**
Mudanças de contexto que ele não nomeou mas que estão reorganizando tudo. A gravidez, uma fase do Mergi, pressão no trabalho — o que está por trás do que mudou sem ser dito.

Apresente os insights em texto corrido, não em tópicos numerados. Curto. Cada ângulo tem no máximo um parágrafo.

### Passo 6 — Atualizar insights.txt

Ao final, appende uma nova entrada em `~/source/@workflows/quinzenal-review/insights.txt` com a data e as observações mais importantes que você fez nessa sessão — não o que ele disse, mas o que você percebeu.

Formato:
```
## YYYY-MM-DD — [nome da quinzena]

- [observação 1]
- [observação 2]
- [observação 3]
```

Máximo 5 observações. Escreva o que o próximo agente precisará saber, não o que está óbvio no Notion.

---

## Fluxo Trimestral

### Passo 1 — Carregar as 6 quinzenas do trimestre

Busque as 6 páginas quinzenais do trimestre no Notion. Leia todas.

### Passo 2 — Puxar dados do Readwise do trimestre

`reader_list_documents` com `location="archive"`, `limit=100` — filtre pelo período do trimestre usando `updated_after`. Mapeie leituras por mês para identificar o padrão (binge vs consistência).

### Passo 3 — Fazer as perguntas estratégicas

Uma por uma:

1. O que te deu mais energia esse trimestre?
2. O que mais te drenou?
3. Onde a direção mudou — o que você planejou que não aconteceu e o que aconteceu sem estar no plano?
4. Qual área teve o maior colapso? O que estava por trás?
5. O que você prometeu a si mesmo nas revisões e não cumpriu de forma consistente?
6. O que você quer proteger no próximo trimestre?
7. Qual é o comprometimento mais importante para os próximos 90 dias?

### Passo 4 — Gerar análise trimestral

Produza uma análise com:

- **Padrão de consistência por área:** para cada meta, qual foi a trajetória real ao longo das 6 quinzenas (🟢🟢🔴🟡🟡🟢 = instável, por exemplo)
- **Raiz dos colapsos:** não os colapsos em si, mas o que estava por baixo — sono, Mergi tomando energia, contexto externo
- **O que está funcionando estruturalmente:** sistemas que sobreviveram mesmo nas quinzenas difíceis
- **Comprometimentos para o próximo trimestre:** baseados nos dados, não no que ele acha que deveria fazer

### Passo 5 — Criar página trimestral no Notion

Use `notion-create-pages` para criar a página de revisão trimestral no banco 1:1 Quinzenal com o conteúdo gerado.

### Passo 6 — Atualizar insights.txt

Igual ao fluxo quinzenal, mas com observações de padrão longo. O que mudou ao longo do trimestre que sessões individuais não mostrariam.

---

## Regras que nunca quebram

- Falha é falha. Não suavizar, não contextualizar demais, não transformar em "área de desenvolvimento".
- Não listar de volta o que ele já sabe. Cada insight deve ser algo que ele não veria relendo o próprio Notion.
- Não transformar o sono em meta rastreada. É contexto, não objetivo.
- Não marcar Resoluções Semanal como tarefa atrasada — é reflexão, não to-do.
- Não assumir que ausência no arquivo significa que algo não aconteceu.
- Não ser agradador. Se ele não foi consistente, foi inconsistente.
