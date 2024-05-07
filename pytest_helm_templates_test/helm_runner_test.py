from os import path
from tempfile import TemporaryDirectory
from typing import Optional

import pytest
import yaml

from pytest_helm_templates.helm_runner import HelmRunner
from pytest_helm_templates_test.test_helpers import fixture_path


def test_computed_values_raises_error_if_local_chart_not_found() -> None:
    with pytest.raises(ValueError) as ex:
        HelmRunner().computed_values(chart="/almost/certainly/not/a/real/path")

    expected_error = "Computed values can only be rendered for local charts."
    assert expected_error in str(ex)


@pytest.mark.parametrize(
    "use_relative_chart_path",
    (False, True),
)
def test_computed_values_returns_expected_values(use_relative_chart_path: bool) -> None:
    test_chart_absolute_path = fixture_path("charts/test-chart")
    test_chart_path = test_chart_absolute_path
    charts_path: Optional[str] = None
    if use_relative_chart_path:
        charts_path = fixture_path("charts")
        test_chart_path = path.relpath(test_chart_path, charts_path)

    helm_runner = HelmRunner(cwd=charts_path)
    values = helm_runner.computed_values(chart=test_chart_path)
    with open(
        f"{test_chart_absolute_path}/values.yaml",
        encoding="utf-8",
        mode="r",
    ) as file:
        expected_values = yaml.safe_load(file)
    assert values == expected_values


def test_computed_values_can_handle_values_given_as_a_dict() -> None:
    test_chart_path = fixture_path("charts/test-chart")

    helm_runner = HelmRunner()
    values = helm_runner.computed_values(
        chart=test_chart_path,
        values=[{"serviceAccount": {"create": False}}],
    )
    with open(
        f"{test_chart_path}/values.yaml",
        encoding="utf-8",
        mode="r",
    ) as file:
        expected_values = yaml.safe_load(file)

    # Make expected values match our overridden value
    expected_values["serviceAccount"]["create"] = False
    assert values == expected_values


def test_computed_values_includes_dependency_values() -> None:
    test_chart_path = fixture_path("charts/test-chart")

    helm_runner = HelmRunner()
    values = helm_runner.computed_values(
        chart=test_chart_path,
        values=[{"dependency": {"enabled": True}}],
    )
    with open(
        f"{test_chart_path}/values.yaml",
        encoding="utf-8",
        mode="r",
    ) as file:
        expected_values = yaml.safe_load(file)

    # Make expected values include expected dependency values
    expected_values["dependency"] = {
        "config": True,
        "enabled": True,
        "global": {},
    }
    assert values == expected_values


@pytest.mark.parametrize(
    "use_relative_chart_path",
    (False, True),
)
def test_dependency_build_runs_without_exception(use_relative_chart_path: bool) -> None:
    test_chart_absolute_path = fixture_path("charts/test-chart")
    test_chart_path = test_chart_absolute_path
    charts_path: Optional[str] = None
    if use_relative_chart_path:
        charts_path = fixture_path("charts")
        test_chart_path = path.relpath(test_chart_path, charts_path)

    helm_runner = HelmRunner(cwd=charts_path)
    helm_runner.dependency_build(chart=test_chart_path)


@pytest.mark.parametrize(
    "use_relative_chart_path",
    (False, True),
)
def test_dependency_update_runs_without_exception(
    use_relative_chart_path: bool,
) -> None:
    test_chart_absolute_path = fixture_path("charts/test-chart")
    test_chart_path = test_chart_absolute_path
    charts_path: Optional[str] = None
    if use_relative_chart_path:
        charts_path = fixture_path("charts")
        test_chart_path = path.relpath(test_chart_path, charts_path)

    helm_runner = HelmRunner(cwd=charts_path)
    helm_runner.dependency_update(chart=test_chart_path)


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
    expected_notes_excerpt = "Visit http://127.0.0.1:8080 to use your application"
    assert expected_notes_excerpt in notes


def test_notes_can_handle_values_given_a_dict() -> None:
    test_chart_path = fixture_path("charts/test-chart")

    helm_runner = HelmRunner()
    notes = helm_runner.notes(
        chart=test_chart_path,
        name="test-chart",
        values=[{"service": {"type": "LoadBalancer"}}],
    )
    expected_notes_excerpt = "It may take a few minutes for the LoadBalancer IP"
    assert expected_notes_excerpt in notes


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


def test_template_returns_expected_helm_template_output_for_remote_chart() -> None:
    helm_runner = HelmRunner()
    manifests = helm_runner.template(
        chart="hello-world",
        name="test-chart",
        repo="https://helm.github.io/examples",
        version="0.1.0",
    )

    manifest_names = {manifest["metadata"]["name"] for manifest in manifests}
    expected_manifest_names = {"test-chart-hello-world"}
    assert expected_manifest_names == manifest_names

    manifest_kinds = {manifest["kind"] for manifest in manifests}
    expected_manifest_kinds = {"Deployment", "Service", "ServiceAccount"}
    assert expected_manifest_kinds == manifest_kinds


def test_template_can_handle_values_given_a_dict() -> None:
    test_chart_path = fixture_path("charts/test-chart")

    helm_runner = HelmRunner()
    manifests = helm_runner.template(
        chart=test_chart_path,
        name="test-chart",
        values=[{"serviceAccount": {"create": False}}],
    )

    manifest_names = {manifest["metadata"]["name"] for manifest in manifests}
    assert "test-chart-service-account" not in manifest_names


@pytest.mark.parametrize(
    "use_relative_chart_path",
    (False, True),
)
def test_values_returns_expected_values(use_relative_chart_path: bool) -> None:
    test_chart_absolute_path = fixture_path("charts/test-chart")
    test_chart_path = test_chart_absolute_path
    charts_path: Optional[str] = None
    if use_relative_chart_path:
        charts_path = fixture_path("charts")
        test_chart_path = path.relpath(test_chart_path, charts_path)

    helm_runner = HelmRunner(cwd=charts_path)
    values = helm_runner.values(chart=test_chart_path)
    with open(
        f"{test_chart_absolute_path}/values.yaml",
        encoding="utf-8",
        mode="r",
    ) as file:
        expected_values = yaml.safe_load(file)
    assert values == expected_values


def test_values_returns_expected_values_for_remote_chart() -> None:
    helm_runner = HelmRunner()
    values = helm_runner.values(
        chart="hello-world",
        repo="https://helm.github.io/examples",
        version="0.1.0",
    )
    assert "image" in values
    assert "replicaCount" in values
