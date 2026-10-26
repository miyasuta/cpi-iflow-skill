# Choosing components

Pick the standard component for each purpose first; a Groovy Script is the last resort. Then look up whether the skill can write it: that fills the "Written by" column of the flow table ([process.md](process.md)). The writable part repeats the Scope in [SKILL.md](../../SKILL.md); if the two differ, SKILL.md wins.

Main SAP sources: [Guidelines for Modifying Content](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/guidelines-for-modifying-content-6a7c9a1.md) ("When to Use What?"), [Communication between Integration Flows](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/communication-between-integration-flows-ab5db7b.md), [Apply a Balanced Encapsulation of the Integration Logics](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/apply-a-balanced-encapsulation-of-the-integration-logics-e010db3.md), [Handle Errors Gracefully](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/handle-errors-gracefully-42c95f7.md).

## Purpose → component

| Purpose | Standard component | Skill writes it? |
|---|---|---|
| Receive an HTTP call | HTTPS sender | Yes: add to an iFlow without a sender; Address, CSRF, authorization ([../components/https-sender.md](../components/https-sender.md)). Custom User Role: UI. |
| Start on a schedule | Timer start event | No (UI) |
| Set headers, properties, or a fixed or templated body | Content Modifier | Yes: rows with Type `constant` / `expression`, body ([../components/content-modifier.md](../components/content-modifier.md)). Other source types (XPath, Header, Property, …): UI. |
| Branch on a header value | Router | Yes, directly after Start, Non-XML `=` on a header, one Content Modifier and its own End per route, a default route ([../components/router.md](../components/router.md)). Anywhere else, XPath conditions, routes that merge or have more steps: UI. |
| Call an HTTP/REST service and use the reply | Request Reply + HTTP receiver | Yes: GET or POST, Authentication None or OAuth2 Client Credentials with a deployed credential ([../components/request-reply.md](../components/request-reply.md), [../components/http-receiver.md](../components/http-receiver.md)). Other methods, Basic, certificates, timeouts, request headers: UI. |
| Read or write an OData service | Request Reply + OData receiver | No (UI) |
| Change the format only (XML ↔ JSON, CSV → XML) | Converter | No (UI) |
| Map to a different structure (XML or JSON) | Message Mapping (or XSLT for XML → XML) | No (UI) |
| Keep only part of an XML body | Filter | No (UI) |
| Merge in data from another call | Content Enricher | No (UI) |
| Process the items of a message one by one | Splitter (and Gather) | No (UI) |
| Encode, compress, encrypt | Encoder, Decoder, Encryptor | No (UI) |
| Handle errors | Exception Subprocess | Yes, one per iFlow: Error Start → one Content Modifier → End Message ([../components/exception-subprocess.md](../components/exception-subprocess.md)). Error End, Escalation End, other inner steps: UI. |
| Split one iFlow into parts | Local Integration Process + Process Call | No (UI) |
| Call another iFlow on the same tenant, synchronously | ProcessDirect (receiver in the caller, sender in the callee) | No (UI). Not the HTTP receiver ([guidelines.md](guidelines.md), A5). |
| Call another iFlow asynchronously, retry later | JMS queue | No (UI) |
| Values that change per landscape | Externalized parameters | Yes for the HTTPS sender Address and Content Modifier header values, when `parameters.prop` exists ([../externalized-parameters.md](../externalized-parameters.md)). Other fields: UI. |
| Anything that needs the script API or has no graphical step | Groovy Script | Yes, last resort, one step per iFlow (below) |

## Groovy Script: the last resort

Use a script only when no row above does the job, or when the task needs the script API (for example custom header properties in the message log). SAP: "We recommend using scripts only if you need to access our script APIs or in case there's no graphical flow step available" ([Guidelines for Modifying Content](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/guidelines-for-modifying-content-6a7c9a1.md)).

- Every Groovy row in a declaration explains in "Why this shape" which standard component was considered and why it does not fit.
- Keep a script to one task; a second task is a second step (UI, since the skill writes one Groovy step per iFlow) or a standard component.
- A component the skill cannot write is **not** a reason for a script. Hand it to the UI ([process.md](process.md)).
- Skill limits: one Groovy Script step per iFlow, `processData`, a script file in `src/main/resources/script/`, no Script Collection ([../components/groovy-script.md](../components/groovy-script.md)).
