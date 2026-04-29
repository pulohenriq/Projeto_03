# =============================================================
# steampy.py - Sistema Principal SteamPy
# Plataforma de organização, consumo e análise de jogos digitais
# =============================================================

import csv
import os
from datetime import datetime
from collections import Counter

from jogos import Jogo
from filabacklog import FilaBackLog
from pilharecente import PilhaRecentes


# =============================================================
# CLASSE SESSAO DE JOGO
# =============================================================
class SessaoJogo:
    def __init__(self, jogo, tempo_jogado):
        self.jogo               = jogo
        self.tempo_jogado       = tempo_jogado
        self.data_sessao        = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.percentual_simulado = 0.0
        self.status             = self._calcular_status(tempo_jogado)

    def _calcular_status(self, horas):
        if horas < 2:
            return "iniciado"
        elif horas < 10:
            return "em_andamento"
        elif horas < 20:
            return "muito_jogado"
        else:
            return "concluido_simbolicamente"

    def exibir(self):
        print(f"  Jogo   : {self.jogo.titulo}")
        print(f"  Tempo  : {self.tempo_jogado}h  |  Status: {self.status}")
        print(f"  Data   : {self.data_sessao}")
        print(f"  {'-'*40}")


# =============================================================
# CLASSE PRINCIPAL STEAMPY
# =============================================================
class SteamPy:
    def __init__(self):
        self.catalogo_lista  = []          # lista de objetos Jogo
        self.catalogo_dict   = {}          # dict: id -> Jogo
        self.backlog         = FilaBackLog()
        self.recentes        = PilhaRecentes(limite=20)
        self.historico       = []          # lista de SessaoJogo
        self.tempo_por_jogo  = {}          # dict: jogo_id -> horas totais
        self.recomendacoes   = []          # lista de Jogo
        self.ranking         = []          # lista de Jogo ordenada por tempo

    # ----------------------------------------------------------
    # PARTE 1 - CARREGAMENTO DO CATÁLOGO
    # ----------------------------------------------------------
    def carregar_jogos(self, nome_arquivo="dataset.csv"):
        self.catalogo_lista = []
        self.catalogo_dict  = {}
        contador = 0
        invalidas = 0

        try:
            with open(nome_arquivo, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        def safe_float(val):
                            try:
                                return float(val) if val.strip() != "" else 0.0
                            except:
                                return 0.0

                        jogo = Jogo(
                            idJogo      = contador,
                            titulo      = row["title"].strip(),
                            console     = row["console"].strip(),
                            genero      = row["genre"].strip(),
                            publisher   = row["publisher"].strip(),
                            developer   = row["developer"].strip(),
                            critic_score= safe_float(row["critic_score"]),
                            totalSales  = safe_float(row["total_sales"]),
                            naSales     = safe_float(row["na_sales"]),
                            jpSales     = safe_float(row["jp_sales"]),
                            palSales    = safe_float(row["pal_sales"]),
                            otherSales  = safe_float(row["other_sales"]),
                            releaseDate = row["release_date"].strip()
                        )
                        self.catalogo_lista.append(jogo)
                        self.catalogo_dict[contador] = jogo
                        contador += 1
                    except Exception:
                        invalidas += 1

            print(f"\n  Catálogo carregado: {contador} jogos  ({invalidas} linha(s) ignorada(s))")
        except FileNotFoundError:
            print(f"\n  ERRO: arquivo '{nome_arquivo}' não encontrado.")
        except Exception as e:
            print(f"\n  ERRO ao carregar: {e}")

    # ----------------------------------------------------------
    # PARTE 2 - BUSCA, FILTROS E ORDENAÇÃO
    # ----------------------------------------------------------
    def listar_jogos(self, lista=None, limite=50):
        alvo = lista if lista is not None else self.catalogo_lista
        if not alvo:
            print("  Nenhum jogo encontrado.")
            return
        print(f"\n  {'='*65}")
        print(f"  {'CATALOGO DE JOGOS':^65}")
        print(f"  {'='*65}")
        for numero, j in enumerate(alvo[:limite], 1):
            print(f"  {numero:>4}. [{j.console}] {j.titulo} | {j.genero} | Nota: {j.critic_score} | Vendas: {j.totalSales}M")
        if len(alvo) > limite:
            print(f"\n  ... e mais {len(alvo) - limite} jogos. Total: {len(alvo)}")

    def buscar_jogo_por_nome(self, termo):
        termo = termo.lower().strip()
        resultado = [j for j in self.catalogo_lista if termo in j.titulo.lower()]
        print(f"\n  Resultados para '{termo}': {len(resultado)} jogo(s)")
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_genero(self, genero):
        genero = genero.strip().lower()
        resultado = [j for j in self.catalogo_lista if j.genero.lower() == genero]
        print(f"\n  Gênero '{genero}': {len(resultado)} jogo(s)")
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_console(self, console):
        console = console.strip().lower()
        resultado = [j for j in self.catalogo_lista if j.console.lower() == console]
        print(f"\n  Console '{console}': {len(resultado)} jogo(s)")
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_nota(self, nota_minima):
        resultado = [j for j in self.catalogo_lista if j.critic_score >= nota_minima]
        print(f"\n  Nota >= {nota_minima}: {len(resultado)} jogo(s)")
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_vendas(self, vendas_minimas):
        resultado = [j for j in self.catalogo_lista if j.totalSales >= vendas_minimas]
        print(f"\n  Vendas >= {vendas_minimas}M: {len(resultado)} jogo(s)")
        self.listar_jogos(resultado)
        return resultado

    def filtrar_por_publisher(self, publisher):
        publisher = publisher.strip().lower()
        resultado = [j for j in self.catalogo_lista if j.publisher.lower() == publisher]
        print(f"\n  Publisher '{publisher}': {len(resultado)} jogo(s)")
        self.listar_jogos(resultado)
        return resultado

    def ordenar_jogos(self, criterio):
        opcoes = {
            "1": ("titulo",      False, "Título (A-Z)"),
            "2": ("critic_score",True,  "Nota (maior primeiro)"),
            "3": ("totalSales",  True,  "Vendas Totais (maior primeiro)"),
            "4": ("releaseDate", False, "Data de Lançamento"),
            "5": ("console",     False, "Console (A-Z)"),
            "6": ("genero",      False, "Gênero (A-Z)"),
        }
        if criterio not in opcoes:
            print("  Critério inválido.")
            return
        campo, reverso, label = opcoes[criterio]
        self.catalogo_lista.sort(key=lambda j: getattr(j, campo) or "", reverse=reverso)
        print(f"\n  Catálogo ordenado por: {label}")
        self.listar_jogos()

    # ----------------------------------------------------------
    # PARTE 3 - BACKLOG (FILA)
    # ----------------------------------------------------------
    def adicionar_ao_backlog(self, jogo):
        self.backlog.enqueue(jogo)

    def mostrar_backlog(self):
        self.backlog.mostrar()

    def jogar_proximo(self):
        if self.backlog.is_empty():
            print("  Backlog vazio. Adicione jogos primeiro.")
            return
        jogo = self.backlog.dequeue()
        print(f"\n  Iniciando: [{jogo.console}] {jogo.titulo}")
        horas = self._pedir_tempo()
        self.registrar_sessao(jogo, horas)

    def salvar_backlog(self, nome="backlog.txt"):
        self.backlog.salvar(nome)

    def carregar_backlog(self, nome="backlog.txt"):
        self.backlog.carregar(self.catalogo_dict, nome)

    # ----------------------------------------------------------
    # PARTE 4 - RECENTES (PILHA)
    # ----------------------------------------------------------
    def mostrar_recentes(self):
        self.recentes.mostrar()

    def retomar_ultimo_jogo(self):
        jogo = self.recentes.topo()
        if jogo is None:
            print("  Nenhum jogo recente para retomar.")
            return
        print(f"\n  Retomando: [{jogo.console}] {jogo.titulo}")
        horas = self._pedir_tempo()
        self.registrar_sessao(jogo, horas)

    # ----------------------------------------------------------
    # PARTE 5 - SIMULAÇÃO DE TEMPO / SESSÃO
    # ----------------------------------------------------------
    def _pedir_tempo(self):
        while True:
            try:
                entrada = input("  Quantas horas jogou nesta sessão? ").strip()
                horas = float(entrada)
                if horas < 0:
                    print("  Valor inválido.")
                    continue
                return horas
            except ValueError:
                print("  Digite um número válido.")

    def registrar_sessao(self, jogo, tempo):
        sessao = SessaoJogo(jogo, tempo)

        # Acumula tempo total do jogo
        self.tempo_por_jogo[jogo.id] = self.tempo_por_jogo.get(jogo.id, 0) + tempo

        # Recalcula status com tempo total acumulado
        total = self.tempo_por_jogo[jogo.id]
        sessao.status = sessao._calcular_status(total)

        # Salva no histórico
        self.historico.append(sessao)

        # Empilha nos recentes
        self.recentes.push(jogo)

        # Atualiza ranking
        self._atualizar_ranking()

        print(f"\n  Sessão registrada!")
        print(f"  Tempo nesta sessão : {tempo}h")
        print(f"  Tempo total em '{jogo.titulo}': {total}h")
        print(f"  Status: {sessao.status}")

        # Salva histórico e recentes automaticamente
        self.salvar_historico()
        self.recentes.salvar()

    # ----------------------------------------------------------
    # PARTE 6 - HISTÓRICO COMPLETO
    # ----------------------------------------------------------
    def mostrar_historico(self):
        if not self.historico:
            print("  Nenhuma sessão registrada ainda.")
            return
        print(f"\n  {'='*55}")
        print(f"  {'HISTÓRICO COMPLETO DE SESSÕES':^55}")
        print(f"  {'='*55}")
        for i, s in enumerate(self.historico, 1):
            total = self.tempo_por_jogo.get(s.jogo.id, 0)
            print(f"  {i}. {s.jogo.titulo} | sessão: {s.tempo_jogado}h | total: {total}h | {s.status} | {s.data_sessao}")
        print(f"  {'='*55}")

    def salvar_historico(self, nome="historico_jogo.txt"):
        try:
            with open(nome, "w", encoding="utf-8") as f:
                f.write("titulo;tempo_sessao;tempo_total;status;data\n")
                for s in self.historico:
                    total = self.tempo_por_jogo.get(s.jogo.id, 0)
                    f.write(f"{s.jogo.titulo};{s.tempo_jogado};{total};{s.status};{s.data_sessao}\n")
        except Exception as e:
            print(f"  Erro ao salvar histórico: {e}")

    def carregar_historico(self, nome="historico_jogo.txt"):
        try:
            with open(nome, "r", encoding="utf-8") as f:
                linhas = f.readlines()
            for linha in linhas[1:]:
                linha = linha.strip()
                if not linha:
                    continue
                partes = linha.split(";")
                if len(partes) < 4:
                    continue
                titulo      = partes[0]
                tempo_s     = float(partes[1])
                tempo_total = float(partes[2])
                # Busca jogo no catálogo pelo título
                jogo = next((j for j in self.catalogo_lista if j.titulo == titulo), None)
                if jogo:
                    self.tempo_por_jogo[jogo.id] = tempo_total
                    sessao = SessaoJogo(jogo, tempo_s)
                    sessao.status = sessao._calcular_status(tempo_total)
                    if len(partes) > 4:
                        sessao.data_sessao = partes[4]
                    self.historico.append(sessao)
            if self.historico:
                print(f"  Histórico carregado: {len(self.historico)} sessão(ões).")
                self._atualizar_ranking()
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"  Erro ao carregar histórico: {e}")

    # ----------------------------------------------------------
    # PARTE 7 - RECOMENDAÇÕES
    # ----------------------------------------------------------
    def recomendar_jogos(self):
        if not self.historico:
            print("  Jogue alguns jogos primeiro para receber recomendações.")
            return []

        # Identifica perfil do usuário
        generos_jogados   = [s.jogo.genero   for s in self.historico]
        consoles_jogados  = [s.jogo.console  for s in self.historico]
        pub_jogados       = [s.jogo.publisher for s in self.historico]
        notas_jogadas     = [s.jogo.critic_score for s in self.historico if s.jogo.critic_score > 0]

        genero_fav   = Counter(generos_jogados).most_common(1)[0][0]
        console_fav  = Counter(consoles_jogados).most_common(1)[0][0]
        pub_fav      = Counter(pub_jogados).most_common(1)[0][0]
        nota_media   = sum(notas_jogadas) / len(notas_jogadas) if notas_jogadas else 0

        # IDs já jogados e no backlog
        ids_jogados  = {s.jogo.id for s in self.historico}
        ids_backlog  = {j.id for j in self.backlog.dados}
        ids_excluir  = ids_jogados | ids_backlog

        print(f"\n  Perfil detectado:")
        print(f"  Gênero favorito  : {genero_fav}")
        print(f"  Console favorito : {console_fav}")
        print(f"  Publisher favorita: {pub_fav}")
        print(f"  Nota média jogada: {nota_media:.1f}")
        print(f"\n  Critério: gênero={genero_fav}, console={console_fav}, nota>={nota_media:.1f}")

        # Pontua cada jogo do catálogo
        pontuados = []
        for jogo in self.catalogo_lista:
            if jogo.id in ids_excluir:
                continue
            pontos = 0
            if jogo.genero    == genero_fav:   pontos += 3
            if jogo.console   == console_fav:  pontos += 2
            if jogo.publisher == pub_fav:       pontos += 1
            if nota_media > 0 and jogo.critic_score >= nota_media:
                pontos += 2
            if pontos > 0:
                pontuados.append((pontos, jogo))

        pontuados.sort(key=lambda x: (-x[0], -x[1].totalSales))
        self.recomendacoes = [j for _, j in pontuados[:20]]

        print(f"\n  {'='*55}")
        print(f"  {'TOP RECOMENDAÇÕES':^55}")
        print(f"  {'='*55}")
        for i, j in enumerate(self.recomendacoes[:10], 1):
            print(f"  {i}. [{j.console}] {j.titulo} | {j.genero} | Nota: {j.critic_score}")
        print(f"  {'='*55}")
        return self.recomendacoes

    # ----------------------------------------------------------
    # PARTE 8 - RANKING PESSOAL
    # ----------------------------------------------------------
    def _atualizar_ranking(self):
        vistos = {}
        for s in self.historico:
            vistos[s.jogo.id] = s.jogo
        self.ranking = sorted(vistos.values(),
                              key=lambda j: self.tempo_por_jogo.get(j.id, 0),
                              reverse=True)

    def gerar_ranking_pessoal(self):
        if not self.ranking:
            print("  Nenhum jogo jogado ainda.")
            return

        print(f"\n  {'='*60}")
        print(f"  {'RANKING PESSOAL':^60}")
        print(f"  {'='*60}")

        # 1. Jogos mais jogados (por tempo)
        print(f"\n  >> JOGOS MAIS JOGADOS (por tempo total)")
        for i, j in enumerate(self.ranking[:10], 1):
            h = self.tempo_por_jogo.get(j.id, 0)
            print(f"  {i}. {j.titulo} ({j.console}) — {h}h")

        # 2. Gêneros mais jogados
        print(f"\n  >> GÊNEROS MAIS JOGADOS")
        genero_tempo = {}
        for s in self.historico:
            g = s.jogo.genero
            genero_tempo[g] = genero_tempo.get(g, 0) + s.tempo_jogado
        for i, (g, h) in enumerate(sorted(genero_tempo.items(), key=lambda x: -x[1])[:5], 1):
            print(f"  {i}. {g} — {h}h")

        # 3. Consoles mais jogados
        print(f"\n  >> CONSOLES MAIS JOGADOS")
        console_tempo = {}
        for s in self.historico:
            c = s.jogo.console
            console_tempo[c] = console_tempo.get(c, 0) + s.tempo_jogado
        for i, (c, h) in enumerate(sorted(console_tempo.items(), key=lambda x: -x[1])[:5], 1):
            print(f"  {i}. {c} — {h}h")

        # 4. Top por nota dentro do histórico
        print(f"\n  >> TOP JOGOS POR NOTA (do histórico)")
        jogos_hist = list({s.jogo.id: s.jogo for s in self.historico}.values())
        jogos_hist.sort(key=lambda j: j.critic_score, reverse=True)
        for i, j in enumerate(jogos_hist[:5], 1):
            print(f"  {i}. {j.titulo} — Nota: {j.critic_score}")

        print(f"  {'='*60}")

    # ----------------------------------------------------------
    # PARTE 9 - DASHBOARD
    # ----------------------------------------------------------
    def exibir_dashboard(self):
        total_sessoes  = len(self.historico)
        total_tempo    = sum(s.tempo_jogado for s in self.historico)
        media_sessao   = total_tempo / total_sessoes if total_sessoes > 0 else 0

        jogos_unicos   = {s.jogo.id: s.jogo for s in self.historico}
        notas_hist     = [j.critic_score for j in jogos_unicos.values() if j.critic_score > 0]
        nota_media_h   = sum(notas_hist) / len(notas_hist) if notas_hist else 0

        # Status
        status_count = {"iniciado": 0, "em_andamento": 0,
                        "muito_jogado": 0, "concluido_simbolicamente": 0}
        for jid, jogo in jogos_unicos.items():
            total_h = self.tempo_por_jogo.get(jid, 0)
            if total_h < 2:
                status_count["iniciado"] += 1
            elif total_h < 10:
                status_count["em_andamento"] += 1
            elif total_h < 20:
                status_count["muito_jogado"] += 1
            else:
                status_count["concluido_simbolicamente"] += 1

        # Favoritos
        generos_lista  = [s.jogo.genero  for s in self.historico]
        consoles_lista = [s.jogo.console for s in self.historico]
        genero_fav     = Counter(generos_lista).most_common(1)[0][0]  if generos_lista  else "N/A"
        console_fav    = Counter(consoles_lista).most_common(1)[0][0] if consoles_lista else "N/A"

        # Jogo mais jogado
        jogo_mais = max(jogos_unicos.values(),
                        key=lambda j: self.tempo_por_jogo.get(j.id, 0),
                        default=None)

        # Jogo mais popular e melhor nota no histórico
        jogo_popular = max(jogos_unicos.values(),
                           key=lambda j: j.totalSales, default=None)
        jogo_melhor_nota = max(jogos_unicos.values(),
                                key=lambda j: j.critic_score, default=None)

        sep = "="*55
        print(f"\n  {sep}")
        print(f"  {'🎮  DASHBOARD STEAMPY':^55}")
        print(f"  {sep}")
        print(f"  {'CATÁLOGO':<35} {len(self.catalogo_lista):>10} jogos")
        print(f"  {'BACKLOG':<35} {self.backlog.tamanho():>10} jogos")
        print(f"  {'RECENTES (pilha)':<35} {self.recentes.tamanho():>10} jogos")
        print(f"  {'SESSÕES JOGADAS':<35} {total_sessoes:>10}")
        print(f"  {'TEMPO TOTAL JOGADO':<35} {total_tempo:>9.1f}h")
        print(f"  {'MÉDIA POR SESSÃO':<35} {media_sessao:>9.1f}h")
        print(f"  {'-'*55}")
        print(f"  {'JOGO MAIS JOGADO':<35} {jogo_mais.titulo[:18] if jogo_mais else 'N/A':>18}")
        print(f"  {'GÊNERO FAVORITO':<35} {genero_fav:>18}")
        print(f"  {'CONSOLE FAVORITO':<35} {console_fav:>18}")
        print(f"  {'NOTA MÉDIA (histórico)':<35} {nota_media_h:>17.1f}")
        print(f"  {'-'*55}")
        print(f"  {'INICIADOS':<35} {status_count['iniciado']:>10}")
        print(f"  {'EM ANDAMENTO':<35} {status_count['em_andamento']:>10}")
        print(f"  {'MUITO JOGADOS':<35} {status_count['muito_jogado']:>10}")
        print(f"  {'CONCLUÍDOS SIMBOLICAMENTE':<35} {status_count['concluido_simbolicamente']:>10}")
        print(f"  {'-'*55}")
        print(f"  {'RECOMENDAÇÕES DISPONÍVEIS':<35} {len(self.recomendacoes):>10}")
        pop_str  = jogo_popular.titulo[:18]   if jogo_popular   else "N/A"
        nota_str = jogo_melhor_nota.titulo[:18] if jogo_melhor_nota else "N/A"
        print(f"  {'JOGO MAIS POPULAR (histórico)':<35} {pop_str:>18}")
        print(f"  {'MELHOR NOTA (histórico)':<35} {nota_str:>18}")
        print(f"  {sep}\n")

    # ----------------------------------------------------------
    # PARTE 10 - PERSISTÊNCIA (carregar tudo ao iniciar)
    # ----------------------------------------------------------
    def inicializar(self, dataset="dataset.csv"):
        self.carregar_jogos(dataset)
        self.carregar_backlog()
        self.carregar_historico()
        self.recentes.carregar(self.catalogo_dict)


# =============================================================
# MENU INTERATIVO
# =============================================================
def _escolher_jogo(plataforma, lista=None):
    """Auxiliar: busca um jogo pelo nome e retorna o objeto escolhido."""
    alvo = lista if lista else plataforma.catalogo_lista
    termo = input("  Digite parte do nome do jogo: ").strip()
    resultado = [j for j in alvo if termo.lower() in j.titulo.lower()]
    if not resultado:
        print("  Nenhum jogo encontrado.")
        return None
    # Mostra até 100 resultados para o usuário escolher
    exibir = resultado[:100]
    for i, j in enumerate(exibir, 1):
        print(f"  {i:>3}. [{j.console}] {j.titulo} | {j.genero} | Nota: {j.critic_score}")
    if len(resultado) > 100:
        print(f"  ... e mais {len(resultado) - 100} resultados. Refine a busca.")
    total_exibido = len(exibir)
    while True:
        try:
            entrada = input(f"  Escolha o número (1-{total_exibido}): ").strip()
            num = int(entrada)
            if 1 <= num <= total_exibido:
                return exibir[num - 1]
            print(f"  Número inválido. Digite entre 1 e {total_exibido}.")
        except ValueError:
            print("  Digite um número.")


def menu():
    plataforma = SteamPy()

    print("\n" + "="*55)
    print("        BEM-VINDO AO STEAMPY")
    print("="*55)

    dataset = input("  Nome do arquivo dataset (Enter = dataset.csv): ").strip()
    if not dataset:
        dataset = "dataset.csv"
    plataforma.inicializar(dataset)

    opcoes = {
        "1" : "Listar jogos",
        "2" : "Buscar jogo por nome",
        "3" : "Filtrar por gênero",
        "4" : "Filtrar por console",
        "5" : "Filtrar por nota mínima",
        "6" : "Filtrar por vendas mínimas",
        "7" : "Filtrar por publisher",
        "8" : "Ordenar catálogo",
        "9" : "Adicionar jogo ao backlog",
        "10": "Ver backlog",
        "11": "Jogar próximo do backlog",
        "12": "Ver jogos recentes",
        "13": "Retomar último jogo",
        "14": "Registrar tempo de jogo (avulso)",
        "15": "Ver histórico completo",
        "16": "Ver recomendações",
        "17": "Ver ranking pessoal",
        "18": "Ver dashboard",
        "19": "Salvar backlog",
        "0" : "Sair",
    }

    while True:
        print("\n" + "="*45)
        print("              MENU STEAMPY")
        print("="*45)
        for k, v in opcoes.items():
            print(f"  {k:>2}. {v}")
        print("="*45)

        escolha = input("  Opção: ").strip()

        # 1 - Listar
        if escolha == "1":
            limite = input("  Quantos jogos exibir? (Enter = 50): ").strip()
            lim = int(limite) if limite.isdigit() else 50
            plataforma.listar_jogos(limite=lim)

        # 2 - Buscar por nome
        elif escolha == "2":
            termo = input("  Digite parte do título: ").strip()
            plataforma.buscar_jogo_por_nome(termo)

        # 3 - Filtrar gênero
        elif escolha == "3":
            genero = input("  Gênero (ex: Action, Racing, Sports): ").strip()
            plataforma.filtrar_por_genero(genero)

        # 4 - Filtrar console
        elif escolha == "4":
            console = input("  Console (ex: PS4, X360, PC): ").strip()
            plataforma.filtrar_por_console(console)

        # 5 - Filtrar nota
        elif escolha == "5":
            try:
                nota = float(input("  Nota mínima (0-10): ").strip())
                plataforma.filtrar_por_nota(nota)
            except ValueError:
                print("  Valor inválido.")

        # 6 - Filtrar vendas
        elif escolha == "6":
            try:
                vendas = float(input("  Vendas mínimas (em milhões): ").strip())
                plataforma.filtrar_por_vendas(vendas)
            except ValueError:
                print("  Valor inválido.")

        # 7 - Filtrar publisher
        elif escolha == "7":
            pub = input("  Publisher (ex: Rockstar Games): ").strip()
            plataforma.filtrar_por_publisher(pub)

        # 8 - Ordenar
        elif escolha == "8":
            print("  1. Título  2. Nota  3. Vendas  4. Data  5. Console  6. Gênero")
            crit = input("  Critério: ").strip()
            plataforma.ordenar_jogos(crit)

        # 9 - Adicionar ao backlog
        elif escolha == "9":
            jogo = _escolher_jogo(plataforma)
            if jogo:
                plataforma.adicionar_ao_backlog(jogo)

        # 10 - Ver backlog
        elif escolha == "10":
            plataforma.mostrar_backlog()

        # 11 - Jogar próximo do backlog
        elif escolha == "11":
            plataforma.jogar_proximo()

        # 12 - Ver recentes
        elif escolha == "12":
            plataforma.mostrar_recentes()

        # 13 - Retomar último
        elif escolha == "13":
            plataforma.retomar_ultimo_jogo()

        # 14 - Registrar sessão avulsa
        elif escolha == "14":
            jogo = _escolher_jogo(plataforma)
            if jogo:
                horas = plataforma._pedir_tempo()
                plataforma.registrar_sessao(jogo, horas)

        # 15 - Histórico
        elif escolha == "15":
            plataforma.mostrar_historico()

        # 16 - Recomendações
        elif escolha == "16":
            plataforma.recomendar_jogos()

        # 17 - Ranking
        elif escolha == "17":
            plataforma.gerar_ranking_pessoal()

        # 18 - Dashboard
        elif escolha == "18":
            plataforma.exibir_dashboard()

        # 19 - Salvar backlog
        elif escolha == "19":
            plataforma.salvar_backlog()

        # 0 - Sair
        elif escolha == "0":
            plataforma.salvar_backlog()
            plataforma.salvar_historico()
            plataforma.recentes.salvar()
            print("\n  Dados salvos. Até mais!\n")
            break

        else:
            print("  Opção inválida.")


# =============================================================
# PONTO DE ENTRADA
# =============================================================
if __name__ == "__main__":
    menu()