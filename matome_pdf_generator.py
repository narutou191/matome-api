"""
Gerador de PDF para Simulador MATOME
Usa reportlab para criar PDFs de alta qualidade
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors as rl_colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime
import io

# Cores
COR_OURO = rl_colors.HexColor('#c9a84c')
COR_ESCURO = rl_colors.HexColor('#2d2d2d')
COR_FUNDO = rl_colors.HexColor('#f5f3ef')
COR_ANTES_BG = rl_colors.HexColor('#fff5f5')
COR_ANTES_BORDER = rl_colors.HexColor('#f0c0c0')
COR_ANTES_TEXT = rl_colors.HexColor('#cc0000')
COR_DEPOIS_BG = rl_colors.HexColor('#f5fff8')
COR_DEPOIS_BORDER = rl_colors.HexColor('#a0d8b0')
COR_DEPOIS_TEXT = rl_colors.HexColor('#006600')

def format_yen(value):
    """Formata número como ¥ com separadores"""
    if isinstance(value, str):
        value = int(value.replace('¥', '').replace('.', '').strip())
    value = int(value)
    if value == 0:
        return '¥ 0'
    return '¥ ' + f'{value:,}'.replace(',', '.')

def gerar_pdf_matome(dados):
    """Gera PDF MATOME a partir dos dados da simulação"""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=15*mm, bottomMargin=15*mm,
        leftMargin=15*mm, rightMargin=15*mm
    )

    story = []

    # ===== HEADER =====
    title_style = ParagraphStyle(
        'Title',
        fontName='Helvetica-Bold',
        fontSize=32,
        textColor=COR_OURO,
        spaceAfter=3
    )
    story.append(Paragraph('<b>MATOME</b>', title_style))

    subtitle_style = ParagraphStyle(
        'Subtitle',
        fontName='Helvetica',
        fontSize=10,
        textColor=rl_colors.grey,
        spaceAfter=8
    )
    story.append(Paragraph('まとめ · SOLUCIONANDO SUA DÍVIDA NO JAPÃO 🇯🇵', subtitle_style))

    # Info cliente
    info_style = ParagraphStyle(
        'Info',
        fontName='Helvetica',
        fontSize=10,
        textColor=COR_ESCURO,
        spaceAfter=10
    )
    idade = dados.get('idade', '')
    data = dados.get('data', datetime.now().strftime('%d/%m/%Y'))
    info_text = f"{idade} anos · Simulação: {data}" if idade else f"Simulação: {data}"
    story.append(Paragraph(info_text, info_style))

    # Linha divisória
    line_table = Table([['']],colWidths=[170*mm])
    line_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (0, 0), 2),
        ('BOTTOMPADDING', (0, 0), (0, 0), 2),
        ('LINEABOVE', (0, 0), (0, 0), 4, COR_OURO),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 8*mm))

    # ===== RESULTADO =====
    result_title = ParagraphStyle(
        'ResultTitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=COR_OURO,
        spaceAfter=10,
        letterSpacing=1
    )
    idade_display = f", {dados.get('idade', '')} ANOS" if dados.get('idade') else ""
    story.append(Paragraph(f'③ RESULTADO{idade_display}', result_title))

    # Cards antes/depois
    story.append(_criar_cards(dados))
    story.append(Spacer(1, 10*mm))

    # Card economia
    story.append(_criar_economia(dados))
    story.append(Spacer(1, 10*mm))

    # Resumo
    story.append(_criar_resumo(dados))

    # Build
    doc.build(story)
    return buffer.getvalue()

def _criar_cards(dados):
    """Cards antes e depois"""

    # Totais
    items_antes = [
        ('住宅ローン', dados.get('fin', 0)),
        ('車ローン', dados.get('car', 0)),
        ('クレジット', dados.get('crt', 0)),
        ('電気代', dados.get('luz', 0)),
        ('ガス代', dados.get('gas', 0)),
        ('その他', dados.get('out', 0) + dados.get('out2', 0)),
    ]
    total_antes = sum(v for _, v in items_antes if v > 0)

    antes_lines = ['❌ SITUAÇÃO ATUAL · 現状', '']
    for label, value in items_antes:
        if value > 0:
            antes_lines.append(f'{label}: {format_yen(value)}')
    antes_lines.extend(['', f'TOTAL: {format_yen(total_antes)}'])
    antes_text = '<br/>'.join(antes_lines)

    pmt_a = int(dados.get('pmt_a', 0))
    pmt_b = int(dados.get('pmt_b', 0))
    depois_lines = [
        '✅ COM MATOME · まとめ後',
        '',
        f'Parte A · 住宅+Obras<br/>{dados.get("anos_a", 35)} anos · {dados.get("taxa_a", 2.84):.2f}%<br/>{format_yen(pmt_a)}',
        '',
        f'Parte B · まとめ<br/>{dados.get("anos_b", 10)} anos · {dados.get("taxa_b", 3.29):.2f}%<br/>{format_yen(pmt_b)}',
        '',
        f'TOTAL: {format_yen(pmt_a + pmt_b)}'
    ]
    depois_text = '<br/>'.join(depois_lines)

    card_table = Table([
        [
            Paragraph(antes_text, ParagraphStyle('Antes', fontName='Helvetica', fontSize=9, textColor=COR_ANTES_TEXT)),
            Paragraph(depois_text, ParagraphStyle('Depois', fontName='Helvetica', fontSize=9, textColor=COR_DEPOIS_TEXT))
        ]
    ], colWidths=[80*mm, 80*mm])

    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), COR_ANTES_BG),
        ('BACKGROUND', (1, 0), (1, 0), COR_DEPOIS_BG),
        ('BORDER', (0, 0), (0, 0), 1, COR_ANTES_BORDER),
        ('BORDER', (1, 0), (1, 0), 1, COR_DEPOIS_BORDER),
        ('PADDING', (0, 0), (1, 0), 10),
        ('VALIGN', (0, 0), (1, 0), 'TOP'),
    ]))

    return card_table

def _criar_economia(dados):
    """Card economia"""
    eco = int(dados.get('eco_mensal', 0))

    eco_text = f'<font size=14 color="#c9a84c"><b>ECONOMIA MENSAL · 月の節約額</b></font><br/><br/>'
    eco_text += f'<font size=16 color="#c9a84c"><b>{format_yen(eco)} / mês</b></font><br/><br/>'
    eco_text += f'{format_yen(eco*12)} por ano<br/>{format_yen(eco*120)} em 10 anos'

    eco_table = Table([[Paragraph(eco_text, ParagraphStyle('Eco', fontName='Helvetica', fontSize=11))]], colWidths=[170*mm])
    eco_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), COR_ESCURO),
        ('PADDING', (0, 0), (0, 0), 15),
        ('ALIGNMENT', (0, 0), (0, 0), 'CENTER'),
    ]))

    return eco_table

def _criar_resumo(dados):
    """Resumo final"""
    pmt_a = int(dados.get('pmt_a', 0))
    pmt_b = int(dados.get('pmt_b', 0))
    data = dados.get('data', datetime.now().strftime('%d/%m/%Y'))

    resumo = f'<b>Proposta MATOME · {data}</b><br/><br/>'
    resumo += f'<font color="#c9a84c">Parte A (Casa+Obras):</font> {format_yen(dados.get("total_a", 0))} · {dados.get("anos_a", 35)} anos · {dados.get("taxa_a", 2.84):.2f}% → <b>{format_yen(pmt_a)}/mês</b><br/>'
    resumo += f'<font color="#7ab4d4">Parte B (Dívidas):</font> {format_yen(dados.get("total_b", 0))} · {dados.get("anos_b", 10)} anos · {dados.get("taxa_b", 3.29):.2f}% → <b>{format_yen(pmt_b)}/mês</b>'

    resumo_table = Table([[Paragraph(resumo, ParagraphStyle('Resumo', fontName='Helvetica', fontSize=9))]], colWidths=[170*mm])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), COR_FUNDO),
        ('BORDER', (0, 0), (0, 0), 1, rl_colors.grey),
        ('PADDING', (0, 0), (0, 0), 10),
    ]))

    return resumo_table

if __name__ == '__main__':
    dados_teste = {
        'nome': 'Yamamoto Hiroshi',
        'idade': '41',
        'data': '23/05/2026',
        'fin': 90000,
        'car': 30000,
        'crt': 0,
        'luz': 20000,
        'gas': 15000,
        'out': 15000,
        'out2': 0,
        'pmt_a': 65206,
        'pmt_b': 11938,
        'eco_mensal': 77856,
        'anos_a': 35,
        'taxa_a': 1.74,
        'anos_b': 35,
        'taxa_b': 2.19,
        'total_a': 20500000,
        'total_b': 3500000
    }

    pdf = gerar_pdf_matome(dados_teste)
    with open('C:\\Users\\hiros\\Downloads\\test_matome_novo.pdf', 'wb') as f:
        f.write(pdf)
    print('[OK] PDF gerado: C:\\Users\\hiros\\Downloads\\test_matome_novo.pdf')
