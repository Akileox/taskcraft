# taskcraft Roadmap

## 최종 비전
인간의 시연 영상에서 신체 구조(embodiment)에 종속되지 않는 task representation을
추출하면, 형태가 다른 agent에도 이식할 수 있는가? — 이 질문이 장기 연구 목표다.
Latent World Model을 매개로 삼아 사람 시연 → 다른 형태의 로봇으로 과제를
재현하는 것(Morphology-Agnostic Imitation from Human Video via Latent World Models)이
최종적으로 다루고 싶은 문제다.

taskcraft는 이 아이디어의 첫 검증대다. Minecraft를 testbed로 골랐는데, long-horizon
task(나무 → 도구 제작 → 채굴)가 사람이 하는 도구 사용/제어의 축소판이면서도
비교적 통제 가능한 환경이기 때문이다.

## 확정 스코프 (10주, ~2026-09 입대 전 완료)
- 목표: 나무 → 작업대 → 돌곡괭이 → (가능하면) 철 채굴
- 핵심 산출물: 같은 서브태스크에서 BC vs DAgger, BC vs PPO 비교 실험 + 리포트
- stretch (시간 남을 때만): 다이아 채굴 진입
- World Model / Planning / Cross-Embodiment: 이번 프로젝트에서 코드화하지 않는다.
  아이디어와 이유는 이 문서에만 기록하고, 실제 구현은 복학 후 랩 합류 시점에
  다시 판단한다.

## 마일스톤 (날짜가 아니라 의존성 순서로 관리)
| 순서 | 마일스톤 | 완료 기준 |
|---|---|---|
| 1 | 환경/도구 세팅 | ✅ 완료 — MineRL이 Windows 네이티브에서 정상 실행됨 (환경 생성 + step 호출 성공). 상세: docs/research_notes/04 |
| 2 | Observation pipeline | DINO 등으로 RGB → feature 추출, 시각화로 sanity check 완료 |
| 3 | BC baseline | 나무 캐기~작업대까지 정성적으로 안정적으로 성공 |
| 4 | DAgger 비교 | BC 대비 distribution shift 완화 효과를 정량적으로 비교 |
| 5 | PPO 비교 | VRAM 제약 안에서(encoder freeze) IL 대비 개선 여부 확인 |
| 6 | 분기점 판단 | 철 채굴까지 안정적이면 다이아 도전, 아니면 정리 단계로 전환 |
| 7 | 정리 | 실험 리포트, 데모 영상, README/연구노트 마감 |

## 우선순위 논문 (paper-review skill로 docs/research_notes/에 정리)
- **VPT (Video PreTraining)** — 인간 플레이 영상을 행동 정책으로 연결하는 방법.
  taskcraft의 BC baseline이 직접 참고하는 논문.
- **GROOT N1** — VLA(Vision-Language-Action) 구조. dual-system 아키텍처가
  최종 비전(morphology-agnostic latent)의 아이디어 원류.
- **STEVE-1** — VPT와 동일 셋업(MineRL v1.0, Minecraft 1.16.5)을 쓰는
  instruction-following 에이전트. reproduce-baseline 대상 후보.
- **DreamerV3** — world model 기반 RL의 대표 구조. 이번 프로젝트에서 코드화는
  안 하지만, 개념 이해는 최종 비전과 직결되므로 정독 대상.
- **Voyager** — LLM 기반 장기 계획/자동 커리큘럼. Planning 확장 방향 참고용.

## 참고 결정 로그
- 환경 선택 근거 (MineRL vs MineDojo vs CraftGround): docs/research_notes/01_env_selection.md
- 설치 전략 (Docker vs WSL2 네이티브, 2026-07-14 이후 Windows 네이티브로 재결정):
  docs/research_notes/02_minerl_install_strategy.md, 03_wslg_gpu_incompatibility.md