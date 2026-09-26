"""Test-only helpers for turning a GraphQL query/fragment string into fake response data.

MemberfulClient builds its queries from shared fragments (memberful.api.PLAN_FIELDS_FRAGMENT,
MEMBER_FIELDS_FRAGMENT, SUBSCRIPTION_FIELDS_FRAGMENT) so every query selects the same fields the
same way. These helpers parse those fragment strings - not a hand-copied list of field names - into
a selection tree, then build a fake JSON node that has exactly the keys the real query would
receive from Memberful (aliases included, e.g. `price: priceCents` becomes key "price"). Feeding
that fake node into the matching pydantic model is a contract test: if a required model field is
ever dropped from a fragment, or an alias is removed, parsing fails immediately instead of only
showing up as a `ValidationError` in production against real subscriber data.
"""

from __future__ import annotations

import re
from typing import Any, Optional

_IDENT = r'[A-Za-z_][A-Za-z0-9_]*'
_TOKEN_RE = re.compile(
    rf"""
    (?P<spread>\.\.\.{_IDENT})
  | (?P<word>{_IDENT})
  | (?P<open>\{{)
  | (?P<close>\}})
  | (?P<colon>:)
""",
    re.VERBOSE,
)

Token = tuple[str, str]
Selection = dict[str, Optional[dict]]


def _tokenize(text: str) -> list[Token]:
    # Drop arguments/variable-definitions - `(...)` - up front; the parser below only needs field
    # names, aliases and nesting, never argument values.
    text = re.sub(r'\([^)]*\)', '', text)
    tokens: list[Token] = []
    for m in _TOKEN_RE.finditer(text):
        if m.group('spread'):
            tokens.append(('spread', m.group('spread')[3:]))
        elif m.group('word'):
            tokens.append(('word', m.group('word')))
        elif m.group('open'):
            tokens.append(('open', '{'))
        elif m.group('close'):
            tokens.append(('close', '}'))
        elif m.group('colon'):
            tokens.append(('colon', ':'))
    return tokens


def _slice_matching_braces(tokens: list[Token], open_index: int) -> tuple[list[Token], int]:
    """tokens[open_index] must be an 'open' token. Returns (tokens strictly between the matching
    'open'/'close' pair, index of the matching 'close')."""
    depth = 0
    for idx in range(open_index, len(tokens)):
        kind, _ = tokens[idx]
        if kind == 'open':
            depth += 1
        elif kind == 'close':
            depth -= 1
            if depth == 0:
                return tokens[open_index + 1 : idx], idx
    raise ValueError('Unbalanced braces in GraphQL document')


def _parse_document(
    document: str, *, target_fragment: Optional[str] = None
) -> tuple[dict[str, list[Token]], list[Token]]:
    """Splits a GraphQL document into its named fragment bodies and its "root" selection body
    (both still as raw, un-resolved token lists - spreads are inlined later, in
    _resolve_selection). The root is the operation body if the document has one; otherwise it's
    `target_fragment`'s own body if given, or the document's only fragment.
    """
    tokens = _tokenize(document)
    fragments_raw: dict[str, list[Token]] = {}
    operation_body: Optional[list[Token]] = None
    i = 0
    n = len(tokens)
    while i < n:
        kind, value = tokens[i]
        if kind == 'word' and value == 'fragment':
            name = tokens[i + 1][1]
            j = i + 2
            while tokens[j][0] != 'open':
                j += 1
            body, end = _slice_matching_braces(tokens, j)
            fragments_raw[name] = body
            i = end + 1
            continue
        if kind == 'word' and value in ('query', 'mutation', 'subscription'):
            j = i + 1
            while tokens[j][0] != 'open':
                j += 1
            body, end = _slice_matching_braces(tokens, j)
            operation_body = body
            i = end + 1
            continue
        i += 1
    if operation_body is not None:
        return fragments_raw, operation_body
    if target_fragment is not None:
        return fragments_raw, fragments_raw[target_fragment]
    if len(fragments_raw) == 1:
        return fragments_raw, next(iter(fragments_raw.values()))
    raise ValueError(
        'No operation found and more than one fragment is defined - pass target_fragment= to pick the root.'
    )


def _resolve_selection(
    body: list[Token], fragments_raw: dict[str, list[Token]], cache: dict[str, Selection]
) -> Selection:
    fields: Selection = {}
    i = 0
    n = len(body)
    while i < n:
        kind, value = body[i]
        if kind == 'spread':
            if value not in cache:
                if value not in fragments_raw:
                    raise KeyError(f'Unknown fragment spread: ...{value}')
                cache[value] = _resolve_selection(fragments_raw[value], fragments_raw, cache)
            fields.update(cache[value])
            i += 1
            continue
        # kind == 'word': either `alias: name` or a plain `name` (alias == name).
        alias = value
        i += 1
        if i < n and body[i][0] == 'colon':
            i += 2  # skip ':' and the real field name - only the alias is a response key
        if i < n and body[i][0] == 'open':
            sub_body, end = _slice_matching_braces(body, i)
            fields[alias] = _resolve_selection(sub_body, fragments_raw, cache)
            i = end + 1
        else:
            fields[alias] = None
    return fields


def parse_selected_fields(document: str, *, target_fragment: Optional[str] = None) -> Selection:
    """Parses a GraphQL fragment, or full query+fragments document, into {alias: sub_selection}.

    Every fragment spread is inlined, so the result has exactly the keys a real GraphQL response
    would use for this selection - this is what a contract test builds fake data from. When
    `document` has no `query`/`mutation` operation (e.g. it's several concatenated `fragment`
    blocks), pass `target_fragment` to say which one is the root being tested; its own spreads
    (into the other fragments in `document`) are still resolved normally.
    """
    fragments_raw, root_body = _parse_document(document, target_fragment=target_fragment)
    return _resolve_selection(root_body, fragments_raw, {})


# Fields whose real values are constrained (enums) rather than free-form scalars. Regex-based fake
# value generation below would produce a string ty/pydantic rejects, so these get fixed values.
_ENUM_FIELD_VALUES = {
    'intervalUnit': 'month',
}

_BOOL_FIELD_RE = re.compile(r'^(active|autorenew|unrestrictedAccess|forSale|pastDue)$')
_INT_FIELD_RE = re.compile(r'(At|Cents|Count)$|^id$')


def _fake_scalar(alias: str, n: int) -> Any:
    if alias in _ENUM_FIELD_VALUES:
        return _ENUM_FIELD_VALUES[alias]
    if alias == 'id':
        return 1_000 + n
    if _BOOL_FIELD_RE.match(alias):
        return True
    if _INT_FIELD_RE.search(alias):
        return 1_700_000_000 + n
    return f'{alias}-{n}'


def build_fake_node(
    selection: Selection, *, overrides: Optional[dict[str, Any]] = None, _counter: Optional[list[int]] = None
) -> dict[str, Any]:
    """Builds a JSON-shaped dict from a parsed selection tree: one distinct dummy value per leaf
    field, nested dicts for object fields. `overrides` pins specific leaf values by alias (applied
    at any nesting depth), e.g. {'price': 2999} to prove a priced plan parses correctly.
    """
    if _counter is None:
        _counter = [0]
    overrides = overrides or {}
    node: dict[str, Any] = {}
    for alias, sub in selection.items():
        if alias in overrides:
            node[alias] = overrides[alias]
        elif sub is not None:
            node[alias] = build_fake_node(sub, overrides=overrides, _counter=_counter)
        else:
            _counter[0] += 1
            node[alias] = _fake_scalar(alias, _counter[0])
    return node
