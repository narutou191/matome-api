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

    Args:
        lat: Latitude
        lon: Longitude
        tipo: Risk type ("1"-"5")
        output_path: Where to save the PDF
        zoom: Map zoom level (default 15)

    Raises:
        Exception: If browser fails or PDF generation fails
    """
    layers = TIPO_LAYERS.get(tipo, TIPO_LAYERS["1"])
    disp = TIPO_DISP.get(tipo, TIPO_DISP["1"])

    # Build URL with coordinates and layer configuration
    url = (
        f"https://disaportal.gsi.go.jp/hazardmap/maps/index.html"
        f"?ll={lat},{lon}"
        f"&z={zoom}"
        f"&base=pale"
        f"&ls={layers}"
        f"&disp={disp}"
        f"&vs=c1j0l0u0t0h0z0"
    )

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        try:
            # Create context with Japanese locale
            context = await browser.new_context(
                viewport={"width": 1280, "height": 900},
                locale="ja-JP"
            )

            page = await context.new_page()

            # Navigate to portal
            await page.goto(url, wait_until="networkidle")

            # Wait for map to fully render
            await asyncio.sleep(5)

            # Try to close any popups
            try:
                close_buttons = await page.query_selector_all(
                    "button.close, .modal-close, [aria-label='Close']"
                )
                if close_buttons:
                    await close_buttons[0].click()
                    await asyncio.sleep(1)
            except Exception:
                pass  # Popups may not exist, that's fine

            # Generate PDF
            await page.pdf(
                path=output_path,
                format="A4",
                print_background=True,
                margin={
                    "top": "10mm",
                    "bottom": "10mm",
                    "left": "10mm",
                    "right": "10mm",
                },
            )

            await context.close()

        finally:
            await browser.close()
