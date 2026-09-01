# INDI 논문 리뷰: taskcraft 관점에서

## 이 논문이 실제로 하는 일

Act with Intent(INDI)는 단일 embodiment, 즉 로봇 팔 하나를 대상으로 하는 VLA 정책 내부에 "이 행동 구간이 지금 왜 필요한가"라는 intent 표현을 끼워 넣는 연구다. 학습 시에만 존재하는 teacher VLM이 이미 실행된 행동 구간(관측, 지시, 대략적 액션 요약, 비디오)을 사후에 해석해서 intent 타깃과 목적문 타깃을 만들고, 배포되는 디코더는 그 타깃을 중간 레이어에서 복원하도록 증류받는다. 핵심은 이 intent가 단순한 보조 손실(auxiliary loss)로 붙는 게 아니라, 게이트 $$\alpha \sim \text{Bernoulli}(0.5)$$로 강제된 정보 병목을 통과해야만 액션 예측에 영향을 줄 수 있고, intent-mismatch loss로 그 내용이 실제로 다운스트림 예측을 좌우하는지까지 검증한다는 점이다.

taskcraft는 사람 시연이라는 다른 embodiment의 관측에서 latent task representation을 뽑아 로봇에 이식하는 것이 목표이므로, 문제 설정 자체는 INDI와 크게 다르다. 그런데 "latent가 정말 의미 있는 정보를 담고 있는가"를 어떻게 강제하고 검증할 것인가라는 방법론 층위에서는 참고할 지점이 많다.

## 핵심 차이: intent는 embodiment 내부의 의미론, taskcraft의 latent는 embodiment 사이의 대응

가장 근본적인 차이는 이것이다. INDI의 intent는 teacher VLM이 같은 로봇, 같은 관측 공간, 같은 액션 공간 안에서 "이 궤적이 수행한 국소적 목적"을 사후에 언어와 시각으로 재서술한 것이다. 즉 저수준 실현(어떻게 움직였는가)과 고수준 목적(무엇을 이루려 했는가)을 같은 embodiment 안에서 분리하는 문제다. 반면 taskcraft가 필요로 하는 latent world model은 사람 손의 움직임과 로봇 관절의 움직임처럼 액션 공간과 관측 공간 자체가 다른 두 embodiment 사이에서 공유되는 task representation을 찾아야 한다. INDI에서는 애초에 "다른 신체 구조로 이식했을 때도 이 표현이 여전히 유효한가"라는 질문이 제기되지 않는다. teacher와 학생 디코더가 같은 로봇 데이터, 같은 액션 파라미터화를 공유하기 때문에, intent 표현이 embodiment-specific한 단서(관절 배치, 그리퍼 형태 등)에 암묵적으로 의존해도 아무 문제가 드러나지 않는다.

이 차이는 학습 신호의 방향에도 나타난다. INDI는 이미 실행된 로봇 행동을 teacher가 해석해서 지도 신호를 만드는 사후적(post-hoc), 단일 도메인 증류다. taskcraft는 사람 시연이라는 소스 도메인에서 뽑은 표현을 로봇이라는 타깃 도메인에서 실제로 사용 가능해야 하는 교차 도메인 전이 문제다. 따라서 INDI가 정렬 손실 $$\mathcal{L}_I$$에서 사용하는 코사인 유사도 정렬은 "같은 좌표계 안에서 두 표현을 가깝게 만드는" 것이지만, taskcraft에서는 애초에 사람 도메인과 로봇 도메인이 같은 좌표계에 있다는 보장 자체가 없다는 점을 계속 의식해야 한다.

## taskcraft가 가져다 쓸 수 있는 부분

방법론적으로 가장 값진 것은 latent 표현이 지름길을 학습하지 않고 실제로 쓰이는지를 검증하는 두 가지 장치다.

첫째, 정보 병목을 확률적으로 강제하는 게이트다. INDI는 학습 중 $$\alpha=0$$일 때 VLA 문맥에 대한 직접 접근을 차단해서, 문맥 정보가 반드시 intent 쿼리라는 좁은 통로를 통과하도록 만든다. taskcraft의 latent world model에서도 로봇 정책이 관측을 직접 참조할 수 있는 우회로가 남아 있으면, latent가 사람 시연의 task 의미를 담기보다 로봇 자신의 관측에서 지름길을 찾을 위험이 있다. 이 게이팅 아이디어는 사람 시연에서 뽑은 latent가 실제로 정책의 유일한 조건 신호가 되도록 학습 스케줄을 설계하는 데 그대로 응용할 수 있다.

둘째, intent-mismatch loss 형태의 검증 장치다.

$$
\mathcal{L}_{\mathrm{mis}} = \max\!\left(0,\ m + \mathcal{D}_{\mathrm{right}} - \mathcal{D}_{\mathrm{swap}}\right)
$$

이 손실은 올바른 latent를 썼을 때의 다운스트림 손실이 배치 내 다른 샘플의 latent로 바꿔치기했을 때보다 확실히 낮아지도록 강제한다. taskcraft에서 이는 곧바로 "이 latent가 정말 이 task를 나타내는가"를 검증하는 진단 도구이자 학습 손실로 변형될 수 있다. 예를 들어 같은 task를 다른 embodiment(사람, 로봇)에서 뽑은 latent끼리는 바꿔 넣어도 정책 손실이 크게 나빠지지 않아야 하고(embodiment-invariance), 서로 다른 task의 latent를 바꿔 넣으면 손실이 확실히 나빠져야 한다(task-discriminativeness)는 이중 기준으로 확장해서 쓸 수 있다. 즉 mismatch loss를 하나 더 분기시켜 "같은 task, 다른 embodiment"와 "다른 task"를 구분하는 대조 신호로 재설계하면, latent world model이 embodiment-agnostic한 축과 task-specific한 축을 분리해서 학습하는지 직접 점검할 수 있다.

셋째, 표현 정렬을 별도의 생성 헤드 없이 처리하는 self-conditioning 방식(clean target으로 학습하고 no-gradient로 재노이즈한 예측을 입력으로 쓰는 방식)도, 사람 비디오의 미래 프레임이나 궤적을 보조 타깃으로 latent world model에 지도할 때 추가 디코더 없이 표현 공간에서 바로 정렬하는 가벼운 구현으로 참고할 만하다.

## taskcraft가 이 논문과 달리 반드시 유지해야 할 부분

가장 중요한 것은 embodiment-invariance를 검증하는 축을 별도로 확보하는 것이다. INDI는 teacher와 학생이 같은 로봇 데이터를 보기 때문에 intent 표현이 로봇의 신체 구조에 특이적인 정보를 얼마나 담고 있는지 전혀 측정하지 않는다. taskcraft는 latent가 사람 손 궤적과 로봇 관절 궤적 양쪽에서 동일한 task 축을 가리키는지, 즉 embodiment를 바꿔도 latent에서 복원되는 task 의미가 보존되는지를 명시적인 평가 지표(예: cross-embodiment retrieval, latent swap 후 정책 성공률)로 반드시 따로 확인해야 한다. 이 논문의 mismatch loss를 그대로 가져오되, "다른 embodiment, 같은 task"라는 조건을 추가하지 않으면 INDI와 같은 함정, 즉 latent가 특정 신체의 저수준 실현 정보를 몰래 인코딩하고도 검증을 통과하는 상황을 그대로 재현하게 된다.

둘째, teacher의 역할 차이를 유지해야 한다. INDI의 teacher VLM은 이미 실행된 로봇 행동을 사후에 해석하는, 말하자면 지도(supervision) 생성기다. taskcraft에서 latent world model은 그 자체가 사람 비디오라는 다른 도메인의 관측을 예측/설명하는 생성 모델이어야 하며, 단순히 로봇 행동에 대한 사후 해설을 만드는 역할로 축소되어서는 안 된다. 즉 taskcraft의 latent는 정책 학습의 보조 타깃이기 이전에, 서로 다른 두 도메인의 관측을 공통으로 설명할 수 있는 world model의 상태여야 한다는 원래 목표를 놓치지 않아야 한다.

셋째, BC vs DAgger vs PPO 비교라는 현재 스코프에서, INDI가 보여준 "행동 복제 손실 위에 의미론적 목적 신호를 추가하면 크게 개선된다"는 결과는 alignment 신호의 효과이지 policy learning 알고리즘 선택의 효과가 아니라는 점을 구분해서 봐야 한다. taskcraft의 BC/DAgger/PPO 비교는 latent 표현이 고정된 상태에서 정책 학습 방식이 covariate shift와 exploration을 어떻게 다루는지를 보는 것이므로, INDI식 intent 증류를 도입하더라도 그것이 BC 계열의 문제(누적 오차, 분포 이탈)를 대신 해결해주는 것은 아니라는 점을 명확히 유지해야 한다. INDI의 장치는 latent 품질을 높이는 정칙화 기법으로만 받아들이고, MineRL testbed에서의 알고리즘 비교 축과는 독립적으로 다뤄야 taskcraft 실험 설계가 흐려지지 않는다.

## 정리

INDI는 taskcraft와 문제 설정이 다르지만, "latent가 실제로 의미 있는 정보를 담고 있는지"를 정보 병목과 mismatch loss로 강제하고 검증하는 구체적인 공학적 장치를 제공한다는 점에서 참고 가치가 크다. 다만 이 논문은 단일 embodiment 안에서의 의미론적 분리 문제이므로, taskcraft는 이 장치들을 가져오되 반드시 embodiment를 가로지르는 검증 축(같은 task, 다른 embodiment에서 latent를 교환해도 정책이 성립하는가)을 추가로 설계해야 하고, latent world model이 사후 해설 생성기로 축소되지 않도록 원래의 world model 목표를 유지해야 한다.