import pytest

from pymodaq.utils.leco.daq_move_LECODirector import DAQ_Move_LECODirector
from pymodaq.utils.leco.daq_xDviewer_LECODirector import DAQ_xDViewer_LECODirector
from pymodaq.utils.leco.rpc_method_definitions import (
    GenericDirectorMethods,
    MoveDirectorMethods,
    ViewerDirectorMethods,
)


@pytest.mark.parametrize("name", GenericDirectorMethods)
def test_ViewerDirector_has_generic_methods(name):
    assert hasattr(DAQ_xDViewer_LECODirector, name)


@pytest.mark.parametrize("name", ViewerDirectorMethods)
def test_ViewerDirector_has_necessary_methods(name):
    assert hasattr(DAQ_xDViewer_LECODirector, name)


@pytest.mark.parametrize("name", GenericDirectorMethods)
def test_MoveDirector_has_generic_methods(name):
    assert hasattr(DAQ_Move_LECODirector, name)


@pytest.mark.parametrize("name", MoveDirectorMethods)
def test_MoveDirector_has_necessary_methods(name):
    assert hasattr(DAQ_Move_LECODirector, name)
