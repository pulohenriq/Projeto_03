# =============================================================
# ARQUIVO 1 - jogo.py
# Classe que representa um jogo do catálogo SteamPy
# =============================================================

class Jogo:
    def __init__(self, idJogo, titulo, console, genero, publisher, developer,
                 critic_score, totalSales, naSales, jpSales, palSales, otherSales, releaseDate):
        self.id           = idJogo
        self.titulo       = titulo
        self.console      = console
        self.genero       = genero
        self.publisher    = publisher
        self.developer    = developer
        self.critic_score = critic_score
        self.totalSales   = totalSales
        self.naSales      = naSales
        self.jpSales      = jpSales
        self.palSales     = palSales
        self.otherSales   = otherSales
        self.releaseDate  = releaseDate

    def exibir(self):
        print(f"  ID         : {self.id}")
        print(f"  Título     : {self.titulo}")
        print(f"  Console    : {self.console}")
        print(f"  Gênero     : {self.genero}")
        print(f"  Publisher  : {self.publisher}")
        print(f"  Developer  : {self.developer}")
        print(f"  Nota       : {self.critic_score}")
        print(f"  Vendas Tot.: {self.totalSales}M")
        print(f"  Vendas NA  : {self.naSales}M")
        print(f"  Vendas JP  : {self.jpSales}M")
        print(f"  Vendas PAL : {self.palSales}M")
        print(f"  Outras     : {self.otherSales}M")
        print(f"  Lançamento : {self.releaseDate}")
        print(f"  {'-'*40}")

    def exibir_resumido(self):
        print(f"  [{self.id}] {self.titulo} | {self.console} | {self.genero} | Nota: {self.critic_score} | Vendas: {self.totalSales}M")

    def linha_backlog(self):
        return f"{self.id};{self.titulo};{self.console}"

    def linha_recentes(self):
        return f"{self.id};{self.titulo};{self.console}"
