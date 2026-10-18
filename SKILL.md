---
name: cpi-iflow-skill
description: Use when editing an SAP Cloud Integration (CPI) integration flow locally in a Git repository connected through Cloud Integration Git Access - files such as <iFlow>/src/main/resources/scenarioflows/integrationflow/*.iflw, META-INF/MANIFEST.MF, metainfo.prop. Covers changing Content Modifier headers, exchange properties and message body, inserting a Content Modifier, inserting a Groovy Script step or changing its script (script/*.groovy), changing the iFlow Description, adding an HTTPS sender to an empty iFlow or changing its Address, CSRF and authorization settings, inserting a Request Reply step with an HTTP receiver (GET, no authentication) or changing the receiver's Address and Query, adding an Exception Subprocess that returns an error response (Error Start, Content Modifier, End Message) or changing the Content Modifier in it, and externalized parameters ({{name}}, parameters.prop, parameters.propdef). Also use when asked to add any other step or adapter to an iFlow in such a Git Access repository, or to create a new iFlow in it, so that unsupported requests are declined instead of invented.
---

# CPI iFlow local editing (v0)

Edit Cloud Integration iFlows as files, then let the user pull them into CPI. Every key, value and version this skill uses comes from real iFlows pushed from a CPI tenant ([cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples)). CPI accepts or rejects `.iflw` files in ways that are not documented, so **only write what the references show**.

## Scope

Supported:
- Content Modifier: add, change or reorder Message Header and Exchange Property rows with Type `constant` or `expression`; set the Message Body
- Insert a Content Modifier between two existing nodes
- Change the iFlow Description
- Add an HTTPS sender to an iFlow that has none (an empty iFlow created in CPI; verified with CSRF protection off, saved in CPI before deployment)
- Change an existing HTTPS sender's Address or CSRF protection
- Change an existing HTTPS sender's authorization (not yet verified for local edits; see the reference)
- Groovy Script: insert a step with a new script file between two existing nodes (verified once, after a Content Modifier), and change the code of an existing script file (verified). Reading an HTTP request header in a script needs Allowed Header(s); setting it locally is unverified
- Request Reply: insert a Request Reply step between two existing nodes and connect an HTTP receiver to the existing receiver participant, with Method GET and Authentication None (verified once, in an empty iFlow); change an existing HTTP receiver's Address or Query (verified)
- Exception Subprocess: add one with Error Start → Content Modifier → End Message to an iFlow that has none, to return an error response (headers, body, HTTP status through `CamelHttpResponseCode`) (verified once, in an empty iFlow); change the Content Modifier inside an existing one (verified)
- Externalized parameters: externalize the HTTPS sender Address or a Content Modifier header cell value as `{{name}}` with its default value (verified locally), or a Content Modifier body (same pattern, seen only in a UI sample); change the value of an existing parameter in `parameters.prop` (verified only for an iFlow with no values set in the Configure screen; otherwise tell the user it is unverified)

Not supported (no real sample yet):
- Any other step or adapter (Router, JavaScript or other script types, receiver adapters other than HTTP, Splitter, Local Integration Process, Message Mapping, …)
- Exception Subprocess ending with Error End or Escalation End, any step inside it other than one Content Modifier, or more than one Exception Subprocess
- HTTP receiver: any Method other than GET, Send Body, any Authentication other than None (credentials), or any other setting (proxy, timeout, headers, retry)
- Groovy Script with a Script Collection (`scriptBundleId`), a function other than `processData` (`scriptFunction`), or a script file outside `src/main/resources/script/`
- Other Content Modifier Source Types (Header, Property, XPath, Number Range, variables), `<` or `&` in a message body
- Creating a new iFlow from scratch (`MANIFEST.MF`, `.project`, …) or changing component versions. A new iFlow starts empty in CPI: the user creates it there, connects it to the branch and pushes; then edit it locally
- Externalizing any other field or part of a value, reusing, renaming or removing a parameter, special characters in a parameter value, or creating `parameters.prop` / `parameters.propdef` when the iFlow has none yet

For an unsupported request, **do not write the XML**. Tell the user that this skill has no verified sample for it, and offer two options: build that part in the CPI designer (then Push and continue locally), or add a sample for it first (make the change in the UI, one action per commit, and Push). Do the supported part of a mixed request only if the user agrees.

## Workflow

The user performs the CPI steps in the CPI web UI. Tell them exactly what to do and ask for the result.

For a new iFlow, ask the user to create it empty in CPI (Sender, Start, End, Receiver), connect it to the branch and Push, then start at step 1. The skill never writes a new iFlow folder.

1. **Start clean.** Ask the user to Push every change saved in CPI (designer or Configure screen), then pull the branch locally. Unpushed CPI changes cause Pull to be rejected when the same place changed, and a local Description change is silently dropped.
2. **Edit locally.** Find the iFlow by `Bundle-Name` in `META-INF/MANIFEST.MF`, not by the `.iflw` file name.
3. **Check:** `python3 scripts/check_iflw.py <iFlow folder>`. Fix every error before committing, and fix what each warning points to (edge waypoints, overlapping shapes, a `>` escaped only once, an unused parameter, an unreferenced `.groovy` file). For each `.iflw` it also reads `parameters.prop` and `parameters.propdef` from the iFlow's `src/main/resources/` folder (two levels above `scenarioflows/integrationflow/<name>.iflw`), so keep the Git Access layout: every `{{name}}` must be defined in both files, and every Groovy Script step's `script` file must exist in `src/main/resources/script/`.
4. **Commit and push** to the branch connected to the iFlow.
5. **In CPI:** Pull → open the iFlow (view mode is enough) and **check that your change is there** (the new step, the changed value, the edited script, the receiver's Address); if it is not, Pull again → Deploy (no Edit or Save needed) → wait for Started → call it and compare with the expected result. A Pull without errors once left the old content in CPI, and the old version was deployed (cause unverified). If the iFlow was never saved in the CPI designer, ask the user to Edit → Save before Deploy (deploying it without Save worked only twice so far). If the deployment fails or the result is wrong, ask the user to open the iFlow and check the Problems tab.
6. **Do not Push from CPI.** The next local edit continues from your own commit. Pushing from CPI can end in a dead end when other iFlows on the branch changed: Push says the artifact is "behind" and Pull says "already up to date". Only if the user did Edit → Save or changed Configure values in CPI: close edit mode (Cancel), reload the page if the iFlow still shows as locked, Push, and pull locally before the next edit. If that Push is rejected as "behind", follow "Push rejected: artifact is behind" in [references/workflow.md](references/workflow.md).

If Pull fails or the designer shows errors, see "When Pull fails" in [references/workflow.md](references/workflow.md).

## Rules

- Use only `ifl:property` keys, `cmdVariantUri` values and `componentVersion` values that appear in the references. If something is not there, stop and ask the user. Never invent keys, values or versions.
- Keep every existing step's version pair as it is. For a new Content Modifier, copy the 7-key template in [references/components/content-modifier.md](references/components/content-modifier.md); for a new Groovy Script step, the 7-key template in [references/components/groovy-script.md](references/components/groovy-script.md); for a new HTTPS sender, the 20-key message flow in [references/components/https-sender.md](references/components/https-sender.md); for a new Request Reply step, the 3-key service task in [references/components/request-reply.md](references/components/request-reply.md) and the 48-key HTTP receiver message flow in [references/components/http-receiver.md](references/components/http-receiver.md); for a new Exception Subprocess, the template in [references/components/exception-subprocess.md](references/components/exception-subprocess.md). An older Content Modifier version pair already in the iFlow is fine; CPI accepts it and does not migrate it.
- For every element you add or change, write its `bpmndi` `BPMNShape` (nodes, participants) or `BPMNEdge` (sequence and message flows) and keep all references consistent. Coordinates only need to be roughly right.
- **Never move or resize existing shapes** (steps, Start/End, sender/receiver, the pool). CPI puts existing coordinates back after Pull, so a new step placed where a moved shape used to be ends up hidden under it. Put a new step where it overlaps nothing: free space between its neighbors, else below the row inside the pool (unverified how it is drawn). If it does not fit, still move nothing and ask the user to run the designer's auto layout after Pull. Fix every overlap warning from `check_iflw.py`. See "Layout to imitate" in [references/iflw-structure.md](references/iflw-structure.md).
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
| HTTPS sender keys and settings, adding an HTTPS sender to an empty iFlow | [references/components/https-sender.md](references/components/https-sender.md) |
| Groovy Script step template, script file, Allowed Header(s) | [references/components/groovy-script.md](references/components/groovy-script.md) |
| Request Reply step template, inserting it and connecting a receiver | [references/components/request-reply.md](references/components/request-reply.md) |
| HTTP receiver keys, Address, Query, response headers | [references/components/http-receiver.md](references/components/http-receiver.md) |
| Exception Subprocess template, error response, `CamelHttpResponseCode`, `${exception.message}` | [references/components/exception-subprocess.md](references/components/exception-subprocess.md) |
| Externalized parameters: `{{name}}`, `parameters.prop`, `parameters.propdef`, Configure values | [references/externalized-parameters.md](references/externalized-parameters.md) |

Facts marked **unverified** in the references were not tested. When a task depends on one, tell the user and ask them to check the result in CPI.
