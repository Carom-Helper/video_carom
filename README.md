# video_carom

# How to install
```
git clone 
cd Carom-API-Server
git submodule update --init --recursive
cd src/detect/npu_yolo/utils/box_decode/cbox_decode
python setup.py build_ext --inplace
cd ../../../../../../
```

# 도커 컨테이너로부터 이미지 작성 (docker container commit)
```bash
docker container commit caromvideo_sz caromvideo_image
```
```bash
docker cinatainer commit [옵션] <컨테이너 식별자> [새로 만들 이미지명 :태그명]
```

|옵션|설명|
|------|---|
|--author, -a| 작성자 지정(ex: sz(sz@gmail.com))|
|--message, -m| 메시지 지정|
|--change, -c| commit 시, Dockerfile 명령 지정|
|--pause, -p| 컨테이너를 일시정지하고 commit|

- 도커 이미지 확인
```
docker image ls

REPOSITORY                                                                            TAG                          IMAGE ID       CREATED              SIZE
caromvideo_image                                                                      latest                       3cd559ba4ccf   About a minute ago   4.14GB

```
- tar 파일 생성
```bash
docker save -o caromvideo.tar caromvideo_image
```
```
docker save -o 파일_이름.tar 이미지_이름
```

# 도커 이미지 파일 로드
```bash
docker load -i caromvideo.tar
```

- 도커 이미지 확인
```
docker image ls
```

- 도커 컨테이너 생성
```
docker run caromvideo
```

# 도커 로드
```
# 이미지 로드
docker load [옵션] [파일명]
docker load -i baseimage.tar
```

# USB CP 하기
```
# USB 메모리 Device 정보 확인, USB 메모리의 디렉토리 경로 확인 가능
$ sudo fdisk -l

# USB 메모리 인식시키기 mount 경로 '/media/usb'생성
$ mkdir /media/usb

# USB 파일시스템이 fat 일 경우에는 아래와 같은 옵션 
$ sudo mount -t vfat /dev/sdb1 /media/usb

# USB 파일시스템이 ntfs 일 경우
$ sudo mount -t ntfs-3g /dev/sdb1 /media/usb

# mount 경로 '/media/usb' 디렉토리 내용 조회해보면, USB 메모리에 넣어준 파일 확인 가능
$ ls /media/usb

# /media/usb/ 디렉토리에 존재하는 폴더를 현재 디렉토리에 복사
$ cp -r /dev/sdb1/폴더명 /옮길디렉토리명

# 옮길 파일을 디렉토리로 보존 복사
$ cp -p /dev/sdb1 /media/usb 

# USB 마운트 
$ sudo umount /dev/sdb1

# 확인
$ df -h
```
