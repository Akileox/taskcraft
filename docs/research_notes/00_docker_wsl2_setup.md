# 00. Docker + WSL2 + GPU 세팅

## 목표/배경
MineRL은 Java 8, Malmo 네이티브 빌드 등 의존성이 예민해서 로컬에 직접 설치하면
버전 충돌 가능성이 높다. Docker로 실행 환경을 통째로 고정해서 이 문제를 피하고,
동시에 재현성(나중에 다른 컴퓨터/OS에서도 동일 환경을 다시 만들 수 있음)을
확보하는 것이 목표다.

## 핵심 개념
- **Image**: 프로그램 실행에 필요한 OS, 라이브러리, 설정을 통째로 박제해놓은
  읽기 전용 템플릿. 클래스에 비유하면 이해가 빠르지만, 정확히는 "실행 환경의
  스냅샷"이다.
- **Container**: image를 실제로 실행한 상태. 하나의 image로 여러 container를
  독립적으로 띄울 수 있다.
- **WSL2 (Windows Subsystem for Linux 2)**: Windows 안에서 리눅스 커널을
  가상화해서 돌리는 기능. MineRL 등 리눅스 기반 도구를 Windows에서 쓰기 위해 필요.
- **Docker Desktop의 WSL2 backend**: Docker가 WSL2 위에서 동작하도록 하는 설정.
  이걸 켜야 WSL2 터미널 안에서 `docker` 명령어를 쓸 수 있다.

## 진행 과정

### 1. WSL2 + Docker Desktop 설치
- PowerShell(관리자 권한)에서 `wsl --install`로 WSL2 + Ubuntu 설치
- Docker Desktop 설치 시 "Use WSL 2 based engine" 옵션 체크
- Docker Desktop → Settings → Resources → WSL Integration에서 사용 중인
  distro(Ubuntu) 토글 켬

### 2. GPU 인식 테스트 — 첫 번째 에러
명령어:
```
docker run --rm --gpus all nvidia/smi
```
에러:
```
The command 'docker' could not be found in this WSL 2 distro.
We recommend to activate the WSL integration in Docker Desktop settings.
```
원인: Docker Desktop이 실행 중이 아니었거나, WSL Integration 설정이 아직
반영되지 않은 상태였음.
해결: Docker Desktop 앱을 완전히 실행한 상태로 두고, WSL 터미널을 완전히
껐다가 재시작.

### 3. 두 번째 에러 — permission denied
에러:
```
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```
원인: WSL Integration을 켠 직후 소켓이 아직 제대로 반영되지 않은 상태.
해결: PowerShell(관리자 권한)에서 `wsl --shutdown`으로 WSL을 완전히 종료 후
재시작. (참고: 이 방법으로 안 되면 `sudo usermod -aG docker $USER` 후
WSL 창을 완전히 재시작하는 방법도 있음 — 이번엔 필요 없었음)

### 4. 세 번째 에러 — 잘못된 이미지 이름
명령어:
```
docker run --rm --gpus all nvidia/smi
```
에러:
```
Unable to find image 'nvidia/smi:latest' locally
docker: Error response from daemon: pull access denied for nvidia/smi,
repository does not exist or may require 'docker login'
```
원인: `nvidia/smi`는 존재하지 않는 이미지 이름. `nvidia-smi`는 이미지가
아니라 컨테이너 안에서 실행할 명령어인데, 이미지명 없이 명령어만 써서 발생.
해결: 올바른 CUDA 베이스 이미지를 지정하고, 그 안에서 `nvidia-smi`를 실행하도록 수정.
```
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

## 최종 확인
위 명령어 실행 결과, RTX 5060Ti(16GB VRAM), 드라이버 정상 인식 확인.
`docker run --rm --gpus all`로 컨테이너 안에서 호스트 GPU에 정상 접근 가능함을 검증.

## 다음에 참고할 점
- `docker` 명령어가 아예 안 먹히면: Docker Desktop 실행 여부 + WSL Integration
  설정부터 확인
- permission denied가 뜨면: `wsl --shutdown` 후 재시작이 첫 번째 시도할 것
- 이미지 이름이 헷갈리면: Docker Hub에서 정확한 이미지명을 먼저 검색 후 사용