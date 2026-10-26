# Choosing components

Pick the standard component for each purpose first; a Groovy Script is the last resort. The chosen component goes into the "Component" column of the flow table ([process.md](process.md)).

Main SAP sources: [Guidelines for Modifying Content](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/guidelines-for-modifying-content-6a7c9a1.md) ("When to Use What?"), [Communication between Integration Flows](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/communication-between-integration-flows-ab5db7b.md), [Apply a Balanced Encapsulation of the Integration Logics](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/apply-a-balanced-encapsulation-of-the-integration-logics-e010db3.md), [Handle Errors Gracefully](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/handle-errors-gracefully-42c95f7.md).

## Purpose → component

| Purpose | Standard component |
|---|---|
| Receive an HTTP call | HTTPS sender |
| Start on a schedule | Timer start event |
| Set headers, properties, or a fixed or templated body | Content Modifier |
| Branch on a header value | Router |
| Call an HTTP/REST service and use the reply | Request Reply + HTTP receiver |
| Read or write an OData service | Request Reply + OData receiver |
| Change the format only (XML ↔ JSON, CSV → XML) | Converter |
| Map to a different structure (XML or JSON) | Message Mapping (or XSLT for XML → XML) |
| Keep only part of an XML body | Filter |
| Merge in data from another call | Content Enricher |
| Process the items of a message one by one | Splitter (and Gather) |
| Encode, compress, encrypt | Encoder, Decoder, Encryptor |
| Handle errors | Exception Subprocess |
| Split one iFlow into parts | Local Integration Process + Process Call |
| Call another iFlow on the same tenant, synchronously | ProcessDirect (receiver in the caller, sender in the callee). Not the HTTP receiver ([guidelines.md](guidelines.md), A5). |
| Call another iFlow asynchronously, retry later | JMS queue |
| Values that change per landscape | Externalized parameters |
| Anything that needs the script API or has no graphical step | Groovy Script, last resort (below) |

## Groovy Script: the last resort

Use a script only when no row above does the job, or when the task needs the script API (for example custom header properties in the message log). SAP: "We recommend using scripts only if you need to access our script APIs or in case there's no graphical flow step available" ([Guidelines for Modifying Content](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/guidelines-for-modifying-content-6a7c9a1.md)).

- Every Groovy row in a declaration explains in "Why this shape" which standard component was considered and why it does not fit.
- Keep a script to one task; a second task is a second step or a standard component.
- How easy a part is to build (for example, that a script is quicker to write than a mapping) is **not** a reason for a script.
