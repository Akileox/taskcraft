# Zero-WAM 리뷰: taskcraft 관점에서

## 이 논문이 실제로 풀고 있는 문제의 축

Zero-WAM은 겉보기에 taskcraft와 매우 비슷한 재료를 쓴다. 인간 시연 비디오를 입력으로 받고, 로봇이 그 비디오를 참고해서 미학습 task를 수행한다. 하지만 자세히 보면 이 논문이 일반화시키는 축은 taskcraft가 목표로 하는 축과 다르다. Zero-WAM은 "같은 로봇(embodiment)이 새로운 task를 zero-shot으로 수행"하는 것을 목표로 하고, 인간 비디오는 그 task를 지정해주는 In-Context 예시일 뿐이다. 액션은 언제나 그 로봇 자신이 생성한 미래 로봇 비디오 $$x^{i+1}$$로부터 inverse dynamics로 디코딩되며, 인간 비디오는 액션 디코더에 직접 attend되지 않는다. 즉 이 논문은 human to robot의 embodiment gap을 "풀어야 할 문제"로 다루기보다, 아