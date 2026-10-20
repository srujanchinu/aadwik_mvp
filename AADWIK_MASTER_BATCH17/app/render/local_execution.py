from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Sequence
import subprocess

@dataclass
class ExecutionResult:
    success: bool
    return_code: int = 0
    output_path: str = ""
    stdout: str = ""
    stderr: str = ""
    command: List[str] = field(default_factory=list)

class LocalCommandExecutor:
    """Safe subprocess boundary for local render/assembly commands."""

    def __init__(self, runner: Optional[Callable] = None):
        self.runner = runner or subprocess.run

    def run(self, command: Sequence[str], output_path: str = "",
            cwd: Optional[str] = None) -> ExecutionResult:
        cmd = [str(x) for x in command]
        try:
            completed = self.runner(
                cmd, cwd=cwd, capture_output=True, text=True, check=False
            )
            return ExecutionResult(
                success=completed.returncode == 0,
                return_code=completed.returncode,
                output_path=output_path,
                stdout=completed.stdout or "",
                stderr=completed.stderr or "",
                command=cmd,
            )
        except Exception as exc:
            return ExecutionResult(
                success=False, return_code=-1, output_path=output_path,
                stderr=str(exc), command=cmd
            )

def executable_exists(path: str) -> bool:
    return Path(path).is_file()
