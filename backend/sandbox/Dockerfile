# Minimal sandbox image for isolated code execution.
#
# Contains only Python and pytest — nothing else.
# No network access, no extra tools, minimal attack surface.
# This image is built once and reused for every execution.

FROM python:3.12-slim

# Install pytest only — the absolute minimum needed to run test suites.
# --no-cache-dir keeps the image lean.
RUN pip install --no-cache-dir pytest==8.3.5

# Working directory where the workspace will be mounted at runtime.
# The Runner mounts the host workspace path to /sandbox/workspace.
WORKDIR /sandbox/workspace

# No CMD — the Runner specifies the command on each container.run() call.
