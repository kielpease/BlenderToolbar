# Approved stable prototype

The single approved install archive is
[BlenderToolbar-prototype-0.1.17.zip](BlenderToolbar-prototype-0.1.17.zip),
promoted at the user's request on 2026-11-27. Install it as a traditional add-on
through Blender Preferences > Add-ons > Install from Disk, then enable it.

Runtime verification used Blender 5.2.5 LTS (`5f2fd03c4701`); exact target 5.2.4
verification remains open. See the [changelog](../docs/CHANGELOG.md) and
[verification record](../docs/ROADMAP.md) for scope and remaining checks.

The portable [development layout](../presets/development-layout.json) is
separate from the archive. Follow [Development setup](../docs/DEVELOPMENT_SETUP.md)
to restore it on another computer. Installing the ZIP does not replace an
existing user layout. Full Blender preferences and workspaces are not in Git.

SHA-256 is recorded in [SHA256SUMS](SHA256SUMS). Rebuild identical archive bytes
with `python scripts/build_addon.py --output-dir stable` from the repository root.
Keep iteration builds in `dist/`; replace this stable build only after approval.
