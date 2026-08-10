# SimWAM 리뷰: taskcraft 관점에서

## 이 논문이 실제로 하는 일

SimWAM은 자율주행이라는 단일 embodiment(차량, 궤적 액션 공간) 안에서 "학습 때는 비디오 생성 모델의 동역학 지식을 주입하고, 추론 때는 그 비디오 모듈을 완전히 떼어낸다"는 효율화 트릭을 구현한 논문이다. Video DiT와 Action DiT를 공동으로 Flow Matching 학습시키되, Isolated Attention Mask로 액션 토큰이 미래 비디오 토큰을 보지 못하게 막아둔다. 그 결과 학습이 끝나면 비디오 모듈을 그냥 잘라내도 액션 모듈이 이미 필요한 지식을 흡수한 상태로 남는다. 여기에 Flow ODE를 SDE로 바꿔 GRPO 강화학습까지 얹어 주행 성능을 끌어올린다.

## taskcraft와의 핵심 차이

taskcraft가 풀고자 하는 문제는 "인코더가 관찰한 embodiment(사람 손, 사람 몸)와 디코더가 실행할 embodiment(로봇 팔, MineRL 에이전트)가 서로 다른데, 그 사이를 잇는 latent가 embodiment에 무관한 task 표현이 될 수 있는가"이다. 즉 latent world model의 역할은 표현 공간을 이질적인 두 embodiment 사이의 공용 인터페이스로 만드는 것이고, 검증 대상은 "이 표현이 몸을 바꿔도 살아남는가"이다.

SimWAM에는 이 질문 자체가 없다. Video DiT와 Action DiT는 같은 관찰 프레임 $$f_0$$을 입력으로 받고, 같은 차량이 만들어낼 미래 프레임과 미래 궤적을 각각 예측하는, 사실상 같은 embodiment의 두 출력 헤드다. Isolated Attention Mask가 막는 것은 "미래 비디오 토큰과 액션 토큰이 서로 참조하는 것"이지, "인코더가 특정 embodiment의 형태·기구학 정보를 latent에 새겨 넣는 것"이 아니다. 그래서 이 마스크는 정보 누출(leakage) 차단 장치가 아니라 추론 지연 시간을 줄이기 위한 계산 그래프 분리 장치에 가깝다. taskcraft가 마주한 "latent가 사람 손의 관절 구조까지 인코딩해버려서 로봇 팔에 이식이 안 되는 문제"는 SimWAM의 스코프 밖에 있다.

또한 SimWAM의 감독 신호는 항상 같은 embodiment의 미래 관찰(비디오 프레임)이다. taskcraft의 latent world model은 사람 시연에서 뽑은 표현이 로봇 embodiment의 동역학 모델 위에서도 예측 가능해야 한다는, cross-embodiment consistency를 요구한다. 이는 SimWAM의 joint flow matching 손실

$$\mathcal{L} = \mathcal{L}_{\text{FM}}^{\text{act}} + \lambda \mathcal{L}_{\text{FM}}^{\text{vid}}$$

식에는 등장하지 않는 항이다. 여기서 $$\lambda$$는 그저 같은 몸 안에서 비디오 지식을 얼마나 액션 인코더에 섞을지 조절하는 가중치일 뿐, taskcraft가 필요로 하는 "embodiment A의 latent와 embodiment B의 latent를 정렬시키는" 크로스 임베디먼트 항의 대응물이 아니다.

## taskcraft가 가져다 쓸 수 있는 부분

가장 직접적으로 참고할 만한 것은 "학습 시점에만 무거운 월드 모델을 붙이고 추론 시점에는 제거한다"는 학습-추론 분리 구조 자체다. taskcraft에서도 Latent World Model이 BC/DAgger/PPO 정책 학습 단계에서는 사람 시연의 동역학·목표 정보를 latent에 주입하는 보조 감독으로 쓰이되, 실제 MineRL 에이전트가 행동을 낼 때는 무거운 월드 모델 없이 가벼운 정책 헤드만으로 추론하는 구조를 설계할 수 있다. 특히 PPO 단계에서 롤아웃마다 월드 모델을 굴리는 비용이 크다면, SimWAM처럼 "월드 모델은 사전학습·distillation 단계에만 살아 있고 RL 시점에는 정책만 남는다"는 배치가 계산 효율 면에서 유효한 선택지가 된다.

Isolated Attention Mask라는 구현 아이디어도 변형해서 쓸 여지가 있다. SimWAM에서는 이걸 "미래 토큰 격리"용으로 썼지만, taskcraft에서는 반대 방향으로, 즉 "embodiment 식별 정보가 latent로 새어나가지 못하게" 인코더와 embodiment-특정 디코더 사이의 특정 어텐션 경로를 차단하는 훈련 트릭으로 재해석할 수 있다. 이는 leak-free encoding을 강제하는 정규화 장치로서, adversarial embodiment classifier 같은 대안보다 구조적으로 더 단순할 수 있다.

Flow ODE를 marginal-preserving SDE로 바꿔 탐색을 여는 방식도, taskcraft의 PPO 비교 실험에서 latent 정책이 확률적 policy로 동작해야 할 때 참고할 수 있는 수식적 템플릿이다. 다만 이는 taskcraft의 핵심 기여와는 다소 거리가 있는 최적화 디테일이다.

## taskcraft가 유지해야 할 부분

SimWAM을 참고하더라도 taskcraft는 다음 두 가지를 절대 흐리면 안 된다.

첫째, latent가 "누구의 몸에서 왔는지"를 지우면서도 "무엇을 하려는지"는 보존해야 한다는 이중 제약이다. SimWAM은 이 제약이 필요 없는 세팅(단일 embodiment)이라 애초에 이 문제를 풀지 않는다. taskcraft는 latent world model의 표현력을 평가할 때 반드시 "사람 시연에서 뽑은 latent로 로봇 embodiment 정책을 학습시켰을 때 성공하는가"라는 cross-embodiment 검증을 유지해야 하며, SimWAM의 결과(같은 embodiment 안에서의 PDMS 향상)를 근거로 이 검증을 생략하거나 약화시키면 안 된다.

둘째, BC vs DAgger vs PPO 비교라는 스코프의 목적이 SimWAM처럼 "지연 시간과 성능의 트레이드오프"가 아니라 "정책 학습 방식이 embodiment-agnostic latent를 얼마나 잘 활용/왜곡하는가"라는 점을 유지해야 한다. SimWAM의 GRPO 최적화는 보상 극대화 자체가 목적이지만, taskcraft에서 PPO를 도입하는 이유는 latent로부터 유도된 보상이나 목표가 embodiment를 바꿔도 여전히 유의미한 학습 신호로 작동하는지를 보기 위함이다. 따라서 taskcraft의 실험 설계는 SimWAM처럼 단일 embodiment 내 성능 지표(PDMS 같은 것)만 보고 끝내는 것이 아니라, embodiment 간 latent 이식 성공률이라는 별도의 축을 계속 측정 대상으로 남겨두어야 한다.