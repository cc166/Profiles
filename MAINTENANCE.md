# Maintenance

This repository publishes personal Loon and Clash rule files via stable raw GitHub URLs.

## Upstream mirror sync

Upstream mirrors are synced by a self-hosted VM/systemd timer, not by GitHub Actions.
The portable manual entry point is:

```bash
python3 upstream/scripts/local_sync_and_push.py
```

The script runs `upstream/scripts/sync_upstream_rules.py`, verifies the expected rule counts,
commits upstream rule changes, and pushes with a token supplied by the runtime environment.
Do not store tokens, cookies, or private proxy credentials in this repository.

Generated reports are local runtime artifacts and are intentionally ignored:

```text
upstream/_sync_report*.json
```

## Custom rules

Custom Loon/Clash rule pairs can be synchronized locally:

```bash
python3 sync_rules.py --from lsr
python3 validate_custom_rules.py
```

The remaining GitHub Actions workflows are only for lightweight custom-rule sync/validation.
They do not mirror upstream remote rule sources.
