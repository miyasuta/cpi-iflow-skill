---
name: cpi-iflow-design
description: Use when the user describes what an SAP Cloud Integration (CPI) integration flow should achieve - what to receive or read, from which system, how to map or convert it, where to send it, how errors are handled - instead of exact steps, and the iFlow (or several iFlows that call each other) has to be designed first. Designs it along SAP's Integration Flow Design Guidelines (standard components before Groovy Script, error handling, ProcessDirect between iFlows, naming, externalized parameters, message log identifiers) and declares the design for approval - assumptions, flow table, reasons, externalized values, build order, open questions, and interfaces between iFlows. Writes no XML and needs no tenant or Git repository, so it also serves people who build iFlows only in the CPI designer.
---

# CPI iFlow design

Turn a goal into an iFlow design that follows SAP's integration flow design guidelines, declare it, and wait for the user's approval. This skill writes no XML, no script and no file, and needs neither a CPI tenant nor a Git repository.

The design is the one the guidelines call for. How the iFlow will be built (in the CPI designer, by a tool, by an AI) never changes it: a part that is hard to build is still declared as the guidelines recommend.

## Workflow

1. **Understand the goal.** What starts the iFlow, what it reads or receives, what it changes, where it sends the result, who waits for a reply. Ask only what blocks the design; put everything else into "0. Assumptions" and "5. Questions".
2. **Choose the components** for each purpose from [references/components.md](references/components.md): a standard component first, Groovy Script last.
3. **Check the guidelines** in [references/guidelines.md](references/guidelines.md): the A items shape the flow; the B items go into step names, section 3 and the identifier step.
4. **Declare** in the format of [references/process.md](references/process.md), in the user's language. For several iFlows, add the Interface sections.
5. **End your turn and wait for the user's explicit approval.** A question or a correction is not approval: revise and declare the whole design again.
6. **After approval**, the declaration stays in the conversation as it is. To build it locally in a Cloud Integration Git Access repository, the user continues with the **cpi-iflow-build** skill, which takes the declaration as its input. To build it in the CPI designer, the user follows the flow table row by row.

## Rules

- Never bend the design to what is easy to build (for example a Groovy Script mapping because Message Mapping takes more work). That is an anti-pattern in itself ([references/guidelines.md](references/guidelines.md), A1–A3).
- Every Groovy Script row says in "2. Why this shape" which standard component was considered and why it does not fit.
- Name every step in English after its role; never a designer default such as `Content Modifier 1`.
- Link each design choice to the SAP guideline it follows. Do not invent guidelines; when no SAP page backs a choice, say so.
- Keep the declaration format exactly as in [references/process.md](references/process.md): the build skill relies on it.
- Do not write `.iflw` XML, scripts or other iFlow files, even after approval. Building is a separate step.

## References

| Task | Read |
|---|---|
| The declaration format (the contract with the build skill), waiting for approval, several iFlows, a full example | [references/process.md](references/process.md) |
| Design guidelines the declaration must respect (anti-patterns, naming, externalization, error handling, security) and how each is checked | [references/guidelines.md](references/guidelines.md) |
| Choosing a standard component for a purpose (Groovy as last resort) | [references/components.md](references/components.md) |
