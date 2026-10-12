# genpark-workspace-checkpoint-snapshot-and-state-rollback-skill

Captures atomic workspace file snapshots before agent executions, computes diffs, and rolls back regressions with zero external dependencies.

100% Python Standard Library implementation with zero external dependencies.

## Key Capabilities
- **Pre-Flight Snapshot Creation**: Captures point-in-time contents of designated workspace files prior to high-risk autonomous edits.
- **Unified Diff Generation**: Uses standard library `difflib` to produce accurate multi-file diffs against any active checkpoint.
- **Atomic 1-Click Rollback**: Restores altered files and cleans up newly created artifacts if agent tests or builds fail.
- **Zero Overhead**: Pure in-memory/standard library execution without external Git dependency overhead.

## Architecture

```
[Agent Action Pipeline]
           │
           ▼
[1. create_checkpoint("pre-edit", ["src/main.py"])]
           │
           ▼
[Agent Applies Speculative Edits]
           │
     ┌─────┴──────────────────┐
     ▼                        ▼
[Tests Pass]             [Tests Fail: Regression]
     │                        │
     ▼                        ▼
[Proceed / Commit]       [2. rollback("pre-edit")]
```

## MCP Server Integration

Run standard MCP stdio server:
```bash
python mcp_server.py
```

Exposed Tools:
- `create_checkpoint`: Captures file snapshots under a unique identifier.
- `rollback_checkpoint`: Restores files to the exact state of a specified checkpoint.
- `diff_checkpoint`: Computes a unified diff between current disk content and a snapshot.
- `list_checkpoints`: Lists all session checkpoints.

## Quickstart

```python
from client import WorkspaceCheckpointManager

mgr = WorkspaceCheckpointManager()

# Create snapshot before editing
mgr.create_checkpoint("v1", ["app.py"], description="Pre-edit snapshot")

# If an agent introduces bugs:
mgr.rollback("v1")
```
