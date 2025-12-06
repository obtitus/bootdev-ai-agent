run:
	docker compose run --rm sandbox_executor python calculator/main.py

install:
	docker compose build
	cp -r calculator sandbox_workspace/