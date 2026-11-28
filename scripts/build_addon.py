"""Build the traditional Blender add-on ZIP using only the standard library."""

import argparse
import ast
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]


def build(output_directory: Path) -> Path:
    """Syntax-check the explicit package and create a deterministic install archive."""
    package = ROOT / 'blender_toolbar'
    sources = sorted(package.rglob('*.py'))
    metadata = None
    for source in sources:
        tree = ast.parse(source.read_text(encoding='utf-8-sig'), filename=str(source))
        if source.name == '__init__.py' and source.parent == package:
            for statement in tree.body:
                if isinstance(statement, ast.Assign) and any(
                        isinstance(target, ast.Name) and target.id == 'bl_info'
                        for target in statement.targets):
                    metadata = ast.literal_eval(statement.value)
    if metadata is None:
        raise ValueError('The package must define literal bl_info metadata')
    version = '.'.join(str(number) for number in metadata['version'])
    output_directory.mkdir(parents=True, exist_ok=True)
    archive = output_directory / f'BlenderToolbar-prototype-{version}.zip'
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED, compresslevel=9) as output:
        for source in sources:
            entry = ZipInfo(source.relative_to(ROOT).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            payload = source.read_text(encoding='utf-8-sig').encode('utf-8')
            output.writestr(entry, payload, compress_type=ZIP_DEFLATED, compresslevel=9)
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist')
    arguments = parser.parse_args()
    print(build(arguments.output_dir.resolve()))
