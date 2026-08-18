def test_vision_package_is_importable():
    from vision.schema import PropertyData
    from vision.normalizer import normalize

    prop = PropertyData(rent=1000)
    assert prop.rent == 1000
    assert callable(normalize)
