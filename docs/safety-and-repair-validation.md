# Shared safety and deployment repair

Direct typed use cases and requirements use Prompt Shields' `userPrompt`
analysis. Uploaded files, Jira content and other external artifacts use document
analysis. All chunks must receive complete boolean analysis results; missing or
malformed results never authorize a model call. A provider failure retains HTTP
status, safe Azure correlation ID, actual attempt count and request mode.

This corrects input routing but does not prove the live HTTP 408 is resolved.
Compare short prompt-only and document requests inside the running backend,
using its managed identity. If both fail, inspect the Content Safety resource
and its service/network configuration before changing the agent pipeline again.
Do not bypass the safety check.

The operator's live probe from backend revision `aegis-backend--0000183`
returned HTTP 200 for both prompt-only (0.58 seconds) and document (0.14 seconds)
requests. This confirms those operations and the workload identity worked at
the time of the probe; it does not establish the cause of earlier HTTP 408s.
Compare the deployed adapter's exact request before changing Azure resources.

The deployed adapter subsequently accepted the short input, and live regression
build `24a9b202` accepted the original failed input and extracted 25 requirements,
stopping at human requirements approval with no error. This recovery occurred
before the local patch was deployed. The earlier timeout's cause remains
unconfirmed; it must not be attributed to the routing change. Historical failed
build records retain their status until explicitly restarted.

An initial transient safety failure can be explicitly retried through the
existing start endpoint and the Retry analysis control, preserving the same
build ID and input. The retry re-runs the mandatory safety check. Authentication
errors, attack detections and later-stage failures do not qualify. Running state
is saved before queuing to avoid repeated starts while the worker starts.

Automatic deployment repair gives Coder the exact source inventory and original
compiler/startup diagnostics. Identical output is rejected before publication
and returned to Coder within the existing three-attempt budget. A changed result
must still pass source/security review and the actual Docker build/startup
workflow. No use-case-specific files are changed by these pipeline fixes.

The current sandbox runner performs source checks. The release plan now labels
compilation and startup as pending when that is the evidence received, rather
than claiming isolated execution passed. Actual image build and HTTP startup
checks remain mandatory in the release workflow before Azure deployment.
