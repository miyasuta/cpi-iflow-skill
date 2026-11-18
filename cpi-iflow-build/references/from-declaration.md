# Building from an approved declaration

The design comes from the **cpi-iflow-design** skill: a design file `docs/<design name>.md` the person approved. Read it from the file, not from the conversation: the file has the answers to the questions. This skill does not design and does not change the design. It reads the declaration row by row, finds the settings of each row in the references, and builds the iFlow through the Workflow in [SKILL.md](../SKILL.md).

The approval of the declaration is an approval of *what* to build. It is not an approval of the values written for it: the stop before push in the Workflow still applies.

## Reading the declaration

The format is defined in cpi-iflow-design ([../../cpi-iflow-design/references/process.md](../../cpi-iflow-design/references/process.md), "Declaration format"). This skill relies on:

- `# <design name>`, then for each iFlow `## Design: <iFlow name>` and sections `0. Assumptions`, `1. Flow`, `2. Why this shape`, `3. Externalized`, `4. Build order`, `5. Questions`
- the flow table with columns `#`, `Step name`, `Component`, `Role`; rows `1`, `2`, … in message order; row `E` (and `E1`, `E2`, … for its inner steps) for the Exception Subprocess; "(existing)" at the end of the Role of steps the iFlow already has
- adapters in the row of the step they belong to: the sender adapter with the Start row, a receiver adapter with its Request Reply row
- the Component column naming the settings that decide a row's shape (method, authentication type, end event type)
- with several iFlows: sections 0–5 per iFlow and an `Interface: <caller> → <callee>` section per connection
- section 5 with questions `Q1`, `Q2`, …, each ending with `Open` or `Answered: <answer>`

The Mermaid diagrams (in section 1, and the overview for several iFlows) are for people. Build from the flow table; if the diagram and the table disagree, stop and send the person back to cpi-iflow-design.

If what the person gives is not an approved design in this form (a goal, a list of wishes, an unapproved or partial design), stop: ask them to design it first with cpi-iflow-design, or to approve the design as it is.

If section 5 still has an `Open` question, stop and send the person back to cpi-iflow-design to answer it there, so that the answer is written into the file.

## What each row needs

For each row, list the settings it uses:

- the component and the settings named in the Component column, from the component's file in [components/](components/)
- the values the Role and section 0 call for (addresses, header names, body, the name of a credential the person deployed in Security Material). Ask for any value the declaration leaves open; never ask for or write a secret
- the fields section 3 externalizes, from [externalized-parameters.md](externalized-parameters.md)
- the Step name, written as the step's name

Then decide the row:

- **Every setting is in the references**: write it with those values, passed explicitly.
- **A shape the references do not describe** (a step placement, routes joining an End, an end type not listed) is unknown too: mark the row unverified and name the shape.
- **A setting is not in the references** (or the component has no file at all): follow "Unknown values" in [SKILL.md](../SKILL.md) for that setting. The rest of the row is still written from the references.
- **"(existing)" rows**: leave them unchanged. Do not copy their settings into new steps unless the references show the same values.

Never change the design to stay inside the references (for example a Groovy Script instead of a Message Mapping because only Groovy Script has a file). A missing value goes through "Unknown values"; it never changes the flow. If a row turns out not to work as declared, stop, say so, and send the person back to cpi-iflow-design to change the design.

Before writing, tell the person which rows need unknown values, so that a designer step (if one is needed) can be done once for all of them.

## Showing the result before push

At the stop before push (Workflow in [SKILL.md](../SKILL.md)), show the flow table with one more column, **Values**:

| # | Step name | Component | Values |
|---|---|---|---|
| 2 | setLogIdentifiers | Content Modifier | references |
| 3 | callBackend | Request Reply + HTTP receiver (POST, OAuth2 Client Credentials) | references |
| 4 | convertToJson | XML to JSON Converter | **unverified**: every setting (no file for this component) |

Mark every row that uses an unknown value as **unverified** and name the settings. Below the table, give the diff summary (or the list of written values) as the Workflow says. Wait for approval.

## Build order and test calls

Follow section 4 of the declaration:

- The person deploys the credentials and other artifacts it lists before the iFlow is deployed. The skill only writes their names.
- When section 4 builds the iFlow in parts, do one round of the Workflow per part (write, stop, push, deploy, call), with the test call it names.

## Several iFlows

Build one iFlow at a time. Build the callee first, so the caller can be tested against it. Take the adapter and address of each connection from its Interface section; settings for that adapter that are not in the references follow "Unknown values" like any other.
