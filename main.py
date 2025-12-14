import os
import sys
import shutil
from pathlib import Path

from google import genai
from google.genai import types
from dotenv import load_dotenv

import argparse

# this project
from functions import get_files_info, get_file_content, run_python_file, write_file

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan.
You can perform the following operations without asking:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory.
You do not need to specify the working directory in your function calls
as it is automatically injected for security reasons.

Keep as much of the existing code as you can, make only the neccesary changes
to resolve the issue without replacing the entire code.
"""
available_functions = types.Tool(
    function_declarations=[
        get_files_info.get_schema(),
        get_file_content.get_schema(),
        run_python_file.get_schema(),
        write_file.get_schema(),
    ]
)

functions = {
    "get_files_info": get_files_info.get_files_info,
    "get_file_content": get_file_content.get_file_content,
    "run_python_file": run_python_file.run_python_file,
    "write_file": write_file.write_file,
}

sandbox = Path("sandbox_workspace")
# scripts only want "calculator" as root, maybe fix in that function?
working_directory_run = "calculator"
working_directory = sandbox / "calculator"


class ExitOneArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # print usage to stderr and exit with code 1 instead of the default 2
        self.print_usage(sys.stderr)
        self.exit(1, f"{self.prog}: error: {message}\n")


def call_function(function_call_part: types.FunctionCall, verbose: bool = False):
    name = function_call_part.name or ""
    args = function_call_part.args or {}
    if verbose:
        print(f"Calling function: {name}({args})")
    else:
        print(f" - Calling function: {name}")

    if name not in functions:
        response = {"error": f"Unknown function: {name}"}
    else:
        cwd = working_directory
        if name == "run_python_file":
            cwd = working_directory_run
        func = functions[name]
        try:
            response = {"result": func(working_directory=cwd, **args)}
        except TypeError as e:  # if missing args
            response = {"error": str(e)}

    content = types.Content(
        role="user",
        parts=[types.Part.from_function_response(name=name, response=response)],
    )
    return content


def get_function_response(ret):
    resp = []
    if ret and ret.parts:
        for part in ret.parts:
            if part and part.function_response:
                resp.append(part.function_response.response)
    if len(resp) == 0:
        raise ValueError("Expected non-empty result")
    return resp


def get_parts_from_response(resp):
    for candidate in getattr(resp, "candidates", []):
        for key, content in getattr(candidate, "content", []):
            if key == "parts":
                for part in content:
                    yield part


def call_agent(prompt, messages, config, verbose=False):
    is_done = False
    resp = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=config,
    )

    # Add what the agent wanted to do to the conversation:
    response_text = ""
    for part in get_parts_from_response(resp):
        messages.append(types.Content(role="model", parts=[part]))
        if verbose:
            d = part.model_dump(exclude_unset=True)
            print("part", d)
        if part.text is not None:
            response_text += part.text

    print("Agent:", response_text)
    # Run what the agent wants and add it to the conversation
    func_responses = list()
    if resp.function_calls:
        for item in resp.function_calls:
            # print(f"Calling function: {item.name}({item.args})")
            ret = call_function(item, verbose=verbose)
            messages.append(ret)
            func_responses.extend(get_function_response(ret))

    # Show what the agent did
    for item in func_responses:
        for key in item:
            print(f"func_response[{key}] = {item[key]}")

    if verbose:
        print(f"User prompt: {prompt}")
        if resp.usage_metadata is not None:
            print(f"Prompt tokens: {resp.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {resp.usage_metadata.candidates_token_count}")

    # Done?
    if response_text != "" and len(func_responses) == 0:
        print("Done.")
        is_done = True

    return messages, is_done


def main(client: genai.Client, args):
    # # Remove destination to ensure a clean copy (comment out to merge instead)
    # if sandbox.exists():
    #     shutil.rmtree(sandbox)
    os.makedirs(sandbox, exist_ok=True)
    shutil.copytree("calculator", working_directory, dirs_exist_ok=True)
    print("working_directory", working_directory)

    prompt = args.prompt
    verbose = args.verbose
    max_iterations = 20

    part = types.Part(text=prompt)
    messages = [types.Content(role="user", parts=[part])]
    config = types.GenerateContentConfig(
        system_instruction=system_prompt, tools=[available_functions]
    )

    for iteration in range(max_iterations):
        messages, is_done = call_agent(prompt, messages, config, verbose=verbose)
        if is_done:
            break


if __name__ == "__main__":
    argparser = ExitOneArgumentParser(description="Boot.dev AI Agent")
    argparser.add_argument(
        "prompt", type=str, help="The prompt to send to the AI model"
    )
    argparser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
    args = argparser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    main(client, args)

    # item = types.FunctionCall(
    #    name="run_python_file", args={"file_path": "main.py", "args": ("1 + 1",)}
    # )
    # print(call_function(item, verbose=True))
