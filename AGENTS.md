# AGENTS.md

This repository is a research workspace for the novel *Cien años de soledad*
(百年孤独) by Gabriel García Márquez. It holds the Spanish original split into
chapters, a cleaning pipeline, and a memory/wiki system for research notes.

## Repo layout

- `00.md`–`20.md` — the novel, one file per chapter (Spanish original). Source data, do not edit.
- `gabriel_garcia_marquez_cien_annos_soledad.txt` — table-of-contents index (Roman numerals + page numbers), not the novel body.
- `cleaned/01.md`–`20.md` — chapter texts cleaned by `clean_text.ts` (headers/footers/page numbers removed). Preferred base for text analysis and quotes.
- `clean_text.ts` — Deno cleaning script (`deno run -A clean_text.ts`).
- `memory/` — research notes, one file per topic, with `Home.md` as the index (auto-loaded each session via `option context-path` in `.crushrc`). This directory is a git submodule whose remote is the wiki repo `btwiuse/cads.wiki`.
- `scripts/sync-wiki.sh` — publishes `memory/` to the wiki (`README.md` → `Home.md`, everything else verbatim).

## Rules

- Corpus files are read-only source data. Research output goes into `memory/`; analysis scripts may be added as new files.
- 适时地 document research findings to `./memory`,每个主题一个文件,并维护 `memory/Home.md` 索引;consolidate 可复用信息供未来的会话参考。
- Every claim about the novel must cite a chapter number (e.g. `ch.05`). Quote in the original Spanish with a chapter reference; notes may be written in Chinese.
- After editing `memory/`, run `scripts/sync-wiki.sh` to publish, then `git submodule update --remote memory` locally to advance the pointer.
