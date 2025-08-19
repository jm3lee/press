import pytest
from pie import process_yaml


def test_main_deprecates_and_exits():
    with pytest.raises(SystemExit) as excinfo:
        process_yaml.main()
    assert (
        "process-yaml is deprecated; YAML metadata is processed automatically."
        in str(excinfo.value)
    )


def test_module_executes_as_script():
    import runpy, sys
    sys.modules.pop("pie.process_yaml", None)
    with pytest.raises(SystemExit):
        runpy.run_module("pie.process_yaml", run_name="__main__")
