PROJECT_NAME := text-scrambler
IMAGE := $(PROJECT_NAME):latest
PORT ?= 8000

.PHONY: help build run shell logs stop ps test test-local collectstatic migrate createsuperuser clean

help:
	@echo "Targets:"
	@echo "  build           Build Docker image ($(IMAGE))"
	@echo "  run             Run app container bound to :$(PORT)"
	@echo "  shell           Open bash in running container"
	@echo "  logs            Tail app logs"
	@echo "  stop            Stop and remove app container"
	@echo "  ps              Show app container status"
	@echo "  test            Run Django tests inside container"
	@echo "  test-local      Run Django tests on host (requires venv)"
	@echo "  collectstatic   Collect static files"
	@echo "  migrate         Run database migrations"
	@echo "  createsuperuser Create Django superuser"
	@echo "  clean           Remove dangling images/containers"

build:
	docker build -t $(IMAGE) .

run: stop
	docker run -d --name $(PROJECT_NAME) \
	  -p $(PORT):8000 \
	  -e DJANGO_SETTINGS_MODULE=config.settings \
		  -e DJANGO_SECRET_KEY=$${DJANGO_SECRET_KEY:-dev-insecure-key} \
	  -e DEBUG=$${DEBUG:-True} \
	  -e ALLOWED_HOSTS=$${ALLOWED_HOSTS:-*} \
	  -e DATABASE_URL=$${DATABASE_URL:-sqlite:////app/db.sqlite3} \
	  $(IMAGE)
	@echo "App running on http://127.0.0.1:$(PORT)"

shell:
	docker exec -it $(PROJECT_NAME) bash || true

logs:
	docker logs -f $(PROJECT_NAME) | cat

stop:
	-@docker rm -f $(PROJECT_NAME) 2>/dev/null || true

ps:
	docker ps --filter name=$(PROJECT_NAME)

test: build stop
	docker run --rm --name $(PROJECT_NAME)-test \
	  -e DJANGO_SETTINGS_MODULE=config.settings \
		  -e DJANGO_SECRET_KEY=$${DJANGO_SECRET_KEY:-dev-insecure-key} \
	  -e DEBUG=True \
	  -e DATABASE_URL=sqlite:////app/db.sqlite3 \
	  $(IMAGE) sh -c "python manage.py test -v 2"

test-local:
	python manage.py test -v 2

collectstatic:
	docker exec -it $(PROJECT_NAME) python manage.py collectstatic --noinput

migrate:
	docker exec -it $(PROJECT_NAME) python manage.py migrate --noinput

createsuperuser:
	docker exec -it $(PROJECT_NAME) python manage.py createsuperuser

clean:
	-@docker image prune -f
	-@docker container prune -f


