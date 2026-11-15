# Router

A Router sends the message down one of several routes, chosen by a condition on a header. One route is the default route and is taken when no condition matches.

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Router | (the step itself) | `componentVersion` | `1.2` |
| Router | (the step itself) | `activityType` | `ExclusiveGateway` |
| Router | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.2.0` |
| Processing > Throw Exception | not selected | `throwException` | `false` |
| Route | Expression Type: Non-XML | `expressionType` | `NonXML` |
| Route | Condition Expression, header equals a value | condition text | `${header.<name>} = '<value>'` (for example `${header.X-Route} = 'a'`; a header name with hyphens is written as it is) |
| Route | Default Route (no condition) | `expressionType` | `XML` or `NonXML` (both deployed); no condition text |
| Route | Default Route | `default` | the id of the default route's flow, set on the Router itself (it must be one of the Router's outgoing flows) |
| Route | Name | `name` | free text, for example `Route 1` |
| Route | optional (deployed with and without) | `componentVersion` | `1.0` |
| Route | optional (deployed with and without) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0` |
| Integration Flow > Runtime Configuration > Allowed Header(s) | the header name used in the condition | `allowedHeaderList` | `<header name>` (on the integration flow); for example `X-Route` |
| End Message (one per route) | (the step itself) | `componentVersion` | `1.1` |
| End Message (one per route) | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0` |

## Pitfalls

- Always write a default route. Every deployed Router had one, and it carried no condition.
- The condition text is written as it is: `$`, `{` and `'` need no escaping, and strings are in single quotes.
- Use the dot form `${header.<name>}` for the header. The bracket form `${header[<name>]}` was rejected as an invalid condition when the iFlow was pushed.
- A header used in a condition must be listed in Allowed Header(s) on the integration flow. Without it, a custom request header never reached the Router: the call always took the default route, and nothing warned about it.
- When no condition matched (no header, or another value), the default route was taken.
- A route whose condition was written with only `expressionType` and the condition text deployed and ran. The two designer keys on a route (`componentVersion`, `cmdVariantUri`) are not needed.
- Each route may end in its own End Message. One route going to a shared End, with another route having its own End, also deployed and ran.
- With an HTTPS sender and a Content Modifier body on each route, the caller got HTTP 200 with the body of the route taken. The routed header, being in Allowed Header(s), also came back in the response in lower case (for example `x-route: a`).
