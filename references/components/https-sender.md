# HTTPS sender adapter

The HTTPS sender adapter is the `bpmn2:messageFlow` in `bpmn2:collaboration` from the sender participant to the start event, configured by `ifl:property` elements. For its place in the file, see [../iflw-structure.md](../iflw-structure.md).

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

## Supported in this skill version

Changing an existing HTTPS sender's Address (`urlPath`), CSRF protection (`xsrfProtection`), and Authorization (`senderAuthType`, with `clientCertificates`). Adding a new adapter is not supported.

| Setting | Local edit |
|---|---|
| Address (`urlPath`) | Verified: edited locally, pulled, saved, deployed, called, and pushed ([96961e9] → [bd394aa]). |
| CSRF protection (`xsrfProtection`) `0` → `1` | Verified the same way ([ca0a3c9] → [159c7c1]). `1` → `0` locally: **unverified**. |
| Authorization (`senderAuthType`, `clientCertificates`) | **Unverified for local edits.** The values below come from changing the setting in the CPI UI and pushing. After such an edit, ask the user to check the adapter's Authorization in the designer after Pull and to report the result. |

## Keys and values

20 keys, as written by CPI when the adapter was connected and only Address and CSRF were set ([03225bf]):

| key | value |
|---|---|
| `ComponentType` | `HTTPS` |
| `ComponentNS` | `sap` |
| `ComponentSWCVName` | `external` |
| `ComponentSWCVId` | `1.5.3` |
| `componentVersion` | `1.5` |
| `cmdVariantUri` | `ctype::AdapterVariant/cname::sap:HTTPS/tp::HTTPS/mp::None/direction::Sender/version::1.5.3` |
| `TransportProtocol` | `HTTPS` |
| `TransportProtocolVersion` | `1.5.3` |
| `MessageProtocol` | `None` |
| `MessageProtocolVersion` | `1.5.3` |
| `direction` | `Sender` |
| `system` | `Sender` |
| `Name` | `HTTPS` |
| `Description` | (empty) |
| `urlPath` | `/s01/content-modifier` (Address) |
| `xsrfProtection` | `0` (CSRF Protected off) |
| `senderAuthType` | `RoleBased` |
| `userRole` | `ESBMessaging.send` |
| `clientCertificates` | (empty) |
| `maximumBodySize` | `40` |

`clientCertificates` can also be a single row of empty cells: `&lt;row&gt;&lt;cell id='clientCertificate.subjectDN'&gt;&lt;/cell&gt;&lt;cell id='clientCertificate.issuerDN'&gt;&lt;/cell&gt;&lt;/row&gt;`. CPI wrote this when Authorization was switched back from Client Certificate to User Role in the UI, and the iFlow pulled, deployed and ran with it ([a3c03ec]). Leave either form as it is.

Change only the keys listed in the next section. Keep all other keys and values, including every version value, as they are.

## Settings

Each row: one setting changed in the UI and pushed; the diff contained only that key (apart from [noise](../workflow.md#diff-noise)).

| UI setting | key | Values | Evidence |
|---|---|---|---|
| Address | `urlPath` | A path such as `/x01/sandbox`. The endpoint is `<runtime host>/http<urlPath>`. After a change, the new path answers and the old one returns HTTP 404. | [758b608], [052b9b2], [96961e9] |
| CSRF Protected | `xsrfProtection` | `0` = off, `1` = on. No other key is added or removed. | [ce88aae] |
| Authorization | `senderAuthType` | `RoleBased` (User Role) or `ClientCertificate` (Client Certificate). These were the two choices in the UI. | [40a9c8b] |
| Client certificate conditions | `clientCertificates` | A table (see [../escaping.md](../escaping.md)). One row: `<row><cell id='clientCertificate.subjectDN'>...</cell><cell id='clientCertificate.issuerDN'>...</cell></row>`, escaped once in the `.iflw`. | [40a9c8b] |

Example from [40a9c8b] (dummy values entered by hand):

```xml
<ifl:property>
    <key>senderAuthType</key>
    <value>ClientCertificate</value>
</ifl:property>
...
<ifl:property>
    <key>clientCertificates</key>
    <value>&lt;row&gt;&lt;cell id='clientCertificate.subjectDN'&gt;DummySubject&lt;/cell&gt;&lt;cell id='clientCertificate.issuerDN'&gt;DummyIssuer&lt;/cell&gt;&lt;/row&gt;</value>
</ifl:property>
```

| Fact | Evidence |
|---|---|
| With `ClientCertificate`, the UI does not save while `clientCertificates` is empty (at least one row is required). An empty value written locally: **unverified**. Always ask the user for the Subject DN and Issuer DN. | [40a9c8b] |
| With `ClientCertificate`, `userRole` (`ESBMessaging.send`) stays in the file. Keep it. | [40a9c8b] |
| `RoleBased` with `ESBMessaging.send` can be called with an OAuth `client_credentials` token. | [052b9b2] |
| With `xsrfProtection` `1`, a POST without a CSRF token returns HTTP 403. To call the iFlow, first send a GET or HEAD to the same endpoint with header `X-CSRF-Token: Fetch`; the response has an `x-csrf-token` header and `Set-Cookie` headers. Then POST with `X-CSRF-Token: <token>` **and those cookies**. The token without the cookies also returns 403. Which of the cookies are required is **unverified**; send all of them. | [ca0a3c9] |
| Runtime behavior with `ClientCertificate`: **unverified** (not deployed). | — |
| The value format when certificates are chosen with the UI's Select button: **unverified**. | — |

## Versions

| Fact | Evidence |
|---|---|
| `version::1.5.3` in `cmdVariantUri`, `componentVersion` `1.5`, and `1.5.3` for `ComponentSWCVId`, `TransportProtocolVersion`, `MessageProtocolVersion` are what the UI wrote on this tenant. | [03225bf] |
| Whether older HTTPS sender versions are accepted: **unverified** (only tested for the Content Modifier). Never change these values. | — |

[03225bf]: https://github.com/miyasuta/cpi-iflow-samples/commit/03225bf
[052b9b2]: https://github.com/miyasuta/cpi-iflow-samples/commit/052b9b2
[159c7c1]: https://github.com/miyasuta/cpi-iflow-samples/commit/159c7c1
[40a9c8b]: https://github.com/miyasuta/cpi-iflow-samples/commit/40a9c8b
[758b608]: https://github.com/miyasuta/cpi-iflow-samples/commit/758b608
[96961e9]: https://github.com/miyasuta/cpi-iflow-samples/commit/96961e9
[a3c03ec]: https://github.com/miyasuta/cpi-iflow-samples/commit/a3c03ec
[bd394aa]: https://github.com/miyasuta/cpi-iflow-samples/commit/bd394aa
[ca0a3c9]: https://github.com/miyasuta/cpi-iflow-samples/commit/ca0a3c9
[ce88aae]: https://github.com/miyasuta/cpi-iflow-samples/commit/ce88aae
