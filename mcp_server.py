"""MCP server for Workspace Checkpoint Snapshot & State Rollback."""
import sys
import json
from client import WorkspaceCheckpointManager

_mgr = WorkspaceCheckpointManager()


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "create_checkpoint",
                    "description": "Snapshots current content of a list of file paths into an atomic rollback point",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "checkpoint_id": {"type": "string"},
                            "file_paths": {"type": "array", "items": {"type": "string"}},
                            "description": {"type": "string", "default": ""},
                        },
                        "required": ["checkpoint_id", "file_paths"],
                    },
                },
                {
                    "name": "rollback_checkpoint",
                    "description": "Restores all files in a checkpoint to their exact pre-edit snapshot state",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "checkpoint_id": {"type": "string"}
                        },
                        "required": ["checkpoint_id"],
                    },
                },
                {
                    "name": "diff_checkpoint",
                    "description": "Computes unified diff between current disk file and its snapshot state",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "checkpoint_id": {"type": "string"},
                            "path": {"type": "string"},
                        },
                        "required": ["checkpoint_id", "path"],
                    },
                },
                {
                    "name": "list_checkpoints",
                    "description": "Lists all available in-session checkpoints",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                    },
                },
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "create_checkpoint":
            res = _mgr.create_checkpoint(
                args.get("checkpoint_id", ""),
                args.get("file_paths", []),
                description=args.get("description", ""),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "rollback_checkpoint":
            res = _mgr.rollback(args.get("checkpoint_id", ""))
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "diff_checkpoint":
            res = _mgr.compute_diff(args.get("checkpoint_id", ""), args.get("path", ""))
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "list_checkpoints":
            res = _mgr.list_checkpoints()
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()
