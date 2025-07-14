build:
	docker build -t data_fetcher -f data_fetcher/Dockerfile .
	docker build -t frontend -f frontend/Dockerfile .
run:
	docker compose up