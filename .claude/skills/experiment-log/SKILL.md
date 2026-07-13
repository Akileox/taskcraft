---
name: experiment-log
description: |
  실험 결과(BC/DAgger/PPO 학습 run, 하이퍼파라미터, 성공/실패, 다음 시도 아이디어)를
  docs/experiment_log.md에 정형화된 포맷으로 기록한다.
  사용자가 "실험 기록해줘", "이번 run 로그 남겨줘", "오늘 결과 정리해줘"라고 하거나,
  학습/평가 스크립트 실행이 끝난 직후, 또는 하이퍼파라미터를 바꿔 재실험할 때 사용한다.
---

# When to use
- 사용자가 "기록해줘", "로그 남겨줘", "정리해줘"라고 명시적으로 요청할 때
- 학습(train)이나 평가(eval) 스크립트가 끝난 직후, 결과 확인 후 자동으로 제안
- config를 바꿔서 재실험을 시작하기 직전 (이전 run과 뭐가 달라졌는지 diff 남기기 위해)

# Procedure
1. 방금 실행한 스크립트의 config(yaml)와 커맨드를 확인한다
2. 결과 지표(성공률, reward, loss 등)를 스크립트 출력이나 wandb/로그 파일에서 가져온다
3. 아래 포맷으로 `docs/experiment_log.md`에 새 항목을 append한다:

```markdown
## [YYYY-MM-DD] {실험 이름}
- Task: (예: wood → crafting table)
- Method: (BC / DAgger / PPO / ...)
- Config: (파일 경로 또는 핵심 하이퍼파라미터 3~5개)
- Result: (정량 지표 + 정성적 관찰)
- 실패/이상 징후: (있다면)
- 다음 시도: (구체적으로 뭘 바꿀지)
```

4. 이전 항목과 비교해서 개선/악화 여부를 한 줄로 요약해 덧붙인다
5. 특이한 실패 패턴이면 `docs/research_notes/`에 별도로 원인 분석을 남길지 사용자에게 물어본다

# Don't
- 이전 로그를 덮어쓰지 않는다 (항상 append)

# 스타일
작성 스타일(비유 최소화, 측정 가능한 서술 등)은 .claude/rules/note-style.md를 따른다.
docs/ 안 파일이라 자동으로 적용됨.
