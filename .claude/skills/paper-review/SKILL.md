---
name: paper-review
description: |
  논문(arXiv PDF, URL, 또는 붙여넣은 텍스트)을 읽고 terrain mapping → mechanism →
  critical evaluation 구조로 요약해 docs/research_notes/에 정형 노트로 저장한다.
  사용자가 논문 링크나 PDF를 주면서 "정리해줘", "요약해줘", "읽어줘"라고 하거나,
  VPT/GROOT/DreamerV3/Voyager 등 이 프로젝트가 참고하는 논문을 다룰 때 사용한다.
---

# When to use
- 사용자가 arXiv 링크, PDF, 또는 논문 텍스트를 주며 정리를 요청할 때
- "이 논문 읽어줘", "노트 만들어줘" 같은 명시적 요청
- docs/roadmap.md에 나열된 우선순위 논문(VPT, GROOT, DreamerV3, Voyager 등)을 다룰 때

# Procedure
1. 논문에서 핵심 정보를 추출: 문제 정의, 방법, 실험 셋업, 결과, 한계
2. 아래 3단계 구조로 `docs/research_notes/{NN}_{논문이름}.md`에 저장:

```markdown
# {논문 제목}

## 1. Terrain Mapping (이 논문이 속한 지형)
- 어떤 서브필드인가 (예: Cross-Embodiment Imitation, World Model)
- 기존 연구 대비 무엇이 새로운가 (한두 문장)

## 2. Mechanism (핵심 메커니즘)
- 방법론을 다이어그램/수식 없이 자연어로 설명
- 이 프로젝트(taskcraft)와 겹치는 컴포넌트는 무엇인가 (예: observation encoder, action space)

## 3. Critical Evaluation
- 이 논문의 가정 중 taskcraft 스코프(나무~철 채굴)에서 깨지는 것은?
- 그대로 가져다 쓸 부분 vs 참고만 할 부분 구분
- 우리 프로젝트에 바로 적용 가능한 구체적 아이디어 1~2개
```

3. 파일명 번호는 기존 research_notes/ 파일들 중 가장 큰 번호 다음으로 매긴다
4. 저작권: 원문을 그대로 복사하지 않는다. 모든 요약은 자기 언어로 재작성.

# Don't
- "좋은 논문이다" 식의 평가 없는 요약으로 끝내지 않는다 — 반드시 3번(Critical Evaluation) 포함

# 스타일
작성 스타일(비유 최소화, 원문 복사 금지 등)은 .claude/rules/note-style.md를 따른다.
docs/ 안 파일이라 자동으로 적용됨.
