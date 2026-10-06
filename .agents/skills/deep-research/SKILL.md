---
name: deep-research
description: Help plan, draft, refine, and preserve ChatGPT Deep Research workflows. Use whenever the user wants to investigate a research question with Deep Research, create or improve its prompt, save a returned report, or continue discussion from that report. Support iterative prompt refinement in chat; keep Zotero/MCP paper retrieval and per-paper deep reading optional so routine use stays lightweight.
---

# Deep Research

Help the user move from a research question to a reusable Deep Research prompt, then preserve the report and any resulting research discussion in the local Research Workspace.

## Working modes

Use the mode that matches the user's request. A session can move between modes, but do not assume the user wants every stage.

### 1. Shape and refine a prompt

Use this mode when the user has a question but has not yet run Deep Research.

1. Identify the research question and project. Read that project's README and only the most relevant recent meeting, spec, experiment, or brainstorm notes. If the project is unclear and a file would be written, ask which project to use.
2. If the question is underspecified, ask one focused question at a time. Do not ask for details that can be inferred from the workspace or conversation.
3. Draft a prompt that states:
   - the question and intended decision or deliverable;
   - known project context and what is already established;
   - scope, exclusions, and relevant date range;
   - preferred source types, prioritizing primary papers and official documentation;
   - the comparisons or evidence to extract;
   - citation requirements, including DOI/URL and page, section, figure, or table when available;
   - a concise output structure and a section for uncertainty or conflicting evidence.
4. Present the draft in a copyable block. Keep it marked as a draft and invite corrections. Revise it from the user's feedback without restarting the process or expanding scope on your own.
5. Treat the prompt as ready only when the user says to finalize it, use it, or otherwise indicates that the wording is ready. Then return the final prompt and explain that the user can run it in ChatGPT Deep Research.

Prompt drafting is an ordinary conversation task. Do not start broad web searches, retrieve many papers, or run expensive analysis merely to improve a draft unless the user asks for that research. This workspace agent may not have access to the ChatGPT Deep Research runner; never claim to have run it when the user must run it separately.

### 2. Save and orient from a returned report

Use this mode when the user provides or points to a completed Deep Research report.

1. Confirm the project from context. If it is ambiguous, inspect project README frontmatter and ask before saving.
2. Preserve the report as Markdown under the project's `papers/` directory, using `YYYY-MM-DD-deep-research-<topic>.md`. Check today's date before creating the dated file. Keep citations and source links intact. Do not silently rewrite the report as though it were the original output.
3. If the user wants an orientation, provide a short map of the report: main findings, strongest cited sources, unresolved questions, and which findings may affect the project. Label report claims separately from the assistant's interpretation.
4. Do not automatically fetch or read every paper cited by the report. The report's bibliography is a candidate list, not an instruction to retrieve the whole library.

If the report is pasted into chat and is too large to preserve faithfully, ask the user to attach or save the Markdown file and provide its path. Do not omit sections without saying so.

### 3. Optional paper-level reading

Use this mode only when the user selects particular papers, asks to check a claim in the original source, or approves a small proposed set of papers for close reading.

- Prefer a Zotero connection if a suitable read-only MCP or local integration is actually available. Otherwise ask for the relevant PDF, Zotero export, annotation, or excerpt. Do not install or configure an MCP server as an assumed prerequisite.
- Retrieve only the selected paper(s) and relevant sections. For a broad batch, propose a small first batch (normally no more than three papers) and wait for the user's choice before retrieving many full texts.
- Verify important claims against the paper itself. Capture DOI/URL and page, section, figure, or table. Note when text extraction is uncertain, especially for equations, figures, or tables.
- Create a per-paper note in `papers/` only when requested or when the paper materially affects a decision. Keep it concise: research question, method, evidence, limitations, and relevance to this project.
- Treat Zotero as the source of truth for bibliographic records, PDFs, and user annotations. Use read-only access by default. Never add, edit, tag, or move Zotero items without explicit instruction.

Full-text retrieval and per-paper notes are optional because reading many documents and carrying their contents into a conversation can consume substantial usage. Prefer a short synthesis of the saved report unless a specific evidence gap warrants close reading.

### 4. Preserve discussion and decisions

When the user and assistant have substantively discussed the report or selected papers, preserve the useful synthesis in `.research/secretary/notes/brainstorm/YYYY-MM-DD-deep-research-<topic>.md` unless the user asks for another destination. Check today's date before creating the dated file.

Record only the durable content, not the full chat transcript:

- question and linked report/paper notes;
- evidence that matters to the project;
- interpretation and competing explanations;
- conclusions, unresolved questions, and next-action candidates.

Keep literature exploration in `papers/` and tentative reasoning or decisions in `brainstorm/`. Do not save AI-created analysis in `references/`, which is for external or user-provided source material and is read-only by default. Do not add TODOs unless the user adopts them.

## Evidence and usage discipline

- Treat Deep Research reports as a cited map of the literature, not a substitute for checking primary sources when a claim changes a research decision.
- Preserve distinctions among a paper's reported result, the Deep Research report's synthesis, and the assistant's inference.
- Prefer targeted source retrieval and small, bounded context over uploading or reading an entire library.
- Ask before expanding a focused task into a broad literature sweep or full-text review of many candidates.
- Use Deep Research for multi-source discovery and synthesis. Use ordinary chat for prompt refinement, discussion of a bounded report, and close reading of selected source passages.

## Output expectations

During prompt refinement, show:

1. a brief statement of the interpreted question;
2. the current copyable prompt draft;
3. the main choice or uncertainty the user can refine.

After saving a report or note, provide its path and a short description of what was recorded. Never claim the report, Zotero connection, or source text is available unless it was actually provided or retrieved.
