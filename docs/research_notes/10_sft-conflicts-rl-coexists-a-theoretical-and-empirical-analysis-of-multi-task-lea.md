# taskcraft 관점 리뷰: SFT Conflicts, RL Coexists

## 이 논문이 실제로 다루는 축

이 논문의 핵심 주장은 하나의 모델(LLM)을 여러 작업(Math, Code, Science, Logic)에 대해 순차적 또는 다단계로 학습시킬 때, SFT는 작업 간 파라미터 업데이트 방향이 크게 겹쳐서(cosine similarity $$0.95$$ 이상) 충돌하고 성능이 붕괴하지만, RL(GRPO)은 advantage의 zero-sum 성질과 on-policy 특성 덕분에 업데이트가 거의 직교($$10^{-5}$$ 수준)해서 여러 작업 능력이 파라미터 공간에서 공존한다는 것이다. 즉 이 논문이 고정하는 것은 embodiment(모델 아키텍처, 관측·행동 공간)이고 변화시키는 것은 task다. 반면 taskcraft가 다루는 축은 정확히 반대다. taskcraft는 task의 의미(사람이 시연한 행동의 목적)를 고정한 채 embodiment를 바꿔가며 그 task representation을 latent world model을 매개로 다른 형태의 로봇에 이식하는 것이 목표다. 이 둘은 표면적으로 "여러 조건에서 하나의 표현을 어떻게 안정적으로 학습, 전달하느냐"라는 문제의식은 닮아 있지만, 변화의 축이 task냐 embodiment냐가 다르기 때문에 이 논문의 결론을 taskcraft에 그대로 대입하면 안 된다.

## 핵심 차이

가장 중요한 차이는 이 논문이 순수하게 파라미터 업데이트 레벨의 간섭(interference)을 다루는 최적화 이론이고, representation 자체가 embodiment 간에 어떻게 정렬되고 전달되는지에 대한 질문은 전혀 다루지 않는다는 점이다. taskcraft의 난제는 사람 영상에서 뽑은 latent task representation이 MineRL 에이전트, 혹은 향후 다른 형태의 로봇의 행동 공간으로 얼마나 잘 매핑되느냐이고, 이것은 gradient orthogonality 문제가 아니라 표현 정렬(representation alignment) 문제다. 이 논문의 이론은 "같은 latent 위에서 여러 downstream policy를 어떤 알고리즘으로 학습시키느냐"라는, taskcraft 파이프라인의 뒷단(디코딩 단계)에만 부분적으로 관련이 있을 뿐이다.

두 번째 차이는 실험 설계의 성격이다. 이 논문은 하나의 모델에 여러 task를 순차적으로 학습시키는 multi-stage, multi-task 세팅을 가정한다. taskcraft의 현재 스코프인 BC vs DAgger vs PPO 비교는 MineRL testbed 안에서 단일 embodiment, 단일 task에 대해 latent representation을 얼마나 잘 행동으로 디코딩하느냐를 비교하는 것이지, 여러 task나 여러 embodiment를 한 모델에 순차적으로 누적 학습시키는 세팅이 아니다. 따라서 이 논문의 정리(Theorem 4.5)가 곧바로 taskcraft의 현재 실험을 설명해주는 것은 아니며, 이는 taskcraft가 향후 "하나의 공유 decoder로 여러 embodiment를 순차 또는 동시에 학습"하는 확장 단계로 갈 때에만 직접적으로 유효해지는 이론이다.

세 번째로 짚어야 할 것은 DAgger의 위치다. 이 논문의 이론적 이분법은 SFT(off-policy, 정답 궤적에 강제로 맞춤, norm-limited interference)와 RL(on-policy, advantage 기반, variance-limited interference)이라는 두 극단만 다룬다. DAgger는 데이터 수집 분포는 on-policy이지만 손실 함수 자체는 여전히 expert action에 대한 cross-entropy, 즉 imitation loss다. 이 논문의 프레임에서는 DAgger가 SFT 쪽에 더 가까운지, RL 쪽에 더 가까운지 이론적으로 애매하게 남는다. taskcraft가 BC, DAgger, PPO를 나란히 비교하는 실험 설계는 바로 이 애매함을 실증적으로 검증할 좋은 위치에 있다.

## taskcraft가 가져다 쓸 수 있는 부분

가장 실용적으로 가져올 수 있는 것은 진단 도구다. 파라미터 업데이트 $$\Delta W$$의 $$L_2$$ norm과, 서로 다른 조건(이 논문에서는 task, taskcraft에서는 embodiment 또는 task) 간 업데이트의 cosine similarity를 측정해서 히트맵으로 비교하는 방법론은 그대로 taskcraft에 이식할 수 있다. 예를 들어 taskcraft가 나중에 하나의 latent-conditioned decoder를 여러 embodiment에 대해 순차적으로 파인튠하는 실험을 하게 된다면, 각 embodiment 학습 단계에서 발생한 $$\Delta W$$의 크기와 방향 유사도를 측정해서 BC 기반 디코더 학습이 실제로 embodiment 간 충돌을 일으키는지, PPO 기반 디코더 학습이 정말로 직교적으로 공존하는지를 정량적으로 보여줄 수 있다.

두 번째