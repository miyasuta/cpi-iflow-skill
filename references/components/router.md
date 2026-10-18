# Router

A Router sends the message down one of several routes, by conditions on headers or properties. In the `.iflw` it is a **`bpmn2:exclusiveGateway`** in the process. Each route is a `bpmn2:sequenceFlow` that leaves the Router; its condition is a child `bpmn2:conditionExpression`, and the default route is named by the Router's `default` attribute. For the place of each element in the file, see [../iflw-structure.md](../iflw-structure.md).

Commit hashes link to [miyasuta/cpi-iflow-samples](https://github.com/miyasuta/cpi-iflow-samples). Anything not confirmed is marked **unverified**.

## Supported in this skill version

| Task | Local edit |
|---|---|
| Put a Router where Start connects to End, with one route per header value (a Content Modifier and its own End on each route) and a default route | Verified once: written locally into an empty iFlow with an HTTPS sender and Allowed Header(s), pulled, deployed without Save, called ([6ef7611]). |
| Add a route with a condition, its Content Modifier and its own End to an existing Router | Verified once ([45bac88]). |

Conditions verified: Non-XML (`expressionType` `NonXML`) with `=` on a request header, `${header.<name>} = '<value>'`, including a header name with hyphens. One default route without a condition.

Not supported (no sample): XML (XPath) conditions, other operators (`!=`, `in`, `regex`, `and`, …) and properties in conditions (documented by SAP, not tested), a Router with *Throw Exception* (`throwException` `true`), routes that join into one End or merge back into one flow, steps other than one Content Modifier on a route, and a Router anywhere other than directly after Start. For these, follow the "unsupported request" rule in [../../SKILL.md](../../SKILL.md).

## Router

```xml
<bpmn2:exclusiveGateway default="SequenceFlow_11" id="ExclusiveGateway_5" name="Router 1">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>componentVersion</key>
            <value>1.2</value>
        </ifl:property>
        <ifl:property>
            <key>activityType</key>
            <value>ExclusiveGateway</value>
        </ifl:property>
        <ifl:property>
            <key>cmdVariantUri</key>
            <value>ctype::FlowstepVariant/cname::ExclusiveGateway/version::1.2.0</value>
        </ifl:property>
        <ifl:property>
            <key>throwException</key>
            <value>false</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:incoming>SequenceFlow_3</bpmn2:incoming>
    <bpmn2:outgoing>SequenceFlow_6</bpmn2:outgoing>
    <bpmn2:outgoing>SequenceFlow_11</bpmn2:outgoing>
</bpmn2:exclusiveGateway>
```

As saved by CPI ([87baf40]). Keep the four keys and values. `default` is the `id` of the default route; it must be one of the Router's `outgoing` flows. Without a default route the Router had no `default` attribute ([40b59fb]); a Router without one is **unverified** at runtime, so always write one.

## Routes

A route with a condition ([87baf40]; the two version keys left out as in [45bac88], see below):

```xml
<bpmn2:sequenceFlow id="SequenceFlow_6" name="Route 1" sourceRef="ExclusiveGateway_5" targetRef="CallActivity_8">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>expressionType</key>
            <value>NonXML</value>
        </ifl:property>
    </bpmn2:extensionElements>
    <bpmn2:conditionExpression id="FormalExpression_SequenceFlow_6_1792309486775" xsi:type="bpmn2:tFormalExpression">${header.X-S06-Route} = 'a'</bpmn2:conditionExpression>
</bpmn2:sequenceFlow>
```

The default route has no `conditionExpression`, and the UI wrote `expressionType` `XML` for it ([87baf40]). Copy that as it is; it worked next to `NonXML` routes, although SAP says the routes of one Router must use the same type ([SAP docs: Define Router](https://github.com/SAP-docs/btp-integration-suite/blob/main/docs/ISuite_Integrations_APIs/define-router-d7fddbd.md)):

```xml
<bpmn2:sequenceFlow id="SequenceFlow_11" name="Route 2" sourceRef="ExclusiveGateway_5" targetRef="CallActivity_10">
    <bpmn2:extensionElements>
        <ifl:property>
            <key>expressionType</key>
            <value>XML</value>
        </ifl:property>
    </bpmn2:extensionElements>
</bpmn2:sequenceFlow>
```

| Fact | Evidence |
|---|---|
| The condition is the element text, written as it is: `$`, `{`, `'` and a header name with hyphens need no escaping. Strings are in single quotes. | [40b59fb], called in [87baf40] and [6ef7611] |
| The `conditionExpression` `id` is `FormalExpression_<route id>_<number>`. CPI renumbers it on every save and Pull, so any number works. | [87baf40], [6ef7611], [45bac88] |
| The UI also writes `componentVersion` `1.0` and `cmdVariantUri` `ctype::FlowstepVariant/cname::GatewayRoute/version::1.0.0` on each route. When written locally, CPI dropped both on Pull and kept only `expressionType`; a route written without them was kept as written. Either way the iFlow ran. Leave them out of new routes, and leave them as they are on existing routes. | [87baf40], [6ef7611], [45bac88] (API downloads after Pull, not committed) |
| A route's `name` (`Route 1`) is free text. | [87baf40] |
| A header in a condition must reach the Router: add it to Allowed Header(s) (`allowedHeaderList`, see [groovy-script.md](groovy-script.md#allowed-headers-reading-request-headers)). It was set in every tested case; a condition on a request header with Allowed Header(s) empty is **unverified**. | [7f96540], [6ef7611] |
| When no condition matched (no header, or another value), the default route was taken. | [87baf40], [6ef7611], [45bac88] |

`check_iflw.py` reports a `default` that is not a route of the Router as an error, and warns about a Router without a default route, a default route with a condition, and another route without one.

## What each route leads to

Each route goes to its own Content Modifier (the 7-key template in [content-modifier.md](content-modifier.md)) and then its own End. The first route reuses the existing `EndEvent_2`; each further route gets a new End with the same two keys:

```xml
<bpmn2:endEvent id="EndEvent_13" name="End 1">
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
    <bpmn2:incoming>SequenceFlow_14</bpmn2:incoming>
    <bpmn2:messageEventDefinition/>
</bpmn2:endEvent>
```

The empty iFlow's `EndEvent_2` has the same two keys ([7456ef8]).

## Putting a Router after Start

Starting from Start → End (`SequenceFlow_3`), as in [6ef7611]:

1. Add the Router with `<bpmn2:incoming>SequenceFlow_3</bpmn2:incoming>` and one `outgoing` per route, and its `default` attribute.
2. Change `SequenceFlow_3`'s `targetRef` from `EndEvent_2` to the Router.
3. Route 1: a route flow Router → Content Modifier, the Content Modifier, and a flow Content Modifier → `EndEvent_2`. Replace `EndEvent_2`'s `incoming` with that last flow.
4. Each further route: a route flow, a Content Modifier, a new End and a flow between them.
5. `bpmndi`: a `BPMNShape` for every new node and a `BPMNEdge` for every new flow; change `BPMNEdge_SequenceFlow_3`'s `targetElement` to the Router's shape and its last waypoint to the Router's left edge.

New IDs only need to be unique. The UI numbers them across element types (`ExclusiveGateway_5`, `SequenceFlow_6`, `CallActivity_8`, …).

### Layout

This layout fits the pool of an empty iFlow (x=250, y=60, 540x220) without moving anything ([45bac88]); Start (x=292) and `EndEvent_2` (x=703, y=142) stay where they are:

| Shape | Bounds (x, y, width, height) |
|---|---|
| Router | 442, 142, 40, 40 |
| Route 1: Content Modifier → `EndEvent_2` | 562, 132, 100, 60 → (existing) 703, 142 |
| Default route, below the row: Content Modifier → End | 567, 205, 100, 60 → 703, 217, 36, 36 |
| Third route, above the row: Content Modifier → End | 567, 70, 100, 60 → 703, 82, 36, 36 |

A route edge to a shape below or above the row has three waypoints: down (or up) from the Router, then right, for example `462,181` → `462,235` → `617,235`. After Pull, CPI put the rewritten `BPMNEdge_SequenceFlow_3` back to its old line (`323.5,158` → `703.5,158`), which runs over the Router and Route 1; the iFlow still ran. How the designer draws this diagram is **unverified**.

## What the caller gets back

With an HTTPS sender and a Content Modifier body on each route: the body of the route taken, HTTP 200. The routed header also came back in the response (lower case, for example `x-s06-route: a`), because it was in Allowed Header(s) ([87baf40], [6ef7611], [45bac88]).

[40b59fb]: https://github.com/miyasuta/cpi-iflow-samples/commit/40b59fb
[45bac88]: https://github.com/miyasuta/cpi-iflow-samples/commit/45bac88
[6ef7611]: https://github.com/miyasuta/cpi-iflow-samples/commit/6ef7611
[7456ef8]: https://github.com/miyasuta/cpi-iflow-samples/commit/7456ef8
[7f96540]: https://github.com/miyasuta/cpi-iflow-samples/commit/7f96540
[87baf40]: https://github.com/miyasuta/cpi-iflow-samples/commit/87baf40
