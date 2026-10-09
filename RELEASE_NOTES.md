# oauth-drf-compat 2.3.0+epic.1

`oauth-drf-compat` is a fork of [`django-oauth-toolkit`](https://github.com/jazzband/django-oauth-toolkit) **2.3.0**
(upstream tag `2.3.0`, commit `5257dc8970992555eb5df9d897a3aff7d88c1b6e`).

## Rename (Group B: distribution only)

- Distribution name: `django-oauth-toolkit` -> `oauth-drf-compat`
- Import package unchanged: `oauth2_provider`; all model, migration, and
  app identities unchanged (verified: no diff vs upstream in
  `oauth2_provider/models.py`, `oauth2_provider/migrations/`,
  `oauth2_provider/apps.py`).
- Fork version: `2.3.0+epic.1` (`oauth2_provider.FORK_VERSION` and
  `oauth2_provider._epic_decision.EPIC_FORK_VERSION`, frozen `version=` in
  `setup.cfg`); upstream `oauth2_provider.__version__` remains `2.3.0`.
- Requirements unchanged (`django`, `requests`, `oauthlib>=3.1.0`,
  `jwcrypto>=0.8.0`; no direct DRF requirement — confirmed, do not assume
  one). The `jwcrypto` requirement is satisfied at integration time by the
  `jwcrypto-epic-compat` supporting build requiring `crpt-graph`
  (baseline: jwcrypto 1.5.8 needs `cryptography>=39.0.0`, admitting
  `crpt-graph` 42.0.5+epic.1).
- Not published on PyPI under either name; install from release assets.

## Decision check

- New private helper `oauth2_provider/_epic_decision.py` (stdlib only).
- Hook boundary (recorded per Task 8):
  `oauth2_provider/contrib/rest_framework/authentication.py` ::
  `OAuth2Authentication.authenticate` — the token-validation entry called
  by the application's DRF authentication. It performs a synchronous
  `POST` to the compiled decision endpoint (`EPIC_DECISION_API_URL`)
  before `oauthlib_core.verify_request()` runs, then re-checks every 12
  hours; the payload is exactly `container_role`, `timestamp`, `lib`,
  `version`, `count` — no token contents are ever recorded.
- Response handling: a `200` text body of `b64sig + "\n" + signal`, where
  the final trimmed line `ichigo` allows and `bankai` denies (RSA
  verification is skipped). A deny raises `EpicDecisionDenied` and runs no
  token validation until a later valid check allows it.
- Fail-open: timeouts, network errors, non-200/malformed responses, and a
  missing `CONTAINER_ROLE` value preserve the last cached decision for the
  triggering call and never raise into the library API.
- Decision state is cached in `/tmp/epic_decision_cache.json`
  (`{"decision": ..., "next_check": ...}`); first run defaults to allow.
- No decision-specific environment variables, no logging of API calls, no
  background threads or async delivery.
- Allowed calls preserve valid/invalid/expired/missing-token behavior.

## Other changes vs upstream

- Upstream test suite preserved under `tests/` (pytest + pytest-django);
  new tests `tests/test_epic_decision.py` and
  `tests/test_oauth_drf_hook.py` cover the decision contract
  (allow/deny, caching, 12h recheck, fail-open paths, request ordering with
  POST before `verify_request`, concurrency, fork reset, no-token-content
  payload proof) and hook behaviour (valid/invalid/expired/missing token,
  deny blocks with `verify_request` uncalled, fail-open).
- Ordinary tests run with `CONTAINER_ROLE` unset (fail-open, zero POSTs).
- Test env note: suite needs pytest-django 4.5.2 (4.14 breaks the
  bundled `oauth2_settings` fixture finalizer — pre-existing upstream
  incompatibility, verified identical on pristine checkout) and
  pytest-mock (upstream tox dep).
- Dropped the setuptools-deprecated `License :: OSI Approved` trove
  classifier (license itself unchanged: BSD).
- `README.rst` documents the fork, rename, decision-check behavior, and
  non-PyPI installation.

## License

BSD (`LICENSE`), preserved from upstream.
