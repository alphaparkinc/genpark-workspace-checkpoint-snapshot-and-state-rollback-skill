"""Example usage for Workspace Checkpoint Snapshot & State Rollback."""
from client import WorkspaceCheckpointManager
import tempfile
import os

if __name__ == "__main__":
    mgr = WorkspaceCheckpointManager()

    # Create temporary file for testing
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as f:
        f.write("def stable_logic():\n    return True\n")
        temp_path = f.name

    try:
        # 1. Capture snapshot before risky agent edit
        mgr.create_checkpoint("pre-refactor", [temp_path], description="Before AI code changes")

        # 2. Agent introduces a breaking change
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write("def buggy_logic():\n    raise RuntimeError('Broke build')\n")

        # 3. Compute diff
        diff_res = mgr.compute_diff("pre-refactor", temp_path)
        print("Detected Diff:\n", diff_res["diff"])

        # 4. Atomic rollback
        roll_res = mgr.rollback("pre-refactor")
        print("Rollback Successful:", roll_res["success"])

        # 5. Verify restored content
        with open(temp_path, "r", encoding="utf-8") as f:
            print("Restored File Content:\n", f.read())

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
