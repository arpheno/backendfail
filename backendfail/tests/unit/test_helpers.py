import pytest

from fiddles.helpers import public_port


@pytest.mark.unit
def test_public_port():
    container = {"Ports": [{"PublicPort": 8000}, {"PublicPort": 9000}]}
    assert public_port(container) is 8000
