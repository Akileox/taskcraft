# SimWAM 리뷰 — taskcraft 관점에서

## 이 논문이 서 있는 자리

SimWAM은 자율주행이라는 단일 embodiment 안에서 "미래를 상상하고 행동한다(Imagine-Then-Act)"는 World-Action Model의 표준 파이프라인을 깨는 논문이다. Video DiT와 Action DiT를 공동 학습시키되 Isolated Attention Mask로 행동 토큰이 미래 비디오 토큰을 참조하지 못하게 막아, 학습 시에는 비디오 생성 모델이 가진 교통 역학 사전지식을 행동 전문가에게 흘려주고 추론 시에는 비디오 분기를 통째로 버린다. 결과적으로 지연시간을 4분의 1 이하로 줄이면서도 NAVSIM PDMS 91.5라는 최상위 성능을 유지한다. 이 구조는 "세계 모델의 지식을 학습 때 흡수시키고 배포 때는 가벼운 정책만 남긴다"는 태스크로, taskcraft가 latent world model을 매개로 하려는 것과 표면적으로 닮아 있다.

## taskcraft와의 핵심 차이

가장 중요한 차이는 SimWAM이 다루는 것이 embodiment 내부의 모달리티 분리이고, taskcraft가 다루는 것은 embodiment 간 표현 이식이라는 점이다. SimWAM의 Video DiT와 Action DiT는 같은 차량, 같은 카메라 시점, 같은 행동 공간(궤적 웨이포인트)을 공유한다. 즉 관측과 행동이 이미 동일한 좌표계와 시간축 위에 정렬되어 있고, Isolated Attention Mask가 하는 일은 그 정렬된 두 흐름 사이에서 "미래 정보 누출을 막는 것" 하나뿐이다. taskcraft가 풀어야 하는 문제는 그보다 한 단계 더 어렵다. 사람 손의 시연 영상과 로봇(혹은 MineRL 에이전트)의 행동 공간은 관측 시점도, 자유도도, 시간 스케일도 다르다. 따라서 taskcraft의 latent는 단순히 "미래를 못 보게 막힌 현재 표현"이 아니라 "특정 몸의 좌표계에서 벗어난 태스크 표현"이어야 한다. SimWAM은 embodiment-agnostic한 표현을 만들 필요가 전혀 없다 — 애초에 하나의 embodiment만 다루기 때문이다. 이 점에서 SimWAM의 성공은 taskcraft가 상정하는 어려움(embodiment gap)을 우회한 결과이지, 그 어려움을 해결한 결과가 아니다.

또 하나 짚어야 할 차이는 지식이 흐르는 방향이다. SimWAM에서는 Video DiT(교사 역할에 가까움)에서 Action DiT로 사전지식이 전이되지만, 둘은 같은 학습 데이터(같은 주행 로그)로부터 동시에 학습되는 co-training 구조이지 별도의 사전학습된 인간 시연 표현을 다른 몸에 전이하는 구조가 아니다. taskcraft는 반대로 사람 시연이라는 하나의 소스에서 학습된 latent를 전혀 다른 학습 곡선을 가진 여러 타깃 embodiment로 재사용해야 하므로, 소스와 타깃의 데이터 분포가 근본적으로 다르다는 문제(distribution shift, 그것도 embodiment 축에서의 shift)를 안고 있다. SimWAM 논문에는 이런 shift가 없다.

## taskcraft가 가져다 쓸 수 있는 부분

Isolated Attention Mask라는 구체적 메커니즘은 taskcraft의 latent leakage 문제에 직접 참고할 수 있다. taskcraft에서 걱정해야 할 것은, latent world model이 embodiment-specific 디코더(정책)를 학습시키는 과정에서 인간 손의 형태나 시점 같은 embodiment-specific 저수준 정보까지 흡수해버려 다른 몸으로 전이할 때 오염이 생기는 것이다. SimWAM처럼 "미래 토큰이 현재 관측 토큰만 참조하도록" 마스킹을 거는 대신, taskcraft에서는 "embodiment-specific 디코더가 latent의 특정 서브스페이스만 참조하도록" 하는 방식으로 변형해볼 수 있다. 즉 attention mask 대신 정보 병목(information bottleneck)이나 gradient reversal 같은 장치로 대체하더라도, "학습 신호는 공유하되 표현 접근은 구조적으로 차단한다"는 설계 철학 자체는 그대로 가져올 만하다.

또한 co-training으로 별도의 distillation 단계 없이 지식 전이를 끝내는 방식도 참고할 가치가 있다. taskcraft가 BC/DAgger/PPO 세 파이프라인을 비교하는 지금 스코프에서, latent world model을 먼저 사전학습하고 그 다음 각 정책 학습 방법을 순차적으로 붙이는 2단계 구조보다는, latent 표현과 정책을 (마스크된 attention 등으로) 동시에 학습시켜 표현이 정책 학습 신호에 맞춰 자연스럽게 조정되게 하는 편이 실험적으로 더 깨끗한 비교가 될 수 있다. 다만 이는 세 정책 학습 방법 사이에서 latent 표현이 서로 다르게 편향될 위험도 만들기 때문에, 비교 실험 설계 시 이 co-training 여부를 통제 변수로 명시할 필요가 있다.

지연시간 대 성능 트레이드오프를 보여주는 Figure 1의 실험 설계 방식, 즉 "무거운 세계 모델 분기를 완전히 제거했을 때 성능이 얼마나 유지되는가"를 정량화하는 축은 taskcraft의 최종 평가에도 그대로 옮겨올 수 있다. taskcraft에서도 latent world model을 추론 시 유지하는 버전과 distill 후 제거하는 경량 버전을 비교하는 ablation이 유용할 것이다.

## taskcraft가 이 논문과 달리 유지해야 할 부분

SimWAM이 굳이 신경 쓰지 않아도 되는, 그러나 taskcraft가 절대 놓지 말아야 할 것은 표현의 embodiment-invariance를 명시적으로 검증하는 절차다. SimWAM은 Action DiT가 비디오 토큰에 접근하지 못하게만 막으면 됐지, 그 결과로 남은 표현이 "차량이라는 몸에 무관한" 표현인지 검증할 필요가 없었다. 하나의 embodiment만 있기 때문이다. taskcraft는 latent world model이 사람 손 시연과 MineRL 에이전트(그리고 향후 다른 로봇 형태) 사이에서 실제로 재사용 가능한 표현인지를, 예를 들어 같은 태스크의 서로 다른 embodiment 시연이 latent 공간에서 가깝게 클러스터되는지 등으로 별도로 검증해야 한다. 이 검증 축을 SimWAM에는 없는 것으로 명확히 인식하고 유지해야 한다.

또한 SimWAM은 관측과 행동이 시간적으로 정렬된 단일 궤적 위에서 동작하기 때문에 시간축 정렬 문제를 고민할 필요가 없었다. taskcraft는 사람 시연 영상과 MineRL 에이전트 행동 시퀀스 사이의 시간 스케일이 다르므로(사람의 한 동작이 에이전트의 여러 스텝에 대응하는 등), latent world model이 이 시간 정렬을 흡수하거나 최소한 명시적으로 다루는 장치를 유지해야 한다. Isolated Attention Mask를 그대로 가져오면 이 시간 정렬 문제는 자동으로 해결되지 않는다는 점을 주의해야 한다.

마지막으로, SimWAM의 RL 단계(Flow-GRPO)는 결국 같은 embodiment, 같은 시뮬레이터(NAVSIM PDM) 안에서의 보상 최적화이기 때문에 보상 신호와 행동 공간이 처음부터 잘 정의되어 있다. taskcraft가 PPO를 비교 대상으로 넣는다면, latent world model에서 나온 표현이 보상 함수 설계나 정책 그래디언트 추정에 어떤 편향을 주는지는 SimWAM에서 답을 얻을 수 없는 부분이므로, 이 지점은 taskcraft 자체의 실험으로 별도로 채워야 한다.