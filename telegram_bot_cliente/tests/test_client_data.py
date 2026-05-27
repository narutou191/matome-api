import pytest
from bot.client_data import ClientData, PersonalInfo

def test_personal_info_valid():
    data = PersonalInfo(
        name_katakana="ジョアン",
        name_full="João Silva",
        birthdate="1990/5/15",
        address="Rua das Flores 123",
        cep="513-0036",
        email="joao@example.com",
        phone="09012345678",
        nationality="Brasil"
    )
    assert data.name_full == "João Silva"

def test_client_data_incomplete():
    client = ClientData()
    assert not client.is_complete()

def test_client_data_with_personal():
    client = ClientData(
        personal=PersonalInfo(
            name_katakana="ジョアン",
            name_full="João Silva",
            birthdate="1990/5/15",
            address="Rua das Flores 123",
            cep="513-0036",
            email="joao@example.com",
            phone="09012345678",
            nationality="Brasil"
        )
    )
    assert client.personal is not None
    assert not client.is_complete()
