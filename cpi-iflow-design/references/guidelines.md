# Design guidelines

What a declared design ([process.md](process.md)) must respect. The list is a first selection, not complete: it covers anti-patterns that are easy to fall into when an AI writes iFlows, and the rules that the tenant's Design Guidelines flagged on this project's samples. SAP's full guidelines start at [Guidelines to Design Enterprise-Grade Integration Flows](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/guidelines-to-design-enterprise-grade-integration-flows-a8cd981.md).

Three groups, by when they apply:

- **A. Decided in the design.** Checked by reviewing the declaration.
- **B. Applied while writing.** The skill follows them by default; some can be checked mechanically.
- **C. Rules for the skill itself.**

"Tenant rule" names a rule of the tenant's **Design Guidelines** (Monitor or the OData API `ExecuteIntegrationDesigntimeArtifactsGuidelines`). Run them on a deployed iFlow to check B items; they are a help, not a pass/fail gate. Several items below have no tenant rule at all (default step names, Groovy overuse, calling the same tenant over HTTP, removing namespaces, too many externalized parameters).

## A. Decided in the design

### A1. Too much or too little scripting
- Use a standard step for every task one exists for (mapping, conversion, splitting, encoding, routing). A script is for what needs the script API or has no graphical step. Too little scripting is also a smell: chains of steps that fight to do what one short script does clearly.
- SAP: [General Scripting Guidelines](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/general-scripting-guidelines-fcbf0f2.md) ("Use standard integration flow steps wherever possible"), [Guidelines for Modifying Content](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/guidelines-for-modifying-content-6a7c9a1.md) ("When to Use What?")
- Skill: one Groovy Script step per iFlow ([../components/groovy-script.md](../components/groovy-script.md)); see [components.md](components.md) for the standard alternatives.
- Check: declaration review. Every Groovy row says in "Why this shape" why no standard step does it.

### A2. One Groovy Script for everything
- Do not put a whole flow (mapping, calls, routing, error handling) into one script. The flow becomes invisible in the designer and in monitoring.
- SAP: [General Scripting Guidelines](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/general-scripting-guidelines-fcbf0f2.md), [Use Scripting Appropriately](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/use-scripting-appropriately-d4dc13c.md)
- Skill: as A1.
- Check: declaration review.

### A3. Reinventing what the platform provides
- Do not hand-write what a step, an adapter or the script API already does: parsing and building XML or JSON for a mapping, Base64 or GZip encoding, HTTP calls from a script, putting credentials into headers by script, open-source classes instead of the script API.
- SAP: [General Scripting Guidelines](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/general-scripting-guidelines-fcbf0f2.md) ("Don't access credentials to write them into http headers. Instead, use standard channels with User Credential Artifacts"; "Direct usage of Open Source classes isn't supported")
- Skill: n/a (a design choice).
- Check: declaration review. Tenant rules "Use Only Supported External Libraries" and "Avoid Accessing Secure Parameter" cover parts of it (judgment conditions not checked by this project).

### A4. Removing XML namespaces without a reason
- Keep namespaces. Strip them only when a named receiver requires it, and say so in "Why this shape".
- SAP: no SAP documentation page found yet; the item comes from a Devtoberfest 2026 talk on CPI anti-patterns.
- Skill: n/a.
- Check: declaration review.

### A5. Calling an iFlow on the same tenant over HTTP
- Between iFlows on the same tenant use ProcessDirect (synchronous) or JMS queues (asynchronous), not HTTP through the public internet.
- SAP: [Communication between Integration Flows](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/communication-between-integration-flows-ab5db7b.md) ("Use the ProcessDirect adapter for synchronous integration flow-to-integration flow communication")
- Skill: cannot write ProcessDirect (UI). The skill *can* call an iFlow on the same tenant with the HTTP receiver and OAuth2 ([../components/http-receiver.md](../components/http-receiver.md)); do not choose that in a design. It exists for testing and for calls across tenants.
- Check: declaration review. Each connection between iFlows has an Interface section ([process.md](process.md)).

### A6. No Exception Subprocess
- Every Integration Process (and Local Integration Process) gets an Exception Subprocess. End it with End Message to reply with a custom error, or with Error End when the run must show Failed (no caller waiting for a reply).
- SAP: [Handle Errors Gracefully](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/handle-errors-gracefully-42c95f7.md)
- Skill: Error Start → one Content Modifier → End Message ([../components/exception-subprocess.md](../components/exception-subprocess.md)). Error End, Escalation End or other inner steps: UI.
- Check: declaration review; tenant rules "Handle Exceptions", "Handle Exceptions in Local Integration Process".

### A7. How the processing is divided
- Group related logic: a Local Integration Process inside one iFlow, or a separate iFlow called through ProcessDirect when the part is reused or must be deployed on its own. Do not nest more than 8 routes in one process.
- SAP: [Apply a Balanced Encapsulation of the Integration Logics](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/apply-a-balanced-encapsulation-of-the-integration-logics-e010db3.md)
- Skill: neither Local Integration Process nor ProcessDirect is in Scope (UI). A design may span several iFlows; the skill builds one per session ([process.md](process.md)).
- Check: declaration review; tenant rule "Use Only Allowed Number of Pools and Flow Steps" (judgment condition not checked by this project).

## B. Applied while writing

### B1. Default names
- Give every step a name that says what it does; never keep `Content Modifier 1`. SAP's naming conventions suggest a camelCase description for steps (`setContentType`), a pattern for the iFlow ID (`<BusinessUnit|Global>_<BusinessObject>_[<Sender>_to_<Receiver>]`), for channels (`<Protocol>_<Direction>_<OperationDefinition>`) and for participants (`<IntegrationType>_<Application>`).
- SAP: [Naming Conventions](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/naming-conventions-7c00e9b.md)
- Skill: step names (the `name` attribute) for the steps it writes; verified for Content Modifier and Groovy Script steps, **unverified** for other step types. Renaming channels and participants is **unverified** (the receiver participant's name is also copied into the HTTP receiver's `system` key); leave them and propose names to set in the UI.
- Check: declaration review (the flow table names). `check_iflw.py` does not check names yet; no tenant rule.

### B2. Too many or too few externalized parameters
- Externalize what changes between landscapes (addresses, credential names, schedules). Keep the interface and the logic fixed (entity names, header names, mappings).
- SAP: [Externalize Volatile Configurations](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/externalize-volatile-configurations-300277d.md)
- Skill: the HTTPS sender Address and Content Modifier header values, only when `parameters.prop` already exists ([../externalized-parameters.md](../externalized-parameters.md)). Other fields: UI.
- Check: declaration review (section 3); tenant rules "Externalize Volatile Configurations for Sender Adapters", "Externalize Volatile Configurations for Receiver Adapters". `check_iflw.py` warns about unused parameters.

### B3. `ESBMessaging.send` everywhere
- Use a dedicated user role for each inbound HTTPS sender (naming pattern `ESBMessaging.send_<InterfaceDescription>_RTCustomRole`), created by the tenant administrator in the User Roles monitor.
- SAP: [Managing User Roles](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/managing-user-roles-4e86f0d.md), [Naming Conventions](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/naming-conventions-7c00e9b.md) ("Custom Roles")
- Skill: only `ESBMessaging.send` is in the samples ([../components/https-sender.md](../components/https-sender.md)). The declaration hands the custom role to the UI.
- Check: tenant rule "Avoid Using a Generic User Role for Sender-Side Authorization".

### B4. MPL attachments without a switch
- Do not write payloads into message processing log attachments by default; tenant storage is limited. If a script logs, make it switchable (log level or an externalized parameter).
- SAP: [Create MPL Attachments in Scripts](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/create-mpl-attachments-in-scripts-17dba92.md), [General Scripting Guidelines](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/general-scripting-guidelines-fcbf0f2.md) ("use a switcher")
- Skill: scripts it writes create no attachments unless the design asks for them, and then behind a switch. Adapter keys such as `enableMPLAttachments` keep their sample values.
- Check: tenant rule "Avoid Creating MPL Attachments".

### B5. CSRF protection
- Turn on CSRF protection for an HTTPS sender unless its callers cannot fetch a token; say which in the declaration.
- SAP: [HTTPS Sender Adapter](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/https-sender-adapter-0ae4a78.md) ("CSRF Protected")
- Skill: `xsrfProtection` `0` → `1` on an existing sender is verified; a new sender is verified with `0` ([../components/https-sender.md](../components/https-sender.md)). A new sender written with `1` is **unverified**: either write it with `1` and tell the user, or add it with `0` and switch to `1` in a second round trip (both steps verified).
- Check: tenant rule "Use CSRF Protection".

### B6. Identifiers for searching message logs
- Set `SAP_Sender`, `SAP_Receiver`, `SAP_MessageType` and `SAP_ApplicationID` (a business ID, for example the order number) early in the flow.
- SAP: [Use Custom Header Properties to Search for Message Processing Logs](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/use-custom-header-properties-to-search-for-message-processing-logs-d4b5839.md)
- Skill: Content Modifier header rows with Type `constant` or `expression` ([../components/content-modifier.md](../components/content-modifier.md)). Values read from the payload by XPath: UI.
- Check: tenant rule "Define Identifiers To Search In Message Processing Logs" (it looks for all four headers).

## C. Rules for the skill itself

### C1. Rely only on documented, supported behavior
- In scripts, use the script API and native Groovy, not internal or open-source classes. In the `.iflw`, write only what the references show ([SKILL.md](../../SKILL.md) Rules); mark everything else unverified and let the user check it in CPI.
- SAP: [General Scripting Guidelines](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/general-scripting-guidelines-fcbf0f2.md) ("SAP does only furnish a guarantee for the officially supported script APIs")
- Check: the skill's own Rules; for scripts, tenant rules "Use Only Supported External Libraries" and the "Ensure Upgrade Readiness" rules (returned as message keys such as `!UNSUPPORTED_INTERNAL_CLASSES_USAGE!`).
