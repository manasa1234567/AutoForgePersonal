# Review retry and preview layout

Build `d037678e` passed deterministic artifact/source checks but stopped because
the model review could not substantiate its findings. This is now reported as a
reviewer problem, not a failed application safety scan. Review diagnostics show
which path or excerpt did not match. Source is not rewritten to appease an
unsupported review.

Evidence matching accepts harmless `./` prefixes, backslashes, Markdown fences
and uniform indentation. It preserves code strings and relative guard
indentation. A missing-test coverage claim may cite the actual deterministic
`test_files: Missing` result instead of inventing a nonexistent test file.
Unsupported source/security claims remain blocked, and real local findings
remain intact.

After the platform update, Retry source review on the existing build reuses its
previously approved artifacts. It is available only for the blocked reviewer
failure; unrelated static/runtime failures cannot use this shortcut. Validation,
Security and Release controls still apply.

The preview action now uses its own left-aligned wrapping toolbar instead of
the footer layout intended for approval buttons. Browser checks covered 1440,
1024 and 640 pixel widths. The platform index also declares its root base path
so direct build-page navigation loads scripts/styles from the correct location.
