from typing import List

import pytest

from pytest_helm_templates.commands.show_values_command import ShowValuesCommand


@pytest.mark.parametrize(
    "actual_arguments,expected_arguments",
    (
        (
            ShowValuesCommand.helm_arguments(chart="chart"),
            ["helm", "show", "values", "chart"],
        ),
        (
            ShowValuesCommand.helm_arguments(chart="chart", repo="test-repo"),
            ["helm", "show", "values", "chart", "--repo", "test-repo"],
        ),
        (
            ShowValuesCommand.helm_arguments(chart="chart", version="1.1.1"),
            ["helm", "show", "values", "chart", "--version", "1.1.1"],
        ),
    ),
)
def test_helm_arguments_yields_expected_arguments(
    actual_arguments: List[str],
    expected_arguments: List[str],
) -> None:
    assert expected_arguments == actual_arguments
