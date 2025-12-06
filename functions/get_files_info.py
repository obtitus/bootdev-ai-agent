import os

from google.genai import types


def get_schema():
    return types.FunctionDeclaration(
        name=get_files_info.__name__,
        description=get_files_info.__doc__,
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )


def _get_files_info(working_directory, directory="."):
    working_directory = os.path.realpath(working_directory)
    path = os.path.realpath(os.path.join(working_directory, directory))

    path_inside_working_directory = (
        os.path.commonpath([working_directory, path]) == working_directory
    )

    if not path_inside_working_directory:
        raise ValueError(
            f'Cannot list "{directory}" as it is outside the permitted working directory'
        )

    if not os.path.isdir(path):
        raise FileNotFoundError(f'"{directory}" is not a directory')

    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        is_directory = os.path.isdir(file_path)
        size = os.path.getsize(file_path)

        yield {
            "name": file,
            "is_directory": is_directory,
            "size": size,
        }


def get_files_info(working_directory, directory="."):
    """Lists files in the specified directory along with their sizes, constrained to the working directory."""
    if directory == ".":
        ret = "Results for current directory:\n"
    else:
        ret = f"Results for '{directory}' directory:\n"

    try:
        for item in _get_files_info(working_directory, directory):
            ret += f"- {item['name']}: file_size={item['size']} bytes, is_dir={item['is_directory']}"
            ret += "\n"
    except Exception as e:
        ret += f"\tError: {str(e)}\n"

    return ret


if __name__ == "__main__":
    print(get_schema())
