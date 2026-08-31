## Project: taskcraft

연구 가설: 인간 시연 영상에서 신체 구조에 종속되지 않는 task representation을
추출하면, 형태가 다른 agent에도 재현 가능하다. Minecraft를 이 아이디어의
첫 testbed로 삼아, IL/RL 기법으로 long-horizon task(나무 → 작업대 → 철 채굴)를
푸는 에이전트를 만들며 기반을 검증한다.

최종 비전(cross-embodiment, world model 등)의 전체 맥락은 docs/roadmap.md 참고.
여기서는 반복하지 않는다.

## 확정 스코프 (2026-08-31 재검토 중 — 입대 2026-09-30 전후, 약 4주 남음)
아래는 원래 스코프였으나 2026-08-12에 재검토 시작, 2026-08-31에 한 번 더 조정.
상세 경위와 근거는 docs/position_paper.md 6절 Q9~Q15, docs/roadmap.md "확정 스코프"
참고 — 여기서는 반복하지 않는다.
- 우선순위를 "간이 cross-embodiment 파일럿"(사람 시연 → world model → Minecraft
  내 embodiment 교체로 이식 검증, 겉날개/보트 중 겉날개 잠정 우세)으로 옮기는 중.
  Target embodiment/검증 task는 아직 미정.
- 파일럿 설계 전에 world model/cross-embodiment 이론을 블로그 "[이론]" 시리즈
  (akileo-vault `04-Projects/taskcraft-theory-series.md` 큐 관리)로 먼저 정리한다.
- World Model / Cross-Embodiment: 이전엔 "코드 작성 안 함"이었으나 재검토로
  무효화됨 — 다만 Genie 수준 정식 구현이 아니라 R3M/VIP 같은 공개 표현을 얼린
  채 쓰는 축소판을 잠정 검토 중(확정 아님).
- (원래 스코프, 참고용) 나무 → 작업대 → 돌곡괭이 → 철 채굴, BC vs DAgger vs PPO
  비교. 재개 여부 미정.

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

## akileo-vault 연동
akileo(사용자)의 개인 지식 볼트는 별도 레포 `C:\KoreaUniv\projects\akileo-vault`
(WSL 경로: `/mnt/c/KoreaUniv/projects/akileo-vault`)에 있다. 이 레포와는 물리적으로
같은 디스크라 절대경로로 읽고 쓸 수 있지만, 이 CLAUDE.md는 taskcraft 작업 디렉토리
기준이라 볼트의 CLAUDE.md는 자동으로 로드되지 않는다.

- 볼트의 파일을 만지기 전에 반드시 `akileo-vault/CLAUDE.md`를 먼저 읽고 그 규칙(노트
  타입 `concept`/`note` 구분, MOC 링크 방식, 커밋 전 사용자 확인 등)을 따른다 —
  여기서 요약해두지 않는다, 원본이 바뀌면 사본은 썩는다.
- 지금 볼트에 열려있는 관련 노트 (2026-08-12 taskcraft 세션에서 해소, 노트 갱신 완료,
  2026-08-31에 embodiment 교체 방식으로 재조정):
  - `01-Notes/입대 전 진로 갈림길 - taskcraft 심화 vs 로보틱스.md` — 미결이던 질문에
    답이 나옴: 간이 cross-embodiment 파일럿(Minecraft 내 embodiment 교체) 채택.
  - `01-Notes/간이 Cross-Embodiment 검증 - 사람 데이터 World Model to 이종 로봇 키트.md`
    — 절충안이 실제 채택된 뒤, 2026-08-31에 target을 물리 로봇 키트에서 Minecraft
    내 embodiment로 다시 조정. (파일명은 최초 절충안 당시 그대로 유지, 내용만 갱신)
  - 신규: `04-Projects/taskcraft-theory-series.md`, `Templates/Theory Series
    Template.md` — 파일럿 설계 전에 먼저 진행하는 [이론] 블로그 시리즈.
- 볼트 노트는 바로 덮어쓰지 않는다 — 변경 초안을 먼저 보여주고 사용자 확인을 받은
  뒤에만 쓴다(볼트 CLAUDE.md의 확인 절차와 동일).