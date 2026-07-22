# 05. Frozen encoder 4종(VPT/R3M/VIP/CLIP) 설치와 GPU 연산 확인

## 배경/질문
마일스톤 2(Observation pipeline)를 시작하기 전에, position_paper.md의 검증 계획에서
비교 대상으로 잡은 네 개의 frozen visual encoder(VPT, R3M, VIP, CLIP)를 실제로
설치하고, 같은 인터페이스(`src/vision/encoders.py`의 `get_encoder(name).encode(frames)`)
뒤에서 GPU로 forward pass가 도는 것까지 확인하는 과정을 기록한다. 04번 노트가
"MineRL 자체가 도는가"를 다뤘다면, 이 노트는 "그 위에서 시각 표현을 뽑는 4개
인코더가 GPU에서 동작하는가"를 다룬다.

## PyTorch/CUDA 설치와 GPU 커널 미스매치

### 증상과 원인
04번 노트 시점에는 아직 PyTorch를 설치하지 않은 상태였다. 처음 설치한 조합은
`torch==2.6.0+cu124`였는데, `torch.cuda.is_available()`은 `True`를 반환하지만
실제 텐서 연산(행렬곱)을 GPU에서 실행하면 다음 에러가 났다.

```
RuntimeError: CUDA error: no kernel image is available for execution on the device
```

이 GPU는 RTX 5060 Ti(Blackwell 아키텍처, compute capability `sm_120`,
`nvidia-smi --query-gpu=name,driver_version,compute_cap`로 확인)다. `cu124` 빌드
시점에는 아직 Blackwell용 커널이 PyTorch 배포 바이너리에 포함되지 않았던 것으로
보인다 — `is_available()`이 `True`인 이유는 드라이버/CUDA 런타임 자체는 인식되기
때문이고, 실제 연산에 필요한 GPU 아키텍처별 컴파일된 커널이 그 wheel 안에
없어서 실행 시점에만 실패한다. 즉 "설치가 됐다"와 "이 GPU에서 동작한다"가
분리되는 사례다.

### 해결
`torch==2.6.0+cu124`, `torchvision`을 제거하고 `torch==2.8.0+cu128`,
`torchvision==0.23.0+cu128`을 `https://download.pytorch.org/whl/cu128` 인덱스에서
재설치했다. 재설치 후 GPU 행렬곱이 실제로 성공하는 것을 확인했다(수치 결과까지
출력해서 확인, 단순히 에러가 안 나는 것 이상을 확인함).

**유의할 점**: `cuda.is_available() == True`는 GPU 커널 호환성을 보장하지
않는다. 새 GPU 세대(특히 출시된 지 얼마 안 된 아키텍처)를 쓸 때는 설치 직후
반드시 실제 연산을 한 번 돌려서 확인해야 한다. 단순 `import torch; print(torch.cuda.is_available())`로는
불충분하다.

## Claude Code Bash 도구의 샌드박스와 Smart App Control 충돌

### 증상
같은 `torch` import 코드가 사용자의 PowerShell 세션에서는 성공하는데, 이 세션의
Bash 도구로 실행하면 실패하는 현상을 겪었다. 처음에는 "누가 설치 명령을
실행했는지가 이후 import 성공 여부에 영향을 줄 리 없다"고 판단했는데, 이는
틀린 판단이었다 — 사용자가 직접 동일한 import를 자신의 PowerShell에서 실행해
성공시킴으로써 반증됐다.

### 원인
실제 원인은 "누가 설치했는가"가 아니라 "누가/어떤 프로세스가 지금 이 코드를
실행하는가"였다. Claude Code의 Bash 도구는 샌드박스화된 실행 컨텍스트에서
프로세스를 띄우는데, Windows의 Smart App Control(코드 무결성 정책,
`HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy\VerifiedAndReputablePolicyState`로
확인 가능)이 이 샌드박스 프로세스가 로드하려는 네이티브 DLL(CUDA 관련 DLL 포함)을
신뢰하지 않은 것으로 보인다. 사용자의 일반 PowerShell 세션은 이 정책의 적용을
받지 않아 문제없이 로드된다.

### 대응 규칙
이후로는 torch/CUDA를 실제로 건드리는 코드(스모크 테스트, 인코더 검증 등)는
전부 사용자가 직접 자신의 PowerShell 세션에서 실행하고, 결과를 콘솔 출력
그대로 붙여넣는 방식으로 전환했다. Claude Code 쪽에서는 코드 작성과 로그 해석만
담당한다. `dangerouslyDisableSandbox` 옵션으로 우회하는 방법도 있지만, GPU
드라이버 레벨 코드를 원격 에이전트 권한으로 실행하는 것 자체가 바람직하지
않다고 판단해 쓰지 않았다.

## third_party/ 벤더링 방식

VPT, R3M, VIP는 PyPI 패키지가 아니라 각 저자의 GitHub 저장소를 직접 클론해서
쓴다. 세 저장소 모두 `third_party/`(저장소 루트에 위치, `.gitignore`에 등록,
커밋하지 않음) 아래 클론했고, 재현성을 위해 실제로 사용한 커밋 해시를 남긴다.

| 프로젝트 | 저장소 | 사용 커밋 |
|---|---|---|
| VPT | `openai/Video-Pre-Training` | `095519f` (2025-09-03) |
| R3M | `facebookresearch/r3m` | `b2334e7` (2022-08-17) |
| VIP | `facebookresearch/vip` | `f98ca99` (2023-10-19) |

CLIP만 벤더링하지 않고 `open_clip_torch`(PyPI, 3.3.0)를 그대로 pip install해서
썼다 — CLIP은 OpenAI가 파이썬 패키지로 공식 배포하지 않지만, `open_clip`이
가중치까지 포함해 관리하는 사실상 표준 구현이라 별도로 클론할 이유가 없었다.

### R3M/VIP를 `--no-deps`로 설치한 이유
`third_party/r3m/setup.py`와 `third_party/vip/setup.py`의 `install_requires`를
비교하면, VIP 쪽이 `omegaconf==2.1.1`, `hydra-core==1.1.1`, `pillow==9.0.1`,
`gdown==4.4.0`처럼 특정 버전에 고정돼 있다(2023년 기준 최신). 이미 설치된
`pillow==11.3.0`(R3M/VIP가 요구하는 이미지 리사이즈에 문제없이 동작) 등을
낡은 버전으로 덮어쓰지 않기 위해, 두 패키지 모두 `pip install -e . --no-deps`로
설치하고, 실제로 필요한 의존성(`gdown`, `omegaconf`, `hydra-core`)만 최신
호환 버전으로 별도 설치했다(`gdown==5.2.2`, `omegaconf==2.3.1`,
`hydra-core==1.3.4` — 세 버전 모두 R3M/VIP의 `load_r3m()`/`load_vip()` 호출
경로에서 실제로 동작 확인됨). VPT는 pip 패키지 형태가 아니라(`setup.py`가
따로 없음) 클론한 디렉토리를 `sys.path`에 직접 추가해서 임포트하는 방식이라
이 문제 자체가 없다.

### 체크포인트 다운로드
- VPT: `models/foundation-model-1x.{model,weights}`(가중치 284MB)를
  `openai/Video-Pre-Training` 저장소 README가 안내하는 URL에서 수동으로 받아
  `third_party/vpt/models/`에 저장했다.
- R3M/VIP: 코드 안에서 자동으로 받는다. `load_r3m("resnet50")`/`load_vip()`를
  처음 호출하면 `gdown`으로 Google Drive에서 받아 각각
  `~/.r3m/r3m_50/model.pt`, `~/.vip/model.pt`에 캐싱한다(두 번째 호출부터는
  캐시를 그대로 씀). Google Drive 다운로드라 다운로드 용량 제한/바이러스 검사
  경고에 걸릴 수 있다는 점은 알아둘 것 — 이번 설치에서는 문제 없이 받아졌다.
- CLIP: `open_clip.create_model_and_transforms("ViT-B-32-quickgelu", pretrained="openai")`
  호출 시 자동으로 받아 `open_clip` 자체 캐시 디렉토리에 저장한다.

## VPT 인코더 통합 중 발견한 shape 버그

`src/vision/encoders.py`의 `VPTEncoder.encode()`를 처음 작성했을 때
`MinecraftPolicy.net()` 호출에서 다음 에러가 났다.

```
ValueError: not enough values to unpack (expected 2, got 1)
```

원인은 VPT의 policy network가 `(batch, time, H, W, C)` 5차원 입력을 기대하는데,
이미지 한 장을 `(batch, H, W, C)` 4차원으로만 넣었기 때문이다. VPT 저장소의
`MinecraftAgentPolicy.act()`를 읽어보면 관측값을
`tree_map(lambda x: x.unsqueeze(1), obs)`로 시간 축을 하나 끼워 넣은 뒤에야
`net()`을 호출한다 — VPT가 원래 시퀀스(recurrent) 입력을 받는 모델이라, 프레임
하나만 넣을 때도 길이 1짜리 시퀀스로 포장해야 하는 것이다. `first`(에피소드
시작 여부 플래그)도 같은 이유로 시간 축이 필요해 `unsqueeze(1)`을 추가해야
했다. 이 두 곳을 고쳐서 해결했다(`encoders.py`의 `img = ...[None, None]`,
`first = self._agent._dummy_first.unsqueeze(1)`).

이 프로젝트에서는 VPT의 시간적/recurrent 문맥은 쓰지 않는다 — 매 프레임마다
hidden state를 리셋하고 독립적으로 인코딩한다. VPT를 포함시킨 이유는 행동
정책(action policy)과 결합된 시각 표현이 R3M/VIP/CLIP 같은 "행동과 분리된"
표현과 실제로 다른 정보를 담는지 비교하기 위해서다 — 시간 축 자체를 비교
대상으로 삼는 게 아니라서 recurrent 문맥은 의도적으로 배제했다.

## 결과
GPU(RTX 5060 Ti)에서 4개 인코더 모두 fake 프레임(64x64x3, MineRL POV와 동일
해상도) 3장을 넣어 forward pass 성공, 선언된 `feature_dim`과 실제 출력 shape가
일치함을 확인했다.

| 인코더 | feature_dim |
|---|---|
| VPT | 1024 |
| R3M | 2048 |
| VIP | 1024 |
| CLIP (ViT-B-32-quickgelu) | 512 |

`src/vision/encoders.py`에 통합 인터페이스로 커밋(`a8ac9a3`)했다.
`third_party/`(클론한 소스 + 다운로드한 체크포인트)는 `.gitignore`에 등록해
커밋하지 않는다.

## 다른 컴퓨터에서 재현하려면

04번 노트의 절차(JDK 8, Python 3.9 venv, MineRL v1.0 설치)가 먼저 끝나 있다고
가정한 뒤, 이 노트가 다루는 부분만 정리하면 다음과 같다.

1. **GPU 아키텍처를 먼저 확인한다.**
   `nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv`로
   compute capability를 확인하고, 그 세대를 지원하는 PyTorch 빌드를 고른다.
   이 프로젝트는 Blackwell(`sm_120`) 기준 `cu128` 인덱스가 필요했다 — GPU
   세대가 다르면 필요한 인덱스도 달라질 수 있으니 그대로 복사하지 말고
   [pytorch.org](https://pytorch.org)의 설치 매트릭스에서 다시 확인해야 한다.
2. `torch`, `torchvision`을 설치한 뒤, `is_available()` 확인에서 그치지 말고
   실제 GPU 행렬곱(`(torch.randn(...) @ torch.randn(...)).sum()`처럼 결과값이
   나오는 연산)까지 돌려서 확인한다.
3. **AI 에이전트(Claude Code 등)의 샌드박스 실행 환경에서 Windows Smart App
   Control이 걸려 있는 머신이라면**, torch/CUDA를 직접 만지는 코드는 에이전트의
   셸 도구가 아니라 사용자 자신의 터미널 세션에서 실행해야 한다. 사전에
   `HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy\VerifiedAndReputablePolicyState`
   레지스트리 값으로 Smart App Control 활성화 여부를 확인해두면 원인 파악
   시간을 아낄 수 있다.
4. `third_party/` 아래 위 표의 커밋 해시로 VPT/R3M/VIP를 클론한다.
   - VPT: README가 안내하는 링크에서 `foundation-model-1x.model`/`.weights`를
     받아 `third_party/vpt/models/`에 둔다.
   - R3M/VIP: `pip install -e . --no-deps`로 설치하고, `gdown`/`omegaconf`/
     `hydra-core`를 최신 버전으로 별도 설치한다(정확한 버전은 위 "third_party/
     벤더링 방식" 절 참고). 체크포인트는 `load_r3m()`/`load_vip()`를 처음
     호출할 때 자동으로 받아지므로 수동 다운로드가 필요 없다. 다만 인터넷이
     막혀 있으면(사내망 등) Google Drive 접근이 안 될 수 있다.
5. `open_clip_torch`는 일반 `pip install`로 충분하다.
6. `scratchpad/encoders_unified_test.py`(또는 동등한 스크립트)로
   `get_encoder(name).encode(fake_frames)`가 4개 인코더 모두에서 선언된
   `feature_dim`과 일치하는 shape를 반환하는지 확인한다.

## 다음에 할 것
- 마일스톤 2 본작업: 실제 MineRL POV 프레임(랜덤 노이즈가 아닌 진짜 게임
  화면)을 이 4개 인코더에 통과시켜 시각화/비교.
- 저녁 이론 공부: VPT 논문(arXiv:2206.11795)부터, 오늘 넣은 4개 인코더가 각각
  왜 필요했는지(R3M/VIP가 embodiment-agnostic 표현으로서 실제로 뭘 보장하는지,
  CLIP을 control로 넣은 이유가 타당한지) 하나씩 재검토.
