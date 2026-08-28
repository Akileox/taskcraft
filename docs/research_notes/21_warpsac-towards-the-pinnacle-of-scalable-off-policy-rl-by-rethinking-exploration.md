# WarpSAC 리뷰: taskcraft 관점

## 이 논문이 다루는 문제와 taskcraft 문제의 근본적 차이

WarpSAC은 오프폴리시 강화학습(SAC 계열)의 안정화 장치들, 즉 파라미터 정규화 투영과 Clipped Double-Q, 리플레이 샘플링 전략을 데이터 체제(CPU 단일 환경 대 GPU 대규모 병렬 환경)에 맞춰 껐다 켰다 하는 것이 핵심 기여입니다. 문제의식 자체가 "한 embodiment 안에서 같은 정책을 얼마나 빨리, 얼마나 안정적으로 학습시킬 것인가"에 머물러 있고, 여러 embodiment 사이에서 task를 어떻게 옮길 것인가, human video에서 무엇을 뽑아낼 것인가에 대한 질문은 전혀 다루지 않습니다.

taskcraft의 핵심 질문은 반대로 embodiment 간 전이입니다. 사람이 시연한 영상에서 embodiment에 묶이지 않는 task representation을 latent world model을 매개로 뽑아내고, 이를 형태가 다른 로봇(MineRL agent)에 이식하는 것이 목표이고, BC, DAgger, PPO 비교는 그 representation을 실제 정책으로 내려받을 때 어떤 학습 패러다임이 distribution shift와 cross-embodiment gap을 가장 잘 견디는지를 보기 위한 실험 축입니다. 즉 WarpSAC은 "학습 속도와 안정성"이라는 알고리즘 내부 최적화 문제이고, taskcraft는 "표현의 이식 가능성"이라는 표현 학습 문제입니다. 두 논문이 같은 강화학습 알고리즘 이름(SAC, PPO)을 언급하더라도 겨냥하는 층위가 다르다는 점을 taskcraft 노트에 명시적으로 남겨둘 필요가 있습니다.

또 하나 짚을 부분은 알고리즘 계열 자체가 다르다는 점입니다. WarpSAC의 모든 기법(SWD, 파라미터 투영, Double-Q)은 리플레이 버퍼를 쓰는 오프폴리시 학습에서만 의미가 있습니다. taskcraft의 PPO 비교군은 온폴리시이므로 리플레이 버퍼 staleness 문제 자체가 존재하지 않고, 파라미터 투영이나 Double-Q 같은 장치를 그대로 이식할 대상이 아닙니다. 이 논문의 기법들이 taskcraft에 직접 적용 가능한 것은 PPO가 아니라 오히려 DAgger의 aggregated dataset 쪽입니다.

## taskcraft가 가져다 쓸 수 있는 부분

가장 값진 것은 구체적 기법보다 방법론적 태도입니다. WarpSAC의 핵심 메시지는 "과대추정 방지 장치나 정규화가 항상 안전한 기본값은 아니고, 데이터 커버리지라는 체제 변수에 조건부로 필요성이 달라진다"는 것입니다. 이는 taskcraft가 BC, DAgger, PPO를 비교할 때도 그대로 적용될 수 있는 관점입니다. 예를 들어 human video demonstration 수가 적은 상황(데이터 제한 체제)에서는 BC의 behavior cloning loss에 강한 정규화나 latent space 상의 보수적 제약이 필요하겠지만, MineRL 환경에서 rollout을 대량으로 생성할 수 있는 PPO fine-tuning 단계에서는 같은 제약이 오히려 latent world model이 담고 있는 표현력을 억누를 수 있습니다. 즉 taskcraft 실험 설계에서 BC, DAgger, PPO 각각에 동일한 정규화 강도나 동일한 critic/decoder 구조를 관성적으로 적용하지 말고, 각 학습 단계가 실제로 어떤 데이터 체제(시연 수, rollout 수, embodiment 다양성)에 놓여 있는지에 따라 하이퍼파라미터를 다르