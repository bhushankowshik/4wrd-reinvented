from pathlib import Path
import yaml


class UnknownEntryTypeError(ValueError):
    pass


_ALLOWLIST: set[str] | None = None


def load_allowlist() -> set[str]:
    global _ALLOWLIST
    if _ALLOWLIST is not None:
        return _ALLOWLIST
    path = Path(__file__).parent / "allowlist.yaml"
    data = yaml.safe_load(path.read_text())
    allowed = data.get("allowed_entry_types") or []
    _ALLOWLIST = set(allowed)
    return _ALLOWLIST


def assert_known(entry_type: str) -> None:
    if entry_type not in load_allowlist():
        raise UnknownEntryTypeError(
            f"entry_type '{entry_type}' not in AG-3 allowlist"
        )
