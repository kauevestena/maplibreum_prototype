# Releasing Maplibreum

Maplibreum publishes with PyPI Trusted Publishing. The workflow uses short-lived OpenID Connect credentials and does not require a stored PyPI API token.

## One-time repository setup

Configure pending trusted publishers before the first upload:

| Index | Project | Owner | Repository | Workflow | Environment |
|---|---|---|---|---|---|
| PyPI | `maplibreum` | `kauevestena` | `maplibreum_prototype` | `publish-to-pypi.yml` | `pypi` |
| TestPyPI | `maplibreum` | `kauevestena` | `maplibreum_prototype` | `publish-to-pypi.yml` | `testpypi` |

- Register the PyPI publisher at <https://pypi.org/manage/account/publishing/>.
- Register the TestPyPI publisher at <https://test.pypi.org/manage/account/publishing/>.
- Create matching `pypi` and `testpypi` GitHub environments.
- Require manual approval on the production `pypi` environment.
- Do not add long-lived PyPI tokens to repository secrets.

## Release checklist

1. Update `maplibreum/_version.py` and replace the `Unreleased` changelog entries with a dated version section.
2. Confirm CI is green on the exact `main` commit to release.
3. Run the `Publish Python distribution` workflow manually. Manual runs publish only to TestPyPI.
4. Install from TestPyPI and perform an import/render smoke test. Runtime dependencies may be resolved from PyPI:

   ```bash
   python -m venv /tmp/maplibreum-test-release
   /tmp/maplibreum-test-release/bin/python -m pip install \
     --index-url https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     maplibreum==VERSION
   /tmp/maplibreum-test-release/bin/python -c \
     "from maplibreum import Map, __version__; print(__version__); print(len(Map().render()))"
   ```

5. Create a GitHub release targeting the verified `main` commit with tag `vVERSION`. Publishing the GitHub release triggers the production PyPI job.
6. Approve the protected `pypi` environment deployment after checking the tag and artifacts.
7. Verify the release from a clean environment with `python -m pip install maplibreum==VERSION`.
8. Confirm the PyPI project links, rendered README, source archive, wheel, and digital attestations.

PyPI distributions are immutable. If an upload is wrong, increment the version; do not attempt to replace an existing file.
