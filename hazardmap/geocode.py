import httpx


async def resolver_cep(cep: str) -> dict:
    """
    Resolve Japanese CEP to address and coordinates.

    Args:
        cep: 7-digit CEP string (e.g. "5191424")

    Returns:
        Dict with address1, address2, address3, lat, lon, endereco_completo

    Raises:
        ValueError: If CEP not found or coordinates unavailable
    """
    # Step 1: CEP → Address via ZipCloud
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={cep}",
            timeout=10.0
        )
        resp.raise_for_status()
        data = resp.json()

    if not data.get("results"):
        raise ValueError(f"CEP {cep} not found in ZipCloud")

    r = data["results"][0]
    address1 = r.get("address1", "")
    address2 = r.get("address2", "")
    address3 = r.get("address3", "")
    endereco_str = f"{address1}{address2}{address3}"

    # Step 2: Address → Coordinates via GSI
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://msearch.gsi.go.jp/address-search/AddressSearch",
            params={"q": endereco_str},
            timeout=10.0
        )
        resp.raise_for_status()
        geo_data = resp.json()

    if not geo_data:
        raise ValueError(f"Coordinates not found for: {endereco_str}")

    lon, lat = geo_data[0]["geometry"]["coordinates"]

    return {
        "address1": address1,
        "address2": address2,
        "address3": address3,
        "lat": lat,
        "lon": lon,
        "endereco_completo": endereco_str,
    }
