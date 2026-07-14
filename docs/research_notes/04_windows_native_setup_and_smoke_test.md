# 04. Windows 네이티브 설치(JDK8/Python/MineRL)와 GLFW 창 리사이즈 hang 해결 (마일스톤 1 완료)

## 배경/질문
03번 노트에서 Windows 네이티브로 전환을 결정한 뒤, 실제로 JDK 8 + Python 3.9 venv +
MineRL v1.0을 설치하고 마일스톤 1의 완료 기준(env 생성 + step 호출 성공)을 확인하는
과정을 기록한다.

## 설치 과정

### JDK 8
- winget으로 Eclipse Temurin 8(`EclipseAdoptium.Temurin.8.JDK`, 8.0.492.9) 설치.
  Temurin은 AdoptOpenJDK의 후신이고 Minecraft 모딩/MineRL 커뮤니티에서 가장 널리
  쓰이는 배포판이라 선택했다. (AdoptOpenJDK 자체 패키지는 더 이상 갱신되지 않음)
- `java -version` → `openjdk version "1.8.0_492"` (Temurin). `JAVA_HOME`, `PATH`가
  설치 프로그램에 의해 시스템 레벨에 자동 등록됨.
- 주의할 점: 설치 전에 이미 열려 있던 터미널(PowerShell, VSCode 통합 터미널 등)은
  PATH가 캐시돼 있어 설치 후에도 `java`를 못 찾는다. 새 터미널을 열어야 한다.
  이 문제로 실제로 한 번 삽질했다 — `java -version`이 안 될 때 시스템 레벨
  PATH(`[System.Environment]::GetEnvironmentVariable("Path","Machine")`)를 직접
  확인해서 실제로는 정상 등록됐다는 걸 확인한 뒤에야 원인이 터미널 세션 문제라는
  걸 알았다.

### Python 3.9
- winget으로 Python 3.9.13 설치(`Python.Python.3.9`). 프로젝트 루트에
  `py -3.9 -m venv .venv`로 가상환경 생성. `.gitignore`에 `.venv`가 이미
  등록돼 있어 커밋 문제는 없었다.

### MineRL v1.0 설치
PyPI의 `minerl` 패키지 최신 버전은 0.4.4(Malmo 계열, Minecraft 1.11.2)로,
CLAUDE.md에 고정한 v1.0(Minecraft 1.16.5, MCP-Reborn)과 다르다. v1.0은 PyPI에
없고 GitHub에서 직접 설치해야 한다. 태그는 v1.0.0/v1.0.1/v1.0.2가 있고, 최신
patch인 v1.0.2를 사용했다 (셋 다 아래 버그를 동일하게 가지고 있음을 확인함).

이 설치 과정에서 Windows 고유의 문제 두 가지를 만났고 둘 다 해결했다.

**1) 긴 경로(long path) 문제**
- 증상: `git clone` 도중 `Filename too long` 에러로 체크아웃 실패. MineRL이
  의존하는 Malmo 하위 모듈의 파일 경로가 Windows 기본 `MAX_PATH`(260자) 제한을
  넘는다.
- 해결: `git config --global core.longpaths true`.

**2) `gradlew.bat` 실행 실패 (MineRL v1.0.x 자체의 Windows 버그, 업스트림 미수정)**
- 증상: `setup.py`의 `prep_mcp()` 함수가 Windows에서 MCP-Reborn(Malmo를 fork한
  Minecraft 1.16.5 클라이언트)을 빌드할 때
  `subprocess.check_call(['gradlew.bat', 'downloadAssets'], cwd=workdir)`를
  호출하는데, `shell=True` 없이 리스트 형태로 `.bat` 파일을 호출하면 그 파일이
  실제로 존재해도 `FileNotFoundError: [WinError 2]`가 발생한다. 최소 재현
  스크립트로 직접 확인했다: 같은 디렉토리에 실제로 있는 `.bat` 파일을 셸 없이
  리스트 인자로 `subprocess.check_call`하면 100% 재현된다. Python subprocess가
  Windows에서 `.bat`/`.cmd` 스크립트를 `CreateProcess`로 직접 실행하지 못하는
  것이 원인이다 (배치 파일은 PE 실행 파일이 아니라 `cmd.exe`를 통해서만
  실행 가능).
- `shell=True`를 추가하면 이번엔 다른 에러로 바뀐다: cmd.exe가 상대경로
  `gradlew.bat`를 못 찾는다 (`'gradlew.bat'은(는) 내부 또는 외부 명령...
  아닙니다`). `cwd`를 정확히 지정했는데도 그렇다. `gradlew` 경로를 절대경로로
  바꾸니 해결됐다.
- v1.0.0, v1.0.1, v1.0.2 세 태그의 `setup.py`를 모두 확인했는데 이 버그는
  고쳐지지 않은 상태였다. GitHub 이슈 #697, #720, #782에 비슷한 증상 보고가
  있었지만 메인테이너의 명확한 해결책은 달려있지 않았다.
- 해결: `git clone --branch v1.0.2`로 로컬에 소스를 받아 `setup.py`의 관련
  두 곳을 수정한 뒤 그 로컬 경로로 `pip install`했다.
  - `gradlew` 변수를 상대경로(`'gradlew.bat'`)가 아니라
    `os.path.join(workdir, 'gradlew.bat')` 절대경로로 변경
  - `downloadAssets`, `clean build shadowJar`를 실행하는 두
    `subprocess.check_call` 호출에 `shell=(os.name == 'nt')` 추가
  - 이 패치는 세션 스크래치 디렉토리의 로컬 클론에만 적용했고 저장소에는
    커밋하지 않았다 (재현 시 이 노트의 절차를 그대로 따라가면 됨).
- 결과: `minerl-1.0.0` wheel 빌드 성공(빌드 산출물 크기 1.3GB — MCP-Reborn
  빌드 결과물이 wheel 안에 통째로 패키징됨), `import minerl` 정상 동작 확인.

## Smoke test: `env.reset()`에서 재현되는 GLFW 창 리사이즈 행(hang)

### 증상
`gym.make("MineRLTreechop-v0")` 이후 `env.reset()`을 호출하면
`socket.timeout: timed out`으로 실패한다 (`minerl/env/_multiagent.py`의
`SOCKTIME = 60.0 * 4`, 즉 240초 타임아웃). 서로 다른 세 번의 시도에서 매번
동일한 지점에서 멈췄다 — 우연이나 일시적 문제가 아니라 재현 가능한 증상이다.

### 로그로 확인한 진행 상황
`MCP-Reborn/logs/latest.log` 기준, 매번 다음까지는 정상적으로 진행된다.
1. LWJGL 3.2.2로 렌더 스레드가 초기화되고 OpenGL 컨텍스트, 텍스처 아틀라스
   생성까지 성공한다. (03번 노트에서 겪은 WSLg의 GLX 컨텍스트 생성 실패와는
   다른 지점 — 이번엔 컨텍스트 생성 자체는 정상적으로 됨)
2. `MalmoEnvServer`가 특정 포트(시도마다 다름, 예: 9309)에서 미션 토큰과
   `MissionInit` XML을 수신한다.
3. 미션의 `VideoProducer` 설정(64x64)에 맞춰 width/height/gamma/FOV/GuiScale을
   적용했다는 로그가 찍힌다.
4. 이후 추가 로그가 전혀 찍히지 않고 그대로 멈춘다. 에러도, JVM 크래시
   리포트도 없다.

### 스레드 덤프로 확인한 직접 원인
멈춰 있는 동안 `jstack <pid>`(JDK 8에 기본 포함된 스레드 덤프 도구)로 확인했다.
Render thread(Minecraft의 메인 스레드)가 다음 호출 스택에서 멈춰 있었다.
스레드 상태 자체는 `RUNNABLE`로 표시되지만 실제로는 native 함수 호출에서
리턴하지 않고 있다.

```
org.lwjgl.system.JNI.invokePPPV (Native Method)
org.lwjgl.glfw.GLFW.glfwGetFramebufferSize
net.minecraft.client.MainWindow.updateFramebufferSize
net.minecraft.client.MainWindow.resize
com.minerl.multiagent.env.EnvServer.lambda$null$7  (EnvServer.java:351)
```

`EnvServer.setGameSetttings()`(`EnvServer.java:334-360`)가 미션이 요구하는
관측 해상도(64x64)에 맞춰 Minecraft 창을 리사이즈하려고 `window.resize()`를
호출하는데, 그 내부에서 부르는 GLFW 네이티브 함수 `glfwGetFramebufferSize`가
리턴하지 않는다. 이 호출 하나가 렌더 스레드를 영구히 막고 있고, 렌더 스레드가
막히니 그 뒤에 이어져야 할 월드 생성/미션 응답도 전혀 진행되지 않는다.

### 확인해서 배제한 원인
- **잔여 프로세스 경합 가설**: 이전 실패 시도의 Java 프로세스가 죽지 않고
  남아 GPU/OpenGL 컨텍스트를 점유하고 있어서 새 프로세스가 못 뜨는 게
  아닌가 의심했다. MineRL 자체 설치 스크립트에도 "이전 시도의 Java 프로세스가
  남아있으면 문제가 된다"는 경고 문구가 있어 유력한 가설이었다. 하지만 모든
  관련 Java 프로세스를 완전히 종료한 깨끗한 상태에서 다시 시도해도 동일하게
  재현되어 이 가설은 배제했다. (부수적으로, 정리 과정에서 VSCode의 Java/Gradle
  확장이 `.venv` 안에 통째로 들어간 MCP-Reborn 소스를 별도 Gradle 프로젝트로
  오인식해 자체 Gradle 데몬을 띄운 것도 발견했다 — MineRL 실행과는 무관한
  별개 현상이었다.)
- **오버레이/화면 캡처 소프트웨어(Parsec, NVIDIA ShadowPlay) 후킹 가설**:
  이 프로세스가 실행되는 동안 Alt+Z(NVIDIA 오버레이) 안내가 뜨는 걸 관찰했고,
  작업 관리자에 `parsecd`(원격 스트리밍)와 `nvcontainer`(NVIDIA 오버레이 관련
  서비스)가 떠 있는 것도 확인했다. 이런 후킹 소프트웨어가 새로 생성된 OpenGL
  창에 개입하면서 전역 USER32 GUI 락을 붙잡고 있는 게 아닌가 의심했다. 두
  프로세스를 모두 완전히 종료한 뒤 재시도했지만 동일한 지점에서 동일하게
  재현되어 이 가설도 배제했다.
- **GPU 드라이버 크래시 가설**: Windows 이벤트 뷰어의 System 로그에서 TDR
  (Timeout Detection and Recovery, 디스플레이 드라이버가 응답 없어 재시작되는
  이벤트, ID 4101/4102)을 검색했으나 해당 이벤트가 전혀 없었다. 드라이버 자체가
  죽은 것은 아니라는 뜻이라 이 가설도 배제했다.
- **DPI 스케일링 불일치 가설**: `System.Drawing.Graphics.DpiX`로 확인한 실제
  디스플레이 DPI는 96(100% 스케일링, 스케일링 없음)이었다. GLFW 3.2.2가 구버전
  이라 Windows 11의 DPI 가상화 경로와 충돌할 가능성을 의심했지만,애초에
  스케일링이 걸려있지 않아 이 경로 자체가 관여할 여지가 적었다.
- **창이 안 보이는 것 자체는 원인이 아니었음**: Windows 작업 관리자에서 이
  Java 프로세스는 "앱"이 아니라 "백그라운드 프로세스"로 분류됐다
  (`Get-Process`로 확인한 `MainWindowHandle=0`, 빈 `MainWindowTitle`). MineRL
  메인테이너(Miffyli)가 별개 이슈(#743)에서 "창이 갱신되지 않는 것은 정상
  동작이며, 관측값은 OpenCV `cv2.imshow`로 확인해야 한다"고 답변한 사례가 있어,
  창이 화면에 안 보이는 것 자체는 정상 동작이라고 판단했고 최종적으로도 맞는
  판단이었다 (아래 최종 해결에서도 창은 계속 비가시 상태로 둔다).

### 네이티브 스택 트레이스로 확인한 진짜 원인
`jstack`은 Java 레벨 스택만 보여주고 `glfwGetFramebufferSize` 아래는
"Native Method"로만 표시되어 정확히 뭘 기다리는지 알 수 없었다. Windows용
네이티브 디버거 `cdb.exe`(WinDbg에 포함, winget `Microsoft.WinDbg`로 설치)를
non-invasive 모드(`-pv`, 프로세스를 죽이거나 일시정지 상태로 남기지 않음)로
붙여서 전체 스레드의 네이티브 콜스택을 덤프했다(`cdb -p <pid> -pv -c "~*kb 20; qd"`).

Render thread가 다음 지점에서 멈춰 있었다 (두 번의 독립적인 재현에서 동일):

```
USER32!ValidateHwnd
USER32!GetClientRect
glfw!glfwGetWin32Monitor+0x881   (실제로는 glfwGetFramebufferSize의 Win32 구현부.
                                   glfw.dll에 private 심볼이 없어 가장 가까운
                                   export 이름으로 잘못 표시됨)
```

이걸 근거로 MCP-Reborn 소스(`MainWindow.java`)를 직접 읽어서 진짜 원인을
찾았다. `resize()` 메서드가 vanilla Minecraft에는 없는, MineRL이 추가한
커스텀 코드였다:

```java
GLFW.glfwSetWindowSize(handle, newWidth, newHeight);
while ((fbWidth == framebufferWidth && fbWidth == framebufferHeight) ||
        (framebufferHeight * newWidth != framebufferWidth * newHeight)) {
   updateFramebufferSize();   // 내부에서 glfwGetFramebufferSize 호출
}
```

`glfwSetWindowSize`는 비동기다 — Windows가 `WM_SIZE` 메시지를 실제로
처리해야 GLFW 내부에 캐시된 프레임버퍼 크기가 갱신된다. 그런데 이 루프는
메시지 큐를 한 번도 펌핑하지 않는다(`glfwPollEvents()`/`glfwWaitEvents()`
호출이 없음). 이 루프를 실행하는 스레드(Render thread)가 바로 그 창의
메시지 큐를 소유한 스레드이기 때문에, 이 루프 밖에서는 아무도 그 메시지를
대신 처리해줄 수 없다 — 즉 `WM_SIZE`가 영원히 처리되지 않고, 조건은 영원히
참으로 남아 무한 루프(사실상 hang)가 된다.

### 해결까지 세 번의 반복
**1차 패치**: 루프 안에 `GLFW.glfwPollEvents()`(non-blocking)를 추가하고
최대 100회 안전장치를 뒀다. 결과: hang은 사라졌지만, `glfwPollEvents()`가
즉시 리턴해버려서 `WM_SIZE`가 도착하기 전에 안전장치가 먼저 소진됐다.
루프가 끝난 뒤 `EnvServer`가 무조건 `mc.updateWindowSize()`를 호출하는데,
그 안의 `calcGuiScale()`이 "프레임버퍼 너비/높이 비율이 창 너비/높이 비율과
같아야 한다"는 불변조건을 검사하다가 `RuntimeException`을 던졌다
(`[Render thread/FATAL]: Error executing task on Client`). 이 예외는
Minecraft의 태스크 실행기가 잡아서 로그만 남기고 게임은 계속 진행했기
때문에, 최종적으로 관측 이미지가 64x64가 아닌 어중간한 크기(176x64)로
나와 `pov.reshape((64,64,3))`가 `ValueError: cannot reshape array of size
33792 into shape (64,64,3)`로 실패했다.

**2차 패치**: `glfwPollEvents()`(non-blocking)를 `glfwWaitEventsTimeout(0.1)`
(메시지가 오거나 최대 0.1초까지 실제로 대기)로 바꿔서 메시지가 도착할
시간을 벌어줬다. 안전장치는 50회로 줄임. 결과: 루프가 실제로 6초 가까이
돌았지만(0.1초 × 50회 ≈ 5초와 일치) 여전히 같은 비율 불일치로 실패했다.
즉 단순히 "메시지를 더 기다리면" 해결되는 문제가 아니었다.

**원인 확정을 위한 디버그 로그**: `resize()` 끝에 실제 시작/목표/최종
프레임버퍼 크기를 출력하는 로그를 추가하고 재빌드해서 확인했다:

```
[MINERL_DEBUG] resize target=64x64 startedFrom=1280x720 finalFramebuffer=176x64
               remainingTries=-1 windowVisible=0
```

**높이는 720→64로 정확히 반영됐는데 너비만 1280→176에서 멈췄다.** 176은
Windows가 제목표시줄(캡션 바)이 있는 표준 창에 강제하는 최소 트랙 너비
(테마/DPI에 따라 대략 130~180px)와 일치하는 값이다. 이 최소 너비 제약은
`GLFW_RESIZABLE` 힌트와 무관하게, 창이 `WS_CAPTION` 스타일(제목표시줄)을
가지고 있기만 하면 Windows 창 관리자가 프로그래�매틱 리사이즈(`SetWindowPos`
경유)에도 강제한다. 높이 방향은 캡션 바 높이만 확보하면 되므로 이런 하한이
훨씬 작아 64까지 문제없이 줄었다.

**최종 해결**: `GLFW_DECORATED = GLFW_FALSE`를 창 생성 힌트에 추가했다.
이 창은 애초에 `GLFW_VISIBLE = GLFW_FALSE`로 화면에 전혀 보이지 않으므로
제목표시줄을 없애도 시각적으로 아무 영향이 없고, 제목표시줄이 없으면
Windows가 강제하는 최소 캡션 너비 제약 자체가 적용되지 않는다.

세 패치를 합친 최종 diff (`MainWindow.java`):
```java
GLFW.glfwWindowHint(GLFW.GLFW_RESIZABLE, GLFW.GLFW_FALSE);
GLFW.glfwWindowHint(GLFW.GLFW_VISIBLE, GLFW.GLFW_FALSE);
GLFW.glfwWindowHint(GLFW.GLFW_DECORATED, GLFW.GLFW_FALSE);   // 추가: 최소 캡션 너비 제약 제거
...
public void resize(int newWidth, int newHeight) {
   ...
   GLFW.glfwSetWindowSize(handle, newWidth, newHeight);
   int remainingTries = 50;
   while (((fbWidth == framebufferWidth && fbWidth == framebufferHeight) ||
           (framebufferHeight * newWidth != framebufferWidth * newHeight)) && remainingTries-- > 0) {
      GLFW.glfwWaitEventsTimeout(0.1);   // 변경: glfwPollEvents() -> glfwWaitEventsTimeout(0.1)
      updateFramebufferSize();
   }
   ...
}
```

### 결과: 마일스톤 1 완료
`gym.make("MineRLTreechop-v0")` → `env.reset()` → `env.step()` 20회 →
`env.close()`까지 정상 동작 확인. `reset()`이 반환한 관측값 키는 `['pov']`이며
`pov`는 정확히 (64, 64, 3) 크기다.

이 패치는 세 군데 모두 로컬 MineRL v1.0.2 클론(`MainWindow.java`)에
적용했고, `gradlew.bat build shadowJar`로 `mcprec-6.13.jar`만 재빌드해서
기존 venv에 반영했다 (MCP-Reborn 전체를 처음부터 다시 받지 않아도 됨 —
gradle 캐시가 이미 있어서 재빌드는 매번 1분 내외로 끝났다). 패치 자체는
저장소에 커밋하지 않았다; 재현 필요 시 이 노트의 diff를 그대로 적용하면 된다.

### 다음에 할 것
- ~~이 발견을 minerllabs/minerl에 업스트림 이슈로 제보~~ → 완료.
  [minerllabs/minerl#814](https://github.com/minerllabs/minerl/issues/814)
- ~~PR 오픈~~ → 완료. [minerllabs/minerl#815](https://github.com/minerllabs/minerl/pull/815)
  (fork: https://github.com/Akileox/minerl, 브랜치 `fix/windows-resize-hang`)
  - 패치는 기존 `scripts/mcp_patch.diff`를 직접 수정하지 않고, 그 위에 얹는
    별도 파일 `scripts/windows_resize_fix.diff`로 분리했다. `MainWindow.java`가
    ForgeGradle 디컴파일 산출물이라 vanilla 텍스트가 결정적이지 않을 수 있어
    (다른 환경에서 디컴파일하면 미세하게 다를 수 있음), `mcp_patch.diff`가
    이미 성공적으로 만들어낸 "패치 적용 후" 상태를 기준으로 diff를 떠서
    안전하게 얹었다. 실제로 `patch -p1`로 적용해서 결과가 최종 테스트한
    파일과 바이트 단위로 완전히 일치하는 것까지 확인함.
  - PR base 브랜치는 `dev`(저장소 기본 브랜치)로 열었다. 연 시점 기준
    `v1.0.2` 태그와 `dev`의 `scripts/mcp_patch.diff` / `patch_mcp.sh` /
    `setup_mcp.sh`가 완전히 동일함을 먼저 확인하고 진행했다.
- 마일스톤 2(Observation pipeline)로 진행.

## 참고 자료
- MineRL GitHub 이슈 #697, #716, #720, #743, #782 (Windows 설치/실행 관련
  유사 증상 보고들, 명확한 해결책은 없었음). #434(macOS)는 창 조작이
  스레드 안전하지 않아 나는 별개의 크래시지만, "이 리사이즈/윈도우 조작
  코드가 플랫폼별로 fragile하다"는 같은 계열의 증상으로 참고할 만하다.
- 03번 노트: WSLg GLX 컨텍스트 생성 실패 (이번 이슈와는 다른 지점이지만
  같은 GPU/드라이버 조합에서 반복되는 그래픽 스택 문제라는 공통점이 있어
  같이 의심했으나, 최종적으로는 GPU/드라이버가 아니라 MineRL 자체의
  Windows 메시지 펌핑 누락 + Windows 창 관리자의 캡션 최소 너비 제약이
  겹친 문제로 결론남)
