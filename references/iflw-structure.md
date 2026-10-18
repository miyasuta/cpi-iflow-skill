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
│   ├── bpmn2:messageFlow  MessageFlow_4          sender adapter (e.g. HTTPS sender): Participant_1 → StartEvent_2
│   └── bpmn2:messageFlow  MessageFlow_8          receiver adapter (e.g. HTTP receiver): ServiceTask_5 → Participant_2
├── bpmn2:process  Process_1  name="Integration Process"
│   ├── bpmn2:extensionElements    process-level ifl:property
│   ├── bpmn2:startEvent  StartEvent_2
│   ├── bpmn2:callActivity  CallActivity_5        a step, e.g. Content Modifier
│   ├── bpmn2:serviceTask  ServiceTask_5          a Request Reply step
│   ├── bpmn2:subProcess  SubProcess_5           an Exception Subprocess: not connected to the flow;
│   │                                           its events, steps and sequenceFlows are its children
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
| `bpmn2:serviceTask` | A Request Reply step. Has `bpmn2:incoming` / `bpmn2:outgoing` children like a `callActivity`, and three `ifl:property` ([components/request-reply.md](components/request-reply.md)). | [f1a9ee9] |
| `bpmn2:messageFlow` (receiver) | A receiver adapter is a `messageFlow` from a Request Reply step to a receiver participant. Example: `MessageFlow_8`, `name="HTTP"`, `sourceRef="ServiceTask_5"`, `targetRef="Participant_7"` ([components/http-receiver.md](components/http-receiver.md)). | [cc4ce46] |
| Receiver participant | Every empty iFlow already has `Participant_2` (`name="Receiver"`) at x=900, y=100. A receiver adapter can target it ([c3ddf1c]); a participant placed in the UI has the single key `ifl:type` ([cc4ce46]). | [c3ddf1c], [cc4ce46] |
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
| Coordinates of **existing** elements (same ID) changed locally came back as CPI's previously saved values in the next Push from CPI, even without any Save in CPI: the end waypoint of a re-targeted edge returned to its old end at the End event (`703.5`), and an End event moved from x=703 to x=730 returned to x=703. Coordinates of **new** shapes and edges kept the local values. References and the run were not affected. Seen 6 times: the 6th in the API download after Pull of [c3ddf1c] (the re-targeted edge went back to `323.5,158 → 703.5,158`), the 4th in files that CPI saved after Pull ([4125596] → [119da02]: the re-targeted edge went back to `323.5,158.0 → 703.5,158.0`), the 5th after [83d2f85], where every moved shape went back and hid the new step (see "Layout to imitate"). | [669b621], [0d5db9d], [c058b69], [119da02], [c3ddf1c] |
| That CPI already uses its saved coordinates for existing elements when it pulls is **unverified** (an inference): after the Pull in [6126bba], the designer drew the new step right next to the End event, as if End were still at x=703. | [6126bba], [c058b69] |
| The designer's auto layout (format) fixes such a diagram. It rewrites every coordinate and the element order, but no key, value or reference. | [4992e7a] → [addffca] |
| A `BPMNEdge` refers to **shape IDs** in `sourceElement` / `targetElement` (`BPMNShape_...`) and has two or more `di:waypoint` with `xsi:type="dc:Point"`. | [03225bf], [40a9c8b] |
| Shape sizes written by CPI: step (`callActivity`, and the `serviceTask` of Request Reply in [f1a9ee9]) 100x60, Start/End 32x32, sender/receiver participants 100x140, the Integration Process participant 540x220 (in S01). | [9d3de86], [40a9c8b] |
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

**Never move existing shapes.** Do not change the `Bounds` of any existing step, Start/End event, sender/receiver participant or the Integration Process pool, and do not widen the pool. CPI puts existing coordinates back to its saved values (all 6 cases above), and that does harm: in one evaluation the existing step, End, Receiver and pool were moved 160 to the right and the new Groovy step was put at the old place of the moved step ([83d2f85]). After Pull, CPI had all existing shapes at their old coordinates and the new step at the written ones, so the new step lay exactly under the existing step and could not be seen in the designer (checked in CPI on 2026-10-18 after a second Pull: the API download of the iFlow had the existing step at x=682, End 842, Receiver 1018, pool width 708, and the new step also at x=682).

Where to put a new step, without overlapping any existing shape:

1. In free space in the row between its neighbors. In the default empty iFlow (Start x=292, End x=703, y=142), two steps fit at x=460 and x=590 (y=128, 100x60) ([3ef66d2], [6126bba]).
2. If the row has no room, below the row (a larger y), inside the pool's height. Example: a new shape at x=580, y=200 was accepted ([4992e7a]). How the designer draws a step placed below the row, and its lines, is **unverified**.
3. If that would put the step outside the pool (for example, a pool of height 137 after auto layout leaves no room below the row), still do not move or resize anything. Place it as well as you can without overlap, and ask the user to run the designer's auto layout after Pull ([4992e7a] → [addffca]), then Save and Push before the next local edit (see [workflow.md](workflow.md)). That auto layout fixes such a placement is **unverified**.

`scripts/check_iflw.py` warns when two shapes of steps, events or sender/receiver participants overlap. It can only check the file as written: in the case above the file had no overlap, and the overlap appeared only after CPI put the moved shapes back. So the rule above, not the check, prevents it.

Write the waypoints of the new and re-targeted edges to the shapes they connect, as in "Inserting a step" below.

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

Write the waypoints of step 6 correctly even though CPI may later put F's old end point back (`703.5` in [669b621], [0d5db9d], [c058b69]). In those cases the old line still passed over N, so the designer showed it correctly. Do not copy such a value from a pushed file when you insert a step.

The UI also updated existing waypoints and the end point of the sender message flow ([9d3de86]); the local insertion worked without those changes ([395e94c]).

Connecting an adapter in the UI added a `messageFlow` and its `BPMNEdge` with `sourceElement="BPMNShape_Participant_1"` and `targetElement="BPMNShape_StartEvent_2"` ([03225bf]).

A Request Reply step is inserted the same way (the step element is a `serviceTask`), and its receiver adapter is a `messageFlow` with a `BPMNEdge` from the step's shape to the receiver participant's shape. Steps in [components/request-reply.md](components/request-reply.md) ([f1a9ee9], [cc4ce46], [c3ddf1c]).

## References that must be consistent

`scripts/check_iflw.py` checks all of these. Whether each single inconsistency makes Pull fail is **unverified**, so all are treated as errors. It also prints a **warning** (exit code stays 0) when the waypoints of an edge do not reach its source or target shape, as in [4992e7a]. Fix the waypoints; the warning means the diagram will look wrong.

- sequenceFlow `sourceRef` / `targetRef` ↔ the nodes' `outgoing` / `incoming`
- messageFlow `sourceRef` / `targetRef` exist (sender: participant → start event; receiver: Request Reply step → participant)
- `BPMNShape` / `BPMNEdge` `bpmnElement` point at existing elements
- `BPMNEdge` `sourceElement` / `targetElement` are the shapes of the flow's `sourceRef` / `targetRef`
- No duplicate IDs

[03225bf]: https://github.com/miyasuta/cpi-iflow-samples/commit/03225bf
[0c0adde]: https://github.com/miyasuta/cpi-iflow-samples/commit/0c0adde
[0d5db9d]: https://github.com/miyasuta/cpi-iflow-samples/commit/0d5db9d
[119da02]: https://github.com/miyasuta/cpi-iflow-samples/commit/119da02
[395e94c]: https://github.com/miyasuta/cpi-iflow-samples/commit/395e94c
[3ef66d2]: https://github.com/miyasuta/cpi-iflow-samples/commit/3ef66d2
[40a9c8b]: https://github.com/miyasuta/cpi-iflow-samples/commit/40a9c8b
[4125596]: https://github.com/miyasuta/cpi-iflow-samples/commit/4125596
[4992e7a]: https://github.com/miyasuta/cpi-iflow-samples/commit/4992e7a
[56e0a25]: https://github.com/miyasuta/cpi-iflow-samples/commit/56e0a25
[57b3074]: https://github.com/miyasuta/cpi-iflow-samples/commit/57b3074
[6126bba]: https://github.com/miyasuta/cpi-iflow-samples/commit/6126bba
[669b621]: https://github.com/miyasuta/cpi-iflow-samples/commit/669b621
[83d2f85]: https://github.com/miyasuta/cpi-iflow-samples/commit/83d2f85
[92c8b77]: https://github.com/miyasuta/cpi-iflow-samples/commit/92c8b77
[9d3de86]: https://github.com/miyasuta/cpi-iflow-samples/commit/9d3de86
[addffca]: https://github.com/miyasuta/cpi-iflow-samples/commit/addffca
[af09698]: https://github.com/miyasuta/cpi-iflow-samples/commit/af09698
[f1a9ee9]: https://github.com/miyasuta/cpi-iflow-samples/commit/f1a9ee9
[bb5e4f0]: https://github.com/miyasuta/cpi-iflow-samples/commit/bb5e4f0
[c058b69]: https://github.com/miyasuta/cpi-iflow-samples/commit/c058b69
[c3ddf1c]: https://github.com/miyasuta/cpi-iflow-samples/commit/c3ddf1c
[cc4ce46]: https://github.com/miyasuta/cpi-iflow-samples/commit/cc4ce46
[fc352ae]: https://github.com/miyasuta/cpi-iflow-samples/commit/fc352ae
