# 01. Minecraft 시뮬레이션 환경 선택

## 배경/질문
Minecraft 기반 RL/IL 실험을 하려면 시뮬레이션 환경(에이전트가 실제로 상호작용하는
인터페이스)을 먼저 골라야 한다. 이 프로젝트는 VPT(OpenAI)의 공개 pretrained
정책과 BASALT 인간 시연 데이터를 재사용할 계획이므로, 이 데이터/모델과 호환되는
환경인지가 선택의 핵심 기준이다.

## 후보
- **MineRL v1.0**: Malmo를 fork한 시뮬레이터. VPT, GROOT, STEVE-1 등 최신 논문이
  표준으로 사용. 사람 플레이어와 동일한 관측(RGB 화면)/행동(마우스+키보드,
  GUI 조작 포함) 공간을 사용한다.
- **MineDojo**: MineRL과 별개로 개발된 프레임워크. 73만 개 이상의 유튜브 영상,
  위키, 레딧 데이터를 함께 제공하고, MineCLIP이라는 비디오-텍스트 인코더로
  리워드를 자동 생성할 수 있다. 크래프팅이 저수준 GUI 조작 없이 고수준 명령
  하나로 성공하도록 단순화되어 있다.
- **CraftGround**: Fabric 기반으로 새로 만들어진 시뮬레이터. 특정 시나리오에서
  Malmo 계열 대비 최대 2.79배 빠른 시뮬레이션 속도를 보인다. 아직 크래프팅
  기능 자체가 구현되어 있지 않고, 활발히 개발 중인 신생 프로젝트다.

## 비교

| 항목 | MineRL v1.0 | MineDojo | CraftGround |
|---|---|---|---|
| 기반 | Malmo fork | Malmo 기반 확장 | Fabric 신규 구현 |
| 액션/관측 공간 | 사람과 동일 (GUI 크래프팅 포함) | 고수준으로 단순화 (크래프팅 자동 성공) | 크래프팅 미구현 |
| VPT/GROOT/STEVE-1 호환 | 호환 (동일 셋업, Minecraft 1.16.5 + MCP-Reborn) | 액션 공간이 달라 pretrained policy 재사용 불가 | API가 Malmo 계열과 완전히 다름, 크래프팅 없어 목표 태스크 수행 불가 |
| 데이터셋 | BASALT 인간 시연 데이터 (Zenodo 미러) | 대규모 유튜브/위키/레딧 자동 수집 데이터 | 별도 대규모 데이터셋 없음 |
| 속도 | 상대적으로 느림 (Malmo 상속) | MineRL과 비슷 | 최대 2.79배 빠름 (일부 시나리오) |
| 성숙도 | 가장 오래되고 널리 쓰임 | 활발, NeurIPS Outstanding Paper 수상 | 신생, 문서/안정성 부족 가능 |

## 최종 선택: MineRL v1.0

### 이유
1. 이 프로젝트가 참고하는 핵심 논문(VPT, GROOT, STEVE-1)이 전부 동일한 셋업
   (MineRL v1.0 + Minecraft 1.16.5 + MCP-Reborn)을 쓴다. 관측/행동 공간을
   사람 플레이어와 일치시켜야 사람 시연 데이터 및 pretrained 정책과 호환되기
   때문이다.
2. VPT의 pretrained encoder/policy를 재사용해서 GPU 자원(RTX 5060Ti 16GB)
   제약 안에서 학습 시간을 줄이려는 계획과 직접 연결된다. MineDojo나
   CraftGround를 쓰면 이 재사용 자체가 불가능해진다.
3. BASALT 데이터셋으로 바로 Behavior Cloning을 시작할 수 있다.

### 트레이드오프로 포기한 것
- MineDojo의 대규모 언어-비디오 데이터와 MineCLIP 리워드 모델은 쓸 수 없다.
  다만 이번 프로젝트 목표(작업대~철 채굴)는 sparse reward를 직접 설계하거나
  BC/DAgger로 우회 가능해서, 지금 단계에서는 큰 손실이 아니라고 판단했다.
- CraftGround의 속도 이점은 포기한다. 다만 크래프팅이 아직 없어서 애초에
  이번 목표 태스크 수행이 불가능하므로 선택지에서 제외된 것에 가깝다.

## 참고 자료
- GROOT 논문: MineRL 1.16.5 + MCP-Reborn 셋업을 VPT, STEVE-1과 동일하게 사용한다고 명시
- MinecraftEnv(CraftGround 기반) 저장소: 크래프팅 미구현 명시
- CraftGround 논문(2026): Malmo 대비 최대 2.79배 속도 향상 보고
- MineDojo 공식 문서/저장소: 태스크 수, 데이터셋 규모, MineCLIP 설명