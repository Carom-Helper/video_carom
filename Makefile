USR=sz
SRC_NAME=caromvideo
APP_NAME=${SRC_NAME}_${USR}
IMAGE_NAME=${SRC_NAME}_image
TARGET_PATH=`pwd`
MODEL_VOLUME = ${TARGET_PATH}:/$(SRC_NAME)
 
# Build and run the container
build:
	@echo "====<VIDEO_TARGET_PATH=${VIDEO_TARGET_PATH}>==="
	@echo 'docker image build'
	docker image build --build-arg fname=$(SRC_NAME) -t $(IMAGE_NAME) .

run:
	@echo 'docker run -tiu --name="$(APP_NAME)" $(IMAGE_NAME)'
	docker run -ti --name "$(APP_NAME)" --shm-size 32gb --privileged -v $(MODEL_VOLUME) $(IMAGE_NAME)

stop:
	@echo 'stop docker $(APP_NAME)'
	docker stop $(APP_NAME)
start :
	docker start $(APP_NAME)
exec :
	docker exec -it $(APP_NAME)
attach:
	docker start $(APP_NAME)
	docker attach $(APP_NAME)
rm:
	@echo 'rm docker $(APP_NAME)'
	docker rm -f $(APP_NAME)

rmi:
	@echo 'rmi docker $(IMAGE_NAME)'
	docker rmi $(IMAGE_NAME)