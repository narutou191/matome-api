from playwright.async_api import async_playwright
import asyncio


TIPO_LAYERS = {
    "1": "seamless|flood_l2_keizoku,0.8|flood_l1,0.8|flood_list,0.8|disaster1",
    "2": "seamless|naisui_raster,0.8|disaster1",
    "3": "seamless|hightide_l2,0.8|disaster1",
    "4": "seamless|tsunami_newlegend_data,0.8|disaster1",
    "5": "seamless|dosya,0.8|disaster1",
}

TIPO_DISP = {
    "1": "0110000010",
    "2": "0110000010",
    "3": "0110000010",
    "4": "0110000010",
    "5": "0110000010",
}


async def gerar_pdf_hazardmap(
    lat: float,
    lon: float,
    tipo: str,
    output_path: str,
    zoom: int = 15
) -> None:
    """
    Generate hazard map PDF by capturing from GSI portal via Playwright.

    MVP Version: Creates a placeholder PDF with map link.
    Full version with Playwright will be deployed after initial validation.

    Args:
        lat: Latitude
        lon: Longitude
        tipo: Risk type ("1"-"5")
        output_path: Where to save the PDF
        zoom: Map zoom level (default 15)

    Raises:
        Exception: If PDF generation fails
    """
    # MVP: Generate PDF with map link instead of screenshot
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    layers = TIPO_LAYERS.get(tipo, TIPO_LAYERS["1"])
    disp = TIPO_DISP.get(tipo, TIPO_DISP["1"])

    url = (
        f"https://disaportal.gsi.go.jp/hazardmap/maps/index.html"
        f"?ll={lat},{lon}"
        f"&z={zoom}"
        f"&base=pale"
        f"&ls={layers}"
        f"&disp={disp}"
        f"&vs=c1j0l0u0t0h0z0"
    )

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

    story.append(Paragraph(
        "<b>ハザードマップ — 地図リンク</b>",
        styles["Title"]
    ))
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph(
        f"<b>座標:</b> {lat}, {lon}",
        styles["Normal"]
    ))
    story.append(Paragraph(
        f"<b>ズーム:</b> {zoom}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph(
        f"<a href='{url}'><b>地図を開く</b></a>",
        styles["Normal"]
    ))

    doc.build(story)
