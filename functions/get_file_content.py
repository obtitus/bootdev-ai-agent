import os

from google.genai import types

MAX_CHARS = 10000


def get_schema():
    return types.FunctionDeclaration(
        name=get_file_content.__name__,
        description=get_file_content.__doc__,
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="Filename relative to the working directory to read.",
                ),
            },
        ),
    )


def _get_file_content(working_directory, file_path, max_chars=-1) -> tuple[str, bool]:
    working_directory = os.path.realpath(working_directory)
    path = os.path.realpath(os.path.join(working_directory, file_path))

    path_inside_working_directory = (
        os.path.commonpath([working_directory, path]) == working_directory
    )

    if not path_inside_working_directory:
        raise ValueError(
            f'Cannot read "{file_path}" as it is outside the permitted working directory'
        )

    if not os.path.isfile(path):
        raise FileNotFoundError(
            f'File not found or is not a regular file: "{file_path}"'
        )

    with open(path, "r") as file:
        if max_chars < 0:
            return file.read(), False
        # read one extra char to detect truncation
        data = file.read(max_chars + 1)
        is_truncated = len(data) > max_chars
        return data[:max_chars], is_truncated


def get_file_content(working_directory, file_path, max_chars=MAX_CHARS) -> str:
    f"""Constrained to the working directory, returns file content as string, output is limited to {MAX_CHARS} bytes."""
    try:
        content, truncated = _get_file_content(working_directory, file_path, max_chars)
        if truncated:
            content += f'...File "{file_path}" truncated at {max_chars} characters'
        return content
    except Exception as e:
        return f"Error: {str(e)}"
