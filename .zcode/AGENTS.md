# ⚠️ 本文件已废弃

ZCode 的工作区指令入口是**仓库根部的 [`/AGENTS.md`](../AGENTS.md)**（自动加载）。
本目录（`.zcode/`）下生效的内容只有：

- `rules/` — 项目规则（由根 AGENTS.md 按需引用）
- `skills/<name>/SKILL.md` — ZCode 技能（自动发现）

原 LeeCommonSkills 模板协调规则仍保留在 `.trae/AGENTS.md`（供 Trae 使用）。
