# Wan-Animate-2 리뷰: taskcraft 관점에서

## 이 논문이 실제로 풀고 있는 문제 vs taskcraft가 풀려는 문제

Wan-Animate-2는 겉보기에 taskcraft와 문제 설정이 놀랍도록 비슷하다. 둘 다 "하나의 소스에서 관찰된 행동을, 형태가 다른 대상에 어떻게 옮길 것인가"를 다루고, 둘 다 명시적 표현(스켈레톤, 관절 각도)과 암묵적 표현(learned latent) 사이의 트레이드오프를 정면으로 마주한다. 하지만 목적함수를 뜯어보면 완전히 다른 문제다. Wan-Animate-2의 성공 기준은 "생성된 비디오가 그럴듯하게 보이는가"이다. 즉 최종 산출물이 픽셀 공간의 지각적 품질이고, 물리적 인과관계나 실행 가능성은 검증 대상이 아니다. 반면 taskcraft의 성공 기준은 "다른 embodiment의 로봇이 실제로 그 task를 수행할 수 있는가"이다. Latent World Model이 중간에 있다는 점은 비슷해 보이지만, Wan-Animate-2에서 World Model에 해당하는 DiT는 결국 렌더러 역할을 하는 것이고, taskcraft에서 Latent World Model은 정책이 그 안에서 planning이나 imitation을 수행하기 위한 dynamics 근사여야 한다. 이 차이는 사소하지 않다. 렌더링이 목적이면 표현이 시각적으로만 일관되면 충분하지만, 정책 학습의 매개체가 되려면 표현이 상태 전이의 인과 구조를 실제로 보존해야 한다. taskcraft는 이 지점에서 Wan-Animate-2의 "그럴듯함" 기준을 그대로 가져오면 안 되고, BC/DAgger/PPO로 평가했을 때 실제 task 성공률이라는 훨씬 엄격한 기준을 유지해야 한다.

## Identity drift 대 embodiment drift, 같은 딜레마의 다른 심각도

논문이 지적하는 명시적 모션의 identity drift(체형이 다른 캐릭터로 스켈레톤을 옮기면 부자연스러워짐)와 암묵적 latent의 고주파 손실(표정, 손가락 디테일 소실)이라는 이분법은 taskcraft의 문제의식과 구조적으로 정확히 대응한다. taskcraft에서도 관절 각도나 end-effector trajectory 같은 명시적 표현을 human demonstration에서 뽑아 MineRL 에이전트에 그대로 이식하면, 사람 손과 Minecraft 에이전트의 action space가 근본적으로 다르기 때문에 (사람은 연속적 손가락 조작, MineRL 에이전트는 이산적 키 입력과 마우스 델타) 매핑 자체가 깨진다. 반대로 지나치게 압축된 latent를 쓰면 "블록을 어떤 순서로 놓았는가", "어느 시점에 시야를 돌렸는가" 같은 task-critical한 세부 동역학이 사라질 위험이 있다. 다만 애니메이션에서는 identity drift가 "보기에 어색함"이라는 연속적이고 관대한 실패 모드인 반면, taskcraft에서는 embodiment 이식 실패가 "task 실패"라는 이산적이고 냉정한 실패 모드로 나타난다. 즉 taskcraft에서 이 딜레마는 논문에서보다 훨씬 덜 관대한 형태로 다시 나타나며, 이 사실이 표현 설계의 검증 기준을 더 엄격하게 만들어야 하는 이유가 된다.

## 가져다 쓸 수 있는 부분: Sparse-Ref Attention의 설계 원리

taskcraft가 실질적으로 참고할 만한 부분은 구체적인 아키텍처가 아니라 하나의 설계 원리다. Sparse-Ref Attention은 참조 비디오와 타깃 비디오 사이의 전체 cross-attention 복잡도

$$O(N_r \times N_l)$$

를, 프레임 단위 시간 정렬이라는 도메인 지식을 이용해

$$O(N_l)$$

로 줄인다. 핵심은 "모든 것과 모든 것을 연결하지 않고, 대응 관계가 알려진 것끼리만 연결한다"는 발상이다. taskcraft에서 사람 시연과 로봇 rollout 사이에 latent state를 정렬할 때도 비슷한 구조를 적용할 수 있다. 예를 들어 사람 시연의 각 시점을 task phase(예: 재료 접근, 도구 사용, 배치 완료 같은 sub-goal 단위)로 분절하고, Latent World Model이 embodiment 간 정보를 교환할 때 전체 시퀀스에 대한 dense attention 대신 같은 phase에 속한 프레임끼리만 정렬하도록 제한하면, 불필요한 embodiment-specific 디테일(사람 손 모양, 신체 비율)이 전역적으로 섞여 들어가는 것을 막을 수 있다. 이는 표현 압축의 효율 문제라기보다, 어떤 정보를 어떤 단위로 공유할지에 대한 inductive bias를 아키텍처에 심는 방법론으로서 유의미하다. 또한 Dual-Branch 구조에서 노이즈가 섞인 흐름과 깨끗한 참조 흐름의 timestep을 분리해 간섭을 차단하는 아이디어도, taskcraft에서 human demonstration encoder와 robot policy decoder를 하나의 world model에 결합할 때 두 도메인의 통계적 특성이 서로 오염되지 않도록 분리하는 설계에 참고할 수 있다.

## taskcraft가 이 논문과 달리 반드시 유지해야 할 것

첫째, 검증 루프의 성격이다. Wan-Animate-2는 지각적 품질(FID류 지표, 사람이 보기에 자연스러운가)로 검증되지만, taskcraft는 latent 표현이 실제로 policy 학습에 유용한지를 BC, DAgger, PPO라는 서로 다른 학습 패러다임에서 task 성공률로 검증해야 한다. 이 세 방법을 비교하는 이유 자체가, 표현의 압축 정도와 정책 학습 방식 사이의 상호작용을 보기 위함이므로, Wan-Animate-2처럼 단일 생성 품질 지표로 표현의 우수성을 판단하는 방식으로 수렴해서는 안 된다.

둘째, 인과성과 실행 가능성의 보존이다. 애니메이션에서는 물리적으로 불가능한 동작이 나와도 시각적으로 그럴듯하면 실패가 아니지만, taskcraft의 Latent World Model은 embodiment가 실제로 실행 가능한 action sequence로 decode될 수 있어야 한다. 즉 표현이 압축되더라도 최소한 target embodiment의 action space에서 realizable한 정보만 담아야 하며, 이는 Wan-Animate-2가 신경 쓰지 않는 제약이다.

셋째, 목적의 방향성이다. Wan-Animate-2는 "동일한 동작을 다른 외형으로 재현"하는 1대1 이식(retargeting)에 가깝고, 카메라 시점 변경 같은 부가 기능도 결국 렌더링 조건의 확장일 뿐이다. 반면 taskcraft는 사람이라는 하나의 embodiment에서 여러 개의 서로 다른 로봇 embodiment로 task semantics를 일반화해야 하는 다대다 문제이며, 이 일반화 가능성 자체가 검증 대상이다. 따라서 taskcraft는 특정 embodiment 쌍에 대해 잘 작동하는 아키텍처를 만드는 데 그치지 않고, MineRL 테스트베드 안에서도 최소 두 개 이상의 이질적인 embodiment(예: 서로 다른 action space나 관찰 해상도를 가진 에이전트)에 대해 동일한 latent representation이 전이되는지를 별도로 확인하는 실험 설계를 유지해야 한다. 이는 Wan-Animate-2류 연구에서는 애초에 요구되지 않는 검증축이다.