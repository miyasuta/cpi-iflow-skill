# Local Integration Process and Process Call

A Local Integration Process is a separate pool in the iFlow that holds a group of steps with one purpose. The main Integration Process runs it with a Process Call step and continues after it with the same message. When to use one is a design question (cpi-iflow-design, guidelines A7).

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Local Integration Process | (the process itself) | `componentVersion` | `1.1` |
| Local Integration Process | (the process itself) | `cmdVariantUri` | `ctype::FlowElementVariant/cname::LocalIntegrationProcess/version::1.1.3` |
| Local Integration Process | (the process itself) | `processType` | `directCall` |
| Local Integration Process > Processing > Transaction Handling | From Calling Process | `transactionalHandling` | `From Calling Process` |
| Local Integration Process > Processing > Timeout (in min) | the default | `transactionTimeout` | `30` |
| Local Integration Process | Name | `name` (on the process and on its participant) | the purpose, for example `prepareWrite` |
| Process Call | (the step itself) | `componentVersion` | `1.0` |
| Process Call | (the step itself) | `activityType` | `ProcessCallElement` |
| Process Call | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::NonLoopingProcess/version::1.0.4` |
| Process Call | (the step itself) | `subActivityType` | `NonLoopingProcess` |
| Process Call > Local Integration Process | the process to call | `processId` | the id of the Local Integration Process, for example `Process_2` (not its name) |

## Pitfalls

- The Local Integration Process starts with a plain Start event and ends with a plain End event. After its End, the main flow continued with the step after the Process Call.
- A Process Call placed at the start of one route of a Router (the other route skipping it), with both routes joining the next step, deployed and ran: only the route with the Process Call ran the Local Integration Process.
- A Request Reply with an HTTP receiver (Basic, Cloud Connector) inside a Local Integration Process deployed and called the receiver. The receiver participant sits outside the pools, as for the main process.
- Headers set inside the Local Integration Process (by a Content Modifier, by a Groovy Script, and the response headers of a Request Reply such as `x-csrf-token`) were still on the message in the main process after the Process Call. With HTTP Session Reuse `onExchange` on the integration flow, a CSRF token fetched inside the Local Integration Process and the `Cookie` header built there were accepted by a write sent from the main process.
- A Router inside a Local Integration Process, with one route through a Content Modifier and the default route with no step, both leading to the process's End, deployed and ran both routes.
- An Exception Subprocess inside a Local Integration Process ending with Error End (Error Start, then Error End) passed the error on: the main process's own Exception Subprocess ran, the message was `FAILED`, and an iFlow calling this one through ProcessDirect got the original error text (for example `HTTP operation failed invoking <URL> with statusCode: 404`). See [exception-subprocess.md](exception-subprocess.md).
- At log level INFO, a failed message's log lists the Process Call and the steps inside the Local Integration Process by name, in the order they ran, up to the failing one.
- Moving existing steps into a Local Integration Process means removing them from the main process and inserting them again inside it; their settings must be written again in full.
