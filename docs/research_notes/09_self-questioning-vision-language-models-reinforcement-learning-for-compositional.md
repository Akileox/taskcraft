# Self-Questioning VLM 논문 리뷰 — taskcraft 관점

## 이 논문이 다루는 문제와 taskcraft의 문제가 다른 층위에 있다는 점부터

이 논문은 VLM이 단일 forward pass로 답을 내는 대신, 스스로 sub-question을 만들고 풀어가며 최종 답에 도달하도록 GRPO 기반 RL로 학습시킨다. 여기서 학습되는 것은 언어/시각 모달리티 안에서의 추론 분해(compositional reasoning decomposition)이고, 대상은 정적인 이미지 한 장과 QA 쌍이다. 반면 taskcraft가 다루는 것은 시간에 따라 전개되는 물리적 행동 시퀀스이고, 목표는 사람의 embodiment(팔, 손 형태, 자유도)에서 관찰된 task를 다른 embodiment(Minecraft agent의 action space)로 옮기는 것이다. 즉 이 논문의 "발현"은 추론 그래프의 구조이고, taskcraft가 원하는 "발현"은 행동이 world state를 어떻게 바꾸는가에 대한 embodiment-invariant latent다. 둘 다 "사람이 단계별로 가르치지 않아도 구조가 나온다"는 점에서 형식적으로 닮았지만, 하나는 discrete symbolic reasoning의 분해이고 다른 하나는 continuous state-transition의 추상화다. 이 차이를 논문 노트도 인정하고 있는데, 이 지점을 taskcraft 쪽에서 더 명확히 해둘 필요가 있다. 즉 이 논문을 참고할 때는 "구조가 RL 보상만으로 창발한다"는 현상 자체를 가져오는 것이지, self-questioning이라는 메커니즘 자체를 이식하려는 시도는 아니라는 점을 분명히 해야 한다.

## taskcraft가 가져다 쓸 수 있는 부분

첫째는 알고리즘 차원이다. taskcraft의 10주 실험이 BC, DAgger, PPO를 비교하는 설계인데, PPO는 critic network를 별도로 학습해야 해서 Minecraft 같은 sparse/delayed reward 환경에서 critic이 불안정해지는 문제가 흔하다. GRPO는 critic 없이 동일 상태(혹은 동일 초기 조건)에서 뽑은 여러 rollout 그룹 내 상대적 보상만으로 advantage를 정규화한다.

$$\hat{A}_i = \frac{R(y_i, a^*) - \mu_g}{\sigma_g}$$

이 구조를 그대로 MineRL의 action rollout 비교에 적용하면, 같은 latent task representation을 조건으로 여러 policy rollout을 그룹으로 묶어 상대적으로 좋은 rollout에 advantage를 주는 방식이 가능하다. PPO의 critic 학습 불안정성을 우회하는 대안으로, "PPO vs GRPO" 비교 축을 실험에 하나 추가하는 것도 고려할 만하다. 특히 memory 절반 절감이라는 실용적 이점은 Minecraft testbed처럼 자원이 제한된 실험 환경에서 매력적이다.

둘째는 보상 설계 철학이다. 이 논문의 보상 함수는 매우 단순하다.

$$R(y, a^*) = \begin{cases} 1.0 & \text{if } \text{Format}(y) \land \text{Correct}(y, a^*) \\ -1.0 & \text{otherwise} \end{cases}$$

포맷 준수와 최종 정답이라는 두 조건만으로 중간 추론 구조 전체가 유도된다는 것은, taskcraft에서도 중간 latent 표현에 대한 dense supervision을 설계하려는 유혹을 줄이는 근거가 될 수 있다. 즉 "latent가 행동-상태 전이를 어떻게 인코딩해야 하는가"를 직접 감독하려 하기보다, 최종 task 성공 여부와 최소한의 구조적 제약(예: latent가 시간축에서 일관되게 변해야 한다는 정도)만 주고 나머지는 RL이 채우도록 두는 설계가 이 논문의 정신과 맞닿아 있다.

셋째는 "format tax" 현상이다. CLEVR 같은 단순 도메인에서는 sub-question을 강제하면 오히려 성능이 떨어진다는 관찰은, Minecraft testbed 중에서도 단순한 task(예: 나무 캐기)에는 굳이 복잡한 latent world model 구조를 강제하지 않는 편이 나을 수 있다는 가설로 이어진다. taskcraft 실험 설계에서 task 난이도별로 latent 구조의 이득이 다르게 나타나는지 확인하는 ablation을 넣을 근거가 된다.

## taskcraft가 이 논문과 달리 반드시 유지해야 할 부분

가장 중요한 차이는 이 논문에는 embodiment mismatch가 없다는 점이다. 이 논문의 policy는 학습 시점과 추론 시점에 동일한 VLM, 동일한 action space(텍스트 생성)를 쓴다. taskcraft는 사람 시연(하나의 embodiment)에서 얻은 표현을 전혀 다른 action space를 가진 embodiment로 전이해야 하므로, 이 논문의 self-questioning 구조를 그대로 가져와도 "누구의 관점에서 sub-question을 던지는가"라는 문제, 즉 latent가 특정 embodiment의 action statistics에 과적합되지 않도록 막는 메커니즘이 별도로 필요하다. 이 논문의 GRPO는 이런 문제를 다루지 않으므로, taskcraft는 GRPO의 advantage 정규화 아이디어만 빌리고 그룹을 구성하는 기준(같은 task, 다른 embodiment rollout을 그룹으로 묶을지, 같은 embodiment 내 다른 seed를 묶을지)은 독자적으로 설계해야 한다.

또한 이 논문은 정답 문자열 포함 여부(containment matching)라는 검증 가능한 즉각적 보상이 있는 도메인이라 RL이 잘 작동한다. Minecraft testbed에서 latent world model 매개 task는 이런 명확한 ground-truth reward가 없는 경우가 많다(사람 시연 영상에는 "정답 상태"라는 라벨이 없다). 따라서 taskcraft는 이 논문처럼 binary reward에 전적으로 의존하기보다, latent 예측 오차나 world model consistency 같은 self-supervised 신호와 최종 task 성공 신호를 함께 쓰는 hybrid 구조를 유지해야 한다. 이 논문의 단순함을 그대로 복제하면 reward signal이 지나치게 희소해질 위험이 있다.

마지막으로, 이 논문의 KL penalty 항

$$\mathcal{L}(\theta) = -\mathbb{E} \left[ \min\left(r_t \hat{A}_t, \text{clip}(r_t, 1-\epsilon, 1+\epsilon)\hat{A}_t\right) - \beta D_{\text{KL}}(\pi_\theta \parallel \pi_{\text{ref}}) \right]$$

는 사전학습된 VLM의 언어/시각 능력 붕괴를 막기 위한 장치인데, taskcraft에서는 참조할 만한 대응물이 명확하지 않다. Latent World Model을 사람 시연으로 사전학습한 뒤 로봇 embodiment에 RL로 fine-tune한다면, 이 KL penalty에 대응하는 것은 "latent가 원래의 embodiment-agnostic task semantics에서 너무 멀어지지 않도록" 하는 제약이 될 것이다. 이 부분은 이 논문에서 빌려올 수 있는 설계 아이디어이지만, 정확히 무엇을 reference로 삼을지(사람 시연 latent인지, task label인지)는 taskcraft가 별도로 정의해야 하는 문제로 남는다.