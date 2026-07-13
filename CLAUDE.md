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
- GPU passthrough 확인 (Docker, 참고용 — MineRL 자체는 Docker로 안 돌림): `docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi`
- (MineRL 설치/학습/평가 커맨드는 설치 완료 후 여기 추가)

## 환경 제약
- Windows + WSL2(Ubuntu), RTX 5060Ti 16GB
- MineRL은 WSL2에 직접 설치(Java JDK 8 + pip)하는 걸 기본으로 한다. Docker로
  실행하지 않는다 — 공식 유지보수 Docker 이미지가 없고, headless 대안(xvfb)이
  NVIDIA 드라이버와 충돌하는 사례가 많이 보고돼 있어, WSLg의 네이티브 디스플레이로
  우회 없이 실행하는 쪽이 더 안정적이다. 이유 상세: docs/research_notes/02_minerl_install_strategy.md
- Docker/GPU passthrough 자체는 검증 완료 상태로 남겨두고(docs/research_notes/00),
  나중에 재현성 패키징이 필요해지면(컴퓨터 이전 등) 그때 다시 활용한다
- VRAM 제약으로 풀 파인튜닝 대신 encoder freeze + policy head(또는 LoRA)만
  학습하는 걸 기본으로 한다
- MineRL v1.0 (Minecraft 1.16.5, MCP-Reborn) 고정 — VPT/GROOT/STEVE-1과 동일 셋업.
  버전 바꾸면 pretrained weight 호환성 깨짐

## Don't
- world_model/, planner/ 폴더를 미리 만들지 않는다 — 실제로 그 단계에 도달했을 때 생성
- checkpoint(.pth 등)나 데이터셋을 git에 커밋하지 않는다
- 실험 결과를 임의로 요약하지 않는다 — 원본 로그 수치 그대로 experiment_log에 기록
- 스코프 확장(cross-embodiment 코드화 등)이 필요해 보이면 먼저 사용자에게 알리고 확인받는다