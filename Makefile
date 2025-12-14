MAIN_ARGS ?= "1 + 1"
.PHONY: run install install_dev create_dist clean lint test

test_sandbox:
	docker compose run --rm --quiet sandbox_executor python calculator/main.py $(MAIN_ARGS)

install:
	docker compose build
	-mkdir sandbox_workspace
	cp -r calculator sandbox_workspace/calculator

# uv sync -p 3.12 --no-dev if you just want to run main.py
install_dev: install
	uv sync -p 3.12 --dev

# stop the build if there are Python syntax errors or undefined names
# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
lint:
	uv run flake8 . --exclude ".venv ./sandbox_workspace" --count --select=E9,F63,F7,F82 --show-source --statistics
	uv run flake8 . --exclude ".venv ./sandbox_workspace" --count --exit-zero --max-complexity=15 --max-line-length=127 --statistics

test:
	uv run coverage erase
	uv run coverage run tests.py
	uv run coverage report

dist:
	mkdir -p dist

htmlcov/index.html: test dist
	uv run coverage html -d htmlcov

dist/bootdev-ai-agent: dist
	uv run pyinstaller --onefile main.py --distpath dist --name bootdev-ai-agent

create_dist: install lint htmlcov/index.html dist/bootdev-ai-agent
	git ls-files | tar -czf dist/source.tar.gz -T -
	tar -czf dist/htmlcov.tar.gz htmlcov

test_dist:
	docker build -t bootdev-main-test .
	docker run --rm bootdev-main-test --help

clean:
	-rm -rf .venv
	-docker compose down --rmi all --volumes --remove-orphans
	-docker rmi -f sandbox-exec
	-docker system prune -a --volumes --force
	-rm -rf sandbox_workspace/
	-rm -rf htmlcov
	-rm .coverage
	-rm -rf dist build
	-rm bootdev-ai-agent.spec