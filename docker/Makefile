IMAGE_NAME = my-python-app
CONTAINER_NAME = my-running-app

.PHONY: all build run clean

all: build run

build:
	@echo building image:
	docker build -t $(IMAGE_NAME) .

run:
	@echo running container:
	docker run -it --rm --name $(CONTAINER_NAME) -p 5000:5000 $(IMAGE_NAME)

clean:
	docker rmi $(IMAGE_NAME)
