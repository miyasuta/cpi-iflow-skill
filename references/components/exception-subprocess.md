# Exception Subprocess

An Exception Subprocess catches an error raised in the Integration Process and builds the reply instead. In the `.iflw` it is a **`bpmn2:subProcess`** inside the process. It is not connected to the main flow (no `incoming` / `outgoing`). Its own events, steps and sequence flows are child elements of the `subProcess`, not of the process. For the place of each element in the file, see [../iflw-structure.md](../iflw-structure.md); for the Content Modifier inside it, see [content-modifier.md](content-modifier.md).

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

## Supported in this skill version

| Task | Local edit |
|---|---|
| Add an Exception Subprocess with Error Start → Content Modifier → End Message to an iFlow that has none | Verified once: written locally into an empty iFlow (with an HTTPS sender and a Groovy Script step that throws), pulled, deployed without Save, called ([111453a]). |
| Change the Content Modifier inside an existing Exception Subprocess (header rows, body) | Verified: pulled, deployed without Save, called ([d66cf44]). |

Not supported (no sample): ending the subprocess with Error End or Escalation End, any step inside it other than one Content Modifier, more than one Exception Subprocess, and an Exception Subprocess in a Local Integration Process. SAP's rules for what may be placed inside are in [Define Exception Subprocess](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/690e0784c90342669a5f1461ae65b95f.html?locale=en-US&state=PRODUCTION&version=Cloud).

## Template

The `subProcess` has three keys. The Error Start event has no `extensionElements` of its own; its two keys sit inside `bpmn2:errorEventDefinition`, and its `cmdVariantUri` has **no `version::` part**. The End Message event inside has the same keys as the main End event. All keys and versions come from the UI samples [3052ccb] (placed in the UI) and [f34d292] (Content Modifier added in the UI); the hand-written IDs below are the ones verified in [111453a].

Put the `subProcess` in `bpmn2:process` right after the process's `extensionElements` (where the UI put it, and where the verified local edit put it):

```xml
<bpmn2:subProcess id="SubProcess_Local1" name="Exception Subprocess 1">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.1</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>ErrorEventSubProcessTemplate</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::ErrorEventSubProcessTemplate/version::1.1.0</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:endEvent id="EndEvent_Local1" name="End 1">
        <bpmn2:extensionElements>
            <ifl:property>
                <key>componentVersion</key>
                <value>1.1</value>
            </ifl:property>
            <ifl:property>
                <key>cmdVariantUri</key>
                <value>ctype::FlowstepVariant/cname::MessageEndEvent/version::1.1.0</value>
            </ifl:property>
        </bpmn2:extensionElements>
        <bpmn2:incoming>SequenceFlow_Local3</bpmn2:incoming>
        <bpmn2:messageEventDefinition/>
    </bpmn2:endEvent>
    <bpmn2:callActivity id="CallActivity_Local2" name="Build Error Response">
        <!-- the 7 keys of a new Content Modifier: see content-modifier.md and the example below -->
        <bpmn2:incoming>SequenceFlow_Local2</bpmn2:incoming>
        <bpmn2:outgoing>SequenceFlow_Local3</bpmn2:outgoing>
    </bpmn2:callActivity>
    <bpmn2:startEvent id="StartEvent_Local1" name="Error Start 1">
        <bpmn2:outgoing>SequenceFlow_Local2</bpmn2:outgoing>
        <bpmn2:errorEventDefinition>
            <bpmn2:extensionElements>
                <ifl:property>
                    <key>cmdVariantUri</key>
                    <value>ctype::FlowstepVariant/cname::ErrorStartEvent</value>
                </ifl:property>
                <ifl:property>
                    <key>activityType</key>
                    <value>StartErrorEvent</value>
                </ifl:property>
            </bpmn2:extensionElements>
        </bpmn2:errorEventDefinition>
    </bpmn2:startEvent>
    <bpmn2:sequenceFlow id="SequenceFlow_Local3" sourceRef="CallActivity_Local2" targetRef="EndEvent_Local1"/>
    <bpmn2:sequenceFlow id="SequenceFlow_Local2" sourceRef="StartEvent_Local1" targetRef="CallActivity_Local2"/>
</bpmn2:subProcess>
```

Replace the comment with the Content Modifier's 7 keys (the order of the keys does not matter). The verified error response ([111453a]) had these values:

| Key | Value |
|---|---|
| `headerTable` | Two rows, both Type `constant`: `CamelHttpResponseCode` = `422`, `X-X04-Error` = `caught` (escaped as in [content-modifier.md](content-modifier.md)) |
| `propertyTable` | empty |
| `bodyType` | `expression` |
| `wrapContent` | `X04 error: ${exception.message}` |

| Fact | Evidence |
|---|---|
| Hand-written IDs (`SubProcess_Local1`, `StartEvent_Local1`, `EndEvent_Local1`, `CallActivity_Local2`, `SequenceFlow_Local2`, `SequenceFlow_Local3`) were kept by Pull. The UI numbers them in sequence (`SubProcess_5`, `StartEvent_6`, `EndEvent_7`, `SequenceFlow_8`, …). Use IDs that are not used anywhere else in the file. | [111453a], [3052ccb] |
| A new Exception Subprocess in the UI already contains Error Start, End Message and one sequence flow between them. Adding a Content Modifier in the UI re-targeted that flow to the step and added a new flow to the End, exactly like an insertion in the main flow. | [3052ccb], [f34d292] |
| After Pull, CPI's copy of the iFlow had an **empty** `<bpmn2:extensionElements/>` inside the Error Start's `errorEventDefinition`; the two keys were gone (seen twice). The iFlow still deployed and the subprocess still caught the error. Why CPI drops them, whether a Save in the designer puts them back, and whether they may be left out locally are **unverified**. Write them as in the template (that is what the UI saves). | [111453a], [d66cf44] |

## Layout

Write a `BPMNShape` for the `subProcess` and for each node inside it, and a `BPMNEdge` for each flow inside it. Shapes inside the subprocess use the same absolute coordinates as everything else in the diagram. Do not move existing shapes ([../iflw-structure.md](../iflw-structure.md)).

| Fact | Evidence |
|---|---|
| In the UI, the subprocess shape was 400x140, placed below the main row; the pool grew to 464x330 and every existing shape got new coordinates matching the designer's auto layout. Whether the user ran auto layout or CPI rearranged the diagram when the subprocess was placed is unknown. | [3052ccb] |
| The verified local layout kept every existing shape and put a 400x80 subprocess below the main row, inside the existing pool (540x220 at y=60; main row y=128–188): subprocess x=290 y=196, Error Start 32x32 at x=311 y=220, Content Modifier 100x60 at x=431 y=206, End 32x32 at x=598 y=220, edges from shape edge to shape edge at y=236. Pull kept these coordinates. How the designer draws a subprocess this low is **unverified** (nobody looked). | [111453a] |
| If the free space in the pool is smaller than this, do not move or resize existing shapes; place the subprocess where it overlaps nothing and ask the user to run the designer's auto layout after Pull. | [../iflw-structure.md](../iflw-structure.md) |

The verified shapes and edges ([111453a]):

```xml
<bpmndi:BPMNShape bpmnElement="SubProcess_Local1" id="BPMNShape_SubProcess_Local1">
    <dc:Bounds height="80.0" width="400.0" x="290.0" y="196.0"/>
</bpmndi:BPMNShape>
<bpmndi:BPMNShape bpmnElement="StartEvent_Local1" id="BPMNShape_StartEvent_Local1">
    <dc:Bounds height="32.0" width="32.0" x="311.0" y="220.0"/>
</bpmndi:BPMNShape>
<bpmndi:BPMNShape bpmnElement="CallActivity_Local2" id="BPMNShape_CallActivity_Local2">
    <dc:Bounds height="60.0" width="100.0" x="431.0" y="206.0"/>
</bpmndi:BPMNShape>
<bpmndi:BPMNShape bpmnElement="EndEvent_Local1" id="BPMNShape_EndEvent_Local1">
    <dc:Bounds height="32.0" width="32.0" x="598.0" y="220.0"/>
</bpmndi:BPMNShape>
<bpmndi:BPMNEdge bpmnElement="SequenceFlow_Local2" id="BPMNEdge_SequenceFlow_Local2" sourceElement="BPMNShape_StartEvent_Local1" targetElement="BPMNShape_CallActivity_Local2">
    <di:waypoint x="343.0" xsi:type="dc:Point" y="236.0"/>
    <di:waypoint x="431.0" xsi:type="dc:Point" y="236.0"/>
</bpmndi:BPMNEdge>
<bpmndi:BPMNEdge bpmnElement="SequenceFlow_Local3" id="BPMNEdge_SequenceFlow_Local3" sourceElement="BPMNShape_CallActivity_Local2" targetElement="BPMNShape_EndEvent_Local1">
    <di:waypoint x="531.0" xsi:type="dc:Point" y="236.0"/>
    <di:waypoint x="598.0" xsi:type="dc:Point" y="236.0"/>
</bpmndi:BPMNEdge>
```

`check_iflw.py` checks the nodes, flows, shapes and edges inside a `subProcess` like those of the main flow, reports a flow that leaves its subprocess, and warns about overlapping shapes inside it (shapes inside the subprocess's own shape are not an overlap).

## Add an Exception Subprocess

1. Check that the iFlow has no `bpmn2:subProcess` yet.
2. Add the template to `bpmn2:process` after its `extensionElements`, with unused IDs, and fill in the Content Modifier's 7 keys.
3. Add the shapes and edges (see "Layout"). Existing elements need no change: the subprocess is not connected to them.
4. Run `check_iflw.py`, commit, push, and follow the round trip in [../workflow.md](../workflow.md). To test it, the main flow must raise an error; in the verified sample a Groovy Script step threw one (`throw new Exception("X04 test failure")`).

To change the reply later, edit only the Content Modifier inside, as in [content-modifier.md](content-modifier.md) ([d66cf44]).

## Runtime behavior (HTTPS sender)

| Fact | Evidence |
|---|---|
| When a step in the main flow throws, the Exception Subprocess runs and its End Message sends the reply to the HTTPS sender: the Content Modifier's headers come back as response headers and its body as the response body. The main flow does not continue after the failing step. | Calls of [f34d292], [111453a], [d66cf44] |
| A header `CamelHttpResponseCode` (Type `constant`) sets the HTTP status of the reply: `422` gave 422 and `503` gave 503. The header itself is not returned to the caller. (`500` was also returned when set, but that is the default for errors, so it proves nothing.) | [111453a], [d66cf44], [f34d292] |
| With End Message, the message processing log status is `COMPLETED`, not `FAILED`; the error information is still kept in the log. SAP's documentation is inconsistent on this point. | Message processing logs of the three calls |
| `${exception.message}` for a Groovy Script that runs `throw new Exception("X")` was `java.lang.Exception: java.lang.Exception: X@ line 4 in script1.groovy` (class name twice before the text, script line after it). Do not promise the user only the bare message text. For errors from other steps the format is **unverified**. | Calls of [f34d292], [111453a], [d66cf44] |
| What the sender gets without an Exception Subprocess, or with Error End instead of End Message, is **unverified** here (SAP documents that Error End hands the error to the default handler and the log ends `FAILED`). | [Define Exception Subprocess](https://help.sap.com/docs/CLOUD_INTEGRATION/368c481cd6954bdfa5d0435479fd4eaf/690e0784c90342669a5f1461ae65b95f.html?locale=en-US&state=PRODUCTION&version=Cloud) |

[111453a]: https://github.com/miyasuta/cpi-iflow-samples/commit/111453a
[3052ccb]: https://github.com/miyasuta/cpi-iflow-samples/commit/3052ccb
[d66cf44]: https://github.com/miyasuta/cpi-iflow-samples/commit/d66cf44
[f34d292]: https://github.com/miyasuta/cpi-iflow-samples/commit/f34d292
