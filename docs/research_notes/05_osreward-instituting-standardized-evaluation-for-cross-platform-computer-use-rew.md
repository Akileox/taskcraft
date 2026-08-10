# OSReward 리뷰 — taskcraft 관점

## 1. 문제 설정이 다르다: Reward Modeling vs Representation Transfer

OSReward는 철저히 **평가(evaluation) 문제**다. 이미 존재하는 CUA 에이전트의 궤적이 "성공했는가"를 판정하는 judge/reward model을 만드는 것이 목표이고, 판정 대상은 동일한 액션 공간(클릭·타이핑·스크롤)을 쓰는 플랫폼들(Web/Windows/Ubuntu/Android)이다. 즉 "cross-platform"이라 부르지만 embodiment 자체의 이질성은 크지 않다 — GUI라는 공통 인터페이스 안에서 표면만 다르다.

반면 taskcraft는 **표현 학습·전이(representation learning/transfer) 문제**다. 사람 시연이라는 하나의 embodiment에서 task representation을 뽑아 액션 공간·관절 구조·관측 모달리티가 근본적으로 다른 로봇(MineRL 상에서는 agent embodiment)으로 이식하는 것이 목표다. 여기서 latent world model(LWM)은 판정자가 아니라 **embodiment-invariant한 state-transition bottleneck**이다.

이 둘을 같은 축에 놓고 보면 안 된다는 게 첫 번째 결론이다: OSReward의 성과를 그대로 "taskcraft용 reward model"로 이식하려는 유혹이 생길 수 있는데, 이는 스코프 이탈이다. taskcraft에서 LWM의 역할은 *judge*가 아니라 *representation*이며, 이 구분을 계속 명시적으로 유지해야 한다.

## 2. 공명하는 지점: Narration vs State Grounding

OSReward가 밝힌 Leniency Bias의 본질 — "VLM judge가 에이전트의 self-narration에 속아 실제 환경 상태 변화를 확인하지 않는다" — 은 taskcraft가 LWM을 굳이 매개로 삼는 이유와 방법론적으로 정확히 같은 문제의식을 공유한다. taskcraft도 "행동/서사가 아니라 world-state 전이"를 embodiment-agnostic한 신호로 삼겠다는 가설에 기대고 있다.

여기서 얻을 수 있는 진짜 시사점은 다음과 같다: **LW