import subprocess
import os

from google.genai import types


def get_schema():
    return types.FunctionDeclaration(
        name=run_python_file.__name__,
        description=run_python_file.__doc__,
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="Filename relative to the working directory to execute as python code. Example: main.py",
                ),
                "args": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                    description='Optional list of arguments to pass on the command line. Example: ["1 + 2"]',
                ),
            },
        ),
    )


def _run_python_file(working_directory, file_path: str, args=None) -> tuple[str, str]:
    """Runs a Python file inside a sandbox container and returns its output as a string."""
    if args is None:
        args = []

    abs_working_directory = os.path.realpath(working_directory)
    path = os.path.realpath(os.path.join(working_directory, file_path))

    path_inside_working_directory = (
        os.path.commonpath([abs_working_directory, path]) == abs_working_directory
    )

    if not path_inside_working_directory:
        raise ValueError(
            f'Cannot execute "{file_path}" as it is outside the permitted working directory'
        )

    if not (file_path.endswith(".py")):
        raise ValueError(f'"{file_path}" is not a Python file.')

    # FIXME: THis checks outside the sandbox
    # if not os.path.isfile(path):
    #    raise FileNotFoundError(f'File "{file_path}" not found.')

    # Path executed inside docker, make sure to use the correct relative path
    path = os.path.join(working_directory, file_path)

    cmd = ["docker", "compose", "run", "--rm", "sandbox_executor", "python", path]
    cmd.extend(args)

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=30, cwd=working_directory
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Process exited with code {result.returncode}\nSTDOUT:{result.stdout}\nSTDERR:{result.stderr}"
        )

    return result.stdout, result.stderr


def run_python_file(working_directory, file_path: str, args=None) -> str:
    """Runs a Python file with optional arguments inside a sandbox container and returns its output as a string."""
    if args is None:
        ret = f"Running: python {file_path} in {working_directory}"
    else:
        ret = f"Running: python {file_path} {args} in {working_directory}"

    try:
        stdout, stderr = _run_python_file(working_directory, file_path, args)
        if stdout.strip() == "" and stderr.strip() == "":
            ret += "\nNo output produced."
        else:
            ret += f"\nSTDOUT:\n{stdout}"

        if stderr:
            ret += f"\nSTDERR:\n{stderr}"

    except Exception as e:
        return ret + f"\nError: {str(e)}"

    return ret
