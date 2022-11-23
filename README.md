# video_carom

# 도커 컨테이너 image 추출
```bash
docker commit caromvideo_sz caromvideo_image
```
```bash
docker commit '컨테이너이름' '새로 만들이미지 이름'
```
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

- tar 파일 생성 확인
```
ls
```

- 도커 이미지 파일 로드
```bash
docker load -i caromvideo.tar
```
```
docker image ls
```

- 도커 컨테이너 생성
```
docker run caromvideo
```

- 도커 로드
```
# 이미지 로드
docker load [옵션] [파일명]
docker load -i baseimage.tar
```
