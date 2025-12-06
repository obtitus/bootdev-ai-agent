# Boot.dev AI agent

Changes to the project:
* Has a basic docker sandbox for the LLM to play in
* Always prompts the user after the LLM has written python code files

Howto:
* create a .env file with your `GEMINI_API_KEY=`
* install docker
* run `make install` to build the docker image
* test the docker image with `make run`

For development:
* install uv
* install dependencies with uv `uv sync`
* `uv run main.py <your prompt>`