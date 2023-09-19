build:
	docker build -t mev-bot-app:latest -f docker/Dockerfile .

up:
	docker-compose -f docker/docker-compose.yaml up -d --build

down:
	docker-compose -f docker/docker-compose.yaml down

stop:
	docker-compose -f docker/docker-compose.yaml stop

restart:
	docker-compose -f docker/docker-compose.yaml down && docker-compose -f docker/docker-compose.yaml up -d --build

pytest:
	docker exec -it merchant-database bash -c 'psql -U mev-bot -d template1 -c "create extension if not exists hstore;"'
	docker exec -it merchant-app bash -c 'pytest -vv'

pytest-special:
	docker exec -it merchant-database bash -c 'psql -U mev-bot -d template1 -c "create extension if not exists hstore;"'
	docker exec -it merchant-app bash -c 'pytest -k $(arg)'

makemigrations:
	docker exec -it merchant-app bash -c 'alembic revision --autogenerate -m "$(arg)"'

migrate:
	docker exec -it merchant-app bash -c 'alembic upgrade head'

migrate-to:
	docker exec -it merchant-app bash -c 'alembic upgrade $(arg)'

enter:
	docker exec -it merchant-app bash

search-transaction:
	docker exec -it merchant-crypto-daemon bash -c 'python main_daemon.py -n $(n) -s $(s) -e $(e)'
