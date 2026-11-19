# Request Reply

A Request Reply step calls an external receiver synchronously and continues with its response. The receiver and its adapter are set separately; for the HTTP receiver see [http-receiver.md](http-receiver.md).

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Call > External Call | Request Reply (the step itself) | `componentVersion` | `1.0` |
| Call > External Call | Request Reply (the step itself) | `activityType` | `ExternalCall` |
| Call > External Call | Request Reply (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::ExternalCall/version::1.0.4` |

The step has these 3 keys and no settings of its own.

## Pitfalls

- In the iFlow file the step is a service task, not a call activity like Content Modifier and Groovy Script.
- Every deployed Request Reply had a receiver adapter connected to it. Write the step and its receiver together; the receiver is a message flow from the step to a receiver participant.
- The receiver participant may be the one every new iFlow already has, or a new one. Both deployed.
- After the step, the message body is the receiver's response body; the body the step received is not returned.
- Headers of the receiver's response also stayed on the message and came back to the caller, for example `x-powered-by`.
- A Request Reply with an HTTP receiver (GET, no authentication) deployed and returned the receiver's response when written into an iFlow with an HTTPS sender, with the step placed between Start and End or after a Groovy Script step.
- Only the HTTP receiver has been deployed with this step.
- A Request Reply inside a Local Integration Process also called its HTTP receiver, and the response headers it let through stayed on the message in the main process. See [local-integration-process.md](local-integration-process.md).
- The step's id and name need not be the ones the designer gives: a step written with its own id and name deployed, was called, and the designer showed the name given.
