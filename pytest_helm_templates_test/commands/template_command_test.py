from typing import List

import pytest

from pytest_helm_templates.commands.template_command import TemplateCommand


@pytest.mark.parametrize(
    "actual_arguments,expected_arguments",
    (
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
            ),
            ["helm", "template", "name", "chart", "--dry-run=client", "--include-crds"],
        ),
        (
            TemplateCommand.helm_arguments(
                api_versions=[],
                chart="chart",
                name="name",
            ),
            ["helm", "template", "name", "chart", "--dry-run=client", "--include-crds"],
        ),
        (
            TemplateCommand.helm_arguments(
                api_versions=["v1", "apps/v1"],
                chart="chart",
                name="name",
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--api-versions",
                "v1,apps/v1",
                "--dry-run=client",
                "--include-crds",
            ],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                dry_run="server",
                name="name",
            ),
            ["helm", "template", "name", "chart", "--dry-run=server", "--include-crds"],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                include_crds=False,
                name="name",
            ),
            ["helm", "template", "name", "chart", "--dry-run=client"],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                is_upgrade=False,
                name="name",
            ),
            ["helm", "template", "name", "chart", "--dry-run=client", "--include-crds"],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                is_upgrade=True,
                name="name",
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--dry-run=client",
                "--include-crds",
                "--is-upgrade",
            ],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                kube_version="v1.29.0",
                name="name",
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--dry-run=client",
                "--include-crds",
                "--kube-version",
                "v1.29.0",
            ],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                namespace="test-namespace",
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--dry-run=client",
                "--include-crds",
                "--namespace",
                "test-namespace",
            ],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                no_hooks=False,
            ),
            ["helm", "template", "name", "chart", "--dry-run=client", "--include-crds"],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                no_hooks=True,
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--dry-run=client",
                "--include-crds",
                "--no-hooks",
            ],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                repo="test-repo",
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--dry-run=client",
                "--include-crds",
                "--repo",
                "test-repo",
            ],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                show_only=[],
            ),
            ["helm", "template", "name", "chart", "--dry-run=client", "--include-crds"],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                show_only=["templates/test1.yaml", "templates/test2.yaml"],
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--dry-run=client",
                "--include-crds",
                "--show-only",
                "templates/test1.yaml",
                "--show-only",
                "templates/test2.yaml",
            ],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                skip_tests=True,
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--dry-run=client",
                "--include-crds",
                "--skip-tests",
            ],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                values=[],
            ),
            ["helm", "template", "name", "chart", "--dry-run=client", "--include-crds"],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                values=["values1.yaml", "values2.yaml"],
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--dry-run=client",
                "--include-crds",
                "--values",
                "values1.yaml",
                "--values",
                "values2.yaml",
            ],
        ),
        (
            TemplateCommand.helm_arguments(
                chart="chart",
                name="name",
                version="1.1.1",
            ),
            [
                "helm",
                "template",
                "name",
                "chart",
                "--dry-run=client",
                "--include-crds",
                "--version",
                "1.1.1",
            ],
        ),
    ),
)
def test_helm_arguments_yields_expected_arguments(
    actual_arguments: List[str],
    expected_arguments: List[str],
) -> None:
    assert expected_arguments == actual_arguments