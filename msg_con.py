from flask import Flask, render_template
import pandas as pd
from datetime import datetime

app = Flask(__name__)

ARQUIVO = "/home/silvapaiva/Documentos/curso/python/CON.ods"


# =========================================================
# FUNÇÃO PARA FORMATAR HORÁRIO
# =========================================================

def formatar_horario(valor):

    # Se estiver vazio ou for NaN
    if pd.isna(valor):
        return ""

    # Converte para texto
    valor = str(valor).strip().lower()

    # Se estiver vazio
    if valor == "":
        return ""

    # Remove espaços
    valor = valor.replace(" ", "")

    try:

        # Troca "h" por ":"
        valor = valor.replace("h", ":")

        # Exemplo:
        # 9h -> 9:
        # 9: -> 9:00
        if valor.endswith(":"):
            valor += "00"

        # Caso seja somente número
        # Exemplo: 9 ou 10
        if ":" not in valor:

            numero = float(valor)

            horas = int(numero)

            minutos = int(
                round((numero - horas) * 60)
            )

            return f"{horas:02d}:{minutos:02d}"

        # Divide horas e minutos
        partes = valor.split(":")

        horas = int(partes[0])

        minutos = int(partes[1])

        return f"{horas:02d}:{minutos:02d}"

    except Exception:

        # Se não conseguir interpretar,
        # mantém o valor original
        return str(valor)


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
def dashboard():

    # =====================================================
    # PLANILHA 1 - MENSAGENS
    # =====================================================

    df = pd.read_excel(
        ARQUIVO,
        sheet_name="Planilha1",
        engine="odf"
    )

    # Remover espaços extras dos nomes das colunas
    df.columns = df.columns.str.strip()

    hoje = datetime.now()

    # =====================================================
    # CONVERTER PRAZO PARA DATA
    # =====================================================

    df["Prazo"] = pd.to_datetime(
        df["Prazo"],
        dayfirst=True,
        errors="coerce"
    )

    # =====================================================
    # CALCULAR DIAS RESTANTES
    # =====================================================

    df["DIAS_RESTANTES"] = (
        df["Prazo"] - hoje
    ).dt.days

    # =====================================================
    # CARDS
    # =====================================================

    # Total
    total = len(df)

    # Vencidas
    vencidas = len(
        df[df["DIAS_RESTANTES"] < 0]
    )

    # Atenção - até 3 dias
    atencao = len(
        df[
            (df["DIAS_RESTANTES"] >= 0) &
            (df["DIAS_RESTANTES"] <= 3)
        ]
    )

    # No prazo
    prazo = len(
        df[df["DIAS_RESTANTES"] > 3]
    )

    # =====================================================
    # ORDENAR MENSAGENS PELO PRAZO
    # =====================================================

    df = df.sort_values(
        by="Prazo"
    )

    # Substituir NaN por vazio
    df = df.fillna("")

    # Converter mensagens para lista de dicionários
    mensagens = df.to_dict(
        orient="records"
    )


    # =========================================================
    # PLANILHA 2 - HORÁRIOS DE DESPACHO
    # =========================================================

    despachos = pd.read_excel(
        ARQUIVO,
        sheet_name="Planilha2",
        engine="odf"
    )

    # Remover espaços dos nomes das colunas
    despachos.columns = despachos.columns.str.strip()

    # =====================================================
    # CONVERTER DIA PARA DATA
    # =====================================================

    despachos["Dia"] = pd.to_datetime(
        despachos["Dia"],
        dayfirst=True,
        errors="coerce"
    )

    # =====================================================
    # FORMATAR HORÁRIO
    # =====================================================

    despachos["Horário do Despacho"] = (
        despachos["Horário do Despacho"]
        .apply(formatar_horario)
    )

    # =====================================================
    # TRATAR CAMPOS VAZIOS
    # =====================================================

    despachos["Setor"] = (
        despachos["Setor"]
        .fillna("")
    )

    despachos["Horário do Despacho"] = (
        despachos["Horário do Despacho"]
        .fillna("")
    )

    # =====================================================
    # ORDENAR DESPACHOS
    # =====================================================

    despachos = despachos.sort_values(
        by=["Dia", "Horário do Despacho"]
    )

    # =====================================================
    # CONVERTER PARA LISTA DE DICIONÁRIOS
    # =====================================================

    horarios_despacho = despachos.to_dict(
        orient="records"
    )


    # =====================================================
    # ENVIAR DADOS PARA O HTML
    # =====================================================

    return render_template(
        "index.html",

        total=total,
        vencidas=vencidas,
        atencao=atencao,
        prazo=prazo,

        mensagens=mensagens,

        horarios_despacho=horarios_despacho
    )


# =========================================================
# INICIAR SERVIDOR
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)

