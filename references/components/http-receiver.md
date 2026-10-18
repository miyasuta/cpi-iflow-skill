# HTTP receiver adapter

The HTTP receiver adapter is the `bpmn2:messageFlow` in `bpmn2:collaboration` from a Request Reply step ([request-reply.md](request-reply.md)) to a receiver participant, configured by `ifl:property` elements. For its place in the file, see [../iflw-structure.md](../iflw-structure.md).

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

## Supported in this skill version

Method **GET or POST**, Authentication **None or OAuth2 Client Credentials**.

| Task | Local edit |
|---|---|
| Connect an HTTP receiver (GET, None) from a new Request Reply step to the existing receiver participant | Verified once: pulled, deployed without Save, called; the response body was the receiver's, byte for byte ([c3ddf1c]). Steps in [request-reply.md](request-reply.md). |
| Change the Address (`httpAddressWithoutQuery`) | Verified: pulled, deployed without Save, called ([1b378b8], [ba66a4e]). |
| Set the Query (`httpAddressQuery`) | Verified with `$select=ProductID,ProductName`, written as it is ([1b378b8]). Cleared to `<value/>` in [ba66a4e]. |
| Set Authentication to OAuth2 Client Credentials with a Credential Name | Verified once on an existing receiver: pulled, deployed without Save, called ([ba66a4e]). See "Authentication". |
| Change the Method from GET to POST | Verified once: pulled, deployed without Save, called; the message body reached the receiver ([5b2d746]). See "Method". |

Not supported (no sample): any other Method (PUT, DELETE, Dynamic, …), Send Body `true`, any other Authentication (Basic, OAuth2 SAML Bearer Assertion, client certificate, …), a dynamic Credential Name (`${header.…}`), externalizing Authentication or Credential Name, proxy, timeout, request header and retry settings, and the HTTP receiver behind any step other than Request Reply. For these, follow the "unsupported request" rule in [../../SKILL.md](../../SKILL.md). `check_iflw.py` warns about an `httpMethod` or `authenticationMethod` value that no sample has.

## Keys and values

48 keys, in the order CPI wrote them when the adapter was connected in the UI with Address, Method GET and Authentication None, everything else left at its default ([cc4ce46]). The message flow was `id="MessageFlow_8"`, `name="HTTP"`, `sourceRef="ServiceTask_5"`, `targetRef="Participant_7"`.

```xml
<bpmn2:messageFlow id="MessageFlow_8" name="HTTP" sourceRef="ServiceTask_5" targetRef="Participant_2">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>apiName</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>Description</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>methodSourceExpression</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>apiArtifactType</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>providerAuth</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>retryOnExceptionsTable</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>ComponentNS</key>
            <value>sap</value>
        </ifl:property>
        <ifl:property>
            <key>privateKeyAlias</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>httpMethod</key>
            <value>GET</value>
        </ifl:property>
        <ifl:property>
            <key>apiprovider_location_id</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>allowedResponseHeaders</key>
            <value>*</value>
        </ifl:property>
        <ifl:property>
            <key>Name</key>
            <value>HTTP</value>
        </ifl:property>
        <ifl:property>
            <key>internetProxyType</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocolVersion</key>
            <value>1.22.0</value>
        </ifl:property>
        <ifl:property>
            <key>retryOnException</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>proxyPort</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>ComponentSWCVName</key>
            <value>external</value>
        </ifl:property>
        <ifl:property>
            <key>streaming</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>enableMPLAttachments</key>
            <value>true</value>
        </ifl:property>
        <ifl:property>
            <key>pooledConnectionIdleTimeout</key>
            <value>300000</value>
        </ifl:property>
        <ifl:property>
            <key>httpAddressQuery</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>httpRequestTimeout</key>
            <value>60000</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentSWCVId</key>
            <value>1.22.0</value>
        </ifl:property>
        <ifl:property>
            <key>providerName</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>allowedRequestHeaders</key>
            <value>traceparent</value>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocol</key>
            <value>None</value>
        </ifl:property>
        <ifl:property>
            <key>direction</key>
            <value>Receiver</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentType</key>
            <value>HTTP</value>
        </ifl:property>
        <ifl:property>
            <key>httpShouldSendBody</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>throwExceptionOnFailure</key>
            <value>true</value>
        </ifl:property>
        <ifl:property>
            <key>proxyType</key>
            <value>default</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.22</value>
        </ifl:property>
        <ifl:property>
            <key>retryIteration</key>
            <value>1</value>
        </ifl:property>
        <ifl:property>
            <key>proxyHost</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>providerUrl</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>retryOnConnectionFailure</key>
            <value>false</value>
        </ifl:property>
        <ifl:property>
            <key>system</key>
            <value>Receiver</value>
        </ifl:property>
        <ifl:property>
            <key>authenticationMethod</key>
            <value>None</value>
        </ifl:property>
        <ifl:property>
            <key>locationID</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>retryInterval</key>
            <value>5</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocol</key>
            <value>HTTP</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::AdapterVariant/cname::sap:HTTP/tp::HTTP/mp::None/direction::Receiver/version::1.22.0</value>
        </ifl:property>
        <ifl:property>
            <key>httpErrorResponseCodes</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>credentialName</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>apiDisplayName</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocolVersion</key>
            <value>1.22.0</value>
        </ifl:property>
        <ifl:property>
            <key>providerRelativeUrl</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>httpAddressWithoutQuery</key>
            <value>https://services.odata.org/V4/Northwind/Northwind.svc/Products(2)</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>
```

This is the template as written locally in [c3ddf1c]: identical to [cc4ce46] except `targetRef` (`Participant_2`, the existing receiver), `system` (`Receiver`, that participant's `name`; the UI wrote `Receiver1`, the name of the participant it was connected to) and the Address. Copy it and change only:

| key | What to write |
|---|---|
| `httpAddressWithoutQuery` | The Address: the full URL without the query string, written as it is (`(1)` was not escaped in [cc4ce46]). Escape `&` as `&amp;` (XML). |
| `httpAddressQuery` | The Query, without `?`. Empty if none. `$select=ProductID,ProductName` was written as it is (no URL encoding, no escaping) and reached the receiver ([1b378b8]). A query containing `&` (written `&amp;` in XML) is **unverified**; whether CPI URL-encodes the query is **unverified**. |
| `system` | The `name` of the receiver participant in `targetRef`. A different value is **unverified**. |
| `authenticationMethod`, `credentialName` | Only for OAuth2 Client Credentials; see "Authentication". |
| `httpMethod` | Only for POST; see "Method". |

Keep every other key and value, including every version value (`componentVersion` `1.22`, `version::1.22.0` and the `1.22.0` values), as they are.

What some keys mean (read from the values and the defaults in the [SAP Help page of the HTTP receiver adapter](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/2da452effb764b3bb28f8e0a2f5bd480.html); Address, Query, Method, Authentication and Credential Name were changed one at a time, see "Authentication" and "Method"): `httpMethod` Method, `authenticationMethod` Authentication, `credentialName` Credential Name, `httpShouldSendBody` Send Body, `httpRequestTimeout` Timeout in ms, `allowedRequestHeaders` Request Headers (default `traceparent`), `allowedResponseHeaders` Response Headers (default `*`), `throwExceptionOnFailure` Throw Exception on Failure, `proxyType` Proxy Type (`default` for the UI's default, Internet). Apart from the values in "Authentication" and "Method", do not change them; their other values are not in any sample.

## Authentication

The UI wrote OAuth2 Client Credentials as exactly two values in the 48-key message flow; no other key changed, not even `privateKeyAlias` or `cmdVariantUri` ([0f6e144]):

| key | None (template above) | OAuth2 Client Credentials |
|---|---|---|
| `authenticationMethod` | `None` | `OAuth2 Client Credentials` (the display name, with spaces; not `OAuth2ClientCredentials`) |
| `credentialName` | `<value/>` | The **Name** of an OAuth2 Client Credentials artifact in Security Material, written as it is (for example `s05-oauth-client`) |

The same two values written locally on an existing receiver were kept by Pull and the call worked ([ba66a4e]). The skill never creates the credential: ask the user for the name of the OAuth2 Client Credentials artifact that is already deployed in **Monitor → Integrations and APIs → Security Material**. Never write a client ID, secret or token anywhere. Which settings of that artifact are needed (Client Authentication, `grant_type` in the Token Service URL, Scope) is **unverified**; the one that worked was created from a service key of the receiver tenant ([SAP Help: Deploying an OAuth2 Client Credentials Artifact](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/801b106885b14d2788223956ce9786e5.html)). What happens when the name does not exist in Security Material (failed deployment or failed call) is **unverified**.

### Calling an iFlow on the same tenant

Verified with an HTTPS sender that has Authorization **User Role** `ESBMessaging.send` ([0f6e144]):

- Address: `<runtime host>/http<Address of the target HTTPS sender>`, for example `https://<tenant>.it-cpitrial05-rt.cfapps.us10-001.hana.ondemand.com/http/s02/groovy-script`. The runtime host is the `url` in the `oauth` section of a service key of a Process Integration Runtime instance with plan `integration-flow` (the host with `-rt`; not the host of the `api` plan). It is the same URL a client uses to call that iFlow.
- Credential: an OAuth2 Client Credentials artifact made from the `clientid`, `clientsecret` and `tokenurl` of a service key of an `integration-flow` instance whose role matches the target sender's User Role (`ESBMessaging.send`) ([SAP docs: OAuth with Client Credentials Grant for Integration Flow Processing](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/40-RemoteSystems/oauth-with-client-credentials-grant-for-integration-flow-processing-6c052ce.md)). The user creates both.
- If the target has CSRF protection on, the call needs a CSRF token; only targets with CSRF protection off were called (**unverified** otherwise).

## Method

Changing the Method to POST in the UI changed only `httpMethod` (`GET` → `POST`, [5461d27]). Write only that line:

| Method | `httpMethod` | `httpShouldSendBody` | What the receiver gets |
|---|---|---|---|
| GET | `GET` | `false` | No body: the receiver read an empty string, not `null` ([ba66a4e]) |
| POST | `POST` | `false` (left as it is; the UI hides Send Body for POST) | The current message body ([5461d27], [5b2d746]) |

`methodSourceExpression` stays empty. Request headers other than `traceparent` (the default of `allowedRequestHeaders`), including `Content-Type` and custom headers, probably do not reach the receiver; **unverified**.

## What the caller gets back

Seen in the calls to Northwind ([cc4ce46], [c3ddf1c], [1b378b8]) and to another iFlow ([5461d27], [ba66a4e], [5b2d746]) through an HTTPS sender with Response Headers `*`:

- The response body is the receiver's body, byte for byte. The request body is not returned.
- The receiver's response headers come back to the caller, in lower case: for example `content-type`, `odata-version`, `etag`, `expires`, `vary`, `access-control-*`. The value of `content-type` was lower-cased too (`IEEE754Compatible=false` became `ieee754compatible=false`; the reason is **unverified**).
- The receiver's `Content-Length` and `Cache-Control` did not come back (the response was chunked), and `server` was `SAP`.
- CPI adds `sap_messageprocessinglogid` and other `sap_*` headers.
- When the receiver is another iFlow, its own headers come back too (for example a header its script set), and `x-correlationid` appears twice.

A query string on the call to the iFlow probably reaches the receiver too (`CamelHttpQuery`, per SAP Help); **unverified**, so call the iFlow without one.

## Outbound connection

The trial tenant reached `https://services.odata.org` with the default Proxy Type, and the server certificate (root CA DigiCert Global Root G2) was trusted ([cc4ce46]). For a receiver whose certificate chain ends at another root CA, the tenant keystore may need that CA ([SAP Help: Setting Up Outbound HTTP Connections](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/92dd2a6fdb6045f98d23c828d1567fef.html)); this tenant's keystore was not checked. If a call fails with a certificate or connection error, ask the user to check the message processing log.

[0f6e144]: https://github.com/miyasuta/cpi-iflow-samples/commit/0f6e144
[1b378b8]: https://github.com/miyasuta/cpi-iflow-samples/commit/1b378b8
[5461d27]: https://github.com/miyasuta/cpi-iflow-samples/commit/5461d27
[5b2d746]: https://github.com/miyasuta/cpi-iflow-samples/commit/5b2d746
[ba66a4e]: https://github.com/miyasuta/cpi-iflow-samples/commit/ba66a4e
[c3ddf1c]: https://github.com/miyasuta/cpi-iflow-samples/commit/c3ddf1c
[cc4ce46]: https://github.com/miyasuta/cpi-iflow-samples/commit/cc4ce46
