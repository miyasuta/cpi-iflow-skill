# HTTP receiver

The HTTP receiver is the adapter on the message flow from a Request Reply step to a receiver participant. It calls an HTTP endpoint and returns the response to the iFlow. See [request-reply.md](request-reply.md) for the step in front of it.

## Settings

All 48 keys below were part of iFlows that were deployed and called with Method GET and Authentication None, and the rows for Method POST, PUT and DELETE, a Query with several pairs, a custom Request Header, another Timeout, OAuth2 Client Credentials and Basic were deployed and called too. Keep the version values as they are. The designer's version `1.22.1` (`ComponentSWCVId`, `TransportProtocolVersion`, `MessageProtocolVersion` `1.22.1`, `cmdVariantUri` ending in `version::1.22.1`, `componentVersion` `1.22`) also deployed and ran.

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
| Address | the full URL without the query string, for example `https://services.odata.org/V4/Northwind/Northwind.svc/Products(2)` | `httpAddressWithoutQuery` | the URL as it is (parentheses are not escaped) |
| Query | `$select=ProductID,ProductName` | `httpAddressQuery` | the query without `?`, as it is (no URL encoding, no escaping) |
| Query | several pairs, for example `a=1&b=2` | `httpAddressQuery` | the pairs joined with `&`, as they are (`&` escaped once as `&amp;` in the `.iflw`) |
| Query | empty | `httpAddressQuery` | empty |
| Query | from an exchange property | `httpAddressQuery` | `${property.<name>}`, for example `${property.odataQuery}`; with the property empty, the call also worked (a GET of one entity) |
| Address | a parameter followed by exchange properties | `httpAddressWithoutQuery` | for example `{{A4H_BaseUrl}}${property.odataServicePath}${property.odataResourcePath}` |
| Method | GET | `httpMethod` | `GET` |
| Method | POST | `httpMethod` | `POST` |
| Method | PUT | `httpMethod` | `PUT` |
| Method | Delete | `httpMethod` | `DELETE` (upper case; the UI shows `Delete`) |
| Method | Dynamic | `httpMethod` | `DYNAMIC` |
| Source Expression (Method Dynamic) | the method from an exchange property | `methodSourceExpression` | `${property.<name>}`, for example `${property.odataMethod}`; the property held `GET`, `POST`, `PATCH` or `DELETE` |
| Authentication | None | `authenticationMethod` | `None` |
| Authentication | OAuth2 Client Credentials | `authenticationMethod` | `OAuth2 Client Credentials` (the display name, with spaces) |
| Authentication | Basic | `authenticationMethod` | `Basic` |
| Credential Name | none (Authentication None) | `credentialName` | empty |
| Credential Name | OAuth2 Client Credentials | `credentialName` | the Name of an OAuth2 Client Credentials artifact in Security Material, for example `s05-oauth-client` |
| Credential Name | Basic | `credentialName` | the Name of a User Credentials artifact in Security Material, for example `ZCpiDevEchoBasic` |
| Send Body | the default (for GET and DELETE; hidden for POST) | `httpShouldSendBody` | `false` (it stayed `false` with PUT and DELETE too) |
| Send Body | selected (Method Dynamic) | `httpShouldSendBody` | `true` |
| Timeout in ms | the default | `httpRequestTimeout` | `60000` |
| Timeout in ms | another value | `httpRequestTimeout` | the milliseconds, for example `30000` |
| Request Headers | the default | `allowedRequestHeaders` | `traceparent` |
| Request Headers | a custom header besides the default | `allowedRequestHeaders` | names separated by `\|`, for example `traceparent\|X-Fwd` |
| Request Headers | only custom headers | `allowedRequestHeaders` | names separated by `\|`, for example `x-csrf-token\|If-Match\|Content-Type\|Accept\|sap-client\|Cookie` |
| Response Headers | the default | `allowedResponseHeaders` | `*` |
| Response Headers | only some headers | `allowedResponseHeaders` | names separated by `\|`, for example `x-csrf-token\|ETag\|set-cookie` |
| Throw Exception on Failure | selected | `throwExceptionOnFailure` | `true` |
| Throw Exception on Failure | not selected | `throwExceptionOnFailure` | `false` |
| Proxy Type | Internet (default) | `proxyType` | `default` |
| Proxy Type | On-Premise (Cloud Connector) | `proxyType` | `sapcc` |
| Location ID (Proxy Type On-Premise) | empty, or a parameter whose value is empty | `locationID` | empty, or `{{<name>}}` |
| Integration Flow > Runtime Configuration > HTTP Session Reuse | None | `httpSessionHandling` (on the integration flow) | `None` |
| Integration Flow > Runtime Configuration > HTTP Session Reuse | On Exchange | `httpSessionHandling` (on the integration flow) | `onExchange` |
| Retry tab (field label not recorded) | not selected (defaults) | `retryOnException` | `false` |
| Retry tab (field label not recorded) | not selected (defaults) | `retryOnConnectionFailure` | `false` |
| Retry tab (field label not recorded) | not selected (defaults) | `retryIteration` | `1` |
| Retry tab (field label not recorded) | not selected (defaults) | `retryInterval` | `5` |
| (no UI label recorded) | the default | `streaming` | `false` |
| (no UI label recorded) | the default | `enableMPLAttachments` | `true` |
| (no UI label recorded) | the default | `pooledConnectionIdleTimeout` | `300000` |
| (no UI label recorded) | left empty | `apiName`, `apiArtifactType`, `apiDisplayName`, `apiprovider_location_id`, `providerAuth`, `providerName`, `providerRelativeUrl`, `providerUrl`, `methodSourceExpression` (not Method Dynamic), `privateKeyAlias`, `internetProxyType`, `proxyHost`, `proxyPort`, `locationID` (Proxy Type Internet), `httpErrorResponseCodes`, `retryOnExceptionsTable` | empty |

## Pitfalls

- The value of `authenticationMethod` for OAuth2 Client Credentials is the display name with spaces. The value `OAuth2ClientCredentials` (no spaces) was accepted when pushed, nothing warned about it, and the deployment then failed with a generation error that named no cause. With `OAuth2 Client Credentials` the deployment succeeded.
- The Credential Name must be the Name of an artifact in Security Material (Monitor > Integrations and APIs > Security Material), already deployed: OAuth2 Client Credentials for OAuth2 Client Credentials, User Credentials for Basic. Ask the user for the name; never write a client ID, a user, a secret, a password or a token anywhere.
- A Credential Name with no deployed artifact is not checked at deploy: the deployment succeeded, and the call failed with HTTP 500 even with Throw Exception on Failure not selected. The message log said `No credentials for <name> available. Deploy suitable credentials or adapt credential name in integration flow.`
- With Basic, SAP's design guideline check reports `USE_SECURE_AUTHENTICATION_METHODS` (High). The deployment was not blocked.
- With Method GET the receiver got no body: it read an empty string, not `null`. With Method POST it got the current message body, and `httpShouldSendBody` stayed `false`.
- A URL with parentheses, such as `Products(4)`, is written as it is. A Query with `$`, `=` and `,` is written as it is and reached the receiver.
- A Query with `&` is not URL-encoded: the receiver read `a=1&b=2` as it was written.
- The receiver gets the adapter's Method, not the method the iFlow was called with: a POST to the iFlow reached the receiver as PUT or DELETE.
- With the default Request Headers (`traceparent`), a header the iFlow received was not passed to the receiver. Listed in Request Headers (and in Allowed Header(s) of the calling iFlow), it was passed on.
- To call another iFlow on the same tenant, the Address is `<runtime host>/http<Address of the target HTTPS sender>`. The runtime host is the `-rt` host, the one a client uses to call that iFlow. The target had User Role `ESBMessaging.send` and CSRF protection off, and the Credential was an OAuth2 Client Credentials artifact made from a service key whose role is `ESBMessaging.send`. That call succeeded. With Basic, a User Credentials artifact whose user and password are the client ID and secret of such a service key worked too.
- With the default Proxy Type, the tenant reached `https://services.odata.org`.
- With Proxy Type On-Premise, the Address is the virtual host and port of the Cloud Connector mapping with `http://`, for example `http://abaptrial:443`, even when the Cloud Connector reaches the backend over HTTPS. An empty Location ID worked for a Cloud Connector with no Location ID.
- When the Cloud Connector was disconnected, the call returned HTTP 503 after about 30 seconds with the body `Cannot open tunnel with tunnelId: ...`. That is not an error in the iFlow.
- With Method Dynamic, the receiver got the method held in the property named in `methodSourceExpression`: `GET`, `POST`, `PATCH` and `DELETE` all reached the backend as such.
- With Throw Exception on Failure not selected, a backend error status (`403`, `404`) did not raise an error: the iFlow went on, `CamelHttpResponseCode` held the status, and the body was the backend's error body.
- Response Headers limited to some names: only those names came back into the message (for example `x-csrf-token` and `ETag`). A header not listed (`set-cookie`) was not in the message even though the backend sent it.
- Writing to a CSRF-protected SAP backend (OData on ABAP) through the HTTP receiver worked with these three together (without them the write returned HTTP 403 `CSRF token is invalid`): HTTP Session Reuse `onExchange` on the integration flow; a GET with header `x-csrf-token: Fetch` whose Response Headers include `x-csrf-token` and `set-cookie`; and a Groovy Script after it that turns the `set-cookie` values into one `Cookie` header (`name=value` pairs joined with `; `), with `Cookie` and `x-csrf-token` in the Request Headers of the write. With `onExchange` alone, the write sent the token but no cookie. Whether the script works without `onExchange` was not tried. Copying `${header.set-cookie}` into `Cookie` with a Content Modifier, with HTTP Session Reuse `None`, did not work either.
- The token fetch and the write may be two different HTTP receiver channels in the same iFlow; with the cookie passed as above, the token from one was accepted by the other.
- What the caller gets back: the response body is the receiver's body, unchanged, and the request body is not returned. The receiver's response headers come back in lower case, and CPI adds `sap_*` headers. When the receiver is another iFlow, the headers that iFlow set come back too.
