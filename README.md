# Comparativo de Moagem — Unidades do Grupo

Apresentação de diretoria com a moagem das quatro unidades do Grupo CRV, safra 2026
contra safra 2025, na janela de **abril a setembro** nos dois anos.

Mesmo padrão visual e de navegação do relatório `comparativo_colhedora`: página única,
uma tela por tópico, sem rolagem de documento.

## Como abrir

Basta abrir o `index.html` no navegador — não precisa de servidor nem de internet.
Para apresentar, use F11 (tela cheia). Navegação: setas ←/→, barra de espaço, as
bolinhas do rodapé, os botões ou o índice do topo.

Se preferir servir por HTTP (o repositório já traz `.claude/launch.json`):

```bash
python -m http.server 8731
```

## Páginas

| # | Página | O que responde |
|---|---|---|
| — | Capa | Números-chave da safra e a decisão em foco |
| 1 | Panorama do grupo | Quanto o grupo moeu mês a mês e como a vantagem sobre 2025 encolhe |
| 2 | Quem puxa, quem trava | Quanto cada unidade somou ou subtraiu; o grupo com e sem a CRV-MG |
| 3 | Unidade a unidade | Os quatro painéis na mesma escala, mês a mês |
| 4 | Mês a mês por empresa | Com filtro de empresa: moagem do mês em barras e moagem média por dia em linha |
| 5 | Colhedora · CRV-MG | Seis indicadores da frota CH570, safra e mês a mês |
| 6 | Caminhão canavieiro | Oito indicadores da frota de caminhões, incluindo raio médio |
| 7 | Transbordo | Sete indicadores da frota de transbordo |
| 8 | Irrigação localizada | Área aplicada por mês, 2025 contra 2026, com alternador de acumulado |

### A página 4

Barras = moagem total do mês (eixo da esquerda, faixa de baixo do quadro).
Linhas = moagem média por dia daquele mês (eixo da direita, faixa de cima).
O filtro no topo troca entre o grupo consolidado e cada uma das quatro unidades.

As duas faixas são separadas de propósito: numa unidade que cresceu muito, a
linha de t/dia de 2025 passaria por dentro das barras se as duas séries
dividissem o mesmo quadro.

**Dias usados no cálculo do t/dia:** abril conta da data de abertura da safra até
30/04 (por isso o mesmo mês pode cair no total e subir no ritmo diário); nos
demais meses, dias corridos. A base não traz apontamento de parada, então o
indicador é moagem por **dia de safra**, não por dia efetivamente moído.

### As páginas 5, 6 e 7 (frota)

São a **mesma página montada três vezes**: muda o conjunto de indicadores e a chave
de `window.FROTA`. O HTML dos três slides e os links do índice são gerados por JS a
partir do array `PAGINAS`. Para somar um equipamento novo, basta acrescentar os
dados e uma entrada nesse array.

**A coluna `Km Rodado` da planilha significa coisas diferentes em cada aba** — é o
ponto que mais confunde quem for mexer nisso:

| Aba | `Km Rodado` é | Indicadores |
|---|---|---|
| `colhedora` | **horas** de máquina | t/dia, h/dia, l/t, l/h, t/h, R$/t |
| `caminhão` | **quilômetro** rodado | t/dia, km/dia, l/t, l/km, t/km, raio médio, t/viagem, R$/t |
| `transbordo` | **horas** de máquina | t/dia, h/dia, l/t, l/h, t/h, t/viagem, R$/t |

As grandezas confirmam cada leitura: a colhedora faz 33 l/h e 14 h/dia, o transbordo
9,3 l/h e 15 h/dia, o caminhão 447 km/dia com 0,98 l/km e raio de 49 km. O cabeçalho
da aba `colhedora` já vem com `hora / Dia` escrito; nas outras duas as colunas
derivadas (`lt / Km`, `Ton / Km`) herdam o rótulo do relatório de transporte e por
isso estão renomeadas no `index.html`.

O **raio médio** é indicador de contexto (`bomSobe: null`): varia, mas não é bom nem
ruim subir — aparece com selo neutro e sem "melhorou/piorou". Sai de
`km ÷ viagens × 0,5`, porque a viagem é ida e volta.

### Quem entra na conta

Sai da conta a máquina que, somando os seis meses, **não chegou a `MIN_TON` (5.000 t)
na safra** — frotas de apontamento esporádico, com dois dias de pesagem e R$ 300/t,
que sujavam todo indicador por tonelada. O critério é por **máquina-safra**, não por
máquina: uma frota com um ano ruim de apontamento sai só daquele ano e continua no
outro.

Efeito do corte: colhedora não perde nenhuma máquina (todas passam dos 5.000 t),
caminhão perde 11 máquinas-safra (0,8% do volume) e transbordo perde 11 (0,4%). A
regra aparece na faixa de insight de cada página e no rodapé de cada modal, com os
números das frotas que ficaram de fora.

Por causa disso, **os totais de cada mês não ficam gravados no arquivo**: são
calculados em tempo de execução por `preparaFrota()`, a partir do detalhe por máquina.
Assim gráfico, fichas e modal enxergam exatamente as mesmas linhas, e mudar `MIN_TON`
reajusta as três páginas inteiras.

### Detalhes da página 5

Seis indicadores da frota John Deere CH570 da CRV-MG, só dessa unidade — é a
única com esse detalhe na planilha. Cada ficha do topo é uma disputa **2025 ×
2026**: os dois valores lado a lado, o de 2026 em destaque, e a variação num selo
ao lado. Clicar na ficha troca o indicador do gráfico.

### Painel de detalhe — "de onde saiu este número"

Dois níveis de abertura, no mesmo espírito do `comparativo_colhedora`:

- **Clicar numa barra do gráfico** abre aquele mês **máquina a máquina**: uma
  linha por frota com dias, horas, litros, tonelada, combustível, manutenção,
  gasto e o indicador, ordenada do melhor para o pior, com a linha de total
  fechando exatamente o número do gráfico.
- **Clicar em "ver a conta"**, no canto da ficha ativa, abre o **mês a mês da
  safra**: numerador, denominador e indicador de cada ano, lado a lado, com a
  linha da safra e a variação.

No topo de cada painel vai a conta explícita — por exemplo
`33,80 t/h = 302.905 t ÷ 8.960,5 h`. Fecha no botão, no fundo escuro ou com Esc.

O detalhe por máquina são 1.163 registros (249 da colhedora, 437 do caminhão e 477
do transbordo), embutidos em `FROTA.<equipamento>.maquinas` em formato de array
posicional — o campo `campos` de cada frota descreve a ordem das posições.

No indicador de **custo**, a barra é empilhada em combustível e manutenção, com o
valor de cada parcela escrito dentro do próprio segmento (some quando a barra
fica estreita demais ou o segmento baixo demais para o número caber), e um
quadro abre ao lado do gráfico com, para cada parcela: o R$/t e sua variação, o
valor absoluto da safra contra o de 2025, e quanto cada uma representa do custo
total. O quadro mede a altura que sobrou no cartão e encolhe junto (variável CSS
`--qf`), para a linha de total nunca ser cortada num projetor de tela baixa. Nos
demais indicadores o quadro some e o gráfico ocupa o cartão inteiro.

Cada indicador é uma **razão entre somas do mês**, nunca uma média de médias —
assim uma máquina que rodou três dias não pesa igual a uma que rodou o mês todo.
As contas do conjunto medido em horas (colhedora e transbordo):

| Indicador | Conta |
|---|---|
| Tonelada por máquina/dia | Σ tonelada ÷ Σ dias-máquina |
| Horas por dia | Σ horas ÷ Σ dias-máquina |
| Litros por tonelada | Σ litros ÷ Σ tonelada |
| Litros por hora | Σ litros ÷ Σ horas |
| Tonelada por hora | Σ tonelada ÷ Σ horas |
| Custo por tonelada | Σ gasto ÷ Σ tonelada (aberto em combustível e manutenção) |

No caminhão, `horas` dá lugar a `km`: km/dia, l/km e t/km. Raio médio é
`Σ km ÷ Σ viagens × 0,5` e tonelada por viagem é `Σ tonelada ÷ Σ viagens`.

**Cobertura:** nenhuma das três frotas cobre a moagem inteira da unidade — a
colhedora responde por 90% da moagem da CRV-MG em 2026, o caminhão por 91% e o
transbordo por 87%. Por isso a tonelada dessas páginas não bate com a da página 4,
e cada uma traz essa ressalva no próprio texto.

### A página 8 (irrigação)

Área irrigada mês a mês nas duas safras, com alternador entre **mês a mês** e
**acumulado**. A janela vai do início de cada safra até **30/09** nos dois anos — o
que a base traz de outubro fica de fora, porque outubro/2025 está fechado e
outubro/2026 tem um dia só.

Abril não compara desempenho, compara calendário: a safra 2026 abriu em 14/04 e a
2025 em 19/04, o que explica o salto de +465% no mês. Por isso abril fica fora do
ranking de melhor e pior mês do insight, e o texto traz também a variação de maio em
diante (+1,1%).

Os dados ficam em `window.IRRIGACAO`, uma chave por tipo. Hoje só existe
`localizada`; **convencional** entra como mais uma chave e mais uma entrada em
`PAGINAS_IRRIGA` — a página se monta sozinha, igual às de frota.

## Atualizar os dados

Todos os números saem de **um único bloco** no `index.html`, marcado com o comentário
`DADOS — moagem mensal por unidade`:

```js
window.MOAGEM = {
  meses: ["Abril", ...],
  unidades: [
    {cod:"AGRO-RTB", nome:"Agro Rubiataba", curto:"Rubiataba", cor:"#12224A",
     a2025:[...], a2026:[...], ini2025:"2025-04-21", ini2026:"2026-04-16"},
    ...
  ]
};
```

Para incluir outubro e os meses seguintes, acrescente o nome em `meses` e `mesesCurto`
e mais um valor em cada `a2025` / `a2026`. **Todo o resto é calculado em tempo de
execução** — KPIs, variações, insights, tabelas e gráficos se ajustam sozinhos, e os
textos das faixas douradas são montados a partir dos próprios números.

As datas em `ini2025` / `ini2026` alimentam o cálculo de t/dia da página 4: os dias de
abril são contados da data de abertura até 30/04.

Os indicadores de frota ficam num segundo bloco, `window.FROTA`, com uma chave por
tipo de equipamento: `colhedora`, `caminhao` e `transbordo`. Cada uma traz um registro
por mês com `maq`, `dias`, `horas` ou `km`, `litros`, `ton`, `gasto`, `comb`, `manut`
e (nas duas de transporte) `viagens`. Um equipamento novo entra como mais uma chave
aqui e mais uma entrada em `PAGINAS`, no JS — a página se monta sozinha.

Fonte dos dados: `MOAGEM COMPARATIVO.xlsx` (UGS), abas `Planilha1`, `colhedora`,
`caminhão` e `transbordo`; e `Produção localizada - SAFRA 2025/2026.xlsx`, aba
`Banco Localizada`, para a irrigação.

## Convenções mantidas do `comparativo_colhedora`

- Paleta: navy `#12224A`, dourado `#C9A227`, verde `#2E7D46`, vermelho `#C0392B`.
- Cor fixa por unidade, a mesma dos dois relatórios: Rubiataba navy, CRV-GO dourado,
  CRV-MG azul `#2E86C1`, Uruaçu verde.
- Safra anterior sempre em cinza-azulado `#B8C0D0` ou na cor da unidade esmaecida;
  a safra corrente em cor cheia.
- Gráficos em SVG montado em JavaScript, sem biblioteca externa.
- O `viewBox` de cada gráfico é medido a partir do cartão em tempo de execução, para o
  texto sair no tamanho pedido em qualquer resolução de projetor.

## Observação sobre o período

A safra 2026 segue em andamento. Toda comparação deste material usa a **mesma janela de
seis meses** nos dois anos (abril a setembro) — não há projeção nem estimativa de
fechamento.
