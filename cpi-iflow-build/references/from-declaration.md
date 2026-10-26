# Building from an approved declaration

The design comes from the **cpi-iflow-design** skill: a declaration the user approved, in the conversation. This skill does not design and does not change the design. It decides, row by row, who builds each step (this skill or the user in the CPI designer), shows that to the user, writes its rows, and hands the rest over.

## What the declaration looks like

The format is defined in cpi-iflow-design ([../../cpi-iflow-design/references/process.md](../../cpi-iflow-design/references/process.md), "Declaration format"). This skill relies on:

- `## Design: <iFlow name>`, then sections `0. Assumptions`, `1. Flow`, `2. Why this shape`, `3. Externalized`, `4. Build order`, `5. Questions`
- the flow table with columns `#`, `Step name`, `Component`, `Role`; rows `1`, `2`, … in message order, `E` (and `E1`, `E2`, …) for the Exception Subprocess; "(existing)" at the end of the Role of steps the iFlow already has
- with several iFlows: sections 0–5 per iFlow and an `Interface: <caller> → <callee>` section per connection

If what the user gives is not an approved declaration in this form (a goal, a list of wishes, an unapproved or partial design), stop: ask the user to design it first with cpi-iflow-design, or to approve the declaration as it is.

If section 5 still has open questions that change the flow, ask them before marking the rows.

## 1. Mark who builds each row

Add a column **Written by** to the flow table. Decide it **only** from the Scope section of [SKILL.md](../SKILL.md), including the limits inside each Supported item:

- **Skill**: the component *and the way it is used* are Supported in Scope. Marked "verified once" is enough.
- **UI**: everything else. A component that is in Scope but used outside its limits is UI too, for example:
  - a Router that is not directly after Start, or a route with more than one step
  - a second Exception Subprocess, an Exception Subprocess ending in Error End or Escalation End, or any step inside it other than one Content Modifier
  - a second Groovy Script step in the same iFlow
  - an HTTP receiver with Basic authentication, a timeout, or other settings outside Scope
  - ProcessDirect, OData, JMS, Timer start, Message Mapping, Converter, Splitter, Local Integration Process, … (not in Scope at all)
- **Skill (unverified)**: inside Scope, but a combination nobody tested (for example a new Request Reply step written directly with POST and OAuth2 Client Credentials). Say what is unverified.
- **exists**: rows whose Role ends with "(existing)".
- Settings count too. If the design calls for an `ifl:property` value that no sample has (for example a custom User Role instead of `ESBMessaging.send`), the skill writes the step with the sample value and hands that one setting to the UI: "The guideline asks for a dedicated role; the skill has no verified sample for it, so set it in the designer."
- Externalizing a field the skill cannot externalize (anything but the HTTPS sender Address and Content Modifier header or body values, see [externalized-parameters.md](externalized-parameters.md)), or any externalization in an iFlow that has no `parameters.prop` yet, is UI.
- Step names: a free `name` is verified for Content Modifier and Groovy Script steps; for other step types it is **unverified**, so mention it when the skill writes one. Renaming channels and participants is **unverified** (the receiver participant's name is also copied into the HTTP receiver's `system` key); leave them and hand the names over.

Never change the design to stay inside Scope (for example mapping with a Groovy Script because Message Mapping is not in Scope). A row the skill cannot write is UI, nothing else.

### What the skill can write, by component

This repeats the Scope in [SKILL.md](../SKILL.md); if the two differ, SKILL.md wins.

| Component | Skill writes it? |
|---|---|
| HTTPS sender | Yes: add to an iFlow without a sender; Address, CSRF, authorization ([components/https-sender.md](components/https-sender.md)). A new sender is verified with CSRF off; written with CSRF on it is **unverified** (either write it on and say so, or add it off and switch it on in a second round trip, both verified). Custom User Role: UI. |
| Timer start event | No (UI) |
| Content Modifier | Yes: rows with Type `constant` / `expression`, body ([components/content-modifier.md](components/content-modifier.md)). Message log identifiers (`SAP_Sender`, `SAP_ApplicationID`, …) as constants or expressions: yes. Other source types (XPath, Header, Property, …): UI. |
| Router | Yes, directly after Start, Non-XML `=` on a header, one Content Modifier and its own End per route, a default route ([components/router.md](components/router.md)). Anywhere else, XPath conditions, routes that merge or have more steps: UI. |
| Request Reply + HTTP receiver | Yes: GET or POST, Authentication None or OAuth2 Client Credentials with a deployed credential ([components/request-reply.md](components/request-reply.md), [components/http-receiver.md](components/http-receiver.md)). Other methods, Basic, certificates, timeouts, request headers: UI. |
| Request Reply + OData receiver | No (UI) |
| Converter, Message Mapping, XSLT, Filter, Content Enricher, Splitter, Gather, Encoder, Decoder, Encryptor | No (UI) |
| Exception Subprocess | Yes, one per iFlow: Error Start → one Content Modifier → End Message ([components/exception-subprocess.md](components/exception-subprocess.md)). Error End, Escalation End, other inner steps: UI. |
| Local Integration Process + Process Call | No (UI) |
| ProcessDirect, JMS | No (UI) |
| Externalized parameters | Yes for the HTTPS sender Address and Content Modifier header values, when `parameters.prop` exists ([externalized-parameters.md](externalized-parameters.md)). Other fields: UI. |
| Groovy Script | Yes, one step per iFlow, `processData`, a script file in `src/main/resources/script/`, no Script Collection ([components/groovy-script.md](components/groovy-script.md)). Scripts create no MPL attachments unless the design asks for them, and then behind a switch. |

## 2. Show the marked table and wait

Show the user:

- the flow table with the **Written by** column, and one line for every "Skill (unverified)" row saying what is unverified
- the build plan:
  1. You: create the empty iFlow `<name>` in CPI (Sender, Start, End, Receiver), connect it to the branch, Push. (Skip if it exists.)
  2. Skill: writes rows `<…>`; you Pull and check.
  3. You: build rows `<…>` in the designer (instructions follow after the skill's part), Save, Deploy, test.
  4. You: Push from CPI; the skill pulls before the next local edit.

Then **end your turn and wait for the user's explicit approval. Before approval, do not write or change any file, do not commit, do not push.** If the user moves a row to the UI, follow that. If the user asks to change the design itself, send them back to cpi-iflow-design.

After approval, write exactly what the Skill rows say. If you find while writing that a row cannot be written as declared, stop, say so, and wait again.

## 3. Write the skill rows and leave room for the UI rows

When a UI row sits between skill rows, the skill still writes all its rows in one edit and keeps the iFlow valid:

- Connect each skill step to the next skill step directly, skipping the UI rows. The iFlow then pulls and deploys, but it does not do its job until the UI rows are in.
- Leave free space in the diagram where each UI step will go (about one step width per missing step, between the neighbors). Never move existing shapes ([SKILL.md](../SKILL.md) Rules).
- In the hand-over, name the two steps between which each UI step is inserted. The user inserts it on the existing connection in the designer.
- If a UI row replaces something the empty iFlow already has (for example a Timer start instead of the message Start with a sender), leave that part as it is and hand it over.

Then continue with the Workflow in [SKILL.md](../SKILL.md) (check, commit, push, Pull in CPI).

## 4. Hand the UI rows to the user

After writing (or right away, when the skill writes nothing), list every UI row in flow order:

```markdown
**<#> <Step name>** — <Component>
- Where: between `<step>` and `<step>` (or: inside the Exception Subprocess, after Error Start)
- Settings: <the values that matter: address, entity, method, credential name, mapping source and target, …>
- Externalize: <fields, with parameter names>
- Name: rename the step to `<Step name>`
```

For example, row 3 of the sales order example in cpi-iflow-design:

```markdown
**3 getSalesOrders** — Request Reply + OData V2 receiver
- Where: between `setLogIdentifiers` and `setContentType` (rows 4 and 5 follow it)
- Settings: a new receiver participant for S/4HANA; Address of API_SALES_ORDER_SRV; entity A_SalesOrder; the fields from your field list; your S/4HANA credential
- Externalize: Address as `s4Address`, Credential Name as `s4Credential`
- Name: rename the step to `getSalesOrders`
```

Then: "Save, Deploy, and run <the test call>. Push from CPI when done, so that the next local edit starts from your version." The Push and the local pull follow step 6 of the Workflow in [SKILL.md](../SKILL.md). After that, the UI-built steps are existing steps for the skill: keep them unchanged, and never copy their keys into new steps unless the references show them.

## Several iFlows

Build one iFlow per session. Build the callee first, so the caller can be tested against it. The ProcessDirect adapters of each Interface section are always UI (not in Scope).
