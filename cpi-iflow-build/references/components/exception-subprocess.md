# Exception Subprocess

An Exception Subprocess catches an error raised in the main process and builds the reply instead. It holds an Error Start event, a Content Modifier that builds the reply, and an End Message event.

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Exception Subprocess | (the step itself) | `componentVersion` | `1.1` |
| Exception Subprocess | (the step itself) | `activityType` | `ErrorEventSubProcessTemplate` |
| Exception Subprocess | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::ErrorEventSubProcessTemplate/version::1.1.0` |
| Error Start | (the event itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::ErrorStartEvent` (no `version::` part) |
| Error Start | (the event itself) | `activityType` | `StartErrorEvent` |
| End Message | (the event itself) | `componentVersion` | `1.1` |
| End Message | (the event itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0` |

The two Error Start keys sit inside the event's error definition. An Error Start without them also deployed and caught the error: CPI removed them from its copy after a pull.

The Content Modifier inside takes the settings of [content-modifier.md](content-modifier.md). The values that deployed for an error reply:

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Message Header | Source Type Constant, name `CamelHttpResponseCode` | `headerTable` | a Constant row with `422` (also `400` and `503`) |
| Message Header | Source Type Constant, any other name | `headerTable` | a Constant row, for example name `X-X04-Error`, value `caught` |
| Message Body > Type | Expression | `bodyType` | `expression` |
| Message Body | the reply text | `wrapContent` | for example `X04 error: ${exception.message}` |

## Ending with Error End

An Exception Subprocess may end with Error End instead of End Message, with no step in between: Error Start, then Error End. The message then fails, and the caller gets the error.

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Error End | (the event itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::ErrorEndEvent` (no `version::` part) |
| Error End | (the event itself) | `activityType` | `EndErrorEvent` |

The two keys sit inside the event's error definition, as for Error Start.

- In an iFlow called through ProcessDirect, an Exception Subprocess ending with Error End made its message `FAILED`, and the calling iFlow's own Exception Subprocess caught the error: its `${exception.message}` held the original error, for example `HTTP operation failed invoking <URL> with statusCode: 503`.

## Pitfalls

- The Exception Subprocess sits in the main process but is not connected to the main flow. Its events, the Content Modifier and their flows are inside it: Error Start, then the Content Modifier, then End Message.
- Every deployed Exception Subprocess ended with End Message and had exactly one Content Modifier between Error Start and End Message.
- When a step in the main flow throws, the Exception Subprocess runs and the End Message sends its reply to the HTTPS sender: the Content Modifier's headers came back as response headers and its body as the response body. The main flow did not continue after the failing step.
- The header `CamelHttpResponseCode` sets the HTTP status of the reply: `400`, `422` and `503` each came back as that status. The header itself was not returned to the caller. `500` is also the default for an error, so a reply of `500` does not show that the header worked.
- With End Message, the message processing log status was `COMPLETED`, and the error information was still kept in the log.
- `${exception.message}` for a Groovy Script that threw `new Exception("X")` was `java.lang.Exception: java.lang.Exception: X@ line 4 in script1.groovy`: the class name twice before the text and the script line after it. Do not promise the user the bare message text.
- To test it, the main flow must raise an error; a Groovy Script step that threw an exception did that.
- Changing only the header rows and body of the Content Modifier inside an existing Exception Subprocess deployed and took effect.
