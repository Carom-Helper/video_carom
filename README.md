# video_carom

# 도커 컨테이너로부터 이미지 작성 (docker container commit)
```bash
docker container commit caromvideo_sz caromvideo_image
```
```bash
docker cinatainer commit [옵션] <컨테이너 식별자> [새로 만들 이미지명 :태그명]
```
- 지정할 수 있는 옵셥
|옵션|설명|
|------|---|---|
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
