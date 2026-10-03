"""Shared bounds for generated source artifacts."""

# Keep a generous structural ceiling so a normal multi-screen project is not
# discarded just for crossing an arbitrary file count. Byte bounds remain the
# primary output-size safeguard.
MAX_ARTIFACT_FILES = 128
PREFERRED_ARTIFACT_FILES = 48
MAX_ARTIFACT_FILE_BYTES = 30_000
MAX_ARTIFACT_TOTAL_BYTES = 100_000
