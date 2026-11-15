# HTTPS sender

The HTTPS sender is the adapter on the message flow from the Sender participant to the Start event. It makes the iFlow callable over HTTPS at its Address.

## Settings

All 20 keys below were part of iFlows that were deployed and called. Keep the version values as they are.

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Adapter | (the adapter itself) | `ComponentType` | `HTTPS` |
| Adapter | (the adapter itself) | `ComponentNS` | `sap` |
| Adapter | (the adapter itself) | `ComponentSWCVName` | `external` |
| Adapter | (the adapter itself) | `ComponentSWCVId` | `1.5.3` |
| Adapter | (the adapter itself) | `componentVersion` | `1.5` |
| Adapter | (the adapter itself) | `cmdVariantUri` | `ctype::AdapterVariant/cname::sap:HTTPS/tp::HTTPS/mp::None/direction::Sender/version::1.5.3` |
| Adapter | (the adapter itself) | `TransportProtocol` | `HTTPS` |
| Adapter | (the adapter itself) | `TransportProtocolVersion` | `1.5.3` |
| Adapter | (the adapter itself) | `MessageProtocol` | `None` |
| Adapter | (the adapter itself) | `MessageProtocolVersion` | `1.5.3` |
| Adapter | (the adapter itself) | `direction` | `Sender` |
| Adapter | (the adapter itself) | `system` | `Sender` |
| Adapter | (the adapter itself) | `Name` | `HTTPS` |
| Adapter | (the adapter itself) | `Description` | empty |
| Address | a path starting with `/`, for example `/s01/content-modifier` | `urlPath` | the path |
| CSRF Protected | not selected | `xsrfProtection` | `0` |
| CSRF Protected | selected | `xsrfProtection` | `1` |
| Authorization | User Role | `senderAuthType` | `RoleBased` |
| (no UI label recorded) | `ESBMessaging.send` | `userRole` | `ESBMessaging.send` |
| Client Certificate Authorization table | none (User Role) | `clientCertificates` | empty, or one row of two empty cells: `<row><cell id='clientCertificate.subjectDN'></cell><cell id='clientCertificate.issuerDN'></cell></row>` (escaped once in the `.iflw`; both deployed) |
| (no UI label recorded) | the default | `maximumBodySize` | `40` |

## Pitfalls

- The endpoint is `<runtime host>/http<urlPath>`. The runtime host is the `-rt` host of the tenant. After the Address was changed, the new path answered and the old path returned HTTP 404 (an HTML page).
- Called before the iFlow showed as started, the endpoint returned 404 `unknown_route`. Call it after it has started.
- With `xsrfProtection` `1`, a POST without a CSRF token returned HTTP 403. Send a GET or HEAD to the same endpoint with the header `X-CSRF-Token: Fetch`; the response carries an `x-csrf-token` header and cookies. Then POST with `X-CSRF-Token: <token>` and those cookies. The token without the cookies also returned 403.
- With `xsrfProtection` `0`, a plain POST worked. Both values deployed, so ask the user which one they want; nothing is chosen for them.
- A custom request header does not reach the iFlow unless its name is in Allowed Header(s) on the integration flow, and nothing warned about it. See [router.md](router.md).
- With `RoleBased` and `ESBMessaging.send`, a call with an OAuth `client_credentials` token whose role is `ESBMessaging.send` worked.
- The Address may also be an externalized parameter written as `{{<parameter name>}}`. It deployed when the parameter was declared with a default value, and the default path answered.
- With only Start and End in the iFlow, the call returned the request body unchanged with HTTP 200.
