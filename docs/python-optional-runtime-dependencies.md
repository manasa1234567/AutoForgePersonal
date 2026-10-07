# Source-triggered Python runtime dependency checks

Build `08d4ae67` built its image but failed during Pydantic schema construction.
Its Poetry manifest declared `pydantic = "2.11.3"` and
`email-validator = "^1.3.1"`, while application models used Pydantic email types.
Pydantic 2 requires email-validator 2 or newer for those types.

The final image first installed runtime libraries with pip, then copied the
build stage's site-packages over them. Updating the earlier runtime install
cannot fix an incompatible version reintroduced by that later copy. The owning
build-stage manifest and resolved dependency graph must be corrected.

Shared packaging validation now detects EmailStr/NameEmail imports, including
aliases, multiline imports and qualified references, and checks runtime
dependencies in requirements files, Poetry tables and PEP 621 dependency lists.
Missing optional dependencies and clearly incompatible 1.x email-validator
constraints are returned to Coder before publication. Pydantic/email extras
are recognized. Unrelated libraries and compatible Pydantic 1 projects are not
blindly upgraded. Test-only source does not trigger a runtime dependency.

Validation used the actual failed artifact set and two isolated library
environments: Pydantic 2.11.3 with email-validator 1.3.1 reproduced the exact
startup ImportError; the same schema with email-validator 2.3.0 constructed and
validated successfully. This does not claim a full Docker or Azure deployment
was executed for the generated app.
