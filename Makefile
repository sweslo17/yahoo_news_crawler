VERSION := $(shell git rev-parse --short HEAD)
UPDATED_DATE := $(shell git log -1 --format=%cd --date=format:%Y%m%d)

BUILD_DOCKER = IMAGE_TAG=$(VERSION)-$(UPDATED_DATE) docker-compose -f docker-compose.yml

.PHONY: build push pull down test test-only

build:
	$(BUILD_DOCKER) build

push:
	$(BUILD_DOCKER) push

pull:
	$(BUILD_DOCKER) pull

down:
	$(BUILD_DOCKER) down

run:
	$(BUILD_DOCKER) up -d
