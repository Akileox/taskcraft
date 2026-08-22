# Zetta 논문 리뷰: taskcraft 관점에서

## 이 논문이 다루는 문제, 다시 정리

Zetta는 이미 학습된 VLA 정책 $$\pi$$를 동결한 채, 그 위에 고주파 런타임 크리틱 $$C$$, 복구 플레이북 $$R$$, 이기종 툴셋 $$\mathcal{T}$$로 구성된 하네스 $$\mathcal{H}$$를 감싸고, 이 하네스만을 3단계 폐루프로 진화시켜 조작 실패(미끄러짐, 접촉 불안정 등)를 실행 시점에 교정하는 프레임워크다. 목적식은 $$\max_{\mathcal{H}} J(\mathcal{H})$$ 이고, 정책 파라미터에 대한 gradient는 명시적으로 0으로 고정된다. 문제 설정 자체가 단일 embodiment, 단일 로봇 팔 안에서의 실행 신뢰성 향상이며, 서로 다른 형태의 로봇 사이에서 task를 옮기는 문제는 애초에 스코프에 없다.

## taskcraft와의 핵심 차이

taskcraft가 풀려는 문제는 "사람 시연 영상에서 뽑아낸 task representation을 다른 embodiment의 정책으로 이식하는 것"이고, 이때 핵심 난제는 embodiment 간 관측, 행동 공간의 불일치를 어떻게 공유 latent로 흡수하느냐다. 반면 Zetta의 핵심 난제는 "이미 같은 embodiment 안에서, 이미 배포된 정책이 저지르는 고주파 실행 오차를 어떻게 정책을 건드리지 않고 실시간으로 흡수하느냐"다. 둘 다 "기저 모델은 동결하고 그 바깥의 무언가를 진화시킨다"는 표층적 구조는 닮았지만, 동결되는 대상과 진화되는 대상의 성격이 정반대에 가깝다.

- Zetta: 동결되는 것은 이미 학습이 끝난 단일 embodiment용 정책 $$\pi$$이고, 진화하는 것은 그 정책을 감싸는 코드/스킬 레이어($$\mathcal{H}$$)다. 여기서 $$\pi$$ 자체는 embodiment-specific하며 이식 대상이 아니다.
- taskcraft: 진화(혹은 학습)의 대상이 바로 embodiment-agnostic한 latent task representation이고, 동결되어야 하는 것은 오히려 이 latent 인터페이스 쪽이며, embodiment마다 바뀌는 것은 그 latent를 소비하는 디코더(정책)다.

즉 Zetta는 "정책은 고정, 하네스는 진화"인데, taskcraft는 구조적으로 보면 "latent representation(인터페이스)은 고정, embodiment별 디코더/정책은 가변"이라는 점에서 무엇을 고정하고 무엇을 바꾸는지가 뒤집혀 있다. 이 차이를 명확히 인식하지 않으면 "정책 동결 후 wrapper 진화"라는 Zetta의 그림을 taskcraft에 그대로 옮겨오려는 유혹이 생기는데, taskcraft에서 진짜로 동결해야 할 대상은 정책이 아니라 latent 인터페이스 쪽이라는 점을 분명히 해야 한다.

또한 Zetta는 온라인 실패 데이터를 계속 쌓아서 하네스를 반복 개선하는 online, closed-loop 시스템인 반면, taskcraft는 (지금 스코프인 Minecraft testbed에서는) 사람 시연이라는 오프라인 데이터로부터 한 번 representation을 뽑고, 그걸 BC, DAgger, PPO라는 서로 다른 학습 패러다임으로 다른 embodiment 정책에 주입해서 비교하는 offline-to-transfer 실험 설계에 가깝다. Zetta가 DAgger와 스스로를 대비시키며 "정책 파라미터를 건드리지 않는다"는 점을 강조한 것과 달리, taskcraft의 DAgger 비교 축은 애초에 정책 파라미터를 online으로 계속 갱신하는 게 목적이므로, Zetta의 "동결" 철학을 그대로 가져오면 DAgger 비교축의 의미 자체가 흐려질 수 있다.

## taskcraft가 가져다 쓸 수 있는 부분

몇 가지는 구조적으로 유용해 보인다.

**시간 스케일 분리(Loop 1/2/3)**는 taskcraft의 실험 파이프라인 설계에 참고할 만하다. Zetta는 고주파 실행 루프(Loop 1)와 저주파 진단, 패치 루프(Loop 2), 검증 후 영구 반영 루프(Loop 3)를 명확히 분리해서 "즉시 반응"과 "구조적 개선"을 섞지 않는다. taskcraft에서도 latent world model로부터 embodiment별 정책을 학습, 평가하는 과정을, (a) 롤아웃 중 즉시 관측되는 실패, (b) 그 실패를 대표 사례로 클러스터링해서 latent representation 자체의 결함인지 디코더 쪽 결함인지 원인을 분리하는 오프라인 진단, (c) 검증을 통과한 개선만 representation에 반영하는 단계로 나누면, "representation을 고쳐야 하는지 embodiment별 디코더를 고쳐야 하는지"를 헷갈리지 않고 추적할 수 있다.

**Validation-Gated Update(Phase III)의 발상**도 유용하다. Zetta는 새로운 스킬 패치를 과거 실패 100% 재현 해결과 held-out 테스트 통과라는 회귀 검증을 거친 뒤에만 영구 메모리에 반영한다. taskcraft에서 latent representation을 조금씩 개선해 나갈 때(예: 새로운 task나 새로운 embodiment 추가 시), 기존에 이식 성공했던 embodiment, task 조합에서 성능이 퇴행하지 않는지 회귀 테스트하는 절차를 명시적으로 두는 것은, latent 공유 인터페이스가 embodiment 수가 늘어날수록 겪기 쉬운 "하나 고치면 다른 게 깨지는" 문제를 조기에 잡는 데 직접 응용 가능하다.

**EOD(Earliest Observable Divergence) 개념**도 은유적으로 빌려올 수 있다. Zetta는 실패 궤적이 성공 궤적 분포로부터 처음 벗어나는 시점을 찾아 실패를 클러스터링한다. taskcraft에서 특정 embodiment로 이식된 정책이 실패할 때, 그 실패가 latent representation이 애초에 task의 핵심 정보를 못 담아서인지(표현 단계 문제) 아니면 디코더가 latent를 행동으로 잘못 변환해서인지(이식 단계 문제)를 구분하는 것이 진단의 핵심인데, "정책의 상태 궤적이 참조 성공 궤적으로부터 언제 처음 갈라지는가"를 관찰 신호로 삼아 이 두 가지를 나누는 방식은 그대로 응용해볼 만하다. 다만 taskcraft에서는 embodiment마다 상태 공간이 다르므로, 원 논문처럼 상태 거리를 직접 재는 대신 latent 공간에서의 거리로 대체해야 한다는 조정은 필요하다.

**VLA 재진입 계약 $$\Psi(s_t)$$** 같은 "제어권 전환 조건을 명시적으로 정의한다"는 태도도 참고할 만하다. taskcraft에서 만약 latent world model이 예측한 plan을 따르다가 embodiment-specific 저수준 controller(예: 물리적 안전을 위한 fallback)로 잠깐 넘어갔다가 다시 latent 기반 정책으로 복귀하는 하이브리드 실행을 고려한다면, "복귀 가능 조건"을 명시적 술어로 정의해 두는 것이 실행 안정성에 도움이 될 수 있다.

## taskcraft가 이 논문과 달리 반드시 유지해야 할 부분

가장 중요한 것은, Zetta 식으로 "정책은 동결하고 그 위에 얇은 레이어만 진화시킨다"는 원칙을 taskcraft의 latent representation 자체에 그대로 적용해서 latent를 통째로 고정해버리는 실수를 피해야 한다는 점이다. Zetta에서 정책이 동결될 수 있는 이유는 애초에 그 정책이 특정 embodiment, 특정 task 분포에서 이미 잘 작동하도록 학습되어 있고, 문제는 그 정책 바깥의 실행 잡음이기 때문이다. 반면 taskcraft의 latent world model은 아직 "여러 embodiment에 걸쳐 무엇이 공유 가능한 정보인가"를 스스로 찾아가는 학습 대상이며, 이걸 너무 일찍 동결하면 embodiment 간 전이 성능 자체가 latent 표현력의 한계에 갇힐 위험이 있다. 즉 taskcraft는 "무엇을 동결하고 무엇을 학습 대상으로 둘 것인가"라는 설계 결정을 Zetta처럼 정책 쪽에 두는 것이 아니라, latent representation의 sufficiency(embodiment 이식에 필요한 정보를 충분히 담고 있는가)를 지속적으로 검증 대상으로 남겨두어야 한다.

둘째로, taskcraft의 존재 이유인 "사람 시연 영상으로부터의 embodiment-agnostic 표현 추출"이라는 표현 학습 축은 Zetta에는 아예 없는 구성 요소이므로, 이 논문에서 어떤 아이디어를 빌려오든 이 축을 대체하거나 희석시켜서는 안 된다. Zetta가 다루는 실행 시점 견고성(robustness) 문제는 taskcraft 파이프라인의 맨 마지