from typing import List, Optional


class ShowValuesCommand:
    @classmethod
    def helm_arguments(
        cls,
        chart: str,
        repo: Optional[str] = None,
        version: Optional[str] = None,
    ) -> List[str]:
        components = ["helm", "show", "values", chart]

        if repo:
            components.append("--repo")
            components.append(repo)

        if version:
            components.append("--version")
            components.append(version)

        return components
