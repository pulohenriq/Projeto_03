# =============================================================
# ARQUIVO 2 - filabacklog.py
# Classe que representa a fila de backlog do usuário (FIFO)
# =============================================================

class FilaBackLog:
    def __init__(self):
        self.dados = []

    def enqueue(self, jogo):
        """Adiciona jogo no final da fila"""
        # Verifica se o jogo já está no backlog para não duplicar
        for j in self.dados:
            if j.id == jogo.id:
                print(f"  '{jogo.titulo}' já está no backlog.")
                return False
        self.dados.append(jogo)
        print(f"  '{jogo.titulo}' adicionado ao backlog.")
        return True

    def dequeue(self):
        """Remove e retorna o primeiro jogo da fila"""
        if self.is_empty():
            return None
        return self.dados.pop(0)

    def is_empty(self):
        """Verifica se a fila está vazia"""
        return len(self.dados) == 0

    def mostrar(self):
        """Exibe todos os jogos do backlog em ordem"""
        if self.is_empty():
            print("  Backlog vazio.")
            return
        print(f"\n  {'='*45}")
        print(f"  {'BACKLOG - FILA DE JOGOS':^45}")
        print(f"  {'='*45}")
        for index, jogo in enumerate(self.dados, start=1):
            print(f"  {index}. [{jogo.console}] {jogo.titulo}")
        print(f"  {'='*45}")
        print(f"  Total: {self.tamanho()} jogo(s) na fila")

    def tamanho(self):
        """Retorna o número de jogos no backlog"""
        return len(self.dados)

    def contem(self, jogo_id):
        """Verifica se um jogo está no backlog pelo ID"""
        for j in self.dados:
            if j.id == jogo_id:
                return True
        return False

    def proximo(self):
        """Retorna o próximo jogo sem remover"""
        if self.is_empty():
            return None
        return self.dados[0]

    def salvar(self, nome_arquivo="backlog.txt"):
        """Salva o backlog em arquivo"""
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                f.write("id;titulo;console\n")
                for jogo in self.dados:
                    f.write(jogo.linha_backlog() + "\n")
            print(f"  Backlog salvo em '{nome_arquivo}'.")
        except Exception as e:
            print(f"  Erro ao salvar backlog: {e}")

    def carregar(self, catalogo_dict, nome_arquivo="backlog.txt"):
        """Carrega o backlog a partir de arquivo usando o catálogo como referência"""
        try:
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                linhas = f.readlines()
            self.dados = []
            carregados = 0
            for linha in linhas[1:]:  # pula cabeçalho
                linha = linha.strip()
                if not linha:
                    continue
                partes = linha.split(";")
                if len(partes) < 1:
                    continue
                jogo_id = int(partes[0])
                if jogo_id in catalogo_dict:
                    self.dados.append(catalogo_dict[jogo_id])
                    carregados += 1
            print(f"  Backlog carregado: {carregados} jogo(s).")
        except FileNotFoundError:
            print("  Nenhum backlog salvo encontrado.")
        except Exception as e:
            print(f"  Erro ao carregar backlog: {e}")
