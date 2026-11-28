# Project Rules (myaudio)

## PCB Design & Routing Guidelines

- **45度配線のみ（直角配線の禁止）**:
  - PCB の配線（`route_trace` 等）では 90度（直角）および鋭角の曲がりを禁止し、必ず **45度配線**（水平・垂直・45度斜めセグメントの組み合わせ）で引き回すこと。
  - パッドやビアからの引き出しも、直角コーナーを作らず 45度（または直線）で接続すること。
- **KiCad ファイルの編集**:
  - 回路図（`.kicad_sch`）および PCB（`.kicad_pcb`）の編集は、直接テキスト編集せず KiCAD MCP ツール経由で行うこと。
