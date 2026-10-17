---
name: cpi-iflow-skill
description: Use when editing an SAP Cloud Integration (CPI) integration flow locally in a Git repository connected through Cloud Integration Git Access - files such as <iFlow>/src/main/resources/scenarioflows/integrationflow/*.iflw, META-INF/MANIFEST.MF, metainfo.prop. Covers changing Content Modifier headers, exchange properties and message body, inserting a Content Modifier, changing the iFlow Description, changing HTTPS sender Address, CSRF and authorization settings, and externalized parameters ({{name}}, parameters.prop, parameters.propdef). Also use when asked to add any other step or adapter to an iFlow in such a Git Access repository, or to create a new iFlow in it, so that unsupported requests are declined instead of invented.
---

# CPI iFlow local editing (v0)

Edit Cloud Integration iFlows as files, then let the user pull them into CPI. Every key, value and version this skill uses comes from real iFlows pushed from a CPI tenant ([cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples)). CPI accepts or rejects `.iflw` files in ways that are not documented, so **only write what the references show**.

## Scope

Supported:
- Content Modifier: add, change or reorder Message Header and Exchange Property rows with Type `constant` or `expression`; set the Message Body
- Insert a Content Modifier between two existing nodes
- Change the iFlow Description
- Change an existing HTTPS sender's Address or CSRF protection
- Change an existing HTTPS sender's authorization (not yet verified for local edits; see the reference)
- Externalized parameters: externalize the HTTPS sender Address or a Content Modifier header cell value as `{{name}}` with its default value (verified locally), or a Content Modifier body (same pattern, seen only in a UI sample); change the value of an existing parameter in `parameters.prop` (verified only for an iFlow with no values set in the Configure screen; otherwise tell the user it is unverified)

Not supported (no real sample yet):
- Any other step or adapter (Router, Groovy Script, Request Reply, receivers, Splitter, Exception Subprocess, Local Integration Process, Message Mapping, …)
- Other Content Modifier Source Types (Header, Property, XPath, Number Range, variables), `<` or `&` in a message body
- Creating a new iFlow or changing component versions
- Externalizing any other field or part of a value, reusing, renaming or removing a parameter, special characters in a parameter value, or creating `parameters.prop` / `parameters.propdef` when the iFlow has none yet

For an unsupported request, **do not write the XML**. Tell the user that this skill has no verified sample for it, and offer two options: build that part in the CPI designer (then Push and continue locally), or add a sample for it first (make the change in the UI, one action per commit, and Push). Do the supported part of a mixed request only if the user agrees.

## Workflow

The user performs the CPI steps in the CPI web UI. Tell them exactly what to do and ask for the result.

1. **Start clean.** Ask the user to Push every change saved in the CPI designer, then pull the branch locally. Unpushed UI changes cause Pull to be rejected when the same place changed, and a local Description change is silently dropped.
2. **Edit locally.** Find the iFlow by `Bundle-Name` in `META-INF/MANIFEST.MF`, not by the `.iflw` file name.
3. **Check:** `python3 scripts/check_iflw.py <iFlow folder>`. Fix every error before committing, and fix what each warning points to (edge waypoints, a `>` escaped only once, an unused parameter). For each `.iflw` it also reads `parameters.prop` and `parameters.propdef` from the iFlow's `src/main/resources/` folder (two levels above `scenarioflows/integrationflow/<name>.iflw`), so keep the Git Access layout: every `{{name}}` must be defined in both files.
4. **Commit and push** to the branch connected to the iFlow.
5. **In CPI:** Pull → open the iFlow and check the Problems tab → Save → Deploy → wait for Started → call it and compare with the expected result.
6. **In CPI:** close edit mode (Cancel) and reload the page if the iFlow still shows as locked, then Push. Pull locally. CPI normalizes the file on save; the next edit starts from that commit.

If Pull fails or the designer shows errors, see "When Pull fails" in [references/workflow.md](references/workflow.md).

## Rules

- Use only `ifl:property` keys, `cmdVariantUri` values and `componentVersion` values that appear in the references. If something is not there, stop and ask the user. Never invent keys, values or versions.
- Keep every existing step's version pair as it is. For a new Content Modifier, copy the 7-key template in [references/components/content-modifier.md](references/components/content-modifier.md). An older Content Modifier version pair already in the iFlow is fine; CPI accepts it and does not migrate it.
- For every element you add or change, write its `bpmndi` `BPMNShape` (nodes, participants) or `BPMNEdge` (sequence and message flows) and keep all references consistent. Coordinates only need to be roughly right.
- When a flow gets a new source or target, also move its `di:waypoint` ends to the new shapes. The designer draws lines along the waypoints; changing only `sourceElement` / `targetElement` leaves the diagram wrong (the iFlow still runs).
- Edit the iFlow Description in `bpmn2:documentation` in the `.iflw`. Never edit `metainfo.prop`: it has no effect and is overwritten by the next Push.
- In `headerTable` / `propertyTable` cell values, escape `<`, `&`, `>` twice (`&amp;lt;`, `&amp;amp;`, `&amp;gt;`). Do not put `<` or `&` in a message body (`wrapContent`): unverified.
- Remind the user to Pull in CPI before every Push from CPI. Pushing while the remote is ahead is unverified.
- Leave everything not needed for the task unchanged. Do not "fix" diff noise such as the `bpmn2:documentation` id or timestamps.
- Never write credentials (client secrets, tokens) into files or commits.

## References

Read only what the task needs:

| Task | Read |
|---|---|
| Any task: round trip, Pull/Push behavior, conflicts, Description, diff noise, testing a deployed iFlow | [references/workflow.md](references/workflow.md) |
| Adding or connecting elements, IDs, `bpmndi`, inserting a step | [references/iflw-structure.md](references/iflw-structure.md) |
| Writing header, property or certificate table values, special characters | [references/escaping.md](references/escaping.md) |
| Content Modifier keys, template, versions, rows, body | [references/components/content-modifier.md](references/components/content-modifier.md) |
| HTTPS sender keys and settings | [references/components/https-sender.md](references/components/https-sender.md) |
| Externalized parameters: `{{name}}`, `parameters.prop`, `parameters.propdef`, Configure values | [references/externalized-parameters.md](references/externalized-parameters.md) |

Facts marked **unverified** in the references were not tested. When a task depends on one, tell the user and ask them to check the result in CPI.
