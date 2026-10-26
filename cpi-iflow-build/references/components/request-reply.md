# Request Reply step

A Request Reply step calls an external receiver synchronously and continues with the response. In the `.iflw` it is a **`bpmn2:serviceTask`** in the process (not a `callActivity` like Content Modifier or Groovy Script). The receiver and its adapter are a `bpmn2:messageFlow` from this step to a receiver participant; for the HTTP receiver, see [http-receiver.md](http-receiver.md). For the place of each element in the file, see [../iflw-structure.md](../iflw-structure.md).

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

Names, roles, addresses and header names in the examples below show the XML shape only. They are not design choices; the approved design declaration or the user decides them ([../from-declaration.md](../from-declaration.md)).

## Supported in this skill version

| Task | Local edit |
|---|---|
| Insert a Request Reply step between two existing nodes and connect an HTTP receiver (GET, Authentication None) to the existing receiver participant | Verified once: written locally into an empty iFlow together with an HTTPS sender, pulled, deployed without Save, called ([c3ddf1c]). |
| Call the receiver with POST or OAuth2 Client Credentials | Change the connected receiver as in [http-receiver.md](http-receiver.md) "Authentication" and "Method" (verified on an existing receiver; writing a new step with these values in one edit is **unverified**, so tell the user). |

Request Reply with any adapter other than the HTTP receiver is not supported (no sample).

## Template

The step has exactly three keys and no settings of its own ([f1a9ee9], placed in the UI; unchanged after the HTTP receiver was connected in [cc4ce46]). Copy it as it is:

```xml
<bpmn2:serviceTask id="ServiceTask_5" name="Request Reply 1">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.0</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>ExternalCall</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::ExternalCall/version::1.0.4</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>SequenceFlow_3</bpmn2:incoming>
    <bpmn2:outgoing>SequenceFlow_6</bpmn2:outgoing>
</bpmn2:serviceTask>
```

| Fact | Evidence |
|---|---|
| The verified local insertion used the ID `ServiceTask_5` and the name `Request Reply 1` exactly as the UI wrote them. Other IDs and names are **unverified** for this step (they work for other steps; see [../iflw-structure.md](../iflw-structure.md#ids)). If `ServiceTask_5` is already used in the file, use another unique ID such as `ServiceTask_Local1` (and `BPMNShape_ServiceTask_Local1`), and tell the user that this is unverified for a Request Reply step. | [c3ddf1c] |
| The shape is 100x60 (`BPMNShape_ServiceTask_5`). The UI put it at x=412, y=132 in an empty iFlow (between Start x=292 and End x=703). | [f1a9ee9] |
| The UI saved a Request Reply step that had no receiver yet. Whether the designer shows an error for it and whether it deploys is **unverified**; always connect the receiver in the same edit. | [f1a9ee9] |
| After the step, the message body is the receiver's response body; the original body is not returned. | Calls of [cc4ce46], [c3ddf1c], [1b378b8] |

Versions: `version::1.0.4` / `1.0` is the pair the UI wrote on this tenant. Do not change it.

## Insert a Request Reply step and connect an HTTP receiver

Verified in [c3ddf1c] on an empty iFlow (Start → End) after adding an HTTPS sender. Every key and value came from [cc4ce46].

1. Insert the `serviceTask` above into the sequenceFlow between the two nodes, exactly like any step: see "Inserting a step between two nodes" in [../iflw-structure.md](../iflw-structure.md). Place its shape where it overlaps nothing (do not move existing shapes).
2. Use the existing receiver participant (`Participant_2`, `name="Receiver"`, `ifl:type="EndpointRecevier"`, which every empty iFlow has). Do not add a new participant. Read its `name`; you need it for `system`.
3. Add the HTTP receiver `messageFlow` at the end of `bpmn2:collaboration` (after the last participant or message flow): `sourceRef` = the Request Reply step, `targetRef` = the receiver participant. Copy the 48 keys from [http-receiver.md](http-receiver.md) and change only `httpAddressWithoutQuery` (Address), `httpAddressQuery` (Query) if needed, and `system` (the receiver participant's `name`).
4. Add its `BPMNEdge` (`BPMNEdge_<message flow id>`, `sourceElement="BPMNShape_ServiceTask_5"`, `targetElement` = the receiver participant's shape) with waypoints from the step to the participant. The verified edge went from the top center of the step to the left edge of the receiver: `462,132` → `900,140` ([c3ddf1c]).
5. Run `check_iflw.py`, commit, push, and follow the round trip in [../workflow.md](../workflow.md). The call returns the receiver's response.

Example of the edge ([c3ddf1c]):

```xml
<bpmndi:BPMNEdge bpmnElement="MessageFlow_8" id="BPMNEdge_MessageFlow_8" sourceElement="BPMNShape_ServiceTask_5" targetElement="BPMNShape_Participant_2">
    <di:waypoint x="462.0" xsi:type="dc:Point" y="132.0"/>
    <di:waypoint x="900.0" xsi:type="dc:Point" y="140.0"/>
</bpmndi:BPMNEdge>
```

How the designer draws this edge (it passes above the End event) is **unverified**; nobody looked at the diagram after Pull. As with every insertion, CPI put the re-targeted existing edge (`BPMNEdge_SequenceFlow_3`) back to its old waypoints after Pull ([../iflw-structure.md](../iflw-structure.md)); the run was not affected.

In the UI sample [cc4ce46], the user placed a second receiver (`Participant_7`, `Receiver1`, below the pool) and connected it instead of `Participant_2`, which was left unconnected. That deployed and ran too. This was the user's own action, not something CPI does; prefer the existing participant.

[1b378b8]: https://github.com/miyasuta/cpi-iflow-samples/commit/1b378b8
[c3ddf1c]: https://github.com/miyasuta/cpi-iflow-samples/commit/c3ddf1c
[cc4ce46]: https://github.com/miyasuta/cpi-iflow-samples/commit/cc4ce46
[f1a9ee9]: https://github.com/miyasuta/cpi-iflow-samples/commit/f1a9ee9
