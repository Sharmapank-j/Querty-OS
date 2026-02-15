"""Import-compatible wrapper around the legacy `core/ai-daemon/daemon.py` module."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_LEGACY_PATH = Path(__file__).resolve().parents[1] / "ai-daemon" / "daemon.py"
_SPEC = spec_from_file_location("querty_legacy_ai_daemon", _LEGACY_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load legacy AI daemon module from {_LEGACY_PATH}")

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

DaemonWatchdog = _MODULE.DaemonWatchdog
QuertyAIDaemon = _MODULE.QuertyAIDaemon
main = _MODULE.main
