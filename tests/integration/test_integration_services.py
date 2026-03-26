import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="Requires Docker services")
def test_integration_placeholder():
    assert True
