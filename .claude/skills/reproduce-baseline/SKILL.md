---
name: reproduce-baseline
description: |
  VPT, STEVE-1 등 공개 baseline 코드/checkpoint를 taskcraft 환경(MineRL v1.0,
  RTX 5060Ti 16GB)에서 재현 가능한 형태로 세팅한다. 원본 repo의 요구사항을
  우리 환경 제약(VRAM, Docker/WSL2)에 맞게 조정한다.
  사용자가 "VPT 재현해줘", "이 baseline 돌려봐", "checkpoint 가져와서 테스트해줘"라고
  할 때 사용한다.
---

# When to use
- 공개된 pretrained checkpoint(VPT, STEVE-1 등)를 처음 가져와서 돌려볼 때
- 원본 논문의 실험을 우리 스코프(나무~철 채굴)로 축소 재현할 때

# Procedure
1. 원본 repo의 requirements(Python 버전, CUDA 버전, VRAM 요구량)를 확인
2. VRAM이 16GB를 초과하면: 풀 파인튜닝 대신 encoder freeze + 경량 head만 학습하는
   방식으로 조정 방안을 먼저 제시하고 사용자 확인을 받는다 (CLAUDE.md 원칙과 일치)
3. 설치 방식은 기본적으로 WSL2 네이티브(pip/conda)로 한다. Docker는 원본 repo가
   공식 유지보수 이미지를 제공하는 경우에만 사용하고, 없다고 해서 새로
   Dockerfile을 작성하지 않는다 — MineRL 사례처럼 관리 부담 대비 이득이
   적을 수 있다 (docs/research_notes/02_mineRL_install_strategy.md 참고)
4. 최소 검증: 원본 논문의 데모 태스크 1개만 우리 환경에서 재현해서 숫자가
   비슷한 범위인지 확인 (완전 일치는 기대하지 않음)
5. 재현 과정, 막힌 지점, 조정한 부분을 `docs/research_notes/`에 별도 파일로 기록
   (paper-review skill과 별개로, "재현 로그"로 남긴다)

# Don't
- VRAM 확인 없이 바로 원본 설정 그대로 학습을 시작하지 않는다
- 재현이 안 돼도 원인 파악 없이 다음 단계로 넘어가지 않는다 — 왜 안 됐는지가
  기록으로서 더 가치 있을 수 있다
- 공식 이미지가 없다는 이유만으로 자동으로 Dockerfile부터 작성하지 않는다 —
  먼저 네이티브 설치로 되는지 확인 후 필요성을 재평가한다