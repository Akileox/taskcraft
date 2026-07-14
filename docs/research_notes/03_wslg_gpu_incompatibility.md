# 03. WSL2/WSLg에서 MineRL 실행 실패 → Windows 네이티브 전환

## 배경/질문
02번 노트에서 "WSL2 네이티브 설치(Docker 미사용)"로 결정하고 JDK 8 + Python 3.9
venv + `pip install git+https://github.com/minerllabs/minerl` 설치까지는 문제
없이 끝났다. 마일스톤 1의 완료 기준(env 생성 + step 호출 성공)을 확인하기 위해
`MineRLTreechop-v0` env로 smoke test를 돌렸는데, `env.reset()` 단계에서 Minecraft
클라이언트(MCP-Reborn)가 기동 직후 크래시했다.

## 관찰된 증상
- 크래시 로그 핵심: `java.lang.IllegalStateException: Failed to initialize GLFW,
  errors: GLFW error during init: [0x10008]` (GLFW 에러 코드 0x10008 =
  `GLFW_PLATFORM_ERROR`), `Backend API: NO CONTEXT`
- 진단 결과 `$DISPLAY`, `$WAYLAND_DISPLAY` 둘 다 빈 값, `/mnt/wslg/run/user/1000/`
  디렉토리가 `root:root` 소유의 빈 디렉토리(정상적으로는 로그인 사용자 소유여야 함)
- Minecraft만의 문제인지 확인하기 위해 `x11-apps`의 `xeyes`를 실행 → 동일하게
  `Error: Can't open display:`로 실패. 즉 Minecraft/LWJGL에 국한된 문제가 아니라
  **WSLg의 GUI compositor(X11/Wayland 서버) 자체가 이 세션에 대해 전혀 뜨지
  않는 상태**였다.
- 컴퓨터 전체 재부팅 후에도 동일하게 재현됨 (일시적 세션 문제가 아님)
- `/etc/wsl.conf`의 `systemd=true` → `systemd=false` 전환 후 재시작해도 동일
  (오히려 `/mnt/wslg/run/user/1000/` 디렉토리 자체가 사라짐) → systemd은
  원인이 아님을 확인하고 `systemd=true`로 원복
- 한편 `nvidia-smi`, 그리고 00번 노트에서 검증한 `docker run --gpus all ...
  nvidia-smi`는 정상 동작 (드라이버 610.62, RTX 5060Ti 16GB 정상 인식,
  CUDA Version 13.3 표시). 즉 **CUDA 연산 경로는 정상, GPU 가속 GUI 렌더링
  경로만 실패**하는 비대칭적인 증상.

## 원인 분석 (확정은 아니고 정황 근거)
- WSLg의 GUI compositor(weston)는 Direct3D12/WDDM 기반 가상 GPU 경로를 통해
  호스트 NVIDIA 드라이버와 통신한다. 이 경로는 CUDA 연산이 쓰는 드라이버
  인터페이스와 별개다 — 하나가 되고 하나가 안 되는 게 기술적으로 모순이 아니다.
- RTX 5060Ti는 최신 GPU(50시리즈)라서, WSL의 GPU 가상화(D3D12/WDDM) 경로에 대한
  드라이버 지원이 CUDA 연산 경로만큼 성숙하지 않았을 가능성이 있다.
- 이전 프로젝트(Isaac Sim, Omniverse RTX 렌더러 — Vulkan 기반)에서도 동일 GPU로
  WSL 안에서 렌더링(Vulkan) 관련 문제가 있었고, 그때도 네이티브 Windows 전환으로
  해결되었다는 사용자 보고가 있음. 두 사례(OpenGL/GLX, Vulkan) 모두 "WSL의
  가상화된 그래픽 스택"이라는 공통점이 있어, 이 GPU/드라이버 조합에서 WSL
  가상 GPU 디스플레이 경로 자체가 불안정하다고 잠정 결론.

## 결정: Windows 네이티브로 전환 (WSL2 미사용)

### 이유
1. 크래시 지점이 정확히 GLX(X11 위의 OpenGL) 컨텍스트 생성이었다. 네이티브
   Windows에서는 Minecraft/LWJGL이 WGL(Windows 고유 OpenGL 인터페이스)로 NVIDIA
   드라이버와 직접 통신하므로, 지금 실패한 WSLg 가상화 경로 자체를 완전히
   우회한다.
2. 같은 GPU에서 이미 한 번(Isaac Sim) 네이티브 Windows 전환으로 해결된 전례가
   있어 재현 가능성이 낮지 않다고 판단.
3. WSLg 자체를 더 파는 것은 페이오프가 불확실하고, 10주 스코프 예산을
   소모한다.

### 트레이드오프로 포기한 것
- 리눅스 툴체인(apt 기반 패키지 관리, 기존에 검증한 JDK8+venv 설치 절차)을
  그대로 못 쓰고 Windows에서 동일한 걸 다시 세팅해야 함
- 00번 노트에서 검증한 Docker+WSL2 GPU passthrough는 이번 스코프에서는
  쓰이지 않음 (참고용으로만 남김)

## 다음 확인할 것
- Windows 네이티브에서 Python 3.9 + JDK 8 + MineRL 설치가 문제없이 되는지
- 같은 smoke test(`MineRLTreechop-v0`, reset + step 20회)가 창을 띄우고
  정상 종료하는지

## 참고 자료
- MineRL GitHub 이슈 #68, #223, #224 (xvfb-NVIDIA 드라이버 충돌 — 이번 사례와는
  다른 증상이지만 "가상 디스플레이 경로 + NVIDIA 드라이버" 조합이 문제가 되는
  선례로 참고)
- 사용자 사전 경험: Isaac Sim(Omniverse RTX 렌더러) on WSL2 + RTX 5060Ti에서
  Vulkan 렌더링 실패 → 네이티브 Windows 전환으로 해결
