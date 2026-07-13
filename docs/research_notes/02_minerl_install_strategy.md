# 02. MineRL 설치 방식: Docker vs WSL2 네이티브

## 배경/질문
00번 노트에서 Docker + WSL2 + GPU passthrough 세팅 자체는 검증을 마쳤다.
그다음 단계로 "MineRL을 Docker 컨테이너 안에서 돌릴 것인가, WSL2에 직접
설치할 것인가"를 결정해야 했다.

## 조사 결과
- minerllabs(MineRL 공식 저장소)는 Docker 이미지를 공식적으로 유지보수하지
  않는다. 검색되는 이미지(`manuelsh/minerl-docker`, `toddhen/minerl` 등)는
  모두 개인이 만든 서드파티 이미지이고, 최신 MineRL v1.0 기준으로
  업데이트됐는지 확인되지 않는다.
- 공식 설치 문서는 Docker가 아니라 "JDK 8 설치 + pip install"을 기본
  경로로 안내한다. WSL2에도 이 방식을 그대로 쓸 수 있다고 명시돼 있다.
- MineRL GitHub 이슈 여러 건(#68, #223, #224)에서, headless 환경에서
  가상 디스플레이(xvfb)를 쓸 때 NVIDIA 드라이버와 충돌하는 문제가 반복
  보고됐다. 공식 성능 팁 문서도 xvfb 사용 시 CPU 렌더링으로 2~3배
  느려진다고 명시한다.
- Windows 11의 WSL2는 WSLg 기능으로 WSL 안의 GUI 앱을 Windows 화면에
  직접 띄울 수 있다. 이 경우 xvfb 같은 가상 디스플레이 우회가 필요 없어,
  위에서 언급된 NVIDIA 드라이버 충돌 문제 자체를 피할 가능성이 있다.

## 결정: WSL2 네이티브 설치 (Docker 미사용)

### 이유
1. 신뢰할 수 있는 공식 Docker 이미지가 없다. 서드파티 이미지를 쓰면
   "Docker 문제인지 MineRL 설정 문제인지" 구분이 더 어려워질 수 있다.
2. 공식 문서 자체가 WSL2 네이티브 설치를 지원 경로로 명시한다 — 즉
   이 경로가 가장 많이 검증된 경로다.
3. WSLg를 활용하면 xvfb 우회 없이 실제 디스플레이로 실행할 수 있어,
   보고된 NVIDIA 드라이버 충돌 문제를 아예 피할 가능성이 있다.

### 트레이드오프로 포기한 것
- Docker의 재현성 이점(다른 컴퓨터에서 동일 환경 즉시 재현)은 지금 당장
  확보하지 못한다. 다만 이건 나중에 WSL2 네이티브 설치가 안정적으로
  작동하는 걸 확인한 뒤, 그 설정을 Dockerfile로 옮겨 pin하는 방식으로
  추후 확보 가능하다고 판단했다.
- 00번 노트에서 검증한 Docker + GPU passthrough 세팅은 이번 결정으로
  당장 쓰이진 않지만, 나중에 재현성 패키징이 필요해지면 그대로 재사용
  가능하다 (허비된 작업이 아님).

## 다음 확인할 것
- WSL2 안에서 MineRL 실행 시 WSLg를 통해 Minecraft 창이 실제로 뜨는지
- 만약 안 뜨면, 그때 xvfb 대안(또는 VirtualGL 조합)을 다시 검토

## 참고 자료
- MineRL 공식 설치 문서 (JDK 8 + pip install 경로)
- MineRL GitHub 이슈 #68, #223, #224 (xvfb-NVIDIA 드라이버 충돌 보고)
- MineRL 공식 성능 팁 문서 (xvfb 사용 시 렌더링 속도 저하 명시)