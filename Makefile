run:
	docker compose run --rm sandbox_executor python calculator/main.py

install:
	docker compose build
	-mkdir sandbox_workspace
	cp -r calculator sandbox_workspace/calculator

clean:
	-rm -rf .venv
	-docker compose down --rmi all --volumes --remove-orphans
	-docker rmi -f sandbox-exec
	-docker system prune -a --volumes --force
	-rm -rf sandbox_workspace/