# 모바일 청첩장 모션그래픽: 인수인계

최종 업데이트: 2026-11-12 · 브랜치 `claude/gallant-rubin-oqpkm6` (PR 없음)

## 1. 확정된 정보

| 항목 | 내용 |
|---|---|
| 신랑 | 하현철 · JAMES HA |
| 신부 | 박서영 · HANNAH PARK |
| 일시 | 2027년 2월 20일 토요일 오후 12시 30분 |
| 장소 | 한국거래소 서울사무소 1층 컨퍼런스홀 (1F CONFERENCE HALL) |
| 모토 | 에베소서 2:20–22. 모퉁잇돌 되신 예수 그리스도 위에 하나씩 세워져 가는 가정 |
| 규격 | 1080×1920, 30fps, 38.03초, H.264 |

## 2. 결정 대기 중 (사용자 선택 필요)

1. **색상**: 기본 네이비, 01 Vintage Ink & Ivory, 03 Charcoal & Muted Red 중 하나
2. **음악**: 아래 5개 중 하나

| 파일 접미사 | 곡 | 비고 |
|---|---|---|
| (없음) | 오리지널 잔잔한 곡 (`bgm.m4a`) | 창작곡 |
| `_찬송가` | 교회의 참된 터는 (AURELIA) | 첫 소절만 웹 검색으로 확인, 나머지는 기억에 의존 |
| `_완전한사랑` | 완전한 사랑 (SANDRINGHAM) | 첫 소절만 확인, 나머지는 기억에 의존. 찬송가 장 번호는 확실하지 않음 |
| `_기쁘다구주` | 기쁘다 구주 오셨네 (ANTIOCH) | 전부 기억에 의존 |
| `_경쾌한버전` | 레퍼런스 무드의 경쾌한 창작곡 (`bgm_groove.m4a`) | 가장 최근 버전. 레퍼런스 음원은 사용하지 않음 |

- 찬송가 선율은 원본 악보와 대조하지 못했습니다. 사용자가 악보 사진을 보내면 교정할 수 있습니다.
- 모든 음악은 코드로 합성했고, 작업자가 직접 들어보지 못했습니다. 음량, 파형, 스펙트럼으로만 검증했습니다.

**선택 후 할 일:**
- 고른 팔레트를 `index.html`의 `:root` 기본값에 반영합니다.
- `wedding-invitation.mp4`를 다시 렌더링하고 음악을 붙입니다.
- 아티팩트(https://claude.ai/artifact/S8ZxMzmgEoKzA1uPx3TkaX, 현재 기본 네이비)를 다시 게시합니다.

## 3. 파일 구조

```
wedding-cornerstone/
  index.html              애니메이션 원본 (폰트 base64 내장, 기본 네이비)
  wedding-invitation.mp4  네이비 + 오리지널 곡
  exports/                01·03 팔레트 × 음악 5종 = 10개 mp4
  music/compose.py        오리지널/찬송가 편곡 (--hymn | --love | --joy)
  music/groove.py         경쾌한 창작곡
  music/*.m4a             음악 단독 파일
  tools/render.js         index.html → mp4 (무음)
  tools/shots.js          특정 시점 스크린샷
  tools/make_palette.py   팔레트 01/03 복사본 생성
  tools/embed_fonts.py    폰트 서브셋 + base64 내장
```

## 4. 타임라인 (index.html)

| 시간(초) | 장면 |
|---|---|
| 0–4.5 | 원형 씰: 2027.02.20 / Saturday, "We're getting married!", "저희, 결혼합니다." |
| 4.5–18.3 | 크림 배경. 모퉁잇돌 슬랩 낙하(5.3–5.9), 에베소서 2:20–22 단어별 등장, 네이비 블록 15개(10.9 + i×0.3), 돔 지붕(15.8–16.4), 십자가와 비둘기 두 마리(16.6–17.3), "그 위에, 하나씩. 단단히.", 네이비 와이프(17.4–18.3) |
| 18.2–24 | WE'RE GETTING MARRIED, GROOM/BRIDE 카드, 초대 문구 |
| 23.4–25.5 | 문 닫힘(SAVE / THE DATE), 접히며 열림 |
| 24.4–29 | 날짜: 02 / 20, FEB, SAT, PM 12:30 |
| 29–33 | 장소 아치 |
| 33–38 | 최종 포스터: 미니 집(십자가·비둘기 36.4–37.0), 가운데 정렬 정보 바, 마퀴 테두리 |

- 페이지는 `render(t)` 결정론 함수로 그립니다.
- `window.seek(t)`, `window.DURATION`, `window.__ready`가 노출되어 있고, `?render=1`로 렌더 모드가 됩니다.

**디자인 규칙**
- 서체: 모두 고딕입니다. 본문은 Pretendard Variable, 국문 디스플레이는 Hada Condensed Bold, 영문/숫자 디스플레이는 Anton(Google Fonts)입니다.
- 손글씨와 명조는 사용자가 원치 않아 제외했습니다.
- 색상 토큰은 `--navy`, `--navy-ray`, `--navy-deep`, `--cream`, `--cream-ray`, `--coral`입니다. 보라색은 쓰지 않습니다.

## 5. 재현 방법

준비 사항:
- 필요한 도구: Playwright(Chromium), ffmpeg, Python 3 + numpy, fontTools/brotli(폰트 재내장 시)
- 폰트 원본(Pretendard, Hada Condensed OTF/TTF)은 저장소에 없습니다. 이미 `index.html`에 내장되어 있으므로, 문구를 바꿔 새 글자가 생길 때만 원본 폰트 파일이 필요합니다.

```bash
cd wedding-cornerstone

# 1) (문구를 바꿨다면) 폰트 재내장
python tools/embed_fonts.py index.html <폰트 폴더>

# 2) 팔레트 복사본
python tools/make_palette.py index.html /tmp/p01.html 01

# 3) 무음 렌더링 (약 3분)
node tools/render.js $PWD/index.html /tmp/silent.mp4 30   # 파일 경로는 절대경로

# 4) 음악 합성 → 음량 정규화
python music/groove.py /tmp/groove.wav          # 또는 compose.py out.wav [--hymn|--love|--joy]
ffmpeg -i /tmp/groove.wav -af loudnorm=I=-14:TP=-1.5 -c:a aac -b:a 192k /tmp/bgm.m4a

# 5) 합치기 (-shortest를 쓰면 영상이 37.97초로 잘리므로 빼기)
ffmpeg -i /tmp/silent.mp4 -i /tmp/bgm.m4a -map 0:v -map 1:a -c copy out.mp4

# 스크린샷 확인
node tools/shots.js $PWD/index.html /tmp/shots 5.9 16.6 36.8
```

4–5단계의 정확한 옵션(비트레이트 등)은 당시 명령 기록과 다를 수 있습니다.

## 6. 알려진 제약

- 이 클라우드 세션에서는 사용자의 맥에 접근할 수 없습니다. 파일은 GitHub(브랜치)나 GitHub Desktop으로 받아야 합니다.
- Higgsfield 크레딧이 0이라 AI 음악 생성은 쓰지 않았습니다.
- hymnary.org와 Wikipedia는 네트워크에서 차단되어 있습니다.
- 레퍼런스 영상의 음악은 저작권 때문에 사용하지 않았습니다. 템포만 분석했고, 결과는 약 112BPM(추정)이었습니다.
