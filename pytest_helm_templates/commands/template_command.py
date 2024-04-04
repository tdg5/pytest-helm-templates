from typing import List, Optional


class TemplateCommand:
    @classmethod
    def helm_arguments(
        cls,
        chart: str,
        name: str,
        api_versions: Optional[List[str]] = None,
        dry_run: Optional[str] = None,
        include_crds: Optional[bool] = None,
        is_upgrade: Optional[bool] = None,
        kube_version: Optional[str] = None,
        namespace: Optional[str] = None,
        no_hooks: Optional[bool] = None,
        repo: Optional[str] = None,
        show_only: Optional[List[str]] = None,
        skip_tests: Optional[bool] = None,
        values: Optional[List[str]] = None,
        version: Optional[str] = None,
    ) -> List[str]:
        _dry_run = dry_run or "client"
        _include_crds = include_crds if include_crds is not None else True
        _is_upgrade = is_upgrade or False
        _no_hooks = no_hooks or False
        _skip_tests = skip_tests or False
        _values = values if values is not None else []

        components = ["helm", "template", name, chart]

        if api_versions:
            comma_separated_api_versions = ",".join(api_versions)
            components.append("--api-versions")
            components.append(comma_separated_api_versions)

        components.append(f"--dry-run={_dry_run}")

        if _include_crds:
            components.append("--include-crds")

        if _is_upgrade:
            components.append("--is-upgrade")

        if kube_version:
            components.append("--kube-version")
            components.append(kube_version)

        if namespace:
            components.append("--namespace")
            components.append(namespace)

        if _no_hooks:
            components.append("--no-hooks")

        if repo:
            components.append("--repo")
            components.append(repo)

        if show_only:
            for template_path in show_only:
                components.append("--show-only")
                components.append(template_path)

        if _skip_tests:
            components.append("--skip-tests")

        if _values:
            for values_file_or_url in _values:
                components.append("--values")
                components.append(values_file_or_url)

        if version:
            components.append("--version")
            components.append(version)

        return components
