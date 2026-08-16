# RT-2 리뷰: taskcraft 관점에서

## 왜 이 논문을 지금 보는가

taskcraft는 사람 시연 영상에서 embodiment-agnostic task representation을 뽑아 Latent World Model을 매개로 다른 형태의 로봇에 이식하는 것을 목표로 한다. 지금 스코프는 Minecraft(MineRL) testbed에서 BC, DAgger, PPO를 비교하는 것이고, 이 비교의 목적은 결국 "task representation을 어떤 학습 알고리즘 위에 얹었을 때 embodiment 이식이 가장 안정적으로 되는가"를 보는 것이다. RT-2는 이 문제의식과 정반대 방향에서 출발한 연구라서, taskcraft의 포지셔닝을 선명하게 만들어주는 좋은 대조군이다.

## 핵심 차이: 표현을 어디에 두는가

RT-2의 전략은 한 문장으로 요약하면, "행동을 언어 토큰 공간에 밀어넣고 웹 스케일 지식으로 그 공간을 확장한다"이다. 6-DoF 위치·회전 변위와 그리퍼 개폐를 256개의 균일 빈으로 양자화해서 8개의 정수 토큰 문자열로 만들고, 이 토큰을 PaLI-X나 PaLM-E 같은 VLM의 기존 어휘 공간에 그대로 끼워 넣는다. 별도의 행동 헤드나 로봇 전용 인코더를 두지 않고, 웹 VQA/캡셔닝 데이터와 로봇 궤적 데이터를 같은 포맷으로 섞어 공동 미세조정한다. 이 방식이 실제로 잘 작동한다는 것이 RT-2의 핵심 실증 결과다.

문제는 이 토큰 스키마 자체가 처음부터 특정 embodiment의 엔드이펙터 자유도에 종속적으로 설계되어 있다는 점이다. $$\Delta\text{pos}_x, \Delta\text{pos}_y, \Delta\text{pos}_z$$와 $$\Delta\text{rot}_x, \Delta\text{rot}_y, \Delta\text{rot}_z$$, $$\text{gripper\_extension}$$이라는 8차원 벡터는 특정 로봇 팔의 관절 구조와 조작 방식을 전제로 한다. 다리 개수가 다르거나 조작 방식이 완전히 다른 에이전트로 옮기려면 이 토큰 스키마 자체를 다시 설계해야 한다. 즉 RT-2가 일반화시킨 것은 "같은 로봇이 새로운 물체와 배경을 다루는 능력"이지, "다른 신체 구조로 재사용 가능한 task 표현"이 아니다. taskcraft가 풀려는 문제는 후자이고, 이 층위 차이가 RT-2와 taskcraft를 가르는 가장 근본적인 지점이다.

taskcraft는 이 지점에서 RT-2와 반대의 설계를 유지해야 한다. task representation은 embodiment-specific한 행동 토큰이 아니라, "행동이 세계 상태를 어떻게 바꾸는가"를 나타내는 latent여야 하고, 이 latent에서 실제 행동으로 내려가는 매핑은 embodiment마다 별도의 디코더가 담당해야 한다. RT-2처럼 표현과 실행을 하나의 토큰 공간에 융합해버리면, 그 순간 embodiment 이식 가능성은 구조적으로 사라진다. 이 분리, latent representation과 embodiment-specific decoder의 분리는 taskcraft가 절대 포기하면 안 되는 설계 원칙이다.

## 그럼에도 가져다 쓸 수 있는 것

RT-2에서 taskcraft가 실제로 빌려올 만한 요소는 몇 가지 있다.

첫째, 공동 미세조정(co-fine-tuning) 아이디어다. RT-2는 로봇 데이터만으로 미세조정하면 파국적 망각이 일어난다는 것을 보이고, 웹 데이터와 로봇 데이터를 일정 비율로 섞어 학습함으로써 사전학습된 표현의 일반화 능력을 보존한다. taskcraft도 사람 시연 영상에서 뽑은 task representation을 Minecraft 같은 특정 testbed의 궤적 데이터에 미세조정할 때 비슷한 망각 위험이 있을 수 있다. Latent World Model을 사람 영상 도메인과 MineRL 도메인 양쪽에서 계속 노출시키면서 학습하는 co-training 스케줄은, RT-2의 비율 혼합 전략(로봇 데이터 50~66%)을 참고해서 설계할 수 있다.

둘째, chain-of-thought 스타일의 중간 계획 삽입이다. RT-2는 `"Instruction: ... Plan: ... Action: ..."` 형태로 자연어 계획을 행동 출력 전에 끼워 넣어 성능을 끌어올렸다. taskcraft에서도 사람 영상에서 뽑은 task representation과 실제 latent action 사이에 중간 수준의 서브골이나 계획 표현을 명시적으로 삽입하면, latent world model이 학습해야 하는 매핑의 복잡도를 낮출 수 있을 것이다. 다만 RT-2와 달리 이 중간 표현도 embodiment-agnostic해야 한다는 제약은 유지해야 한다.

셋째, 출력 제약(constrained decoding) 아이디어는 사소하지만 실용적이다. RT-2가 로봇 제어 상황에서 유효한 행동 토큰만 샘플링하도록 디코딩 어휘를 제약한 것처럼, taskcraft의 embodiment-specific decoder도 각 embodiment의 유효 행동 공간으로 출력을 제약하는 방식을 채택할 수 있다. 이건 표현 설계의 문제가 아니라 디코더 구현 디테일이라서 taskcraft의 embodiment-agnostic 원칙과 충돌하지 않는다.

## BC/DAgger/PPO 비교라는 taskcraft 스코프에서의 시사점

RT-2의 학습 손실 자체는 표준적인 자기회귀 다음 토큰 예측 기반 BC다.

$$\mathcal{L}_{\text{BC}} = -\sum_{t=1}^{T} \log P(y_t \mid y_{<t}, I, x_{\text{prompt}})$$

RT-2는 BC가 가진 "학습 도메인 밖 일반화 실패"라는 고질적 한계를, 알고리즘을 바꾸는 대신 백본과 데이터 혼합 전략으로 우회했다. 이 점은 taskcraft의 BC vs DAgger vs PPO 비교 실험 설계에 직접적인 시사점을 준다. RT-2 사례는 "BC의 일반화 실패는 반드시 DAgger나 PPO 같은 알고리즘 교체로만 해결되는 게 아니라, 표현 학습 쪽에서 웹 스케일 지식을 끌어오는 것으로도 상당 부분 완화될 수 있다"는 것을 보여준다. 그런데 taskcraft에서는 웹 스케일 VLM 같은 외부 지식원이 없고 대신 latent world model이 그 역할을 대신해야 한다. 따라서 taskcraft의 비교 실험에서 중요한 질문은, MineRL 같은 좁은 testbed에서 BC가 covariate shift에 취약할 때 이를 DAgger의 online correction으로 메울지, 아니면 latent representation 쪽의 표현력을 늘려서 메울지, 아니면 PPO의 exploration으로 메울지를 분리해서 보는 것이다. RT-2는 이 세 축 중 표현 쪽 해법만 극단적으로 밀어붙인 사례이고, 그 결과가 "embodiment 이식이 아니라 domain 내 일반화"에 그쳤다는 점을 taskcraft 실험 설계 시 반면교사로 삼을 수 있다. 즉 taskcraft는 표현 확장만으로 문제를 덮으려 하지 말고, latent representation의 embodiment-agnostic 성질을 유지한 채로 BC/DAgger/PPO 각각이 embodiment 이식 성능에 어떤 영향을 주는지를 독립적으로 측정해야 한다.

## 정리

RT-2는 "웹 지식을 로봇 행동에 전이"하는 문제를 embodiment-specific 토큰화와 대규모 공동 미세조정으로 성공적으로 풀었지만, 그 성공은 표현과 실행을 하나로 합친 대가로 얻어진 것이다. taskcraft는 정확히 그 지점에서 갈라져야 한다. task representation은 latent 공간에 embodiment-agnostic하게 남아있어야 하고, embodiment로의 투영은 별도의 디코더가 맡아야 한다는 원칙은 RT-2와 비교할 때 taskcraft가 절대 양보하면 안 되는 핵심 설계다. 대신 co-fine-tuning 전략, 중간 계획 표현의 삽입, 제약된 디코딩 같은 구현 차원의 아이디어는 이 원칙을 해치지 않는 선에서 얼마든지 빌려올 수 있다. 선행연구 비교 절에서는 RT-2류를 "embodiment-specific 토큰화 + 웹 스케일 지식 전이"로, taskcraft를 "embodiment-agnostic latent + embodiment별 디코더"로 대조시키는 것이 포지셔닝상 가장 명확할 것이다.