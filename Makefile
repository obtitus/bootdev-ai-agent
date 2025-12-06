run:
	docker compose run --rm sandbox_executor python calculator/main.py

install:
	uv sync -p 3.12
	docker compose build
	-mkdir sandbox_workspace
	cp -r calculator sandbox_workspace/calculator

# 	 stop the build if there are Python syntax errors or undefined names
#    exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
lint:
	uv run flake8 . --exclude ".venv ./sandbox_workspace" --count --select=E9,F63,F7,F82 --show-source --statistics
	uv run flake8 . --exclude ".venv ./sandbox_workspace" --count --exit-zero --max-complexity=15 --max-line-length=127 --statistics

test:
	uv run coverage erase
	uv run coverage run tests.py
	uv run coverage report

test_html:
	uv run coverage html

clean:
	-rm -rf .venv
	-docker compose down --rmi all --volumes --remove-orphans
	-docker rmi -f sandbox-exec
	-docker system prune -a --volumes --force
	-rm -rf sandbox_workspace/
	-rm -rf htmlcov
	-rm .coverage