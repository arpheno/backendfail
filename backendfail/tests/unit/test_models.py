import pytest

from fiddles.helpers import public_port
from fiddles.models import Fiddle


@pytest.mark.unit
def test_fiddle_template():
    with pytest.raises(NotImplementedError):
        Fiddle().internal_port
    with pytest.raises(NotImplementedError):
        Fiddle().docker_image
    with pytest.raises(NotImplementedError):
        Fiddle().startup_command
    with pytest.raises(NotImplementedError):
        Fiddle().entrypoint
    with pytest.raises(NotImplementedError):
        Fiddle().prefix





