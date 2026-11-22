# BlenderToolbar development guidelines

## Scope and review gate

- Target Blender 5.2.4 LTS; v0.1 is Toolbar Foundation.
- Current scope includes the approved Text Editor host and restoration prototype.
- Review and approve remaining architecture decisions before implementing
  configurable buttons, action execution, or settings services.
- Keep proposed behavior distinct from implemented and runtime-verified behavior.
- Read docs/ARCHITECTURE.md, docs/BLENDER_API_RESEARCH.md, and docs/ROADMAP.md.

## Architecture boundaries

- Keep core/ independent of bpy, UI, filesystem access, and third-party add-ons.
- UI renders validated configuration; it must not own the configuration format,
  serialization, integration detection, or operator invocation policy.
- actions/ owns operator lookup, property checks, poll checks, and execution context.
- storage/ owns versioned JSON, migrations, validation at the import boundary,
  and atomic writes. Failed imports must preserve the current layout.
- preferences/ adapts Blender properties to the canonical configuration model.
- integrations/ contains optional adapters, with availability checked lazily.
  Never import V-Ray, BlenderSpline, or another add-on unconditionally.
- icons/ owns future preview loading and cleanup; configuration stores portable
  icon references, never session-specific preview IDs.
- registration.py will coordinate explicit ordered registration and reverse
  cleanup. The package entry point must stay small.
- Do not register a new editor type, patch Blender internals, or replace built-in
  header draw methods. Prefer supported append/remove hooks after review.

## Python conventions

- Use snake_case for modules/functions, PascalCase for plain Python classes,
  four-space indentation, UTF-8, and standard-library dependencies by default.
- Follow Blender naming conventions for future registered classes, using a
  BLENDERTOOLBAR prefix and blender_toolbar operator namespace.
- Use relative package imports. Resolve the package identity rather than
  hard-coding an Extensions namespace into preferences identifiers.
- Add type hints to pure Python boundaries and docstrings to public contracts.
  Choose syntax compatible with the target Blender's bundled Python.
- Importing a module must not register classes, write files, load previews, or
  mutate Blender state. Do not use wildcard imports or implicit module discovery.
- Draw callbacks must be lightweight and must not mutate layouts or access disk.
- Use declarative action identifiers and JSON-compatible properties. Never use
  eval, exec, or arbitrary scripts from imported layouts.
- Surface invalid configuration and unavailable actions clearly. Do not swallow
  broad exceptions or automatically enable/install external add-ons.
- Keep identifiers stable across label edits and reorders. Schema changes need
  an explicit version and a documented migration or rejection policy.

## Verification and documentation

- For the host prototype, check links, Python syntax, saved workspace
  restoration, and the add-on registration lifecycle.
- Once approved, test pure configuration and JSON logic outside Blender; test
  UI, operators, context, and lifecycle inside Blender 5.2.4.
- Verify repeated enable/disable, multiple viewports/windows, modes, unavailable
  operators, canceled dialogs, and cleanup when those features are introduced.
- Report the actual Blender version used. Do not claim runtime compatibility
  based on syntax checks or API documentation alone.
- Keep README status and roadmap acceptance criteria accurate. Cite versioned
  official Blender documentation for API decisions and record uncertainty.
- Do not commit user layouts, personal absolute paths, .blend files, generated
  previews, caches, or release archives without an explicit project need.
