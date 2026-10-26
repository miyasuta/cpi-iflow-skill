# Design: declare first, then build

When the user gives a goal ("receive orders from A, map them, send them to B") instead of exact steps, decide which components realize it and in which order, **declare that design, and wait for approval**. Nobody builds anything before that. The design follows SAP's integration flow design guidelines ([guidelines.md](guidelines.md)). It is the design the guidelines call for, not the design that is easiest to build: how the iFlow will be built (in the CPI designer, by another tool, by an AI) never changes it.

Related: [guidelines.md](guidelines.md) (what a good design must respect), [components.md](components.md) (which standard component fits a purpose).

## Waiting for approval

- After the declaration, **end your turn**. Do not write any iFlow file, XML or script before the user approves.
- Approval is an explicit yes to the declaration. A question or a correction is not approval: answer it, revise the declaration, show the whole flow table again, and wait again.
- If something must change after approval (a step cannot work as declared, a new step is needed), declare the change and wait again.

## Declaration format

The declaration is the contract between this skill and whoever builds the iFlow. The build skill **cpi-iflow-build** reads it from the conversation as it is (it is not saved to a file), so keep the headings, their order and the flow table columns exactly as below. Change this format only together with cpi-iflow-build.

Write the text in the user's language; keep the headings' numbers, step names and component names in English.

```markdown
## Design: <iFlow name, see "Naming conventions" in guidelines.md (B1)>

### 0. Assumptions
- Trigger: <who or what starts the iFlow: sender system and adapter, or a timer>
- Volume: <messages per call or per run, size>
- Receiver: <system, protocol, what it accepts>
- Authentication: <inbound and outbound; credentials the user deploys in Security Material>
- Data: <formats; where the mapping rules come from>
Correct anything that is wrong before approving.

### 1. Flow
| # | Step name | Component | Role |
|---|---|---|---|
| 1 | <role-based English name> | <component (+ adapter)> | <what it does> |
| … | | | |
| E | <name> | Exception Subprocess (<steps inside>) | <how errors end> |

### 2. Why this shape
- <component choice> — <guideline it follows, with link>
- <for every Groovy Script: why no standard component does it>

### 3. Externalized
- Externalize: <value — reason (changes per landscape)>
- Keep fixed: <value — reason>

### 4. Build order
- <before building: credentials and other artifacts to deploy>
- <which part (or which iFlow) first, and the test call after each part>

### 5. Questions
- <what could not be decided from the goal: retries, volume limits, delta or full load, …>
```

Rules for the flow table:

- One row per step in the order a message passes them. Adapters go in the row of the step they belong to (the sender adapter with the Start row, a receiver adapter with its Request Reply row). The Exception Subprocess is row `E` (inner steps `E1`, `E2`, … if they need their own rows).
- **Step name**: an English name that says what the step does. Never the designer's default (`Content Modifier 1`, `Request Reply 1`). SAP's naming conventions suggest a short camelCase description such as `setContentType` ([guidelines.md](guidelines.md), B1).
- **Component**: the component and the settings that decide its shape (method, authentication type, end event type), because a builder needs them to know what the row is.
- When the design changes an existing iFlow, list its existing steps too and end their Role with "(existing)".

## Several iFlows

A design may span several iFlows (for example, to reuse a part or to call a common error handler). Write sections 0–5 for each iFlow, plus one **Interface** section for each connection between them:

```markdown
### Interface: <caller> → <callee>
- Adapter: ProcessDirect, address `<address>`
- Request: Body <format and structure>; headers <names>; exchange properties <names, if the callee needs them>
- Response: Body <format>; headers <names>
- Errors: <how the callee ends on error (its Exception Subprocess end type) and how the caller handles it>
```

Build one iFlow at a time. Build the callee first, so the caller can be tested against it. Splitting work *inside* one iFlow is done with Local Integration Processes, not with more iFlows ([guidelines.md](guidelines.md), A7).

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
| # | Step name | Component | Role |
|---|---|---|---|
| 1 | Start (hourly) | Timer start event | Starts a run every hour |
| 2 | setLogIdentifiers | Content Modifier | Sets SAP_Sender, SAP_Receiver, SAP_MessageType, SAP_ApplicationID for searching message logs |
| 3 | getSalesOrders | Request Reply + OData V2 receiver | Reads the sales orders from S/4HANA |
| 4 | mapToOrderService | Message Mapping | Maps the S/4HANA structure to the order service structure |
| 5 | convertToJson | XML to JSON Converter | Changes the format only |
| 6 | setContentType | Content Modifier | Sets Content-Type: application/json |
| 7 | postOrders | Request Reply + HTTP receiver (POST, OAuth2 Client Credentials) | Sends the orders |
| 8 | End | End event | |
| E | handleError | Exception Subprocess (Error Start → Error End) | Ends a failed run as Failed in monitoring |

### 2. Why this shape
- Reading S/4HANA: the OData adapter, the standard channel for OData services; no hand-built HTTP calls.
- Mapping: Message Mapping, SAP's recommendation for mapping to a new schema; Converter for a pure format change ("Guidelines for Modifying Content"). No Groovy Script: no step needs the script API.
- Error handling: an Exception Subprocess ("Handle Errors Gracefully"). Error End, not End Message, because no caller waits for a reply and a failed run must show as Failed.
- Identifiers for message monitoring ("Use Custom Header Properties to Search for Message Processing Logs"; tenant rule "Define Identifiers To Search In Message Processing Logs").
- One iFlow, no Local Integration Process: the flow is short and linear.

### 3. Externalized
- Externalize: S/4HANA address and credential name, order service address and credential name, timer schedule — they change per landscape.
- Keep fixed: entity and query options, header names, the mapping, the identifier values — they are part of the interface, not of the landscape.

### 4. Build order
- Before building: you deploy the S/4HANA and order service credentials in Security Material.
- First rows 2–7 with a manual start, and check the JSON that reaches the order service; then the timer (row 1) and row E.

### 5. Questions
- Full load or only orders changed since the last run? Delta needs the last run time stored between runs (more steps).
- Which value for SAP_ApplicationID? A run has many orders; I propose the run's start time.
- Does the order service have an OpenAPI spec? Then Message Mapping can produce JSON directly and row 5 is dropped.
- On failure, is "Failed in monitoring" enough, or do you need a retry or an alert?
```
