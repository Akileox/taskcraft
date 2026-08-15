# DreamX-Phi 1.0 리뷰: taskcraft 관점

## 요약과 방향성 차이

DreamX-Phi 1.0은 양팔 로봇의 SE(3) 궤적을 어텐션 연산 자체에 새겨 넣어(PRoPE), 주어진 액션에 충실한 고품질 비디오 롤아웃을 생성하는 모델이다. 핵심은 액션 조건부 비디오 생성(action to video)이라는 순방향 문제이고, 목표는 특정 embodiment(양팔 로봇)에서의 물리적, 기하학적 충실도다.

taskcraft가 풀려는 문제는 방향이 반대다. 사람 시연 영상에서 embodiment에 종속되지 않는 task representation을 뽑아내는(video to latent) 역방향 문제이며, 그 latent를 다시 다른 embodiment의 action space로 풀어내는(latent to action, cross embodiment) 양방향 매핑이 필요하다. DreamX-Phi의 PRoPE는 정확히 이 지점에서 taskcraft와 반대되는 설계 철학을 보여준다. 이 논문은 로봇의 강체 운동 구조(양팔의 SE(3) 변환)를 어텐션 Q, K, V에 직접 하드코딩함으로써 특정 embodiment의 기구학을 모델 구조 자체에 각인시킨다. 이것이 액션 충실도를 크게 높이는 이유이기도 하지만, 동시에 이 구조는 embodiment가 바뀌면(팔 개수, 관절 구조, 액션 공간이 달라지면) 그대로 재사용할 수 없다는 뜻이다. taskcraft가 만들려는 Latent World Model은 정반대로, 어떤 embodiment의 액션 공간에도 종속되지 않는 task 상태 전이 표현을 학습해야 한다. 즉 DreamX-Phi가 "액션 구조를 모델에 새겨서 충실도를 높이는" 방향이라면, taskcraft는 "액션 구조를 모델에서 분리해서 전이 가능성을 높이는" 방향이다.

## taskcraft가 가져다 쓸 수 있는 부분

세 가지 요소는 방향은 반대여도 기법 자체는 차용할 가치가 있다.

첫째, 객체 중심 가중치 손실이다. 논문의 $$L_{\text{rgb}}^{\text{obj}}$$는 마스크 $$m_i$$로 조작 대상 영역의 손실 가중치를 높여, 화면 대부분을 차지하는 정적 배경 때문에 작은 조작 물체의 신호가 묻히는 문제를 해결한다. 이 아이디어는 taskcraft의 embodiment-agnostic 표현 학습에 그대로 적용할 수 있다. 사람 손과 Minecraft agent의 팔은 겉모습이 다르지만, task와 무관한 embodiment 고유의 시각적 세부(손 모양, 카메라 시점, agent 스킨)는 오히려 latent에서 억제하고, 블록이나 아이템 등 task 관련 엔티티의 상태 변화에 표현력을 집중시키는 방식으로 응용할 수 있다. 즉 이 논문은 "물체 영역을 강조"하지만 taskcraft는 "embodiment 비관련 영역을 억제하고 task 관련 상태 전이를 강조"하는 형태로 뒤집어 쓸 수 있다.

둘째, Frozen V-JEPA와의 Gram 행렬 정렬 손실이다. $$\ell_{\text{JEPA}}^{(b)} = \frac{1}{M_b^2} \lVert S_b S_b^\top - Q_b Q_b^\top \rVert_1$$ 방식은 특정 픽셀이나 피처 축에 얽매이지 않고 시공간적 관계 구조만 맞춘다는 점에서, 서로 다른 embodiment 간에도 유지되어야 할 상대적 관계(물체와 agent의 접촉, 상태 전이 순서 등)를 latent에 담아내는 정렬 신호로 재해석할 수 있다. taskcraft에서는 이를 사람 시연과 로봇, 혹은 human 데이터와 Minecraft agent 데이터 사이의 latent 정렬 손실로 변형해, embodiment는 다르지만 동일한 task를 수행하는 두 시퀀스의 관계 구조가 같도록 강제하는 데 쓸 수 있다.

셋째, DMD2 기반 few step 증류다. PPO 학습은 대량의 rollout을 필요로 하므로, Latent World Model을 policy 학습의 시뮬레이터로 쓸 경우 multi step flow matching 생성은 비용이 너무 크다. 이 논문의 few step distillation 기법은 학습 루프 안에서 world model을 빠르게 여러 번 굴려야 하는 taskcraft의 PPO 실험에 실용적으로 차용 가능하다.

## taskcraft가 이 논문과 달리 반드시 유지해야 할 부분

가장 중요한 것은 양방향성이다. DreamX-Phi는 액션이 주어졌을 때 영상을 생성하는 단방향 모델이지만, taskcraft의 Latent World Model은 영상에서 task latent를 인코딩하는 방향과, 그 latent를 특정 embodiment의 액션으로 디코딩하는 방향을 모두 가져야 한다. PRoPE처럼 특정 embodiment의 기하 구조를 모델 내부에 고정시키는 설계는 이 양방향 전이 가능성과 근본적으로 충돌하므로, taskcraft는 그런 embodiment 특