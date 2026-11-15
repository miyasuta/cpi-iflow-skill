# HTTP receiver

The HTTP receiver is the adapter on the message flow from a Request Reply step to a receiver participant. It calls an HTTP endpoint and returns the response to the iFlow. See [request-reply.md](request-reply.md) for the step in front of it.

## Settings

All 48 keys below were part of iFlows that were deployed and called with Method GET and Authentication None, and the rows for Method POST and OAuth2 Client Credentials were deployed and called too. Keep the version values as they are.

| UI field | UI choice | Key | Value |
|---|---|---|---|
| Adapter | (the adapter itself) | `ComponentType` | `HTTP` |
| Adapter | (the adapter itself) | `ComponentNS` | `sap` |
| Adapter | (the adapter itself) | `ComponentSWCVName` | `external` |
| Adapter | (the adapter itself) | `ComponentSWCVId` | `1.22.0` |
| Adapter | (the adapter itself) | `componentVersion` | `1.22` |
| Adapter | (the adapter itself) | `cmdVariantUri` | `ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None/direction::Receiver/version::1.22.0` |
| Adapter | (the adapter itself) | `TransportProtocol` | `HTTP` |
| Adapter | (the adapter itself) | `TransportProtocolVersion` | `1.22.0` |
| Adapter | (the adapter itself) | `MessageProtocol` | `None` |
| Adapter | (the adapter itself) | `MessageProtocolVersion` | `1.22.0` |
| Adapter | (the adapter itself) | `direction` | `Receiver` |
| Adapter | (the adapter itself) | `Name` | `HTTP` |
| Adapter | (the adapter itself) | `Description` | empty |
| Adapter | the receiver participant the flow points to | `system` | the `name` of that receiver participant, for example `Receiver` or `Northwind` |
| Connection > Address | the full URL without the query string, for example `https://services.odata.org/V4/Northwind/Northwind.svc/Products(2)` | `httpAddressWithoutQuery` | the URL as it is (parentheses are not escaped) |
| Connection > Query | `$select=ProductID,ProductName` | `httpAddressQuery` | the query without `?`, as it is (no URL encoding, no escaping) |
| Connection > Query | empty | `httpAddressQuery` | empty |
| Connection > Method | GET | `httpMethod` | `GET` |
| Connection > Method | POST | `httpMethod` | `POST` |
| Connection > Authentication | None | `authenticationMethod` | `None` |
| Connection > Authentication | OAuth2 Client Credentials | `authenticationMethod` | `OAuth2 Client Credentials` (the display name, with spaces) |
| Connection > Credential Name | none (Authentication None) | `credentialName` | empty |
| Connection > Credential Name | OAuth2 Client Credentials | `credentialName` | the Name of an OAuth2 Client Credentials artifact in Security Material, for example `s05-oauth-client` |
| Connection > Send Body | the default (for GET; hidden for POST) | `httpShouldSendBody` | `false` |
| Connection > Timeout (ms) | the default | `httpRequestTimeout` | `60000` |
| Connection > Request Headers | the default | `allowedRequestHeaders` | `traceparent` |
| Connection > Response Headers | the default | `allowedResponseHeaders` | `*` |
| Connection > Throw Exception on Failure | selected | `throwExceptionOnFailure` | `true` |
| Connection > Proxy Type | Internet (default) | `proxyType` | `default` |
| Connection > Retry | not selected (defaults) | `retryOnException` | `false` |
| Connection > Retry | not selected (defaults) | `retryOnConnectionFailure` | `false` |
| Connection > Retry | not selected (defaults) | `retryIteration` | `1` |
| Connection > Retry | not selected (defaults) | `retryInterval` | `5` |
| Adapter | the defaults | `streaming` | `false` |
| Adapter | the defaults | `enableMPLAttachments` | `true` |
| Adapter | the defaults | `pooledConnectionIdleTimeout` | `300000` |
| Adapter | the defaults, left empty | `apiName`, `apiArtifactType`, `apiDisplayName`, `apiprovider_location_id`, `providerAuth`, `providerName`, `providerRelativeUrl`, `providerUrl`, `methodSourceExpression`, `privateKeyAlias`, `internetProxyType`, `proxyHost`, `proxyPort`, `locationID`, `httpErrorResponseCodes`, `retryOnExceptionsTable` | empty |

## Pitfalls

- The value of `authenticationMethod` for OAuth2 Client Credentials is the display name with spaces. The value `OAuth2ClientCredentials` (no spaces) was accepted when pushed, nothing warned about it, and the deployment then failed with a generation error that named no cause. With `OAuth2 Client Credentials` the deployment succeeded.
- The Credential Name must be the Name of an OAuth2 Client Credentials artifact in Security Material. Ask the user for the name; never write a client ID, a secret or a token anywhere.
- With Method GET the receiver got no body: it read an empty string, not `null`. With Method POST it got the current message body, and `httpShouldSendBody` stayed `false`.
- A URL with parentheses, such as `Products(4)`, is written as it is. A Query with `$`, `=` and `,` is written as it is and reached the receiver.
- To call another iFlow on the same tenant, the Address is `<runtime host>/http<Address of the target HTTPS sender>`. The runtime host is the `-rt` host, the one a client uses to call that iFlow. The target had User Role `ESBMessaging.send` and CSRF protection off, and the Credential was an OAuth2 Client Credentials artifact made from a service key whose role is `ESBMessaging.send`. That call succeeded.
- With the default Proxy Type, the tenant reached `https://services.odata.org`.
- What the caller gets back: the response body is the receiver's body, unchanged, and the request body is not returned. The receiver's response headers come back in lower case, and CPI adds `sap_*` headers. When the receiver is another iFlow, the headers that iFlow set come back too.
