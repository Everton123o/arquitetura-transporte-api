class ErroNormalizacao(Exception):
    def __init__(
        self,
        indice: int,
        empresa_identificada: str | None,
        campo: str | None,
        mensagem: str,
    ):
        self.indice = indice
        self.empresa_identificada = empresa_identificada
        self.campo = campo
        self.mensagem = mensagem

        super().__init__(mensagem)