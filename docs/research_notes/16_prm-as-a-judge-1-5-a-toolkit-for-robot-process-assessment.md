# PRM-as-a-Judge 1.5 리뷰: taskcraft 관점에서

## 이 논문이 실제로 하는 일

PRM-as-a-Judge 1.5는 로봇 조작 롤아웃 비디오를 입력받아, Process Reward Model을 통해 시간에 따른 진행도 곡선 $$p_{0:T}$$를 뽑고, 그 곡선 위에서 최대 진행도(MP), 마일스톤 도달율(MC@q), 경로 가중 진행 길이(PPL), 누적 후회 면적(CRA), 정체 비율(STR), 그리고 1.5에서 새로 추가된 실패 근접도(FNS), 하강 회복률(DRR), 성공 품질 점수(SQS)를 계산하는 평가 툴킷입니다. 핵심은 이진 성공률 하나로는 구분되지 않는 실행 품질의 결을 조밀한 진행도 곡선으로부터 뽑아내는 것이고, 그 진행도 곡선을 생성하는 PRM 자체의 신뢰도를 RoboPulse++라는 구간 단위 벤치마크로 검증한다는 점입니다.

이걸 taskcraft 스코프, 즉 사람 시연 영상에서 embodiment-agnostic task representation을 뽑아 Latent World Model을 매개로 다른 형태의 에이전트에 이식하고 MineRL에서 BC, DAgger, PPO를 비교하는 프로젝트에 놓고 보면, 이 논문은 taskcraft가 풀려는 문제, 즉 "표현을 어떻게 뽑고 어떻게 다른 embodiment로 옮기는가"에는 전혀 관여하지 않습니다. 이 논문은 이미 어떤 정책이 어떤 embodiment 위에서 만들어낸 롤아웃이 주어졌다는 것을 전제하고, 그 롤아웃의 사후 진단만을 다룹니다. 즉 이 논문의 스코프는 taskcraft 파이프라인의 맨 끝, 평가 단계에만 해당합니다.

## 핵심 차이: 표현/전이 문제 vs 사후 진단 문제

taskcraft의 핵심 기여는 사람 시연 영상에서 embodiment에 묶이지 않는 task representation을 latent space에서 뽑아내고, 그 latent가 World Model을 매개로 서로 다른 형태의 에이전트 행동으로 어떻게 그라운딩되는지를 규명하는 것입니다. 반면 이 논문은 그런 표현이나 전이 메커니즘에는 관심이 없고, 이미 존재하는 정책의 실행 결과를 조밀하게 채점하는 방법론입니다. 다시 말해 이 논문의 PRM은 taskcraft의 Latent World Model과 역할이 겹치는 것처럼 보이지만 실제로는 완전히 다른 층위에 있습니다. taskcraft의 Latent World Model은 표현을 만들고 행동을 생성하는 데 관여하는 forward, 생성적 모델인 반면, 이 논문의 PRM은 이미 생성된 궤적을 평가하는 discriminative judge입니다. 이 둘을 혼동해서 taskcraft의 Latent World Model에게 "진행도 판단" 역할까지 억지로 얹으려 하면 안 됩니다. 표현 학습과 전이를 담당하는 모듈과, 그 결과를 평가하는 judge는 taskcraft에서도 분리된 모듈로 유지하는 게 맞습니다.

또 하나 중요한 차이는, 이 논문의 PRM은 단일 embodiment(로봇 팔) 안에서의 sim-to-real 격차를 다루지, 서로 다른 형태의 embodiment 간 task 성취 의미론의 일관성은 다루지 않는다는 점입니다. Figure 8에서 보이는 sim과 real 사이의 최대 진행도 격차는 물리 시뮬레이션의 부정확성 문제이지, taskcraft가 마주할 "사람 손의 pick-up 동작"과 "MineRL 에이전트의 인벤토리 조작"처럼 행동 공간 자체가 다른 embodiment 간 격차와는 성질이 다릅니다. taskcraft가 이 논문에서 얻을 수 있는 건 진단 지표의 아이디어이지, embodiment-agnostic한 진행도 정의 자체는 아닙니다. 진행도를 어떤 표현 공간에서 잴 것인가라는 질문에 이 논문은 답을 주지 않고, 그 답은 여전히 taskcraft의 Latent World Model이 책임져야 합니다.

## taskcraft가 가져다 쓸 수 있는 부분

가장 직접적으로 빌려올 만한 것은 BC, DAgger, PPO를 비교할 때 최종 성공률 하나로 뭉뚱그리지 않는 평가 프로토콜입니다. MineRL 테스트베드에서 BC는 학습 분포를 벗어나면 스스로 복구하지 못한다는 게 잘 알려진 실패 양상인데, 이건 정확히 DRR과 CRA가 잡아내려는 현상입니다. 진행도 곡선에서 최대 낙폭이 발생한 시점 $$t^*$$ 이후 회복 정도를 재는 다음 식은 그대로 taskcraft의 진단 지표로 채택할 만합니다.

$$ d_t = \max_{0 \le i \le t} p_i - p_t, \quad t^* \in \arg\max_t d_t $$

$$ \text{DRR} = \min\left(1, \frac{\max_{t^* \le t \le T} p_t - p_{t^*}}{d_{t^*}}\right), \quad d_{t^*} > 0 $$

DAgger가 covariate shift를 줄인다고 주장할 때, 이 개선이 단순히 정체 없이 매끄럽게 도는 것(STR 개선)인지, 실제로 이탈 후 복구 능력이 향상된 것(DRR 개선)인지를 나눠서 볼 수 있다는 점은 taskcraft 논문에서 BC vs DAgger 차이를 서술할 때 