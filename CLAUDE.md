## Project: taskcraft

연구 가설: 인간 시연 영상에서 신체 구조에 종속되지 않는 task representation을
추출하면, 형태가 다른 agent에도 재현 가능하다. Minecraft를 이 아이디어의
첫 testbed로 삼아, IL/RL 기법으로 long-horizon task(나무 → 작업대 → 철 채굴)를
푸는 에이전트를 만들며 기반을 검증한다.

최종 비전(cross-embodiment, world model 등)의 전체 맥락은 docs/roadmap.md 참고.
여기서는 반복하지 않는다.

## 확정 스코프 (10주, 2026-09 입대 전 완료)
- 목표: 나무 → 작업대 → 돌곡괭이 → (가능하면) 철 채굴
- 핵심 산출물: 같은 서브태스크에서 BC vs DAgger, BC vs PPO 비교 실험 + 리포트
- stretch: 다이아 채굴 진입 (시간 남을 때만)
- World Model / Planning / Cross-Embodiment: 코드 작성 안 함, 아이디어만 roadmap에 기록

## Repo layout
- src/env/       — MineRL wrapper
- src/vision/    — DINO 등 observation pipeline
- src/policy/    — BC/DAgger/PPO 구현
- src/utils/     — 공통 유틸리티
- configs/       — 실험 설정 (yaml). 실험은 항상 여기서 시작
- docs/roadmap.md          — 최종 비전 + 10주 로드맵
- docs/experiment_log.md   — 실험 기록 누적본 (append-only)
- docs/research_notes/     — 논문별 정리

## Commands
- Java 버전 확인 (JDK 8 필요, `1.8.x` 출력돼야 함): `java -version`
- venv activate: `.\.venv\Scripts\Activate.ps1`
- MineRL v1.0 설치: PyPI에 없음, GitHub에서 직접 설치해야 하고 Windows에서는
  공식 소스를 그대로 pip install하면 실패한다 (긴 경로 + gradlew.bat 서브프로세스
  버그 + 창 리사이즈 hang, 총 3곳 패치 필요). 전체 절차와 패치 diff는
  docs/research_notes/04_windows_native_setup_and_smoke_test.md 참고.
  `git config --global core.longpaths true`가 먼저 필요.
- MineRL env smoke test: `gym.make("MineRLTreechop-v0")` → `env.reset()` →
  `env.step()` 확인. 창은 의도적으로 안 보이게 뜬다(GLFW_VISIBLE=false) —
  정상 동작이며, 관측은 `obs['pov']`(64x64x3 RGB)로 직접 받는다.

## 환경 제약
- **Windows 네이티브** (WSL2 아님), RTX 5060Ti 16GB. Python 3.9 venv + JDK 8을
  Windows에 직접 설치해서 사용한다.
- WSL2는 이 프로젝트에서 사용하지 않는다 — WSLg의 GUI compositor가 이 GPU/드라이버
  조합(RTX 5060Ti + driver 610.x)에서 OpenGL(GLX) 컨텍스트 생성에 실패해 Minecraft
  클라이언트가 기동하지 못함(`xeyes` 등 순수 X11 앱도 동일하게 실패, CUDA 연산
  자체는 정상). 이전 프로젝트(Isaac Sim)에서도 동일 GPU에서 WSL 안 Vulkan
  렌더링이 막혔던 적이 있고, 그때도 네이티브 Windows 전환으로 해결됨. 상세 경위:
  docs/research_notes/02_minerl_install_strategy.md, 03_wslg_gpu_incompatibility.md
- Docker/GPU passthrough 검증(docs/research_notes/00)은 WSL2 기준이라 이번
  스코프에서는 참고용으로만 남겨둔다
- VRAM 제약으로 풀 파인튜닝 대신 encoder freeze + policy head(또는 LoRA)만
  학습하는 걸 기본으로 한다
- MineRL v1.0 (Minecraft 1.16.5, MCP-Reborn) 고정 — VPT/GROOT/STEVE-1과 동일 셋업.
  버전 바꾸면 pretrained weight 호환성 깨짐

## Don't
- world_model/, planner/ 폴더를 미리 만들지 않는다 — 실제로 그 단계에 도달했을 때 생성
- checkpoint(.pth 등)나 데이터셋을 git에 커밋하지 않는다
- 실험 결과를 임의로 요약하지 않는다 — 원본 로그 수치 그대로 experiment_log에 기록
- 스코프 확장(cross-embodiment 코드화 등)이 필요해 보이면 먼저 사용자에게 알리고 확인받는다