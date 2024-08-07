import subprocess
import textwrap
from os import path
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import IO, Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

import yaml

from pytest_helm_templates.commands import ShowValuesCommand, TemplateCommand
from pytest_helm_templates.types import DependencyListItem


class HelmRunner:
    def __init__(
        self,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        self.cwd = cwd
        self.env = env

    def values(
        self,
        chart: str,
        repo: Optional[str] = None,
        version: Optional[str] = None,
    ) -> Dict:
        """
        Collect the values of the given chart.
        """
        helm_arguments = ShowValuesCommand.helm_arguments(
            chart=chart,
            repo=repo,
            version=version,
        )

        values_output = self._run(helm_arguments=helm_arguments)
        values = yaml.safe_load(values_output)
        if not isinstance(values, Dict):
            raise ValueError(
                "Unexpected values. Expected dict, got" f" {type(values)}: {values}"
            )
        return values

    def adhoc_template(
        self,
        chart: str,
        content: str,
        name: str,
        api_versions: Optional[List[str]] = None,
        dry_run: Optional[str] = None,
        include_crds: Optional[bool] = None,
        is_upgrade: Optional[bool] = None,
        kube_version: Optional[str] = None,
        namespace: Optional[str] = None,
        repo: Optional[str] = None,
        skip_tests: Optional[bool] = None,
        values: Optional[List[Union[Dict[str, Any], str]]] = None,
        version: Optional[str] = None,
    ) -> Dict:
        """
        Like template, but renders a single adhoc template populated with the
        given content.
        """
        chart_path = Path(chart) if not self.cwd else Path(self.cwd).joinpath(chart)
        if not path.exists(chart_path):
            raise ValueError(
                "Adhoc templates can only be rendered for local charts. Could"
                f" not find local chart `{chart}` ({str(chart_path)})"
            )

        templates_dir_path = chart_path.joinpath("templates")

        with NamedTemporaryFile(
            dir=templates_dir_path,
            encoding="utf-8",
            mode="w",
        ) as temp_file:
            temp_file_name = path.basename(temp_file.name)
            temp_file.write(content)
            temp_file.flush()
            manifests = self.template(
                api_versions=api_versions,
                chart=chart,
                dry_run=dry_run,
                include_crds=include_crds,
                is_upgrade=is_upgrade,
                kube_version=kube_version,
                name=name,
                namespace=namespace,
                repo=repo,
                show_only=[f"templates/{temp_file_name}"],
                skip_tests=skip_tests,
                values=values,
                version=version,
            )
            return manifests[0]

    def computed_values(
        self,
        chart: str,
        values: Optional[List[Union[Dict[str, Any], str]]] = None,
    ) -> Dict:
        """
        Collect the whole tree of values from the given chart and its
        dependencies. This function is a bit hacky in that it depends on having
        a local chart to inject an adhoc template into. There are ways to work
        around that, but an adhoc template seems simpler and less error prone.
        """
        chart_path = Path(chart) if not self.cwd else Path(self.cwd).joinpath(chart)
        if not path.exists(chart_path):
            # We could instead take COMPUTED VALUES from `helm install [name]
            # [chart] --dry-run --debug -f <your_values_file>`, but for now
            # I've taken the easy way out.
            # https://github.com/helm/helm/issues/6772
            raise ValueError(
                "Computed values can only be rendered for local charts. Could"
                f" not find local chart `{chart}` ({str(chart_path)})"
            )

        values_output = self.adhoc_template(
            chart=chart,
            content="{{ toYaml .Values }}",
            name=str(uuid4()),
            values=values,
        )
        if not isinstance(values_output, Dict):
            raise ValueError(
                "Unexpected computed values. Expected dict, got"
                f" {type(values_output)}: {values_output}"
            )
        return values_output

    def dependency_build(self, chart: str) -> None:
        self._run(["helm", "dependency", "build", chart])

    def dependency_list(self, chart: str) -> List[DependencyListItem]:
        dependency_list_output = self._run(["helm", "dependency", "list", chart])
        rows = [row for row in dependency_list_output.split("\n") if row][1:]
        rows_fields = [row.split("\t") for row in rows]
        records = [
            [field.strip() for field in row_fields] for row_fields in rows_fields
        ]
        return [
            DependencyListItem(
                name=record[0],
                repository=record[2],
                status=record[3],
                version=record[1],
            )
            for record in records
        ]

    def dependency_update(self, chart: str) -> None:
        self._run(["helm", "dependency", "update", chart])

    def dependency_update_if_missing(self, chart: str) -> None:
        """
        Like dependency_update, but only triggers dependency_update if any of
        the dependencies are not ok.
        """
        dependency_list = self.dependency_list(chart=chart)
        if not dependency_list or all(item.is_ok for item in dependency_list):
            return
        self.dependency_update(chart=chart)

    def notes(
        self,
        chart: str,
        name: str,
        api_versions: Optional[List[str]] = None,
        dry_run: Optional[str] = None,
        is_upgrade: Optional[bool] = None,
        kube_version: Optional[str] = None,
        namespace: Optional[str] = None,
        repo: Optional[str] = None,
        values: Optional[List[Union[Dict[str, Any], str]]] = None,
        version: Optional[str] = None,
    ) -> str:
        """
        This function is a bit hacky in that it requires creating a copy of
        NOTES.txt that's embedded in a YAML template, as such, it depends on a
        local chart. `helm template` doesn't currently return NOTES.txt, and
        otherwise NOTES.txt is only rendered during `helm install`.

        Related helm issue: https://github.com/helm/helm/issues/6901
        """
        chart_path = Path(chart) if not self.cwd else Path(self.cwd).joinpath(chart)
        if not path.exists(chart_path):
            raise ValueError(
                "Notes can only be rendered for local charts. Could not find local"
                f" chart `{chart}` ({str(chart_path)})"
            )

        templates_dir_path = chart_path.joinpath("templates")
        notes_path = templates_dir_path.joinpath("NOTES.txt")
        if not path.exists(notes_path):
            raise ValueError(f"Unable to find notes template at `{notes_path}`")

        with open(notes_path, encoding="utf-8", mode="r") as notes_file:
            notes_template = notes_file.read()
        indented_notes_template = textwrap.indent(notes_template, "  ")

        notes_result = self.adhoc_template(
            api_versions=api_versions,
            chart=chart,
            content=f"---\nNOTES.txt: |\n{indented_notes_template}",
            dry_run=dry_run,
            include_crds=False,
            is_upgrade=is_upgrade,
            kube_version=kube_version,
            name=name,
            namespace=namespace,
            repo=repo,
            skip_tests=True,
            values=values,
            version=version,
        )
        notes_output = notes_result["NOTES.txt"]
        if not isinstance(notes_output, str):
            raise ValueError(
                "Unexpected notes template output. Expected string, got"
                " {type(notes_output)}: {notes_output}"
            )
        return notes_output

    def template(
        self,
        chart: str,
        name: str,
        api_versions: Optional[List[str]] = None,
        dry_run: Optional[str] = None,
        include_crds: Optional[bool] = None,
        is_upgrade: Optional[bool] = None,
        kube_version: Optional[str] = None,
        namespace: Optional[str] = None,
        repo: Optional[str] = None,
        show_only: Optional[List[str]] = None,
        skip_tests: Optional[bool] = None,
        values: Optional[List[Union[Dict[str, Any], str]]] = None,
        version: Optional[str] = None,
    ) -> List[Dict]:
        chart_path = Path(chart) if not self.cwd else Path(self.cwd).joinpath(chart)

        _values = []
        temp_files: List[IO] = []
        try:
            if values:
                for values_instance in values:
                    if isinstance(values_instance, str):
                        _values.append(values_instance)
                    else:
                        temp_file_path, temp_file = self._reify_values(values_instance)
                        _values.append(temp_file_path)
                        temp_files.append(temp_file)
            helm_arguments = TemplateCommand.helm_arguments(
                api_versions=api_versions,
                chart=str(chart_path),
                dry_run=dry_run,
                include_crds=include_crds,
                is_upgrade=is_upgrade,
                kube_version=kube_version,
                namespace=namespace,
                name=name,
                repo=repo,
                show_only=show_only,
                skip_tests=skip_tests,
                values=_values,
                version=version,
            )
            templates_yaml = self._run(helm_arguments)
        finally:
            for temp_file in temp_files:
                temp_file.close()

        return list(yaml.safe_load_all(templates_yaml))

    def _reify_values(self, values: Dict) -> Tuple[str, IO]:
        temp_file = NamedTemporaryFile(delete=False, mode="w")
        temp_file.write(yaml.safe_dump(values))
        temp_file.flush()
        return temp_file.name, temp_file

    def _run(self, helm_arguments: List[str]) -> str:
        completed_process = subprocess.run(
            helm_arguments,
            capture_output=True,
            cwd=self.cwd,
            env=self.env,
        )

        return_code = completed_process.returncode
        if return_code > 0:
            stderr = completed_process.stderr.decode("utf-8")
            raise RuntimeError(
                f"helm command failed with return code {return_code}:"
                f"exec {helm_arguments}\n{stderr}"
            )

        return completed_process.stdout.decode("utf-8")
