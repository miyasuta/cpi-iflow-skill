# Router

A Router sends the message down one of several routes, chosen by a condition on a header, an exchange property or the XML body. One route is the default route and is taken when no condition matches.

## Settings

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Router | (the step itself) | `componentVersion` | `1.2` |
| Router | (the step itself) | `activityType` | `ExclusiveGateway` |
| Router | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.2.0` |
| Processing > Throw Exception | not selected | `throwException` | `false` |
| Route | Expression Type: Non-XML | `expressionType` | `NonXML` |
| Route | Condition Expression, header equals a value | condition text | `${header.<name>} = '<value>'` (for example `${header.X-Route} = 'a'`; a header name with hyphens is written as it is) |
| Route | Condition Expression, not equal | condition text | `${header.<name>} != '<value>'`, for example `${header.X-V1} != 'c'` |
| Route | Condition Expression, value in a list | condition text | `${header.<name>} in '<v1>,<v2>'` (one quoted string, comma-separated), for example `${header.X-V1} in 'a,z'` |
| Route | Condition Expression, regular expression | condition text | `${header.<name>} regex '<regex>'`, for example `${header.X-V1} regex 'b.*'` |
| Route | Condition Expression, two conditions | condition text | `<condition> and <condition>`, for example `${header.X-V1} = 'c' and ${header.X-A} = '2'` |
| Route | Condition Expression, exchange property | condition text | `${property.<name>} = '<value>'`, for example `${property.p1} = 'x'` |
| Route | Condition Expression, header present | condition text | `${header.<name>} != null`, for example `${header.TravelID} != null` |
| Route | Condition Expression, HTTP method of the HTTPS sender call | condition text | `${header.CamelHttpMethod} = 'POST'` |
| Route | Expression Type: XML | `expressionType` | `XML` |
| Route | Condition Expression, XPath on the body | condition text | an XPath comparison, for example `/r/t = 'a'` |
| Route | Default Route (no condition) | `expressionType` | `XML` or `NonXML` (both deployed); no condition text |
| Route | Default Route | `default` | the id of the default route's flow, set on the Router itself (it must be one of the Router's outgoing flows) |
| Route | Name | `name` | free text, for example `Route 1` |
| Route | optional (deployed with and without) | `componentVersion` | `1.0` |
| Route | optional (deployed with and without) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0` |
| Integration Flow > Runtime Configuration > Allowed Header(s) | the header name used in the condition | `allowedHeaderList` | `<header name>` (on the integration flow); for example `X-Route` |
| Integration Flow > Runtime Configuration > Allowed Header(s) | several names, and a regular expression | `allowedHeaderList` | names separated by `\|` with no spaces; an entry may be a regular expression. For example `X-V1\|X-A\|X-B\|X-P\|X-V1-.*`, where `X-V1-.*` let `X-V1-foo` through |
| End Message (one per route) | (the step itself) | `componentVersion` | `1.1` |
| End Message (one per route) | (the step itself) | `cmdVariantUri` | `ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0` |

## Pitfalls

- Always write a default route. Every deployed Router had one, and it carried no condition.
- The condition text is written as it is: `$`, `{` and `'` need no escaping, and strings are in single quotes.
- Use the dot form `${header.<name>}` for the header. The bracket form `${header[<name>]}` was rejected as an invalid condition when the iFlow was pushed.
- A header used in a condition must be listed in Allowed Header(s) on the integration flow. Without it, a custom request header never reached the Router: the call always took the default route, and nothing warned about it.
- When no `=` condition matched (no header, or another value), the default route was taken.
- A route whose condition was written with only `expressionType` and the condition text deployed and ran. The two designer keys on a route (`componentVersion`, `cmdVariantUri`) are not needed.
- Each route may end in its own End Message. One route going to a shared End, with another route having its own End, also deployed and ran.
- With an HTTPS sender and a Content Modifier body on each route, the caller got HTTP 200 with the body of the route taken. The routed header, being in Allowed Header(s), also came back in the response in lower case (for example `x-route: a`).
- Conditions were checked in the order the routes were written, and the first one that matched won. With only `X-A: 1`, the `${header.X-A} = '1'` route was taken, even though the later `${header.X-V1} != 'c'` route also matched.
- A missing header satisfies `!=`. With no `X-V1` header, `${header.X-V1} != 'c'` was true, so that route was taken instead of the default.
- An XML (XPath) route fails on a body that is not XML. The call returned HTTP 500, the message log said `Content is not allowed in prolog`, and the default route was not taken.
- `${header.<name>} != null` was true when the header was sent and false when it was not, so the default route was taken without it.
- `CamelHttpMethod` and `CamelHttpQuery`, set by the HTTPS sender, were read in conditions and expressions without being in Allowed Header(s).
- Routes may lead into one shared step instead of an End: three routes, each with its own Content Modifier, joined at one Request Reply, and a route with no step at all joined another route's step. This deployed and every route ran.
- A Router may come after another step, for example a Content Modifier whose exchange property the condition reads. Nine routes all leading to one shared End deployed and ran. A Router's default route may also lead into a second Router.
