import pytest
from django.core.exceptions import ValidationError

from fiddles.helpers import public_port
from fiddles.models import Fiddle, FiddleFile


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



@pytest.mark.unit
@pytest.mark.parametrize("x",["*",'asd/$PYTHONPATH','/asd','asd/../..'])
def test_fiddlefail(x):
    with pytest.raises(ValidationError):
        f=FiddleFile(path=x)
        f.clean()
