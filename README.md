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
| 9 | Irrigação convencional | Mesma página para o carretel: área por mês, velocidade na linha e parte em vinhaça |
| 10 | Irrigação por região | A convencional aberta por região, 2025 contra 2026, painéis na mesma escala |
| 11 | Região x região | Duas regiões escolhidas lado a lado numa safra, com a diferença mês a mês |
| 12 | Disponibilidade mecânica | Disponibilidade % da frota mês a mês, 2025 x 2026, com filtro de grupo e especialidade |

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
**acumulado**. O quadro tem duas faixas, como a página 4: **barras** de área
embaixo e **linhas de vazão** em cima, cada uma com seu eixo — em um só eixo a
vazão (dezenas de m³/h) sumiria ao lado da área (milhares de ha). A vazão é sempre
a do mês, mesmo no modo acumulado, porque é uma taxa e não se acumula. Sob cada
mês vão as duas variações: a de área na pílula e a de vazão na linha de baixo.

**Clicar numa barra** abre as fazendas irrigadas naquele mês, da maior para a menor
área, com dias, tanques, vazão e a participação de cada uma no mês. Os totais de cada
mês são construídos a partir dessas mesmas linhas, então a última linha do modal fecha
exatamente com a barra do gráfico. A coluna de dias é por fazenda e não soma os dias do
mês — a mesma data aparece em várias fazendas.

A vazão é a **média ponderada pela área aplicada** — `Σ(ha × vazão) ÷ Σha` — e não
a média simples das linhas do apontamento: é a vazão com que aqueles hectares
foram de fato irrigados. Na safra, a ponderação usa a área de cada mês. A janela vai do início de cada safra até **30/09** nos dois anos — o
que a base traz de outubro fica de fora, porque outubro/2025 está fechado e
outubro/2026 tem um dia só.

Abril não compara desempenho, compara calendário: a safra 2026 abriu em 14/04 e a
2025 em 19/04, o que explica o salto de +465% no mês. Por isso abril fica fora do
ranking de melhor e pior mês do insight, e o texto traz também a variação de maio em
diante (+1,1%).

Os dados ficam em `window.IRRIGACAO`, uma chave por tipo (`localizada` e
`convencional`), e cada página é uma entrada em `PAGINAS_IRRIGA` — a página se
monta sozinha, igual às de frota. O que muda entre as duas está na própria
entrada: `taxa` diz qual campo vai na linha (vazão em m³/h na localizada,
velocidade do carretel em m/h na convencional) e `qtd` qual contagem vai no modal
(tanques ou puxadas).

### A página 9 (irrigação convencional)

Mesmo molde da página 8: mesma janela (início da safra até 30/09), mesmas duas
faixas, mesmo alternador e mesmo modal por fazenda. Cada registro da planilha é
uma **puxada de carretel**, e a área é `puxada × espaçamento ÷ 10.000`.

- **Linha = velocidade do carretel (m/h)**, ponderada pela área como a vazão da
  localizada. Só entram as puxadas com velocidade entre **3 e 120 m/h**: a
  planilha traz velocidade zero quando falta a hora final e valores absurdos
  (negativos, milhares de m/h) quando a hora foi digitada errada. A área dessas
  puxadas continua nas barras; só sai da média de velocidade. Isso cobre **94% da
  área em 2025 e só 71% em 2026** — muita puxada de 2026 está sem hora final — e o
  insight e o rodapé do modal dizem isso. Na safra, a média pondera pela área que
  entrou na conta (`haVel`), não pela área total.
- **Água × vinhaça:** o modal traz a coluna de vinhaça por fazenda, e o insight a
  participação da vinhaça na área (39% em 2026 contra 26% em 2025).
- **Abril:** aqui a safra 2026 abriu *depois* (07/04 contra 04/04) e mesmo assim
  abril subiu, então o texto não atribui o salto ao calendário. O insight escolhe a
  frase conforme a data de abertura e o sinal da variação.

### Lâmina (páginas 9 e 10)

Cada puxada da convencional traz a lâmina na coluna `DESC. LAMINA` (`Água 2º lâmina`,
`Vinhaça 3º lâmina`, `1ª Lam. Bordadura Ág.`…). A área é somada por **número de
lâmina** — água e vinhaça juntas, e a bordadura (cerca de 1% da área) na lâmina do
mesmo número. Só a convencional tem esse corte: a localizada não entra.

- **Página 9:** as barras continuam uma cor por ano; a lâmina vai como
  **observação** sob os meses — uma linha por lâmina, alinhada com cada mês, com
  `2025 → 2026` da área daquela lâmina no mês (no modo acumulado, acumulada até o
  mês). Na margem direita, a variação da lâmina na safra inteira. O modal do mês
  ganha a linha "Por lâmina". A soma das lâminas de cada mês é o total do mês — o
  resíduo de arredondamento fica na maior lâmina. (Já foi testado empilhar as
  barras por lâmina; o gráfico ficou carregado demais e a observação ficou no lugar.)
- **Página 10:** uma fila de fichas por região (2025 → 2026, peso na área da
  região), alinhada com o painel de baixo, no formato das fichas de frota. São só de
  leitura: não trocam o gráfico.

| Lâmina | 2025 (ha) | 2026 (ha) | Variação |
|---|---|---|---|
| 1ª | 9.561 | 7.524 | −21% |
| 2ª | 3.525 | 3.110 | −12% |
| 3ª | 809 | 1.445 | +79% |
| 4ª | 342 | 1.339 | +292% |

A leitura vai no insight da página 9: a área de repetição (2ª lâmina em diante) passou
de 33% para 44% do total. Os dados ficam em `IRRIGACAO.convencional.laminas` (safra),
`laminasMes` (mês a mês) e `laminas` de cada região (posição 0 = 1ª lâmina); uma 5ª
lâmina vira mais uma ficha e mais uma linha da observação sozinha.

### As páginas 10 e 11 (irrigação convencional por região)

A mesma área da página 9 aberta pela coluna **REGIÃO** da aba `faz.` do fechamento
de 2026 — o `banco de dados` de 2026 traz a mesma região em cada registro, e as duas
batem 100%. **A planilha de 2025 não tem essa coluna**: a safra 2025 usa a região
*atual* de cada fazenda (`regiaoFaz`), o que cobre toda a área de 2025. Ou seja, a
comparação é das mesmas fazendas nos dois anos.

| Região | Blocos | Convencional |
|---|---|---|
| 1 | 06 Shekinah, 07 Samir | só água |
| 2 | 01 a 05, 08 a 10 | toda a vinhaça está aqui |
| 3 | 11 Terceira Zona | nenhuma área nas duas safras |

- **Página 10:** um painel por região com área na safra (hoje 1 e 2), na mesma
  escala, com o alternador mês a mês / acumulado. A Região 3 é citada no texto em vez
  de virar um painel vazio.
- **Página 11:** dois seletores (A e B), safra 2026 ou 2025 e mês a mês / acumulado.
  Sob cada mês, quem ficou à frente e por quantos hectares, na cor da região — não é
  bom nem ruim, então a pílula não usa verde e vermelho — e a divisão da área entre
  as duas. Escolher em A a região que está em B troca as duas de lugar. A Região 3
  aparece desabilitada no seletor.

Nas duas, clicar numa barra abre o mesmo modal da página 9 filtrado pela região. O
total de cada região-mês é a soma das linhas de fazenda, então o modal fecha com a
barra. Os dados ficam em `IRRIGACAO.convencional.regioes`; os blocos de cada região
saem da coluna BLOCOS da mesma aba (o nome vem só na primeira linha do bloco, em
célula mesclada, e vale até o próximo).

### A página 12 (disponibilidade mecânica)

**Disponibilidade % = horas fora da oficina ÷ horas do período**, somadas sobre as
frotas do filtro, de 07/04 a 30/09 nos dois anos. Como toda frota tem as mesmas horas
no mês (576 h em abril, 744 ou 720 nos demais), a razão entre somas é também a média
das frotas.

- **Seletor de várias especialidades:** uma lista com caixas de marcar, agrupada
  por grupo. Marcar o grupo marca todas as especialidades dele (o grupo fica
  "meio marcado" quando só parte está); dá para misturar grupos (ex.: caminhão
  canavieiro + colhedora). Nada marcado = frota inteira; "Limpar" volta para ela. O
  grupo é o prefixo da especialidade (`CAMINHAO - BOMBEIRO` → CAMINHAO): a coluna de
  agrupamento do cadastro vem vazia em 10 frotas.
- **Gráfico:** barras de 2025 e 2026 em escala de 0 a 100%, a meta de 85% tracejada e,
  sob cada mês, a diferença em pontos percentuais. Alternador mês a mês / acumulado (o
  acumulado é a disponibilidade da safra até aquele mês).
- **Quadro ao lado:** o que está dentro do filtro, do pior ao melhor na safra 2026, com
  a variação em p.p. — sem filtro, os grupos; com várias especialidades, cada uma; com
  uma só, as frotas. Clicar numa linha filtra só por ela. No pé do quadro, os cards
  do **acumulado da safra** (07/04 a 30/09): 2025, 2026 e a diferença em p.p., em %
  sobre 2025 e em horas de oficina. A página não tem mais as fichas do topo.
- **Diferenças** (pílulas, quadro, cards e texto) são calculadas entre os valores como
  aparecem, com uma casa — 70,6% − 62,2% dá +8,4 p.p. na tela, sem a sobra do
  arredondamento.
- **Clicar numa barra** abre o mês frota a frota, da pior para a melhor, com a conta
  no topo e o total fechando com a barra.

**De onde vem o %.** O % de cada frota no mês é o da **aba `Base`** de cada ano — é
ali que a operação corrige o número. A Base bate com o relatório mensal (abas ABR a
SET) em todas as frotas, menos nas correções feitas à mão; em 2026: setembro das
colhedoras 62504, 62513, 62514, 62515 e 62521, e julho da 62507. Onde a Base concorda,
o arquivo guarda as horas do relatório; onde foi corrigida, as horas saem do % dela.
O relatório mensal diz também quem esteve no relatório do mês e as horas do período.

**Quem fica fora da conta** (fora = não vale 0%, simplesmente não entra naquele mês):

- **Código fora de 60000 a 69999**, a faixa da CRV-MG. As 22xxx (tratores e
  colhedoras de Goiás, que só aparecem no relatório de agosto) saem.
- **Frota que não está na Base daquele ano.** As colhedoras 62500, 62502, 62508 e
  62509 saíram da Base de 2026 (ficaram paradas, a 100% sem uma hora de oficina);
  em 2025, quando trabalharam, continuam.
- **Frota que não aparece no relatório do mês.**
- **Mês em branco na Base**, mesmo com a frota no relatório: em 2026, a 62511 o ano
  todo, a 62507 em agosto e setembro e a 62519 em setembro. Em 2025 a Base não tem
  branco.
- **Frota que ainda não existia.** O relatório mostra a frota a 100% nos meses antes
  da compra, então ela só entra se a **data de aquisição** for anterior ao início do
  período (07/04 em abril, dia 1 nos demais) — o mês da compra, parcial, também fica
  fora. Isso tira 87 frotas de parte de 2025 (as colhedoras 62522 a 62529, os
  tratores 62272 a 62284, caminhões, motos, implementos…) e 4 de 2026.
- **Pedido da operação:** os caminhões canavieiros 60551 a 60555 saem de 2025 — 100% o
  ano todo sem uma hora de oficina; os 60553-55 nem têm data de compra (placas novas,
  ativos a partir de julho/2026).
- Equipamentos do relatório **sem cadastro** (40 a 52 por mês: sopradores,
  geradores, motosserras), porque não têm especialidade.

Com essas regras, a safra 2025 fica em 79,6% e a 2026 em 81,2% (+1,6 p.p.). A aba
`GERAL` da planilha faz a média simples das frotas do cadastro, com Goiás e com as
ausentes valendo 0 e as ainda não compradas a 100% — por isso não bate com a página:
em 2025 a página fica de 0,7 a 1,6 p.p. abaixo dela, em 2026 de 0,5 a 1,0 p.p. acima.
A página diz isso no texto.

Os dados ficam em `window.DISPONIBILIDADE`: horas do período por mês, a lista de
grupos e especialidades e, por frota, as horas em oficina de cada mês nas duas safras
(`null` = fora da conta naquele mês). Fonte: `DISPONIBILIDADE MANUTENÇÃO - frente -
2025.xlsx` e `- 2026.xlsx`, aba `Base` (% e cadastro) e abas ABR a SET (relatório).

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
`caminhão` e `transbordo`; `Produção localizada - SAFRA 2025/2026.xlsx`, aba
`Banco Localizada`, para a irrigação localizada; e `FECHAMENTO FINAL SAFRA 2025.xlsx`
e `FECHAMENTO IRRIGAÇÃO SAFRA 2026.xlsx`, aba `banco de dados`, para a convencional.
A aba `COMPARATIVO MES` dessas planilhas não serve de conferência: os meses finais
de 2025 trazem valores redondos (3.000, 2.800) que não batem com o banco de dados.

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
