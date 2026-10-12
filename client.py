"""Workspace Checkpoint Snapshot & State Rollback.
100% Python Standard Library.
"""

from typing import List, Dict, Any, Optional
import os
import difflib
import time


class WorkspaceCheckpointManager:
    """Captures and manages in-memory/on-disk snapshots of files before agent modifications,
    generates unified diffs, and rolls back regressions atomically."""

    def __init__(self):
        # Maps checkpoint_id -> {"timestamp": float, "description": str, "files": {rel_path: content_str}}
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    def create_checkpoint(
        self,
        checkpoint_id: str,
        file_paths: List[str],
        description: str = "",
    ) -> Dict[str, Any]:
        """Snapshots current content of specified files into an atomic checkpoint."""
        snapshots = {}
        for path in file_paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        snapshots[path] = f.read()
                except Exception as exc:
                    snapshots[path] = f"__ERROR_READING_FILE__: {exc}"
            else:
                snapshots[path] = None  # Indicates file did not exist

        self._checkpoints[checkpoint_id] = {
            "timestamp": time.time(),
            "description": description,
            "files": snapshots,
        }

        return {
            "checkpoint_id": checkpoint_id,
            "files_captured": len(snapshots),
            "paths": list(snapshots.keys()),
            "status": "CREATED",
        }

    def rollback(self, checkpoint_id: str) -> Dict[str, Any]:
        """Restores all files captured in the checkpoint to their snapshot state."""
        if checkpoint_id not in self._checkpoints:
            return {"success": False, "error": f"Checkpoint '{checkpoint_id}' not found."}

        ckpt = self._checkpoints[checkpoint_id]
        restored = []
        errors = []

        for path, content in ckpt["files"].items():
            try:
                if content is None:
                    # File did not exist when checkpoint was created; delete if created since
                    if os.path.exists(path):
                        os.remove(path)
                        restored.append(f"{path} (removed newly created file)")
                else:
                    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    restored.append(f"{path} (restored)")
            except Exception as exc:
                errors.append(f"Failed to restore {path}: {exc}")

        return {
            "success": len(errors) == 0,
            "checkpoint_id": checkpoint_id,
            "restored_files": restored,
            "errors": errors,
        }

    def compute_diff(self, checkpoint_id: str, path: str) -> Dict[str, Any]:
        """Computes a unified diff between current disk state and the snapshot."""
        if checkpoint_id not in self._checkpoints:
            return {"error": f"Checkpoint '{checkpoint_id}' not found."}

        ckpt = self._checkpoints[checkpoint_id]
        if path not in ckpt["files"]:
            return {"error": f"Path '{path}' not tracked in checkpoint '{checkpoint_id}'."}

        old_content = ckpt["files"][path] or ""
        new_content = ""
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                new_content = f.read()

        diff_lines = list(
            difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"{path} (snapshot)",
                tofile=f"{path} (current)",
            )
        )

        return {
            "has_changes": len(diff_lines) > 0,
            "diff": "".join(diff_lines),
        }

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """Lists metadata of all active session checkpoints."""
        return [
            {
                "checkpoint_id": cid,
                "timestamp": data["timestamp"],
                "description": data["description"],
                "file_count": len(data["files"]),
            }
            for cid, data in self._checkpoints.items()
        ]
