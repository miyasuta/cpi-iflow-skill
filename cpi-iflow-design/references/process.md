# Design: declare first, then write

When the user gives a goal ("receive orders from A, map them, send them to B") instead of exact steps, decide which components realize it and in which order, **declare that design, and wait for approval** before writing any XML. The design follows SAP's integration flow design guidelines ([guidelines.md](guidelines.md)). It is never bent to fit what this skill can write: a part the skill cannot write is built by the user in the CPI designer.

Related: [guidelines.md](guidelines.md) (what a good design must respect), [components.md](components.md) (which standard component fits a purpose, and whether the skill can write it).

## When to declare

| Request | Declaration |
|---|---|
| A goal ("get X from A and send it to B as JSON") | Yes |
| Add steps or components (more than one step, or a step whose kind or position the user left open) | Yes |
| Change values of existing steps only (header value, Address, script code, a parameter value) | No. Edit as before. |
| One step with its component and position given ("put a Content Modifier between these two") | No table. If the request hits an "A" anti-pattern in [guidelines.md](guidelines.md) (for example a Groovy Script for what a standard step does), say so in one or two sentences before writing, name the standard component, and let the user decide. |

When unsure, declare. A short declaration costs one turn; a wrong iFlow costs a round trip through CPI.

## Waiting for approval

- After the declaration, **end your turn**. Do not write or change any file, do not commit, do not push, before the user approves.
- Approval is an explicit yes to the declaration. A question or a correction is not approval: answer it, revise the declaration, show the whole flow table again, and wait again.
- After approval, write exactly what the flow table says. If you find while writing that something must change (a step cannot be written as declared, a new step is needed), stop, declare the change, and wait again.

## The "Written by" column

Decide it **only** from the Scope section of [SKILL.md](../../SKILL.md), including the limits inside each Supported item:

- **Skill**: the component *and the way it is used* are Supported in Scope. Marked "verified once" is enough.
- **UI**: everything else. A component that is in Scope but used outside its limits is UI too, for example:
  - a Router that is not directly after Start, or a route with more than one step
  - a second Exception Subprocess, an Exception Subprocess ending in Error End or Escalation End, or any step inside it other than one Content Modifier
  - a second Groovy Script step in the same iFlow
  - an HTTP receiver with Basic authentication, a timeout, or other settings outside Scope
  - ProcessDirect, OData, JMS, Timer start, Message Mapping, Converter, Splitter, Local Integration Process, … (not in Scope at all)
- **Skill (unverified)**: inside Scope, but a combination nobody tested (for example a new Request Reply step written directly with POST and OAuth2 Client Credentials). Say what is unverified.
- Settings count too. If the guidelines call for an `ifl:property` value that no sample has (for example a custom User Role instead of `ESBMessaging.send`), the skill writes the step with the sample value and the declaration hands that one setting to the UI: "The guideline asks for a dedicated role; the skill has no verified sample for it, so set it in the designer."
- Externalizing a field the skill cannot externalize (anything but the HTTPS sender Address and Content Modifier header or body values, see [../externalized-parameters.md](../externalized-parameters.md)), or any externalization in an iFlow that has no `parameters.prop` yet, is UI.

Never change the design to stay inside Scope (for example mapping with a Groovy Script because Message Mapping is not in Scope). That is an "A" anti-pattern in itself.

## Declaration template

Write the declaration in the user's language. Keep this order and the flow table columns.

```markdown
## Design: <iFlow name, see "Naming conventions" in guidelines.md>

### 0. Assumptions
- Trigger: <who or what starts the iFlow: sender system and adapter, or a timer>
- Volume: <messages per call or per run, size>
- Receiver: <system, protocol, what it accepts>
- Authentication: <inbound and outbound; credentials the user deploys in Security Material>
- Data: <formats; where the mapping rules come from>
Correct anything that is wrong before approving.

### 1. Flow
| # | Step name | Component | Role | Written by |
|---|---|---|---|---|
| 1 | <role-based English name> | <component (+ adapter)> | <what it does> | Skill / UI / Skill (unverified: …) |
| … | | | | |
| E | <name> | Exception Subprocess (<steps inside>) | <how errors end> | Skill / UI |

### 2. Why this shape
- <component choice> — <guideline it follows, with link>
- <for every Groovy Script: why no standard component does it>

### 3. Externalized
- Externalize: <value — reason (changes per landscape)>
- Keep fixed: <value — reason>

### 4. Build order
1. You: create the empty iFlow in CPI, connect it to the branch, Push.
2. Skill: writes rows <…>; you Pull and check.
3. You: build rows <…> in the designer (instructions below), Save, Deploy, test.
4. You: Push from CPI; the skill pulls before the next local edit.

### 5. Questions
- <what the skill could not decide: retries, volume limits, delta or full load, …>
```

Rules for the flow table:

- One row per step in the order a message passes them. Adapters go in the row of the step they belong to (the sender adapter with the Start row, a receiver adapter with its Request Reply row). The Exception Subprocess is row `E` (inner steps `E1`, `E2`, … if they need their own rows).
- **Step name**: an English name that says what the step does. Never the designer's default (`Content Modifier 1`, `Request Reply 1`). SAP's naming conventions suggest a short camelCase description such as `setContentType` ([guidelines.md](guidelines.md), B1). A free name is verified for Content Modifier and Groovy Script steps; for other step types it is **unverified**, so mention it when the skill writes one.
- Rows for steps the iFlow already has (Start, End) may say "exists".

## Where the UI steps go while the skill writes its part

When a UI row sits between skill rows, the skill still writes all its rows in one edit and keeps the iFlow valid:

- Connect each skill step to the next skill step directly, skipping the UI rows. The iFlow then pulls and deploys, but it does not do its job until the UI rows are in.
- Leave free space in the diagram where each UI step will go (about one step width per missing step, between the neighbors). Never move existing shapes ([SKILL.md](../../SKILL.md) Rules).
- In the hand-over, name the two steps between which each UI step is inserted. The user inserts it on the existing connection in the designer.
- If a UI row replaces something the empty iFlow already has (for example a Timer start instead of the message Start with a sender), leave that part as it is and hand it over.

## Handing steps to the user

After writing (or right away, when the skill writes nothing), list every UI row in flow order:

```markdown
**<#> <Step name>** — <Component>
- Where: between `<step>` and `<step>` (or: inside the Exception Subprocess, after Error Start)
- Settings: <the values that matter: address, entity, method, credential name, mapping source and target, …>
- Externalize: <fields, with parameter names>
- Name: rename the step to `<Step name>`
```

Then: "Save, Deploy, and run <the test call>. Push from CPI when done, so that the next local edit starts from your version." The Push and the local pull follow step 6 of the Workflow in [SKILL.md](../../SKILL.md). After that, the UI-built steps are existing steps for the skill: keep them unchanged, and never copy their keys into new steps unless the references show them.

## Several iFlows

A design may span several iFlows (for example, to reuse a part or to call a common error handler). Write sections 0–5 for each iFlow, plus one **Interface** section for each connection between them:

```markdown
### Interface: <caller> → <callee>
- Adapter: ProcessDirect, address `<address>` (always UI: not in Scope)
- Request: Body <format and structure>; headers <names>; exchange properties <names, if the callee needs them>
- Response: Body <format>; headers <names>
- Errors: <how the callee ends on error (its Exception Subprocess end type) and how the caller handles it>
```

Build one iFlow per session. Build the callee first, so the caller can be tested against it. Splitting work *inside* one iFlow is done with Local Integration Processes, not with more iFlows ([guidelines.md](guidelines.md), A7).

## Example

Goal from the user: "Every hour, read the sales orders from S/4HANA through OData, turn them into JSON, and POST them to our order service's REST API."

```markdown
## Design: Global_SalesOrder_S4_to_OrderService

### 0. Assumptions
- Trigger: a timer, every hour. No system calls this iFlow.
- Source: S/4HANA OData V2 service API_SALES_ORDER_SRV, entity A_SalesOrder; credential deployed by you in Security Material.
- Volume: up to a few hundred orders per run, sent in one POST as a JSON array.
- Receiver: the order service accepts POST with a JSON array; OAuth2 Client Credentials, credential deployed by you.
- Mapping: you provide the field list (S/4HANA field → order service field). No value mapping.

### 1. Flow
| # | Step name | Component | Role | Written by |
|---|---|---|---|---|
| 1 | Start (hourly) | Timer start event | Starts a run every hour | UI |
| 2 | setLogIdentifiers | Content Modifier | Sets SAP_Sender, SAP_Receiver, SAP_MessageType, SAP_ApplicationID for searching message logs | Skill |
| 3 | getSalesOrders | Request Reply + OData V2 receiver | Reads the sales orders from S/4HANA | UI |
| 4 | mapToOrderService | Message Mapping | Maps the S/4HANA structure to the order service structure | UI |
| 5 | convertToJson | XML to JSON Converter | Changes the format only | UI |
| 6 | setContentType | Content Modifier | Sets Content-Type: application/json | Skill |
| 7 | postOrders | Request Reply + HTTP receiver (POST, OAuth2 Client Credentials) | Sends the orders | Skill (unverified: a new step written with POST and OAuth2 in one edit) |
| 8 | End | End event | | exists |
| E | handleError | Exception Subprocess (Error Start → Error End) | Ends a failed run as Failed in monitoring | UI (Error End is outside Scope) |

### 2. Why this shape
- Reading S/4HANA: the OData adapter, the standard channel for OData services; no hand-built HTTP calls.
- Mapping: Message Mapping, SAP's recommendation for mapping to a new schema; Converter for a pure format change ("Guidelines for Modifying Content"). No Groovy Script: no step needs the script API.
- Error handling: an Exception Subprocess ("Handle Errors Gracefully"). Error End, not End Message, because no caller waits for a reply and a failed run must show as Failed.
- Identifiers for message monitoring ("Use Custom Header Properties to Search for Message Processing Logs"; tenant rule "Define Identifiers To Search In Message Processing Logs").
- One iFlow, no Local Integration Process: the flow is short and linear.

### 3. Externalized
- Externalize: S/4HANA address and credential name, order service address and credential name, timer schedule — they change per landscape.
- Keep fixed: entity and query options, header names, the mapping, the identifier values — they are part of the interface, not of the landscape.
- The skill cannot externalize these fields (and the empty iFlow has no parameters.prop yet), so you externalize them in the designer.

### 4. Build order
1. You: create the empty iFlow Global_SalesOrder_S4_to_OrderService in CPI, connect it to the branch, Push.
2. Skill: writes rows 2, 6 and 7 (Start → 2 → 6 → 7 → End, with space left for 3–5); you Pull and check.
3. You: build rows 1, 3, 4, 5 and E in the designer and externalize the values in section 3; Save, Deploy, run once.
4. You: Push from CPI; the skill pulls before any further local edit.

### 5. Questions
- Full load or only orders changed since the last run? Delta needs the last run time stored between runs (more steps, built in the UI).
- Which value for SAP_ApplicationID? A run has many orders; I propose the run's start time.
- Does the order service have an OpenAPI spec? Then Message Mapping can produce JSON directly and row 5 is dropped.
- On failure, is "Failed in monitoring" enough, or do you need a retry or an alert?
```

Hand-over for row 3 in this example:

```markdown
**3 getSalesOrders** — Request Reply + OData V2 receiver
- Where: between `setLogIdentifiers` and `setContentType` (rows 4 and 5 follow it)
- Settings: a new receiver participant for S/4HANA; Address of API_SALES_ORDER_SRV; entity A_SalesOrder; the fields from your field list; your S/4HANA credential
- Externalize: Address as `s4Address`, Credential Name as `s4Credential`
- Name: rename the step to `getSalesOrders`
```
