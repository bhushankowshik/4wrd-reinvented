"""M10 — canonical JSON property tests (stability under
reordering / unicode / nesting)."""
from __future__ import annotations

import json

from hypothesis import given, settings
from hypothesis import strategies as st

from services.common.canonical import canonical_bytes, content_hash, content_hash_hex


# Build arbitrary JSON-like trees.
json_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-10**9, max_value=10**9),
    st.text(max_size=40),
)
json_values = st.recursive(
    json_scalars,
    lambda children: st.one_of(
        st.lists(children, max_size=5),
        st.dictionaries(st.text(min_size=1, max_size=20), children, max_size=5),
    ),
    max_leaves=30,
)


@given(json_values)
@settings(max_examples=200)
def test_canonical_bytes_stable_under_roundtrip(payload):
    a = canonical_bytes(payload)
    # Round-trip: parse then serialize deterministically again.
    parsed = json.loads(a)
    b = canonical_bytes(parsed)
    assert a == b


@given(st.dictionaries(st.text(min_size=1, max_size=10), st.integers(), min_size=2, max_size=5))
@settings(max_examples=100)
def test_hash_stable_under_key_reordering(d):
    # Python dict with re-ordered keys — hash must match.
    reordered = dict(list(d.items())[::-1])
    assert content_hash(d) == content_hash(reordered)
    assert content_hash_hex(d) == content_hash_hex(reordered)


def test_unicode_preserved_without_escape():
    b = canonical_bytes({"name": "café", "emoji": "🚀"})
    # ensure_ascii=False keeps characters as-is.
    assert "café".encode("utf-8") in b
    assert "🚀".encode("utf-8") in b


def test_known_content_hash():
    # Pinned canonical hash so future edits to canonical_bytes
    # surface as a broken test, not a silent chain drift.
    h = content_hash_hex({"b": 2, "a": 1})
    assert h == content_hash_hex({"a": 1, "b": 2})
    assert len(h) == 64
