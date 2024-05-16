from textwrap import dedent

import pytest
from src.customs import lint


@pytest.mark.parametrize(
    "out,input",
    [
        (
            "test.py:2:0: W001",
            (
                """\
                import re
                re.search("")
                """
            ),
        ),
        (
            "test.py:2:0: W001",
            (
                """\
                from re import search
                search("")
                """
            ),
        ),
        (
            "test.py:4:0: W001",
            (
                """\
                import logging
                import re
                logging.getLogger()
                re.search("")
                """
            ),
        ),
    ],
)
def test_call(input, out, tmp_path, capsys):
    """Test calls at the module level are reported."""
    temp_file = tmp_path / "test.py"
    temp_file.write_text(dedent(input))
    lint([temp_file])
    assert out in capsys.readouterr().out


@pytest.mark.parametrize(
    "out,input",
    [
        (
            "test.py:2:0: W001",
            (
                """\
                import re
                a = re.search("")
                """
            ),
        ),
        (
            "test.py:2:0: W001",
            (
                """\
                from re import search
                a = search("")
                """
            ),
        ),
        (
            "test.py:4:0: W001",
            (
                """\
                import logging
                import re
                log = logging.getLogger()
                a = re.search("")
                """
            ),
        ),
    ],
)
def test_assign(input, out, tmp_path, capsys):
    """Test calls at the module level are reported."""
    temp_file = tmp_path / "test.py"
    temp_file.write_text(dedent(input))
    lint([temp_file])
    assert out in capsys.readouterr().out


@pytest.mark.parametrize(
    "output_does_not_contain,input",
    [
        (
            "W001",
            (
                """\
                import logging
                from logging import getLogger
                logging.getLogger()
                log = logging.getLogger()
                log = getLogger()
                getLogger()
                log = getLogger()
                """
            ),
        )
    ],
)
def test_no_matches(input, output_does_not_contain, tmp_path, capsys):
    """Verify that override logic works.

    This allows calling getLogger() at the module level by default.
    It may be useful to have a user-configurable ignore list.
    """
    temp_file = tmp_path / "test.py"
    temp_file.write_text(dedent(input))
    lint([temp_file])
    assert output_does_not_contain not in capsys.readouterr().out
