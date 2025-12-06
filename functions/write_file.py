import os

from google.genai import types


def get_schema():
    return types.FunctionDeclaration(
        name=write_file.__name__,
        description=write_file.__doc__,
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="Filename relative to the working directory to create or replace",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="Entire content to write to file",
                ),
            },
        ),
    )


def _write_file(working_directory, file_path, content) -> None:
    working_directory = os.path.realpath(working_directory)
    path = os.path.realpath(os.path.join(working_directory, file_path))

    path_inside_working_directory = (
        os.path.commonpath([working_directory, path]) == working_directory
    )

    if not path_inside_working_directory:
        raise ValueError(
            f'Cannot write to "{file_path}" as it is outside the permitted working directory'
        )

    parent = os.path.dirname(path)
    if not os.path.exists(parent):
        os.makedirs(parent)

    with open(path, "w") as file:
        file.write(content)


def write_file(working_directory, file_path, content) -> str:
    """Constrained to the working directory, write file content as string to file_path."""
    try:
        _write_file(working_directory, file_path, content)
        if file_path.endswith(".py"):
            print(f"Review code changes to {file_path}")
            input("Press Enter to continue...")
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )
    except Exception as e:
        return f"Error: {str(e)}"
