# -*- coding: utf-8 -*-
"""Atualiza os blocos de dados do index.html a partir das planilhas.

Reescreve window.MOAGEM, as listas de máquinas de window.FROTA e window.IRRIGACAO.
A Manutenção (DISPONIBILIDADE, CUSTO_OP, CUSTO_ESP) não é tocada.

A janela é a mesma nos dois anos: do início de cada safra até o dia/mês de --fim.
Com --fim 2026-10-15, outubro entra de 1 a 15 em 2025 e em 2026.

Uso (os nomes de arquivo são os que a UGS manda):

    python scripts/atualiza_dados.py --fim 2026-10-15 \
        --moagem "MOAGEM COMPARATIVO - base.xlsx" \
        --loc2025 "Produção localizada - SAFRA 2025.xlsx" \
        --loc2026 "Produção localizada - SAFRA 2026.xlsx" \
        --conv2025 "FECHAMENTO FINAL SAFRA 2025.xlsx" \
        --conv2026 "FECHAMENTO IRRIGAÇÃO SAFRA 2026.xlsx"

Precisa de openpyxl. Sem --gravar, só confere e mostra o resumo.
"""
import argparse, collections, datetime, json, re, sys

import openpyxl

MESES = ["Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
CURTO = ["Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
ABREV = {"abr": 0, "mai": 1, "jun": 2, "jul": 3, "ago": 4, "set": 5, "out": 6, "nov": 7, "dez": 8}

# Correções de digitação na aba Moagem, conferidas contra a pesagem por empresa
# (pesagem 2025 e 2026.xlsx). (código, ano, índice do mês) -> tonelada.
CORRECOES_MOAGEM = {
    # a base traz 147.663; a pesagem da Uruaçu em junho/2026 é 147.632,51
    ("AGRO-URU", 2026, 2): 147633,
}


# ---------------------------------------------------------------- leitura

def num(v, maior=False):
    """Número da planilha. Aceita texto ('5.20', '7,25'); com maior=True, 'a/b'
    vira o maior dos dois (vazão digitada como faixa). Erro do Excel vira None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", ".")
    if not s or s.startswith("#"):
        return None
    try:
        if "/" in s:
            p = [float(x) for x in s.split("/") if x.strip()]
            return max(p) if (maior and p) else None
        return float(s)
    except ValueError:
        return None


def abre(arq):
    return openpyxl.load_workbook(arq, read_only=True, data_only=True)


def linhas(wb, aba):
    return list(wb[aba].iter_rows(values_only=True))


def r1(x):
    return round(x + 0.0, 1)


# ---------------------------------------------------------------- moagem

def le_moagem(wb, nmes):
    """Aba Moagem: uma linha por unidade e mês. Aba Início safra: datas de abertura."""
    ton = collections.defaultdict(lambda: {2025: [None] * nmes, 2026: [None] * nmes})
    for r in linhas(wb, "Moagem")[1:]:
        if not r[0]:
            continue
        i = MESES.index(str(r[2]).strip())
        if i >= nmes:
            continue
        ton[r[0]][2025][i] = int(round(r[3]))
        ton[r[0]][2026][i] = int(round(r[4]))
    for (cod, ano, i), v in CORRECOES_MOAGEM.items():
        if ton[cod][ano][i] != v:
            print("  correção: %s %d %s %s -> %d" % (cod, ano, MESES[i], ton[cod][ano][i], v))
            ton[cod][ano][i] = v
    ini = {}
    for r in linhas(wb, "Início safra")[1:]:
        if r[0]:
            ini[r[0]] = (str(r[2])[:10], str(r[3])[:10])
    return ton, ini


def bloco_moagem(atual, ton, ini, nmes, fim):
    """Mesmo texto do bloco atual, com meses, toneladas e datas novas. Nome, cor
    e ordem das unidades continuam os do index.html."""
    out = ["window.MOAGEM = {",
           "  meses: %s," % json.dumps(MESES[:nmes], ensure_ascii=False).replace(", ", ","),
           "  mesesCurto: %s," % json.dumps(CURTO[:nmes], ensure_ascii=False).replace(", ", ","),
           "  // último mês da janela: vai até este dia nos DOIS anos (null = mês inteiro)",
           "  fimDia: %s," % (fim.day if fim.day < dias_mes(fim) else "null"),
           "  // ordem de exibição em todas as páginas: CRV Minas Gerais, CRV Goiás,",
           "  // Agro Rubiataba e Agro Uruaçu — legendas, pilhas, painéis e seletores",
           "  // seguem esta lista",
           "  unidades: ["]
    us = atual["unidades"]
    for k, u in enumerate(us):
        cod = u["cod"]
        if None in ton[cod][2025] or None in ton[cod][2026]:
            sys.exit("Moagem incompleta para %s: %s" % (cod, ton[cod]))
        out.append('    {cod:"%s", nome:"%s", curto:"%s", cor:"%s",' % (cod, u["nome"], u["curto"], u["cor"]))
        out.append("     a2025:[%s]," % ",".join(map(str, ton[cod][2025])))
        out.append("     a2026:[%s]," % ",".join(map(str, ton[cod][2026])))
        out.append('     ini2025:"%s", ini2026:"%s"}%s' % (ini[cod][0], ini[cod][1], "," if k < len(us) - 1 else ""))
    out += ["  ]", "};"]
    return "\n".join(out)


def dias_mes(d):
    prox = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    return (prox - datetime.timedelta(days=1)).day


# ---------------------------------------------------------------- frota

def mes_ano(v):
    """A coluna Mês vem como texto ('out-2025') ou, em alguns meses, como data."""
    if isinstance(v, datetime.datetime):
        return v.year, v.month - 4
    m, a = str(v).strip().lower().split("-")
    return int(a), ABREV[m[:3]]


def le_frota(wb, nmes):
    """Uma linha por máquina e mês. 'Km Rodado' é hora na colhedora e no
    transbordo (ver README). comb/manut = R$/t da parcela × tonelada."""
    out = {}
    for aba, chave, viag in (("Colhedora", "colhedora", False), ("Caminhão", "caminhao", True),
                             ("Transbordo", "transbordo", True)):
        vistas = {}
        for r in linhas(wb, aba)[1:]:
            if r[0] is None or r[1] is None:
                continue
            ano, m = mes_ano(r[0])
            if m >= nmes:
                continue
            x = [int(r[1]), ano - 2025, m, r1(r[3]), r1(r[4]), r1(r[5]), round(r[7]),
                 round(r[9] * r[5]), round(r[10] * r[5]), int(r[11])]
            if viag:
                x.append(int(r[19]))
            k = (x[0], x[1], x[2])
            if k in vistas:
                sys.exit("%s: máquina repetida no mesmo mês %s" % (aba, k))
            vistas[k] = x
        # ordem do arquivo: ano, mês e, dentro do mês, da maior tonelada para a menor
        out[chave] = sorted(vistas.values(), key=lambda x: (x[1], x[2], -x[5], x[0]))
    return out


def fmt_maquina(x):
    # mesmo formato que já estava no arquivo: uma casa, sem ".0" quando redondo
    def f(v):
        return (("%.1f" % v).rstrip("0").rstrip(".")) if isinstance(v, float) else str(v)
    return "[" + ",".join(f(v) for v in x) + "]"


# ---------------------------------------------------------------- irrigação

def le_localizada(arq, ano, fim):
    lin = []
    for r in linhas(abre(arq), "Banco Localizada")[1:]:
        d = r[0]
        if not isinstance(d, datetime.datetime) or d.year != ano or d.month < 4 or d.date() > fim:
            continue
        if r[2] is None:
            continue
        lin.append(dict(d=d.date(), f=str(r[2]).strip(), ha=num(r[8]) or 0.0,
                        vz=num(r[9], maior=True), tq=int(num(r[7]) or 0)))
    return lin


def agrega_localizada(lin, ano, nmes):
    fz = collections.defaultdict(lambda: dict(ha=0.0, hv=0.0, hav=0.0, dias=set(), tq=0))
    for x in lin:
        F = fz[(x["f"], x["d"].month - 4)]
        F["ha"] += x["ha"]; F["dias"].add(x["d"]); F["tq"] += x["tq"]
        if x["vz"]:
            F["hv"] += x["ha"] * x["vz"]; F["hav"] += x["ha"]
    det = []
    for (f, m), F in fz.items():
        if F["ha"] <= 0 and F["tq"] == 0:
            continue
        det.append([f, ano - 2025, m, r1(F["ha"]), len(F["dias"]), F["tq"],
                    r1(F["hv"] / F["hav"]) if F["hav"] else None])
    meses = []
    for m in range(nmes):
        D = [x for x in det if x[2] == m]
        Fs = [v for k, v in fz.items() if k[1] == m]
        # vazão do mês: ponderada pela área, a partir das mesmas linhas do modal
        hv = sum(x[3] * x[6] for x in D if x[6]); hav = sum(x[3] for x in D if x[6])
        meses.append(dict(ha=r1(sum(x[3] for x in D)), vazao=r1(hv / hav) if hav else None,
                          dias=len(set().union(*[v["dias"] for v in Fs])) if Fs else 0,
                          faz=len(D), tanques=sum(v["tq"] for v in Fs)))
    return meses, det, len({x[0] for x in det}), min(x["d"] for x in lin)


def cod_conv(v):
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return re.sub(r"\s+", "", str(v)).upper()


def lamina(desc):
    m = re.search(r"(\d)\s*[ºª°]", str(desc or ""))
    return int(m.group(1)) if m else None


def le_convencional(arq, ano, fim):
    lin, nomes = [], {}
    for r in linhas(abre(arq), "banco de dados")[1:]:
        d = r[0]
        if not isinstance(d, datetime.datetime) or d.year != ano or d.month < 4 or d.date() > fim:
            continue
        if r[3] is None:
            continue
        c = cod_conv(r[3])
        if r[4]:
            nomes[c] = re.sub(r"\s+", " ", str(r[4])).strip()
        lin.append(dict(d=d.date(), f=c, ha=num(r[16]) or 0.0, vel=num(r[18]),
                        vin="VINH" in str(r[5] or "").upper(), lam=lamina(r[15]), desc=r[15]))
    sem = [x["desc"] for x in lin if not x["lam"]]
    if sem:
        sys.exit("Convencional %d: lâmina não reconhecida em %d puxadas, ex.: %r" % (ano, len(sem), sem[:3]))
    return lin, nomes


def agrega_convencional(lin, ano, nmes, nlam, filtro=None):
    fz = collections.defaultdict(lambda: dict(ha=0.0, dias=set(), pux=0, vs=0.0, hv=0.0, vin=0.0))
    lam_mes = [[0.0] * nlam for _ in range(nmes)]
    for x in lin:
        if filtro and not filtro(x):
            continue
        m = x["d"].month - 4
        F = fz[(x["f"], m)]
        F["ha"] += x["ha"]; F["dias"].add(x["d"]); F["pux"] += 1
        if x["vin"]:
            F["vin"] += x["ha"]
        # velocidade só das puxadas entre 3 e 120 m/h (zero = falta hora final)
        if x["vel"] is not None and 3 <= x["vel"] <= 120:
            F["vs"] += x["ha"] * x["vel"]; F["hv"] += x["ha"]
        lam_mes[m][x["lam"] - 1] += x["ha"]
    det = [[f, ano - 2025, m, r1(F["ha"]), len(F["dias"]), F["pux"],
            r1(F["vs"] / F["hv"]) if F["hv"] else None, r1(F["vin"]), r1(F["hv"])]
           for (f, m), F in fz.items()]
    meses = []
    for m in range(nmes):
        Fs = [v for k, v in fz.items() if k[1] == m]
        D = [x for x in det if x[2] == m]
        hv = sum(v["hv"] for v in Fs); vs = sum(v["vs"] for v in Fs)
        meses.append(dict(ha=r1(sum(x[3] for x in D)), vel=r1(vs / hv) if hv else None,
                          dias=len(set().union(*[v["dias"] for v in Fs])) if Fs else 0,
                          faz=len(D), puxadas=sum(v["pux"] for v in Fs),
                          vinhaca=r1(sum(x[7] for x in D)), haVel=r1(hv)))
    lam_safra = [r1(sum(l[k] for l in lam_mes)) for k in range(nlam)]
    # mês a mês: o resíduo do arredondamento fica na maior lâmina, para a pilha
    # fechar com o total do mês
    lm = []
    for m, l in enumerate(lam_mes):
        rr = [r1(v) for v in l]
        res = r1(meses[m]["ha"] - sum(rr))
        if res and any(rr):
            k = rr.index(max(rr)); rr[k] = r1(rr[k] + res)
        lm.append(rr)
    ini = min(x["d"] for x in lin) if lin else None
    return meses, det, len({x[0] for x in det}), lam_safra, lm, ini


def le_regioes(arq):
    """Aba faz. do fechamento de 2026: região e bloco de cada fazenda. O bloco
    vem só na primeira linha (célula mesclada) e vale até o próximo. Código
    combinado ('9343/44/64') vale para cada fazenda da lista."""
    reg, blocos, atual = {}, collections.defaultdict(list), None
    for r in linhas(abre(arq), "faz.")[2:]:
        if r[0] is None:
            continue
        if len(r) > 6 and r[6]:
            atual = str(r[6]).strip()
        if not isinstance(r[5], (int, float)):
            continue
        n = int(r[5])
        c = cod_conv(r[0])
        if "/" in c:
            partes = c.split("/")
            base = partes[0]
            cods = [base] + [base[:len(base) - len(p)] + p for p in partes[1:]]
        else:
            cods = [c]
        for x in cods:
            reg[x] = n
        if atual and atual not in blocos[n]:
            blocos[n].append(atual)
    return reg, blocos


def nome_bloco(b):
    # "BLOCO 04 - THIAGO AMUY" -> "04 Thiago Amuy"
    m = re.match(r"BLOCO\s*(\d+)\s*-\s*(.*)", b, re.I)
    if not m:
        return b
    pal = [p.lower() if p.lower() in ("de", "da", "do", "das", "dos", "e") else p.capitalize()
           for p in m.group(2).split()]
    return m.group(1).zfill(2) + " " + " ".join(pal)


# ---------------------------------------------------------------- escrita JS

def js(v):
    if v is None:
        return "null"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return "0" if v == 0 else "%.1f" % v
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ",".join(js(x) for x in v) + "]"
    raise TypeError(v)


def js_mes(d, chaves):
    return "{" + ", ".join("%s:%s" % (k, js(d[k])) for k in chaves) + "}"


def js_lista_meses(arr, chaves, ind):
    return "[\n" + ",\n".join(ind + js_mes(m, chaves) for m in arr) + "\n" + ind[:-2] + "]"


def js_dict(d):
    return "{" + ",".join("%s:%s" % (json.dumps(k, ensure_ascii=False), js(v)) for k, v in d.items()) + "}"


def js_fazendas(det):
    return "[\n" + ",\n".join("      " + js(x) for x in det) + "\n    ]"


def ordena_det(det):
    # ano, mês e, dentro do mês, da maior área para a menor
    return sorted(det, key=lambda x: (x[1], x[2], -x[3], x[0]))


def bloco_irrigacao(atual, L, C, regs, regiao_faz, blocos):
    LOC = ["ha", "vazao", "dias", "faz", "tanques"]
    CONV = ["ha", "vel", "dias", "faz", "puxadas", "vinhaca", "haVel"]
    la, ca = atual["localizada"], atual["convencional"]
    o = ["window.IRRIGACAO = {", "  localizada: {",
         '    nome: "%s", unidade: "%s",' % (la["nome"], la["unidade"]),
         '    ini2025: "%s", ini2026: "%s",' % (L[2025]["ini"], L[2026]["ini"]),
         "    fazTotal: [%d, %d]," % (L[2025]["faz"], L[2026]["faz"]),
         "    a2025: " + js_lista_meses(L[2025]["meses"], LOC, "      ") + ",",
         "    a2026: " + js_lista_meses(L[2026]["meses"], LOC, "      ") + ",",
         '    campos: ["fazenda","ano","mes","ha","dias","tanques","vazao"],',
         "    nomes: " + js_dict(L["nomes"]) + ",",
         "    fazendas: " + js_fazendas(ordena_det(L[2025]["det"] + L[2026]["det"])),
         "  },", "  convencional: {",
         '    nome: "%s", unidade: "%s",' % (ca["nome"], ca["unidade"]),
         '    ini2025: "%s", ini2026: "%s",' % (C[2025]["ini"], C[2026]["ini"]),
         "    fazTotal: [%d, %d]," % (C[2025]["faz"], C[2026]["faz"]),
         "    a2025: " + js_lista_meses(C[2025]["meses"], CONV, "      ") + ",",
         "    a2026: " + js_lista_meses(C[2026]["meses"], CONV, "      ") + ",",
         "    laminas: {a2025: %s, a2026: %s}," % (js(C[2025]["lam"]), js(C[2026]["lam"])),
         "    laminasMes: {a2025: %s, a2026: %s}," % (js(C[2025]["lamMes"]), js(C[2026]["lamMes"])),
         "    regioes: ["]
    nums = sorted(regs)
    for k, n in enumerate(nums):
        R = regs[n]
        o.append("      {num:%d, blocos:%s, fazTotal:[%d, %d]," % (
            n, js([nome_bloco(b) for b in sorted(blocos[n])]), R[2025]["faz"], R[2026]["faz"]))
        o.append("       laminas: {a2025: %s, a2026: %s}," % (js(R[2025]["lam"]), js(R[2026]["lam"])))
        o.append("       a2025: [" + ", ".join(js_mes(m, CONV) for m in R[2025]["meses"]) + "],")
        o.append("       a2026: [" + ", ".join(js_mes(m, CONV) for m in R[2026]["meses"]) + "]}" +
                 ("," if k < len(nums) - 1 else ""))
    o += ["    ],",
          "    regiaoFaz: " + js_dict(dict(sorted(regiao_faz.items()))) + ",",
          '    campos: ["fazenda","ano","mes","ha","dias","puxadas","vel","vinhaca","haVel"],',
          "    nomes: " + js_dict(C["nomes"]) + ",",
          "    fazendas: " + js_fazendas(ordena_det(C[2025]["det"] + C[2026]["det"])),
          "  }", "};"]
    return "\n".join(o)


# ---------------------------------------------------------------- index.html

def acha_objeto(html, inicio):
    """Posição [i, j) do texto 'window.X = {...};' a partir de 'inicio'."""
    i = html.index(inicio)
    k = html.index("{", i)
    n = 0
    for j in range(k, len(html)):
        c = html[j]
        if c == "{":
            n += 1
        elif c == "}":
            n -= 1
            if n == 0:
                break
    assert html[j + 1] == ";", "fim do objeto inesperado em %s" % inicio
    return i, j + 2


def carrega(html, nome):
    i, j = acha_objeto(html, "window.%s = {" % nome)
    s = html[html.index("{", i):j - 1]
    s = re.sub(r"//[^\n]*", "", s)
    s = re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:', r'\1"\2":', s)
    s = re.sub(r",(\s*[}\]])", r"\1", s)
    return json.loads(s)


def troca_maquinas(html, chave, maquinas):
    i = html.index("  %s: {" % chave, html.index("window.FROTA = {"))
    a = html.index("maquinas: [", i) + len("maquinas: [")
    n, j = 1, a
    while n:
        c = html[j]
        n += (c == "[") - (c == "]")
        j += 1
    corpo = "\n" + ",\n".join("      " + fmt_maquina(x) for x in maquinas) + "\n    "
    return html[:a] + corpo + html[j - 1:]


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fim", required=True, help="último dia da janela de 2026 (AAAA-MM-DD); vale o mesmo dia/mês em 2025")
    ap.add_argument("--moagem", required=True)
    ap.add_argument("--loc2025", required=True)
    ap.add_argument("--loc2026", required=True)
    ap.add_argument("--conv2025", required=True)
    ap.add_argument("--conv2026", required=True)
    ap.add_argument("--html", default="index.html")
    ap.add_argument("--gravar", action="store_true", help="grava o index.html; sem isto só confere")
    a = ap.parse_args()

    fim = datetime.date.fromisoformat(a.fim)
    nmes = fim.month - 3                       # abril = 1 mês
    fims = {2025: fim.replace(year=2025), 2026: fim}
    html = open(a.html, encoding="utf-8").read()

    print("Janela: início da safra até %s nos dois anos (%d meses)" % (fim.strftime("%d/%m"), nmes))

    # moagem e frota
    wb = abre(a.moagem)
    ton, ini = le_moagem(wb, nmes)
    novo_moagem = bloco_moagem(carrega(html, "MOAGEM"), ton, ini, nmes, fim)
    frota = le_frota(wb, nmes)
    for k, v in frota.items():
        print("  frota %-10s %4d máquina-mês" % (k, len(v)))

    # irrigação localizada
    L = {}
    for ano, arq in ((2025, a.loc2025), (2026, a.loc2026)):
        lin = le_localizada(arq, ano, fims[ano])
        meses, det, faz, ini_ = agrega_localizada(lin, ano, nmes)
        L[ano] = dict(meses=meses, det=det, faz=faz, ini=ini_.isoformat())
        print("  localizada %d: %.1f ha, %d fazendas, de %s a %s" % (
            ano, sum(m["ha"] for m in meses), faz, ini_.strftime("%d/%m"), max(x["d"] for x in lin).strftime("%d/%m")))

    # irrigação convencional, total e por região
    atual = carrega(html, "IRRIGACAO")
    nlam = len(atual["convencional"]["laminas"]["a2025"])
    regiao_faz, blocos = le_regioes(a.conv2026)
    C, nomes_conv, linc = {}, {}, {}
    for ano, arq in ((2025, a.conv2025), (2026, a.conv2026)):
        lin, nomes = le_convencional(arq, ano, fims[ano])
        linc[ano] = lin
        nomes_conv.update(nomes)
        if max(x["lam"] for x in lin) > nlam:
            sys.exit("Convencional %d: apareceu a %dª lâmina — aumente o número de lâminas" % (ano, max(x["lam"] for x in lin)))
        meses, det, faz, lam, lm, ini_ = agrega_convencional(lin, ano, nmes, nlam)
        C[ano] = dict(meses=meses, det=det, faz=faz, lam=lam, lamMes=lm, ini=ini_.isoformat())
        sem_reg = sorted({x["f"] for x in lin} - set(regiao_faz))
        if sem_reg:
            sys.exit("Convencional %d: fazendas sem região na aba faz.: %s" % (ano, sem_reg))
        print("  convencional %d: %.1f ha, %d fazendas, de %s a %s, velocidade cobre %.0f%% da área" % (
            ano, sum(m["ha"] for m in meses), faz, ini_.strftime("%d/%m"), max(x["d"] for x in lin).strftime("%d/%m"),
            100 * sum(m["haVel"] for m in meses) / sum(m["ha"] for m in meses)))
    regs = {}
    for n in sorted(set(regiao_faz.values())):
        regs[n] = {}
        for ano in (2025, 2026):
            meses, det, faz, lam, lm, _ = agrega_convencional(
                linc[ano], ano, nmes, nlam, filtro=lambda x, n=n: regiao_faz.get(x["f"]) == n)
            regs[n][ano] = dict(meses=meses, faz=faz, lam=lam)

    # nomes de fazenda: os que já estavam valem, os novos entram
    C["nomes"] = dict(atual["convencional"]["nomes"])
    for k, v in sorted(nomes_conv.items()):
        C["nomes"].setdefault(k, v)
    L["nomes"] = dict(atual["localizada"]["nomes"])
    for ano in (2025, 2026):
        for x in L[ano]["det"]:
            if x[0] not in L["nomes"] and x[0] in C["nomes"]:
                L["nomes"][x[0]] = C["nomes"][x[0]]
    novo_irriga = bloco_irrigacao(atual, L, C, regs, regiao_faz, blocos)

    if not a.gravar:
        print("Conferido. Rode de novo com --gravar para escrever o %s." % a.html)
        return
    i, j = acha_objeto(html, "window.MOAGEM = {")
    html = html[:i] + novo_moagem + html[j:]
    for k, v in frota.items():
        html = troca_maquinas(html, k, v)
    i, j = acha_objeto(html, "window.IRRIGACAO = {")
    html = html[:i] + novo_irriga + html[j:]
    open(a.html, "w", encoding="utf-8").write(html)
    print("Gravado:", a.html)


if __name__ == "__main__":
    main()
