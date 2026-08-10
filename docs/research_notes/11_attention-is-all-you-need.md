# Transformer 논문과 taskcraft: 도구 상자와 연구 질문의 층위 구분

## 이 논문이 taskcraft에 대해 답하지 않는 것

Attention Is All You Need는 시퀀스 변환 문제에서 순환 구조 없이도 장거리 의존성을 병렬적으로 학습할 수 있음을 보인 아키텍처 논문이다. taskcraft가 던지는 질문, 즉 "사람 시연 영상에서 embodiment에 무관한 task representation을 어떻게 뽑고, 그것을 어떻게 다른 형태의 로봇으로 이식하는가"는 이 논문의 스코프 밖에 있다. Transformer는 시퀀스 내부의 관계를 잘 잡아내는 계산 구조를 제공할 뿐, 서로 다른 embodiment 사이에 존재하는 관측 공간과 행동 공간의 불일치, 즉 correspondence problem 자체를 풀어주지 않는다. 이 점을 먼저 분명히 해두는 것이 이 노트의 출발점이다. 이 논문을 taskcraft의 경쟁 아이디어나 대안 접근으로 다룰 이유는 없고, taskcraft가 latent world model의 인코더나 디코더를 구현할 때 사용할 수 있는 하위 구성요소 후보로 다루는 것이 맞다.

## taskcraft가 가져다 쓸 수 있는 부분

가장 직접적으로 가져다 쓸 수 있는 것은 self-attention이 제공하는 임의 시점 간 고정 연산 거리라는 성질이다. VPT, STEVE-1, GROOT 같은 MineRL 계열 선행 연구들이 이미 self-attention 기반 백본을 쓰고 있다는 점을 taskcraft 노트도 언급했는데, 이는 우연이 아니라 사람 시연 영상에서 "행동이 세계 상태를 어떻게 바꾸었는가"를 latent로 추출하려면 멀리 떨어진 프레임 사이의 관계를 direct하게 참조해야 하기 때문이다. RNN 기반 인코더로는 이 관계가 시간 축을 따라 압축되면서 손실되기 쉬운데, Transformer 구조는 이 부분에서 구조적으로 유리하다.

Multi-Head Attention의 subspace 분할 아이디어도 참고할 만하다. taskcraft가 다루는 latent representation은 결국 embodiment에 무관한 성분과 embodiment에 종속적인 성분이 뒤섞여 있을 가능성이 높은데, 여러 head가 서로 다른 projection 공간에서 독립적으로 관계를 학습하는 구조는, 이후 disentanglement를 시도할 때 head별로 역할을 분리하거나 특정 head 집합만 embodiment-agnostic 성분에 대응시키는 식의 설계로 확장할 여지를 준다. 지금 스코프에서 바로 쓸 필요는 없지만, latent space의 구조를 설계할 때 염두에 둘 만한 선택지다.

Masked self-attention 역시 유용하다. Latent world model이 미래 상태를 자기회귀적으로 예측해야 한다면, 디코더 쪽에서 미래 프레임을 참조하지 못하게 막는 masking 기법은 그대로 필요하다. BC와 DAgger 비교 실험에서 policy가 시퀀스를 소비하는 방식을 설계할 때도 이 마스킹 아이디어는 그대로 재사용 가능하다.

## taskcraft가 이 논문과 달리 유지해야 할 부분

가장 중요하게 유지해야 할 것은, embodiment-agnostic한 표현이 아키텍처의 성질에서 자동으로 따라 나오지 않는다는 전제다. Transformer는 시퀀스 내부 관계를 잘 뽑아내는 도구지만, 그 결과로 나오는 representation이 embodiment 간에 공유 가능한지는 별도의 목적함수나 구조적 제약, 예를 들면 contrastive 방식의 embodiment-invariance loss나 latent bottleneck 설계에서 나와야 한다. 이 논문의 어떤 구성요소도 이 문제를 대신 풀어주지 않으므로, taskcraft는 인코더 아키텍처를 이 논문에서 빌려오더라도 embodiment-agnostic을 강제하는 손실함수나 학습 절차는 독자적으로 설계해야 한다.

Positional encoding 부분은 taskcraft AI 생각에서도 지적된 대로 그대로 가져오기 어려운 지점이다. 사람 손과 로봇 팔, 혹은 Minecraft 에이전트처럼 시간 스케일과 동작 주기가 다른 embodiment들 사이에서는 절대 위치 $$pos$$가 갖는 의미가 서로 다르다. Transformer의 sinusoidal positional encoding은 절대 위치를 명시적으로 주입하는 방식이라서, embodiment마다 한 스텝이 실제로 의미하는 물리적 시간이나 상태 변화량이 다른 상황에는 부적합할 수 있다. 이 부분은 taskcraft가 이 논문의 방식을 그대로 채택하지 않고, 상대적 위치 인코딩이나 이벤트 기반, 즉 상태 변화가 실제로 발생한 시점을 기준으로 하는 인코딩으로 대체하는 방향을 검토해야 한다.

또한 이 논문의 실험 축인 번역 품질(BLEU)과 taskcraft의 실험 축인 BC, DAgger, PPO 비교는 완전히 다른 층위의 문제다. Transformer 논문은 지도학습 시퀀스 변환에서의 성능과 학습 병렬성을 다루지만, taskcraft는 human video demonstration으로부터 얻은 latent를 정책 학습에 어떻게 연결하는지, 그리고 그 정책이 imitation과 온라인 상호작용(DAgger, PPO) 사이에서 어떻게 갈리는지를 봐야 한다. 이 실험 설계는 이 논문과 무관하게 taskcraft 고유의 축으로 유지되어야 하고, Transformer 구조를 인코더로 채택하더라도 그것이 BC vs DAgger vs PPO 비교의 결론을 대체하거나 단순화시키는 것으로 이어지지 않도록 구분해서 다뤄야 한다.

## 정리

이 논문은 taskcraft의 latent world model 구현에서 인코더나 디코더의 기본 블록을 제공할 수 있는 후보이지만, taskcraft가 풀어야 하는 핵심 질문인 embodiment 간 표현 이식 문제에는 직접적인 답을 주지 않는다. self-attention의 장거리 의존성 처리 능력과 multi-head의 subspace 분할 아이디어는 가져다 쓸 만하지만, positional encoding은 절대 위치 의존성 때문에 변형이 필요하고, embodiment-agnostic 성질을 강제하는 손실함수나 학습 절차, 그리고 BC, DAgger, PPO 비교라는 실험 설계는 이 논문과 독립적으로 taskcraft가 스스로 유지하고 발전시켜야 하는 부분이다.