# HTTP receiver adapter

The HTTP receiver adapter is the `bpmn2:messageFlow` in `bpmn2:collaboration` from a Request Reply step ([request-reply.md](request-reply.md)) to a receiver participant, configured by `ifl:property` elements. For its place in the file, see [../iflw-structure.md](../iflw-structure.md).

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

## Supported in this skill version

Only **Method GET with Authentication None**.

| Task | Local edit |
|---|---|
| Connect an HTTP receiver (GET, None) from a new Request Reply step to the existing receiver participant | Verified once: pulled, deployed without Save, called; the response body was the receiver's, byte for byte ([c3ddf1c]). Steps in [request-reply.md](request-reply.md). |
| Change the Address (`httpAddressWithoutQuery`) | Verified: pulled, deployed without Save, called ([1b378b8]). |
| Set the Query (`httpAddressQuery`) | Verified with `$select=ProductID,ProductName`, written as it is ([1b378b8]). |

Not supported (no sample): any other Method, Send Body, any Authentication other than None (Basic, OAuth2, client certificate, …), a Credential Name, proxy, timeout, header and retry settings, and the HTTP receiver behind any step other than Request Reply. For these, follow the "unsupported request" rule in [../../SKILL.md](../../SKILL.md).

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

Keep every other key and value, including every version value (`componentVersion` `1.22`, `version::1.22.0` and the `1.22.0` values), as they are.

What some keys mean (read from the values and the defaults in the [SAP Help page of the HTTP receiver adapter](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/2da452effb764b3bb28f8e0a2f5bd480.html); only Address and Query were changed one at a time): `httpMethod` Method, `authenticationMethod` Authentication, `credentialName` Credential Name, `httpShouldSendBody` Send Body, `httpRequestTimeout` Timeout in ms, `allowedRequestHeaders` Request Headers (default `traceparent`), `allowedResponseHeaders` Response Headers (default `*`), `throwExceptionOnFailure` Throw Exception on Failure, `proxyType` Proxy Type (`default` for the UI's default, Internet). Do not change them; their other values are not in any sample.

## What the caller gets back

Seen in all three calls ([cc4ce46], [c3ddf1c], [1b378b8]) through an HTTPS sender with Response Headers `*`:

- The response body is the receiver's body, byte for byte. The request body is not returned.
- The receiver's response headers come back to the caller, in lower case: for example `content-type`, `odata-version`, `etag`, `expires`, `vary`, `access-control-*`. The value of `content-type` was lower-cased too (`IEEE754Compatible=false` became `ieee754compatible=false`; the reason is **unverified**).
- The receiver's `Content-Length` and `Cache-Control` did not come back (the response was chunked), and `server` was `SAP`.
- CPI adds `sap_messageprocessinglogid` and other `sap_*` headers.

A query string on the call to the iFlow probably reaches the receiver too (`CamelHttpQuery`, per SAP Help); **unverified**, so call the iFlow without one.

## Outbound connection

The trial tenant reached `https://services.odata.org` with the default Proxy Type, and the server certificate (root CA DigiCert Global Root G2) was trusted ([cc4ce46]). For a receiver whose certificate chain ends at another root CA, the tenant keystore may need that CA ([SAP Help: Setting Up Outbound HTTP Connections](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/92dd2a6fdb6045f98d23c828d1567fef.html)); this tenant's keystore was not checked. If a call fails with a certificate or connection error, ask the user to check the message processing log.

[1b378b8]: https://github.com/miyasuta/cpi-iflow-samples/commit/1b378b8
[c3ddf1c]: https://github.com/miyasuta/cpi-iflow-samples/commit/c3ddf1c
[cc4ce46]: https://github.com/miyasuta/cpi-iflow-samples/commit/cc4ce46
