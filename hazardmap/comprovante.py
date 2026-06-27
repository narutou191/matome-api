from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime


def gerar_comprovante(dados: dict, output_path: str) -> None:
    """
    Generate legal proof-of-consultation PDF (comprovante).

    Args:
        dados: Dict with keys: cep, prefeitura, municipio, bairro, tipo, corretor, url_fonte
        output_path: Where to save the PDF
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()
    story = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Title
    titulo = Paragraph(
        "<b>COMPROVANTE DE CONSULTA — ハザードマップ 確認記録</b>",
        styles["Title"],
    )
    story.append(titulo)
    story.append(Spacer(1, 8*mm))

    # Legal subtitle
    legal = Paragraph(
        "Documento gerado para fins de conformidade com a "
        "宅地建物取引業法 第35条 (Lei de Transações Imobiliárias, Art. 35)",
        styles["Normal"],
    )
    story.append(legal)
    story.append(Spacer(1, 8*mm))

    # Data table
    table_data = [
        ["Item", "Informação"],
        ["CEP (〒)", dados.get("cep", "—")],
        ["Prefeitura", dados.get("prefeitura", "—")],
        ["Município", dados.get("municipio", "—")],
        ["Bairro", dados.get("bairro", "—")],
        ["Tipo de Risco", dados.get("tipo", "—")],
        ["Corretor", dados.get("corretor", "—")],
        ["Fonte Oficial", dados.get("url_fonte", "—")],
        ["Data da Consulta", agora],
        ["Base Legal", "宅地建物取引業法 第35条"],
    ]

    tabela = Table(table_data, colWidths=[55*mm, 115*mm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f5f5f5")),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(tabela)
    story.append(Spacer(1, 20*mm))

    # Signature section
    assin_data = [
        ["Assinatura do Corretor", "Assinatura do Comprador"],
        [" \n\n\n_________________________", " \n\n\n_________________________"],
    ]
    assin_table = Table(assin_data, colWidths=[85*mm, 85*mm])
    assin_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(assin_table)
    doc.build(story)
