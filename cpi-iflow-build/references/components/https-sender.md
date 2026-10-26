# HTTPS sender adapter

The HTTPS sender adapter is the `bpmn2:messageFlow` in `bpmn2:collaboration` from the sender participant to the start event, configured by `ifl:property` elements. For its place in the file, see [../iflw-structure.md](../iflw-structure.md).

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

Names, roles, addresses and header names in the examples below show the XML shape only. They are not design choices; the design decides them ([../design/process.md](../design/process.md)).

## Supported in this skill version

Changing an existing HTTPS sender's Address (`urlPath`), CSRF protection (`xsrfProtection`), and Authorization (`senderAuthType`, with `clientCertificates`), and adding an HTTPS sender to an iFlow that has none (see "Add an HTTPS sender to an iFlow that has none" below). Adding any other adapter is not supported.

| Setting | Local edit |
|---|---|
| Address (`urlPath`) | Verified: edited locally, pulled, saved, deployed, called, and pushed ([96961e9] → [bd394aa]). |
| CSRF protection (`xsrfProtection`) `0` → `1` | Verified the same way ([ca0a3c9] → [159c7c1]). `1` → `0` locally: **unverified**. |
| Add an HTTPS sender to an empty iFlow | Verified twice with `xsrfProtection` `0`: pulled, saved, deployed, called, pushed ([6e86930] → [79f6c66]), and together with an inserted Content Modifier ([3ef66d2]). |
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

## Add an HTTPS sender to an iFlow that has none

Start from an iFlow that the user created empty in CPI and pushed (Sender, Start, End, Receiver; no `bpmn2:messageFlow`). Creating the iFlow itself is not supported. Four empty iFlows pushed by CPI had identical `.iflw` files apart from the name, with the IDs used below ([6f994f5], [9bf40a4], [1fb5209], [2f1316e]). Check that `Participant_1`, `StartEvent_2`, `BPMNShape_Participant_1` and `BPMNShape_StartEvent_2` exist before you write.

1. At the end of `bpmn2:collaboration` (after the participant `Participant_Process_1`), add this `bpmn2:messageFlow` with the 20 keys in this order ([79f6c66]). Change only `urlPath`, and `xsrfProtection` if the user asks for CSRF protection (see below):

```xml
<bpmn2:messageFlow id="MessageFlow_4" name="HTTPS" sourceRef="Participant_1" targetRef="StartEvent_2">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>ComponentType</key>
            <value>HTTPS</value>
        </ifl:property>
        <ifl:property>
            <key>Description</key>
            <value/>
        </ifl:property>
        <ifl:property>
            <key>maximumBodySize</key>
            <value>40</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentNS</key>
            <value>sap</value>
        </ifl:property>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.5</value>
        </ifl:property>
        <ifl:property>
            <key>urlPath</key>
            <value>/x02/sandbox</value>
        </ifl:property>
        <ifl:property>
            <key>Name</key>
            <value>HTTPS</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocolVersion</key>
            <value>1.5.3</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentSWCVName</key>
            <value>external</value>
        </ifl:property>
        <ifl:property>
            <key>system</key>
            <value>Sender</value>
        </ifl:property>
        <ifl:property>
            <key>xsrfProtection</key>
            <value>0</value>
        </ifl:property>
        <ifl:property>
            <key>TransportProtocol</key>
            <value>HTTPS</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::AdapterVariant/cname::sap:HTTPS/tp::HTTPS/mp::None/direction::Sender/version::1.5.3</value>
        </ifl:property>
        <ifl:property>
            <key>userRole</key>
            <value>ESBMessaging.send</value>
        </ifl:property>
        <ifl:property>
            <key>senderAuthType</key>
            <value>RoleBased</value>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocol</key>
            <value>None</value>
        </ifl:property>
        <ifl:property>
            <key>MessageProtocolVersion</key>
            <value>1.5.3</value>
        </ifl:property>
        <ifl:property>
            <key>ComponentSWCVId</key>
            <value>1.5.3</value>
        </ifl:property>
        <ifl:property>
            <key>direction</key>
            <value>Sender</value>
        </ifl:property>
        <ifl:property>
            <key>clientCertificates</key>
            <value/>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:messageFlow>
```

2. In `bpmndi:BPMNPlane`, add its edge ([79f6c66], [3ef66d2]):

```xml
<bpmndi:BPMNEdge bpmnElement="MessageFlow_4" id="BPMNEdge_MessageFlow_4" sourceElement="BPMNShape_Participant_1" targetElement="BPMNShape_StartEvent_2">
    <di:waypoint x="90.0" xsi:type="dc:Point" y="170.0"/>
    <di:waypoint x="308.0" xsi:type="dc:Point" y="158.0"/>
</bpmndi:BPMNEdge>
```

3. Do not create `parameters.prop` / `parameters.propdef`; CPI creates them on the first save ([79f6c66]).
4. Run `check_iflw.py`, commit, push. In CPI: Pull → **Edit → Save** → Deploy → call. Both verified additions were saved in the designer before deployment; deploying a never-saved iFlow without Save worked only twice so far ([c3ddf1c], [111453a], see [../workflow.md](../workflow.md)).
5. The first save of an empty iFlow rewrites parts of the file (collaboration properties, participant keys, Start/End size 36x36 → 32x32). This appears in the next Push from CPI and is expected ([79f6c66], see [../workflow.md](../workflow.md) "An iFlow that was never saved in the designer").

Results: the Address answered with HTTP 200 and, with only Start → End, returned the request body unchanged ([6e86930]). All 20 keys were unchanged after the Push from CPI ([79f6c66]).

Not verified: leaving out the `BPMNEdge`, other values than `urlPath` and `xsrfProtection` `0` in a new sender, or an older version.

### CSRF protection for a new sender

When the user connects an HTTPS sender in the CPI UI, CSRF Protected is **on** by default (`xsrfProtection` `1`, [7decca5]); in S02 the user then turned it off ([42c1aeb]). The template above comes from S01, where it is `0`. A new sender written locally with `1` is **unverified**. If the user does not say, ask whether CSRF protection should be on: with `1`, every POST needs a CSRF token and cookies (see "Settings" above).

## Versions

| Fact | Evidence |
|---|---|
| `version::1.5.3` in `cmdVariantUri`, `componentVersion` `1.5`, and `1.5.3` for `ComponentSWCVId`, `TransportProtocolVersion`, `MessageProtocolVersion` are what the UI wrote on this tenant. | [03225bf] |
| Whether older HTTPS sender versions are accepted: **unverified** (only tested for the Content Modifier). Never change these values. | — |

[03225bf]: https://github.com/miyasuta/cpi-iflow-samples/commit/03225bf
[052b9b2]: https://github.com/miyasuta/cpi-iflow-samples/commit/052b9b2
[111453a]: https://github.com/miyasuta/cpi-iflow-samples/commit/111453a
[159c7c1]: https://github.com/miyasuta/cpi-iflow-samples/commit/159c7c1
[1fb5209]: https://github.com/miyasuta/cpi-iflow-samples/commit/1fb5209
[2f1316e]: https://github.com/miyasuta/cpi-iflow-samples/commit/2f1316e
[3ef66d2]: https://github.com/miyasuta/cpi-iflow-samples/commit/3ef66d2
[40a9c8b]: https://github.com/miyasuta/cpi-iflow-samples/commit/40a9c8b
[42c1aeb]: https://github.com/miyasuta/cpi-iflow-samples/commit/42c1aeb
[6e86930]: https://github.com/miyasuta/cpi-iflow-samples/commit/6e86930
[6f994f5]: https://github.com/miyasuta/cpi-iflow-samples/commit/6f994f5
[758b608]: https://github.com/miyasuta/cpi-iflow-samples/commit/758b608
[79f6c66]: https://github.com/miyasuta/cpi-iflow-samples/commit/79f6c66
[7decca5]: https://github.com/miyasuta/cpi-iflow-samples/commit/7decca5
[96961e9]: https://github.com/miyasuta/cpi-iflow-samples/commit/96961e9
[9bf40a4]: https://github.com/miyasuta/cpi-iflow-samples/commit/9bf40a4
[a3c03ec]: https://github.com/miyasuta/cpi-iflow-samples/commit/a3c03ec
[bd394aa]: https://github.com/miyasuta/cpi-iflow-samples/commit/bd394aa
[c3ddf1c]: https://github.com/miyasuta/cpi-iflow-samples/commit/c3ddf1c
[ca0a3c9]: https://github.com/miyasuta/cpi-iflow-samples/commit/ca0a3c9
[ce88aae]: https://github.com/miyasuta/cpi-iflow-samples/commit/ce88aae
