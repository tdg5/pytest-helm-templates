[![code coverage](./.meta/coverage/badge.svg)](./.meta/coverage/report.txt)
[![license](https://img.shields.io/github/license/tdg5/pytest-helm-templates.svg)](https://github.com/tdg5/pytest-helm-templates/blob/main/LICENSE)

# pytest-helm-templates

[Pytest][docs-pytest-org-home] fixtures for unit testing [Helm][helm-sh-home]
charts via the output of [`helm template`][helm-sh-helm-template-docs].

## Prerequisites

This library assumes that `helm` is already available somewhere on the `$PATH`.
If you need to install `helm`, please see [Installing
Helm][helm-sh-installing-helm].

[docs-pytest-org-home]: https://docs.pytest.org/en/8.0.x/ "pytest: pytest documentation"
[helm-sh-helm-template-docs]: https://helm.sh/docs/helm/helm_template/ "Helm | Helm Template"
[helm-sh-home]: https://helm.sh/ "Helm"
[helm-sh-installing-helm]: https://helm.sh/docs/intro/install/ "Helm | Installing Helm"
