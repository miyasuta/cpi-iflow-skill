---
name: cpi-iflow-design
description: Use when the user describes what an SAP Cloud Integration (CPI) integration flow should achieve - what to receive or read, from which system, how to map or convert it, where to send it, how errors are handled - instead of exact steps, and the iFlow (or several iFlows that call each other) has to be designed first. Designs it along SAP's Integration Flow Design Guidelines (standard components before Groovy Script, error handling, ProcessDirect between iFlows, naming, externalized parameters, message log identifiers), writes the design to a Markdown file under docs/ with a flow diagram (assumptions, flow diagram and table, reasons, externalized values, build order, questions, interfaces between iFlows), asks the open questions one at a time, and waits for approval. Writes no XML and needs no tenant or MCP server, so it also serves people who build iFlows only in the CPI designer.
---

# CPI iFlow design

Turn a goal into an iFlow design that follows SAP's integration flow design guidelines, write it to a design file `docs/<design name>.md` with a flow diagram, ask the open questions one at a time, and wait for the user's approval. This skill writes no XML and no script, and needs neither a CPI tenant nor an MCP server.

The design is the one the guidelines call for. How the iFlow will be built (in the CPI designer, by a tool, by an AI) never changes it: a part that is hard to build is still declared as the guidelines recommend.

## Workflow

1. **Understand the goal.** What starts the iFlow, what it reads or receives, what it changes, where it sends the result, who waits for a reply. Ask only what blocks the design; put everything else into "0. Assumptions" and "5. Questions".
2. **Choose the components** for each purpose from [references/components.md](references/components.md): a standard component first, Groovy Script last.
3. **Check the guidelines** in [references/guidelines.md](references/guidelines.md): the A items shape the flow; the B items go into step names, section 3 and the identifier step.
4. **Write the design file** `docs/<design name>.md` in the format of [references/process.md](references/process.md), in the user's language: first the purpose and the related systems and flows (other systems, and iFlows outside this design), then the flow diagram above the flow table. For several iFlows, add the overview diagram and the Interface sections. In the conversation, show the diagram, a short summary and the file path.
5. **Ask the questions of section 5 one at a time**, as "Presenting, questions, approval" in [references/process.md](references/process.md) says: one question per message, with the rows it affects, the options and your recommendation. Update the file after each answer.
6. **When no question is open, ask for the user's explicit approval and end your turn.** A question or a correction is not approval: change the file and ask again.
7. **After approval**, the design file is the input for building. To build it with an MCP server for Cloud Integration, the user continues with the **cpi-iflow-build** skill. To build it in the CPI designer, the user follows the flow table row by row.

## Rules

- Never bend the design to what is easy to build (for example a Groovy Script mapping because Message Mapping takes more work). That is an anti-pattern in itself ([references/guidelines.md](references/guidelines.md), A1–A3).
- Every Groovy Script row says in "2. Why this shape" which standard component was considered and why it does not fit.
- Name every step in English after its role; never a designer default such as `Content Modifier 1`.
- Link each design choice to the SAP guideline it follows. Do not invent guidelines; when no SAP page backs a choice, say so.
- Keep the declaration format exactly as in [references/process.md](references/process.md): the build skill relies on it. The diagram and the flow table always show the same steps.
- Never ask several questions in one message, and never ask for approval while a question is open.
- The design file is the only file this skill writes. Do not write `.iflw` XML, scripts or other iFlow files, even after approval. Building is a separate step.

## References

| Task | Read |
|---|---|
| The design file and its format (the contract with the build skill), the flow diagram, asking questions one at a time, approval, several iFlows, a full example | [references/process.md](references/process.md) |
| Design guidelines the declaration must respect (anti-patterns, naming, externalization, error handling, security) and how each is checked | [references/guidelines.md](references/guidelines.md) |
| Choosing a standard component for a purpose (Groovy as last resort) | [references/components.md](references/components.md) |
