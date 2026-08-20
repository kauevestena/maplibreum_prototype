"""Generate every non-redundant MapLibre map deployed by OpenSidewalkMap."""

from __future__ import annotations

import argparse
from pathlib import Path

from .acquisition import build_map as build_acquisition
from .common import save_map
from .completeness import build_map as build_completeness
from .hazard_analysis import build_map as build_hazard
from .main_webmap import build_map as build_main
from .routing import build_map as build_routing


def generate_all(output_dir: str | Path, source_root: str | Path | None = None) -> list[Path]:
    """Build all five examples, optionally reading data from an OSWM checkout."""

    destination = Path(output_dir).expanduser().resolve()
    root = Path(source_root).expanduser().resolve() if source_root else None

    main_source = root / "webmap_params.json" if root else None
    profiles_source = root / "data/hazard_analysis/profiles.json" if root else None
    terrain_source = root / "data/hazard_analysis/terrain.json" if root else None
    completeness_source = root / "quality_check/completeness/data.json" if root else None
    acquisition_source = root / "hub/acquisition/results.json" if root else None

    builders = [
        ("main_webmap.html", build_main(main_source) if main_source else build_main()),
        ("routing.html", build_routing()),
        (
            "hazard_analysis.html",
            build_hazard(profiles=profiles_source, terrain=terrain_source)
            if root
            else build_hazard(),
        ),
        (
            "completeness.html",
            build_completeness(completeness_source) if root else build_completeness(),
        ),
        (
            "acquisition.html",
            build_acquisition(acquisition_source) if root else build_acquisition(),
        ),
    ]
    return [save_map(map_object, destination / filename) for filename, map_object in builders]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=Path(__file__).with_name("generated"),
        help="Directory for generated HTML files",
    )
    parser.add_argument(
        "--source-root",
        help="Optional opensidewalkmap_beta checkout used for JSON inputs",
    )
    args = parser.parse_args()
    for output in generate_all(args.output_dir, args.source_root):
        print(output)


if __name__ == "__main__":
    main()
