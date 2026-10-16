# .iflw structure

Elements of an `.iflw` file, IDs, `bpmndi` (diagram information), and every place that must change together when a step is inserted.

Facts come from the real files of S01 ([92c8b77]) and `X01_Sandbox` ([40a9c8b]) and from local-edit experiments. Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

## Element layout

```
bpmn2:definitions
├── bpmn2:collaboration  Collaboration_1
│   ├── bpmn2:documentation        iFlow Description
│   ├── bpmn2:extensionElements    iFlow-level ifl:property
│   ├── bpmn2:participant  Participant_1          ifl:type="EndpointSender"     (Sender)
│   ├── bpmn2:participant  Participant_2          ifl:type="EndpointRecevier"   (Receiver)
│   ├── bpmn2:participant  Participant_Process_1  ifl:type="IntegrationProcess" processRef="Process_1"
│   └── bpmn2:messageFlow  MessageFlow_4          adapter (e.g. HTTPS sender)
├── bpmn2:process  Process_1  name="Integration Process"
│   ├── bpmn2:extensionElements    process-level ifl:property
│   ├── bpmn2:startEvent  StartEvent_2
│   ├── bpmn2:callActivity  CallActivity_5        a step, e.g. Content Modifier
│   ├── bpmn2:endEvent  EndEvent_2
│   └── bpmn2:sequenceFlow  SequenceFlow_3, …     connections between nodes
└── bpmndi:BPMNDiagram
    └── bpmndi:BPMNPlane  bpmnElement="Collaboration_1"
        ├── bpmndi:BPMNShape  one per node and per participant
        └── bpmndi:BPMNEdge   one per sequenceFlow and per messageFlow
```

| Element | Fact | Evidence |
|---|---|---|
| `bpmn2:collaboration` | `Collaboration_1`. Holds iFlow-level `ifl:property`, the Description, the participants, and the message flows. | [92c8b77] |
| `bpmn2:documentation` | The iFlow Description. See [workflow.md](workflow.md#iflow-description). | [af09698], [bb5e4f0] |
| `bpmn2:participant` | `Participant_2` is spelled `EndpointRecevier` by CPI. **Keep that spelling.** | [92c8b77] |
| `bpmn2:messageFlow` | An adapter is a `messageFlow` in the collaboration, not a step in the process. Example: `MessageFlow_4`, `name="HTTPS"`, `sourceRef="Participant_1"`, `targetRef="StartEvent_2"`. Settings are `ifl:property` ([components/https-sender.md](components/https-sender.md)). | [03225bf] |
| `bpmn2:startEvent` / `bpmn2:endEvent` | `StartEvent_2` / `EndEvent_2` exist from the empty iFlow onward. Each has `bpmn2:outgoing` / `bpmn2:incoming` children and a `bpmn2:messageEventDefinition`. | [03225bf], [9d3de86] |
| `bpmn2:callActivity` | A step such as a Content Modifier. Has `bpmn2:incoming` / `bpmn2:outgoing` children. Settings are `ifl:property` ([components/content-modifier.md](components/content-modifier.md)). | [9d3de86] |
| `bpmn2:sequenceFlow` | Connection between nodes in the process: `sourceRef` / `targetRef`. | [9d3de86] |
| Step names | The UI numbers new steps (`Content Modifier 1`). A locally added step can have any name (`Added Locally`). | [9d3de86], [395e94c] |

Keep every `ifl:property` of the collaboration, process, events and participants as it is. Change only what the task needs.

## IDs

| Fact | Evidence |
|---|---|
| Any hand-written unique ID (`CallActivity_Local1`, `SequenceFlow_Local1`) is accepted and kept after save and Push. CPI-style numbers are not required. | [395e94c] → [57b3074] |
| On save, only the `id` of `bpmn2:documentation` is regenerated. | [57b3074], [0c0adde] |
| `bpmndi` IDs are `BPMNShape_<element id>` and `BPMNEdge_<element id>`. Hand-written elements following this pattern kept their IDs. Whether other `bpmndi` IDs are accepted is **unverified**; always follow the pattern. | [03225bf], [395e94c] → [57b3074] |
| When the UI inserts a step, the existing sequenceFlow keeps its ID and the new sequenceFlow gets a new ID. | [9d3de86] |
| Element order in the XML does not follow ID order, and CPI may reorder elements on save. | [9d3de86], [57b3074] |

Use IDs such as `CallActivity_Local1`, `SequenceFlow_Local1` for new elements and make sure they are unique in the file.

## bpmndi

**Rule: every node and every participant has a `BPMNShape`, and every sequenceFlow and messageFlow has a `BPMNEdge`, with all references consistent.** When you add or change an element, add or update its shape and edges.

**Rule: when a flow gets a new source or target, also move its `di:waypoint` ends to the new shapes.** The designer draws lines along the waypoints, not along `sourceElement` / `targetElement`.

| Fact | Evidence |
|---|---|
| A step added without `bpmndi` (no shape for the step, no edge for the new flow, the existing edge still pointing at the old target) makes Pull fail with `Artifact pull failed due to unexpected error`. | [56e0a25] |
| The same process plus a shape for the new step, an edge for the new flow, and the re-targeted existing edge pulls, saves, deploys and runs. | [395e94c] |
| Which of those gaps alone breaks Pull is **unverified**. Writing all of them always works. | [56e0a25], [395e94c] |
| Invalid coordinates (a shape at x=-500, y=5000; waypoints (0,0)→(0,0)) are not an error. The designer draws the step in its normal position and CPI rewrites the coordinates on save. Coordinates only need to be roughly right. | [fc352ae] → [0c0adde] |
| Valid coordinates that differ from CPI's layout are not re-laid out when the designer saves (a new shape at x=580, y=200 stayed there). Seen in the designer; the saved file was not pushed before the layout was reformatted. | [4992e7a] |
| The designer draws each line along its waypoints. A re-targeted edge whose waypoints still end at the old target is drawn to the old target, and the new step looks unconnected. Saving does not correct this. The iFlow still runs along the `sequenceFlow` references, so only the diagram is wrong. | [4992e7a] |
| The designer's auto layout (format) fixes such a diagram. It rewrites every coordinate and the element order, but no key, value or reference. | [4992e7a] → [addffca] |
| A `BPMNEdge` refers to **shape IDs** in `sourceElement` / `targetElement` (`BPMNShape_...`) and has two or more `di:waypoint` with `xsi:type="dc:Point"`. | [03225bf], [40a9c8b] |
| Shape sizes written by CPI: step (`callActivity`) 100x60, Start/End 32x32, sender/receiver participants 100x140, the Integration Process participant 540x220 (in S01). | [9d3de86], [40a9c8b] |
| The real files contain exactly this set: a shape for every process node and every participant, an edge for every sequenceFlow and messageFlow (`X01_Sandbox`: 7 shapes, 4 edges). | [40a9c8b] |

### Example (written locally in [395e94c], as saved by CPI in [57b3074])

```xml
<bpmndi:BPMNShape bpmnElement="CallActivity_Local1" id="BPMNShape_CallActivity_Local1">
    <dc:Bounds height="60.0" width="100.0" x="560.0" y="132.0"/>
</bpmndi:BPMNShape>
<bpmndi:BPMNEdge bpmnElement="SequenceFlow_Local1" id="BPMNEdge_SequenceFlow_Local1" sourceElement="BPMNShape_CallActivity_Local1" targetElement="BPMNShape_EndEvent_2">
    <di:waypoint x="610.0" xsi:type="dc:Point" y="160.0"/>
    <di:waypoint x="719.0" xsi:type="dc:Point" y="160.0"/>
</bpmndi:BPMNEdge>
```

### Layout to imitate

After auto layout, CPI wrote this layout ([addffca]). Other coordinates are accepted too, but following it keeps the diagram readable:

- Steps (100x60) and Start/End (32x32) sit in one row with the same center y: steps at `y=110`, Start/End at `y=124` (center y=140), 60 apart.
- A sequenceFlow edge has two waypoints: the right edge of the source shape (x + width, center y) and the left edge of the target shape (x, center y). Example: a step at x=362 to a step at x=522 is `462,140` → `522,140`.

Place a new shape in the row between its neighbors without overlapping them. If there is no room, move the shapes after it to the right, and move the waypoints of every edge that touches a moved shape.

## Inserting a step between two nodes

To insert a new step N into an existing sequenceFlow F (A → B). Confirmed both by a UI insertion ([9d3de86]) and by a local insertion that pulled, deployed and ran ([395e94c]).

1. Add `bpmn2:callActivity` N to the process, with `<bpmn2:incoming>F</bpmn2:incoming>` and `<bpmn2:outgoing>G</bpmn2:outgoing>`.
2. Change F's `targetRef` from B to N.
3. Add a new `bpmn2:sequenceFlow` G with `sourceRef="N"` `targetRef="B"`.
4. In B, replace `<bpmn2:incoming>F</bpmn2:incoming>` with `<bpmn2:incoming>G</bpmn2:incoming>`. A's `outgoing` stays F.
5. Add `BPMNShape_N` for N.
6. Change `targetElement` of `BPMNEdge_F` to `BPMNShape_N`, **and move its last waypoint to the left edge of N**.
7. Add `BPMNEdge_G` with `sourceElement="BPMNShape_N"` `targetElement="BPMNShape_B"`, from the right edge of N to the left edge of B.

Without the waypoint change in step 6, Pull, deploy and the run still work, but the designer shows F going to B and N without an incoming line ([4992e7a]).

The UI also updated existing waypoints and the end point of the sender message flow ([9d3de86]); the local insertion worked without those changes ([395e94c]).

Connecting an adapter in the UI added a `messageFlow` and its `BPMNEdge` with `sourceElement="BPMNShape_Participant_1"` and `targetElement="BPMNShape_StartEvent_2"` ([03225bf]).

## References that must be consistent

`scripts/check_iflw.py` checks all of these. Whether each single inconsistency makes Pull fail is **unverified**, so all are treated as errors.

- sequenceFlow `sourceRef` / `targetRef` ↔ the nodes' `outgoing` / `incoming`
- messageFlow `sourceRef` / `targetRef` exist (participant / start event)
- `BPMNShape` / `BPMNEdge` `bpmnElement` point at existing elements
- `BPMNEdge` `sourceElement` / `targetElement` are the shapes of the flow's `sourceRef` / `targetRef`
- No duplicate IDs

[03225bf]: https://github.com/miyasuta/cpi-iflow-samples/commit/03225bf
[0c0adde]: https://github.com/miyasuta/cpi-iflow-samples/commit/0c0adde
[395e94c]: https://github.com/miyasuta/cpi-iflow-samples/commit/395e94c
[40a9c8b]: https://github.com/miyasuta/cpi-iflow-samples/commit/40a9c8b
[4992e7a]: https://github.com/miyasuta/cpi-iflow-samples/commit/4992e7a
[56e0a25]: https://github.com/miyasuta/cpi-iflow-samples/commit/56e0a25
[57b3074]: https://github.com/miyasuta/cpi-iflow-samples/commit/57b3074
[92c8b77]: https://github.com/miyasuta/cpi-iflow-samples/commit/92c8b77
[9d3de86]: https://github.com/miyasuta/cpi-iflow-samples/commit/9d3de86
[addffca]: https://github.com/miyasuta/cpi-iflow-samples/commit/addffca
[af09698]: https://github.com/miyasuta/cpi-iflow-samples/commit/af09698
[bb5e4f0]: https://github.com/miyasuta/cpi-iflow-samples/commit/bb5e4f0
[fc352ae]: https://github.com/miyasuta/cpi-iflow-samples/commit/fc352ae
