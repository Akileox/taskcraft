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

## 확정 스코프 (2026-08-31 재검토 중 — 입대 2026-09-30 전후, 오늘 기준 약 4주)

**이 절은 2026-08-12부터 재검토 중이다.** 원래 스코프(BC vs DAgger vs PPO 비교)가
아래 최종 비전(embodiment-agnostic task representation)을 직접 검증하지 않는다는
문제를 확인했고(docs/position_paper.md 6절 Q9~Q12), 우선순위를 "간이
cross-embodiment 파일럿"(사람 시연 → world model → 형태가 다른 embodiment로 이식
검증)으로 옮기는 중이다. 2026-08-31에 한 번 더 조정했다 — 물리 로봇 키트는
배송/조립 리스크가 남은 기간(실질 4주)을 통째로 잡아먹을 수 있어 보류하고,
Minecraft 안에서 플레이어의 embodiment 자체를 바꾸는 방안(겉날개 비행 vs 보트
탑승, 겉날개가 잠정 우세)으로 대체했다(position_paper.md 6절 Q13~Q14). 세부 사항
(target embodiment, 검증 task)은 아직 미정 — 확정되는 대로 이 절을 다시 갱신한다.
World Model 코드화를 금지했던 아래 항목도 이 재검토로 무효화됐다(스코프 확장을
CLAUDE.md Don't 규정에 따라 사용자에게 확인받음, position_paper.md 6절 Q10 참고).

- (재검토 전 원래 스코프, 참고용으로 남김) 목표: 나무 → 작업대 → 돌곡괭이 →
  (가능하면) 철 채굴. 핵심 산출물: BC vs DAgger, BC vs PPO 비교 실험 + 리포트.
- (신규, 설계 중) 남은 기간 중 일부는 world model/cross-embodiment 이론을 블로그
  "[이론]" 시리즈(akileo-vault `04-Projects/taskcraft-theory-series.md` 큐 관리)로
  정리하는 데 쓰고, 남는 기간은 Minecraft 내 embodiment 교체 파일럿 설계·실행에
  쓴다.
- World Model / Cross-Embodiment: 이전엔 "코드화하지 않는다"였으나, 위 재검토로
  파일럿 규모로는 실제 구현 대상이 됐다. 다만 Genie 수준의 정식 world model
  학습은 남은 기간 1인 프로젝트로는 불가능하다고 보고, R3M/VIP처럼 이미 공개된
  embodiment-agnostic 표현을 얼린 채 갖다 쓰는 축소판을 현실적인 방향으로 잠정
  검토 중(확정 아님, position_paper.md 6절 Q12).

## 마일스톤 (날짜가 아니라 의존성 순서로 관리, 2026-08-31 재검토로 4번 이후 갱신 필요)
| 순서 | 마일스톤 | 완료 기준 |
|---|---|---|
| 1 | 환경/도구 세팅 | ✅ 완료 — MineRL이 Windows 네이티브에서 정상 실행됨 (환경 생성 + step 호출 성공). 상세: docs/research_notes/04 |
| 2 | Observation pipeline | ✅ 완료 — VPT/R3M/VIP/CLIP 4종 frozen encoder 설치 및 통합 인터페이스 완료(docs/research_notes/05) |
| 3 | [이론] 시리즈 (신규) | 미착수 — world model/cross-embodiment 개념, 큐: akileo-vault `04-Projects/taskcraft-theory-series.md` |
| 4 | 간이 cross-embodiment 파일럿 설계 (신규) | 설계 전 — target embodiment 선정(겉날개/보트, 겉날개 잠정 우세), 검증 task 확정, 최소 파이프라인 정의. [이론] 시리즈 마지막 편에서 구체화 예정 |
| 5 | 파일럿 실행 | 설계 완료 후 착수 |
| 6 | 정리 | 실험 리포트, 데모 영상, README/연구노트 마감 |

(참고: 이전 스코프의 BC baseline/DAgger 비교/PPO 비교 마일스톤은 보류됨 —
position_paper.md 4절/6절 Q9 참고. 재개 여부 미정.)

## 우선순위 논문 (paper-review skill로 docs/research_notes/에 정리)
상세 비교/차별점 분석은 docs/position_paper.md 3절 참고. 여기서는 목록만 관리.

### Minecraft 에이전트 계열 (같은 embodiment 안의 문제)
- **VPT (Video PreTraining)** — 인간 플레이 영상을 행동 정책으로 연결하는 방법.
  taskcraft의 BC baseline이 직접 참고하는 논문.
- **GROOT (Learning to Follow Instructions by Watching Gameplay Videos)** —
  게임플레이 영상을 목표(goal) 지시로 인코딩하는 Minecraft 전용 연구.
  **주의**: NVIDIA의 로봇 파운데이션 모델 "GR00T N1"과 이름만 비슷한 별개
  프로젝트다 (2026-07-21 정정, 아래 참고 항목 참고).
- **STEVE-1** — VPT와 동일 셋업(MineRL v1.0, Minecraft 1.16.5)을 쓰는
  instruction-following 에이전트. reproduce-baseline 대상 후보.
- **DreamerV3** — world model 기반 RL의 대표 구조. 이번 프로젝트에서 코드화는
  안 하지만, 개념 이해는 최종 비전과 직결되므로 정독 대상.
- **Voyager** — LLM 기반 장기 계획/자동 커리큘럼. Planning 확장 방향 참고용,
  우선순위 낮음.

### World model 기반 cross-embodiment 로봇 학습 계열
2026-07-21 추가. 최종 비전의 핵심 주장과 가장 직접적으로 비교해야 할
선행연구인데 원래 빠져 있었다. **이 영역은 비어있지 않다** — NVIDIA/ByteDance/
DeepMind가 2024~2025년에 이미 활발히 다루는 프론티어.
- **R3M / VIP** — 인간 영상 → 로봇 전이 가능한 시각 표현(R3M) / 시간적 진행도
  표현(VIP).
- **Genie (DeepMind, 2024)** — 라벨 없는 영상만으로 프레임 간 잠재 행동을
  비지도로 학습. 이 프로젝트와 메커니즘상 가장 가까움.
- **UniPi / UniSim** — 영상 생성 모델을 정책의 universal interface로 쓰는 접근.
- **DreamGen (NVIDIA, 2025)** — 영상 world model에서 로봇 행동을 얻는 두 방식
  (latent action model vs IDM)을 직접 비교. "공유 latent에 어떤 정보를 쓸
  것인가"를 이미 다루는 논문.
- **GR-1 → GR-2 (ByteDance)** — 대규모 영상 사전학습 + 로봇 파인튜닝.
- **Genie Envisioner (2025)** — 로봇 센싱·정책학습·평가를 하나의 영상 생성
  world model로 통합.
- **RT-X / Open X-Embodiment** — 여러 로봇 embodiment를 하나의 정책으로 묶는
  실제 사례. 다만 전부 팔+그리퍼류로 서로 닮은 집합.

### Morphology-conditioned / modular RL 계열
2026-07-21 추가. "공유 latent에서 embodiment별로 필요한 정보를 matching해서
추출한다"는 아이디어가 이미 연구된 갈래.
- **NerveNet (2018)** — 몸 구조를 그래프로 표현, GNN 정책으로 여러 형태에 대응.
- **MetaMorph (2022)** — 트랜스포머로 무작위 생성 로봇 형태 다수에 일반화.

### 참고: NVIDIA GR00T N1
로봇 파운데이션 모델(VLA, dual-system: VLM 추론 System2 + 디퓨전 트랜스포머
실행 System1). Minecraft GROOT와는 별개 프로젝트. N1(2025-03) → N1.5 → N1.6
→ N1.7(2026-04, 확인 시점 기준 최신)까지 갱신됨. arXiv:2503.14734

## 포지셔닝 문서
논문 이해 자체보다 "내 아이디어가 기존 연구와 어떻게 다른가"를 설명할 수 있는 게
더 중요하다는 판단(2026-07-21)에 따라, docs/position_paper.md에 이 프로젝트의
문제의식 · 선행연구 지형 · 아이디어의 차별점 · 파일럿 결과(성공/실패 무관) ·
다음 단계를 담은 글을 매주 갱신하며 쓴다. 실험(2026-08-12부터 간이
cross-embodiment 파일럿으로 재설계 중, 위 확정 스코프 절 참고)은 이 문서의
근거 자료로 취급한다 — 실험 자체가 아니라 이 문서가 입대 전 최종 산출물이다.

## 참고 결정 로그
- 환경 선택 근거 (MineRL vs MineDojo vs CraftGround): docs/research_notes/01_env_selection.md
- 설치 전략 (Docker vs WSL2 네이티브, 2026-07-14 이후 Windows 네이티브로 재결정):
  docs/research_notes/02_minerl_install_strategy.md, 03_wslg_gpu_incompatibility.md
- Frozen encoder(VPT/R3M/VIP/CLIP) 설치, GPU 커널 호환성, third_party 벤더링 방식:
  docs/research_notes/05_encoder_pipeline_setup.md