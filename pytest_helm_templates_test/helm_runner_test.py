from os import path
from tempfile import TemporaryDirectory
from typing import Optional

import pytest

from pytest_helm_templates.helm_runner import HelmRunner
from pytest_helm_templates_test.test_helpers import fixture_path


def test_notes_raises_error_if_local_chart_not_found() -> None:
    with pytest.raises(ValueError) as ex:
        HelmRunner().notes(chart="/almost/certainly/not/a/real/path", name="test-chart")

    expected_error = "Notes can only be rendered for local charts."
    assert expected_error in str(ex)


def test_notes_raises_error_if_notes_txt_not_found() -> None:
    with TemporaryDirectory() as temporary_directory_path:
        with pytest.raises(ValueError) as ex:
            HelmRunner().notes(chart=temporary_directory_path, name="test-chart")

    expected_error = (
        "Unable to find notes template at"
        f" `{temporary_directory_path}/templates/NOTES.txt`"
    )
    assert expected_error in str(ex)


@pytest.mark.parametrize(
    "use_relative_chart_path",
    (False, True),
)
def test_notes_returns_expected_notes(use_relative_chart_path: bool) -> None:
    test_chart_path = fixture_path("charts/test-chart")
    charts_path: Optional[str] = None
    if use_relative_chart_path:
        charts_path = fixture_path("charts")
        test_chart_path = path.relpath(test_chart_path, charts_path)

    helm_runner = HelmRunner(cwd=charts_path)
    notes = helm_runner.notes(chart=test_chart_path, name="test-chart")
    expected_notes = "1. Get the application URL by running these commands:"
    assert notes.startswith(expected_notes)


@pytest.mark.parametrize(
    "use_relative_chart_path",
    (False, True),
)
def test_template_returns_expected_helm_template_output(
    use_relative_chart_path: bool,
) -> None:
    test_chart_path = fixture_path("charts/test-chart")
    charts_path: Optional[str] = None
    if use_relative_chart_path:
        charts_path = fixture_path("charts")
        test_chart_path = path.relpath(test_chart_path, charts_path)

    helm_runner = HelmRunner(cwd=charts_path)
    manifests = helm_runner.template(chart=test_chart_path, name="test-chart")

    manifest_names = {manifest["metadata"]["name"] for manifest in manifests}
    expected_manifest_names = {
        "test-chart-deployment",
        "test-chart-service",
        "test-chart-service-account",
        "test-chart-test-connection",
    }
    assert expected_manifest_names == manifest_names
