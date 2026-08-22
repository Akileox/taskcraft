# STDR 논문 리뷰: taskcraft 관점에서

## 이 논문이 서 있는 위치

STDR은 "전문가 시연 비디오로부터 조밀 보상을 뽑아내서 RL을 돕는다"는 문제를 푼다. 그런데 여기서 시연 비디오와 RL 롤아웃은 같은 embodiment, 같은 카메라, 같은 액션 공간을 공유한다. 즉 로봇 팔이 스스로 성공한 시연을 남기고, 그 시연으로 학습한 보상 모델이 같은 로봇 팔의 온라인 RL 탐색을 채점하는 구조다. VLM은 여기서 시연 비디오를 $$K$$개의 단계로 나누는 라벨링 도구로만 쓰이고, 실제 보상을 계산하는 Stage Discriminator와 Progress Estimator는 순수하게 그 로봇의 시각 관측(픽셀)에 대해 학습된 판별 모델이다. 다시 말해 STDR은 "embodiment는 고정, 보상 신호의 밀도와 방향성을 어떻게 확보할 것인가"에 집중한 논문이고, taskcraft가 풀려는 "embodiment가 바뀌어도 task representation이 살아남게 하려면 어떻게 해야 하는가"라는 문제는 애초에 스코프 밖에 있다.

## taskcraft와의 핵심 차이

가장 근본적인 차이는 train/deploy 분포 정합성이다. STDR의 보상 모델은 학습 시 본 로봇 시연과 배포 시 관측할 롤아웃이 동일한 embodiment, 동일한 시각 도메인에서 나온다는 것을 전제로 한다. OOD 게이팅(VAE 재구성 오차, 마할라노비스 거리)이 방어하는 것은 어디까지나 "같은 로봇이 정책 탐색 중에 드물게 벗어나는 상태"이지, "애초에 다른 몸으로 관측된 입력이 들어오는 상황"이 아니다. taskcraft는 정반대다. Latent World Model이 인코딩하는 human video의 latent와 Minecraft 에이전트의 실제 롤아웃 latent는 관측 통계, 액션 공간, 심지어 시야 기하 자체가 다르다. 이 gap은 STDR에서 말하는 "정책이 가끔 이탈하는 정도의 OOD"가 아니라 상시적, 구조적인 domain shift다. 따라서 STDR의 OOD 방어 메커니즘을 그대로 가져다 쓰면 낙관적으로 작동할 것이라 기대하면 안 된다. 이 논문에서 OOD는 예외 상황이지만, taskcraft에서는 사실상 기본 조건이다.

두 번째 차이는 표현이 담당하는 역할의 범위다. STDR의 이중 보상 모델은 스칼라 하나(그리고 그 미분 가능한 진행도)만 출력하면 되는 순수 판별 모델이다. 반면 taskcraft의 Latent World Model은 task representation을 추출하는 동시에 그것이 타깃 embodiment의 정책(BC/DAgger/PPO 세 갈래 모두)이 실제로 소비할 수 있는 형태여야 한다. 즉 STDR은 "보상 함수 하나"를 잘 만들면 끝나는 문제고, taskcraft는 그 representation으로부터 행동을 복원하거나 최소한 행동 학습을 안내할 수 있어야 하는, 생성적/예측적 요구가 얹혀 있는 문제다.

세 번째 차이는 embodiment 특정 요소를 다루는 방식이다. STDR의 Grasping Regulation Module은 그리퍼라는 특정 embodiment를 전제로 설계된 검증기다. 이 모듈이 있어야 "물체를 안 잡았는데 다음 단계로 보상이 새는" 문제를 막는데, taskcraft 관점에서 보면 이건 embodiment-specific grounding의 전형적인 예다. STDR은 이걸 문제 삼지 않지만(embodiment가 고정이므로), taskcraft는 이런 "단계 완료를 검증하는 컴포넌트"를 embodiment마다 별도로 두되 그 위의 stage/progress 구조는 공유하는 식의 계층 분리를 스스로 설계해야 한다.

## taskcraft가 가져다 쓸 수 있는 부분

가장 값진 부분은 거시적 단계 전이와 미시적 단계 내 진행도를 분리하는 이중 계층 설계 자체다. VIP, LIV류의 전역 유사도 기반 보상이 겪는 정체(plateau) 문제는 taskcraft에서도 그대로 재현될 가능성이 크다. human video에