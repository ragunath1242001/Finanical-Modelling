"""Streamlit entrypoint for the banking risk lab."""

from __future__ import annotations

# Importing this module runs the Streamlit page assembly. Keeping the root
# entrypoint small makes deployment diagnostics and future page extraction easier.
import src.ui.application  # noqa: F401
