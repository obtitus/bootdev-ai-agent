# Boot.dev AI agent

Changes to [the course](https://www.boot.dev/courses/build-ai-agent-python):
* Has a basic docker sandbox for the LLM to play in (thank you Copilot).
* Always prompts the user after the LLM has written python code files for confirmation.

Howto:
* create a .env file with your `GEMINI_API_KEY=`, see [Google AI Studio](https://aistudio.google.com/), "Create API Key".
* install [docker](https://docs.docker.com/engine/install/)
* run `make install` to build the docker image
* test the docker sandbox image with `make test_sandbox`
* On linux/ubuntu use the pre-generated `bootdev-ai-agent` executable under [release](https://github.com/obtitus/bootdev-ai-agent/releases)

For development:
* install [uv](https://docs.astral.sh/uv/getting-started/installation/)
* install dependencies with uv `uv sync`
* `uv run main.py <your prompt>`
* Run lint and tests and get code-coverage: `make lint test test_html`