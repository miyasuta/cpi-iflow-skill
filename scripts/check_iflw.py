#!/usr/bin/env python3
"""Minimal consistency check for SAP Cloud Integration .iflw files.

Run it after every local edit, before pushing to the Git repository:

    python3 scripts/check_iflw.py <file.iflw | directory> [...]

A directory is searched recursively for *.iflw files.
Exit code: 0 = no errors (warnings may be printed), 1 = errors found,
2 = a path does not exist or no .iflw file was found.

What it checks (see references/iflw-structure.md and references/escaping.md):
- The file is well-formed XML.
- No id is used twice.
- sequenceFlow sourceRef/targetRef exist in the same process and match the
  incoming/outgoing of the nodes (both directions).
- messageFlow sourceRef/targetRef and participant processRef exist.
- Every node in a process and every participant has exactly one BPMNShape;
  every sequenceFlow and messageFlow has exactly one BPMNEdge.
- Every BPMNShape/BPMNEdge points at an existing element; a BPMNEdge's
  sourceElement/targetElement are the shapes of the flow's sourceRef/targetRef.
- headerTable/propertyTable/clientCertificates values, after the one level of
  unescaping done by the XML parser, parse as <row><cell id='...'>...</cell></row>
  fragments.
- Every externalized parameter {{name}} used in an ifl:property value is
  defined in parameters.prop (a name=value line) and in parameters.propdef
  (a <parameter><name>). Both files are looked up in the iFlow's
  src/main/resources folder, two levels above the .iflw
  (src/main/resources/scenarioflows/integrationflow/<name>.iflw). A missing
  file is an error only if the .iflw uses a parameter; an empty file has no
  parameters. A parameters.propdef that is not well-formed XML is an error.
  See references/externalized-parameters.md.
- Every Groovy Script step (callActivity with activityType Script and
  subActivityType GroovyScript) names a script file in 'script', and that
  file exists in src/main/resources/script/ (the value is the file name only).
  What CPI does with a missing script file is unverified, so it is an error.
  See references/components/groovy-script.md.

Warnings (printed, but the exit code stays 0):
- A '>' inside a table cell that is escaped only once (&gt; instead of
  &amp;gt;). Whether CPI accepts it is unverified.
- The line of a BPMNEdge (its waypoints) does not reach the shape of its
  sourceElement or targetElement. The designer draws lines along the waypoints,
  so the diagram looks wrong; the iFlow still runs.
- A parameter in parameters.prop or parameters.propdef that the .iflw does not
  use as {{name}}.
- A .groovy file in src/main/resources/script/ that no Groovy Script step
  names in 'script'.
- Two shapes of process nodes (steps, events) or sender/receiver participants
  overlap. CPI puts moved existing shapes back to their saved coordinates, so
  a new step placed where an existing shape used to be ends up hidden under it.
  Shapes inside the Integration Process pool are not an overlap.

Which bpmndi gaps actually make a Pull fail is not known, so every element is
checked strictly. Uses the Python standard library only.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET

BPMN2 = "http://www.omg.org/spec/BPMN/20100524/MODEL"
BPMNDI = "http://www.omg.org/spec/BPMN/20100524/DI"
IFL = "http:///com.sap.ifl.model/Ifl.xsd"
DC = "http://www.omg.org/spec/DD/20100524/DC"
DI = "http://www.omg.org/spec/DD/20100524/DI"

# Table-type ifl:property values that hold an escaped XML fragment.
TABLE_KEYS = ("headerTable", "propertyTable", "clientCertificates")

# How far (in diagram units) an edge's line may stay from its shapes.
WAYPOINT_TOLERANCE = 10.0

TAG = re.compile(r"<[^<>]*>")

# An externalized parameter in an ifl:property value: {{name}}.
PARAM = re.compile(r"\{\{([^{}]*)\}\}")

SCRIPT_DIR = "script"

PROP_FILE = "parameters.prop"
PROPDEF_FILE = "parameters.propdef"

# Children of a process that are not flow nodes.
NON_NODE_TAGS = {
    "{%s}extensionElements" % BPMN2,
    "{%s}documentation" % BPMN2,
    "{%s}sequenceFlow" % BPMN2,
}


def q(ns, name):
    return "{%s}%s" % (ns, name)


def local(tag):
    return tag.rsplit("}", 1)[-1]


def check_file(path):
    """Return a list of error messages for one .iflw file (empty if OK)."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return ["XML is not well-formed: %s" % e]

    errors = []
    by_id = {}
    for el in root.iter():
        el_id = el.get("id")
        if el_id is None:
            continue
        if el_id in by_id:
            errors.append("duplicate id '%s' (<%s> and <%s>)" % (
                el_id, local(by_id[el_id].tag), local(el.tag)))
        else:
            by_id[el_id] = el

    nodes = {}  # node id -> (element, process id)
    seq_flows = []
    for process in root.iter(q(BPMN2, "process")):
        process_id = process.get("id")
        for child in process:
            if child.tag == q(BPMN2, "sequenceFlow"):
                seq_flows.append((child, process_id))
            elif child.tag not in NON_NODE_TAGS and child.get("id"):
                nodes[child.get("id")] = (child, process_id)

    errors += check_sequence_flows(nodes, seq_flows)

    message_flows = list(root.iter(q(BPMN2, "messageFlow")))
    participants = list(root.iter(q(BPMN2, "participant")))
    for mf in message_flows:
        for attr in ("sourceRef", "targetRef"):
            ref = mf.get(attr)
            if ref not in by_id:
                errors.append("messageFlow '%s': %s '%s' does not exist" % (mf.get("id"), attr, ref))
    for p in participants:
        ref = p.get("processRef")
        if ref is not None and (ref not in by_id or by_id[ref].tag != q(BPMN2, "process")):
            errors.append("participant '%s': processRef '%s' is not a process" % (p.get("id"), ref))

    errors += check_diagram(root, by_id, nodes, participants, seq_flows, message_flows)
    errors += check_tables(root)
    errors += check_parameters(path, root)
    errors += check_scripts(path, root)
    return errors


def check_sequence_flows(nodes, seq_flows):
    errors = []
    flow_by_id = {f.get("id"): f for f, _ in seq_flows}
    for flow, process_id in seq_flows:
        fid = flow.get("id")
        for attr, child_tag in (("sourceRef", "outgoing"), ("targetRef", "incoming")):
            ref = flow.get(attr)
            if ref not in nodes:
                errors.append("sequenceFlow '%s': %s '%s' is not a node of any process" % (fid, attr, ref))
                continue
            node, node_process = nodes[ref]
            if node_process != process_id:
                errors.append("sequenceFlow '%s': %s '%s' is in another process" % (fid, attr, ref))
            listed = [c.text.strip() for c in node.findall(q(BPMN2, child_tag)) if c.text]
            if fid not in listed:
                errors.append("node '%s' does not list sequenceFlow '%s' in <%s> (flow %s is '%s')" % (
                    ref, fid, child_tag, attr, ref))

    for node_id, (node, _) in nodes.items():
        for child_tag, attr in (("incoming", "targetRef"), ("outgoing", "sourceRef")):
            for c in node.findall(q(BPMN2, child_tag)):
                ref = (c.text or "").strip()
                flow = flow_by_id.get(ref)
                if flow is None:
                    errors.append("node '%s': <%s> '%s' is not a sequenceFlow" % (node_id, child_tag, ref))
                    continue
                if flow.get(attr) != node_id:
                    errors.append("node '%s': <%s> '%s' but that flow's %s is '%s'" % (
                        node_id, child_tag, ref, attr, flow.get(attr)))
    return errors


def check_diagram(root, by_id, nodes, participants, seq_flows, message_flows):
    errors = []
    shapes = {}       # shape id -> bpmnElement
    shape_count = {}  # bpmnElement -> number of shapes
    edges = []
    edge_count = {}
    for plane in root.iter(q(BPMNDI, "BPMNPlane")):
        ref = plane.get("bpmnElement")
        if ref not in by_id:
            errors.append("BPMNPlane '%s': bpmnElement '%s' does not exist" % (plane.get("id"), ref))
    for shape in root.iter(q(BPMNDI, "BPMNShape")):
        ref = shape.get("bpmnElement")
        shapes[shape.get("id")] = ref
        shape_count[ref] = shape_count.get(ref, 0) + 1
        if ref not in by_id:
            errors.append("BPMNShape '%s': bpmnElement '%s' does not exist" % (shape.get("id"), ref))
    for edge in root.iter(q(BPMNDI, "BPMNEdge")):
        ref = edge.get("bpmnElement")
        edges.append(edge)
        edge_count[ref] = edge_count.get(ref, 0) + 1
        if ref not in by_id:
            errors.append("BPMNEdge '%s': bpmnElement '%s' does not exist" % (edge.get("id"), ref))

    needs_shape = [("node", n) for n in nodes] + [("participant", p.get("id")) for p in participants]
    for kind, el_id in needs_shape:
        count = shape_count.get(el_id, 0)
        if count == 0:
            errors.append("%s '%s' has no BPMNShape" % (kind, el_id))
        elif count > 1:
            errors.append("%s '%s' has %d BPMNShapes" % (kind, el_id, count))

    flows = [("sequenceFlow", f) for f, _ in seq_flows] + [("messageFlow", f) for f in message_flows]
    for kind, flow in flows:
        count = edge_count.get(flow.get("id"), 0)
        if count == 0:
            errors.append("%s '%s' has no BPMNEdge" % (kind, flow.get("id")))
        elif count > 1:
            errors.append("%s '%s' has %d BPMNEdges" % (kind, flow.get("id"), count))

    flow_by_id = {f.get("id"): f for _, f in flows}
    for edge in edges:
        flow = flow_by_id.get(edge.get("bpmnElement"))
        for attr, flow_attr in (("sourceElement", "sourceRef"), ("targetElement", "targetRef")):
            shape_id = edge.get(attr)
            if shape_id not in shapes:
                errors.append("BPMNEdge '%s': %s '%s' is not a BPMNShape" % (edge.get("id"), attr, shape_id))
                continue
            if flow is not None and shapes[shape_id] != flow.get(flow_attr):
                errors.append("BPMNEdge '%s': %s '%s' shows '%s', but the flow's %s is '%s'" % (
                    edge.get("id"), attr, shape_id, shapes[shape_id], flow_attr, flow.get(flow_attr)))
    return errors


def iter_tables(root):
    """Yield (description, value) for every non-empty table-type ifl:property."""
    for owner in root.iter():
        ext = owner.find(q(BPMN2, "extensionElements"))
        if ext is None:
            continue
        for prop in ext.findall(q(IFL, "property")):
            key = (prop.findtext("key") or "").strip()
            if key not in TABLE_KEYS:
                continue
            value = prop.findtext("value") or ""
            if value.strip():
                yield "%s '%s', %s" % (local(owner.tag), owner.get("id"), key), value


def check_tables(root):
    errors = []
    for where, value in iter_tables(root):
        try:
            table = ET.fromstring("<table>%s</table>" % value)
        except ET.ParseError as e:
            errors.append("%s: value is not a valid table after one level of unescaping (%s). "
                          "Characters < & > inside a cell must be escaped twice in the .iflw "
                          "(&amp;lt; &amp;amp; &amp;gt;)" % (where, e))
            continue
        for row in table:
            if row.tag != "row" or any(c.tag != "cell" or c.get("id") is None for c in row):
                errors.append("%s: expected only <row><cell id='...'>...</cell></row>, found <%s>" % (
                    where, row.tag))
                break
        if table.text and table.text.strip():
            errors.append("%s: text outside <row> elements" % where)
    return errors


def find_warnings(path):
    """Return a list of warning messages for one .iflw file.

    Warnings describe problems that CPI accepts or that are unverified. A file
    that is not well-formed XML has no warnings (check_file reports it).
    """
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return []
    return (warn_tables(root) + warn_waypoints(root) + warn_overlaps(root)
            + warn_parameters(path, root) + warn_scripts(path, root))


def warn_tables(root):
    warnings = []
    for where, value in iter_tables(root):
        try:
            ET.fromstring("<table>%s</table>" % value)
        except ET.ParseError:
            continue  # reported by check_tables
        if ">" in TAG.sub("", value):
            warnings.append("%s: a '>' inside a cell is escaped only once. Write it as &amp;gt; "
                            "in the .iflw (a single escape is unverified)" % where)
    return warnings


def warn_waypoints(root):
    warnings = []
    bounds = {}
    for shape in root.iter(q(BPMNDI, "BPMNShape")):
        b = shape.find(q(DC, "Bounds"))
        try:
            bounds[shape.get("id")] = tuple(float(b.get(k)) for k in ("x", "y", "width", "height"))
        except (AttributeError, TypeError, ValueError):
            continue
    for edge in root.iter(q(BPMNDI, "BPMNEdge")):
        try:
            points = [(float(w.get("x")), float(w.get("y"))) for w in edge.findall(q(DI, "waypoint"))]
        except (TypeError, ValueError):
            continue
        if not points:
            continue
        for attr in ("sourceElement", "targetElement"):
            rect = bounds.get(edge.get(attr))
            if rect is None:
                continue  # reported by check_diagram
            gap = line_to_rect(points, rect)
            if gap > WAYPOINT_TOLERANCE:
                warnings.append("BPMNEdge '%s': its waypoints do not reach %s '%s' (%.0f away). "
                                "The designer draws the line along the waypoints; move them to the "
                                "edges of the connected shapes" % (edge.get("id"), attr, edge.get(attr), gap))
    return warnings


def warn_overlaps(root):
    nodes = set()
    for process in root.iter(q(BPMN2, "process")):
        nodes |= {c.get("id") for c in process if c.tag not in NON_NODE_TAGS and c.get("id")}
    # Sender and receiver participants; the Integration Process pool (processRef) contains the steps.
    nodes |= {p.get("id") for p in root.iter(q(BPMN2, "participant")) if p.get("processRef") is None}
    shapes = []
    for shape in root.iter(q(BPMNDI, "BPMNShape")):
        if shape.get("bpmnElement") not in nodes:
            continue
        b = shape.find(q(DC, "Bounds"))
        try:
            shapes.append((shape.get("id"), tuple(float(b.get(k)) for k in ("x", "y", "width", "height"))))
        except (AttributeError, TypeError, ValueError):
            continue
    warnings = []
    for i, (id_a, a) in enumerate(shapes):
        for id_b, b in shapes[i + 1:]:
            if rects_overlap(a, b):
                warnings.append("BPMNShape '%s' and '%s' overlap, so one hides the other in the designer. "
                                "Place the new shape in free space; do not move existing shapes" % (id_a, id_b))
    return warnings


def rects_overlap(a, b):
    """True if two rectangles (x, y, width, height) share an area (touching edges do not count)."""
    return (a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and
            a[1] < b[1] + b[3] and b[1] < a[1] + a[3])


def line_to_rect(points, rect):
    """Shortest distance between a polyline and a rectangle (x, y, width, height)."""
    if len(points) == 1:
        return point_to_rect(points[0], rect)
    return min(segment_to_rect(points[i], points[i + 1], rect) for i in range(len(points) - 1))


def point_to_rect(p, rect):
    x, y, w, h = rect
    dx = max(x - p[0], 0.0, p[0] - (x + w))
    dy = max(y - p[1], 0.0, p[1] - (y + h))
    return (dx * dx + dy * dy) ** 0.5


def point_to_segment(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    length2 = ax * ax + ay * ay
    t = 0.0 if length2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / length2))
    dx, dy = p[0] - (a[0] + t * ax), p[1] - (a[1] + t * ay)
    return (dx * dx + dy * dy) ** 0.5


def segments_cross(a, b, c, d):
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    d1, d2 = orient(c, d, a), orient(c, d, b)
    d3, d4 = orient(a, b, c), orient(a, b, d)
    return d1 * d2 <= 0 and d3 * d4 <= 0 and not (d1 == d2 == d3 == d4 == 0)


def segment_to_rect(a, b, rect):
    x, y, w, h = rect
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    if point_to_rect(a, rect) == 0 or point_to_rect(b, rect) == 0:
        return 0.0
    sides = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    if any(segments_cross(a, b, c, d) for c, d in sides):
        return 0.0
    return min([point_to_rect(a, rect), point_to_rect(b, rect)] +
               [point_to_segment(c, a, b) for c in corners])


def used_parameters(root):
    """Return the {{name}} parameters used in ifl:property values, in order of use."""
    names = []
    for prop in root.iter(q(IFL, "property")):
        for name in PARAM.findall(prop.findtext("value") or ""):
            if name not in names:
                names.append(name)
    return names


def resources_dir(iflw_path):
    """Return src/main/resources for a .iflw in src/main/resources/scenarioflows/integrationflow/."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(iflw_path))))


def parameter_paths(iflw_path):
    """Return the paths of parameters.prop and parameters.propdef for a .iflw file."""
    resources = resources_dir(iflw_path)
    return os.path.join(resources, PROP_FILE), os.path.join(resources, PROPDEF_FILE)


def read_prop(path):
    """Return {name: value} from a parameters.prop file (comment lines start with # or !)."""
    params = {}
    with open(path, encoding="utf-8") as f:
        for line in f.read().splitlines():
            line = line.strip()
            if not line or line[0] in "#!":
                continue
            name, _, value = line.partition("=")
            params[name.strip()] = value
    return params


def read_propdef(path):
    """Return the <parameter><name> values of a parameters.propdef file.

    An empty file has no parameters. Raises ET.ParseError if it is not well-formed.
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.strip():
        return []
    root = ET.fromstring(text)
    return [(p.findtext("name") or "").strip() for p in root.iter("parameter")]


def load_parameters(iflw_path):
    """Return [(file name, path, set of names or None, error or None)] for prop and propdef."""
    result = []
    for path, reader in zip(parameter_paths(iflw_path), (read_prop, read_propdef)):
        name = os.path.basename(path)
        if not os.path.isfile(path):
            result.append((name, path, None, None))
            continue
        try:
            result.append((name, path, set(reader(path)), None))
        except ET.ParseError as e:
            result.append((name, path, None, "%s is not well-formed XML: %s" % (path, e)))
    return result


def check_parameters(iflw_path, root):
    used = used_parameters(root)
    errors = []
    for name, path, defined, error in load_parameters(iflw_path):
        if error:
            errors.append(error)
        elif defined is None:
            if used:
                errors.append("%s not found at %s, but the .iflw uses %s" % (
                    name, path, ", ".join("{{%s}}" % u for u in used)))
        else:
            errors += ["parameter {{%s}} is used in the .iflw but not defined in %s" % (u, name)
                       for u in used if u not in defined]
    return errors


def warn_parameters(iflw_path, root):
    used = set(used_parameters(root))
    unused = {}  # parameter -> files that define it
    for name, _, defined, _ in load_parameters(iflw_path):
        for d in defined or ():
            if d not in used:
                unused.setdefault(d, []).append(name)
    return ["parameter '%s' in %s is not used as {{%s}} in the .iflw" % (d, " and ".join(files), d)
            for d, files in sorted(unused.items())]


def properties(el):
    """Return {key: value} of an element's ifl:property children."""
    ext = el.find(q(BPMN2, "extensionElements"))
    if ext is None:
        return {}
    return {(p.findtext("key") or "").strip(): (p.findtext("value") or "").strip()
            for p in ext.findall(q(IFL, "property"))}


def groovy_steps(root):
    """Yield (step id, script value) for every Groovy Script step."""
    for el in root.iter(q(BPMN2, "callActivity")):
        props = properties(el)
        if props.get("activityType") == "Script" and props.get("subActivityType") == "GroovyScript":
            yield el.get("id"), props.get("script", "")


def check_scripts(iflw_path, root):
    script_dir = os.path.join(resources_dir(iflw_path), SCRIPT_DIR)
    errors = []
    for step_id, script in groovy_steps(root):
        if not script:
            errors.append("Groovy Script step '%s' has no script file ('script' is empty)" % step_id)
        elif not os.path.isfile(os.path.join(script_dir, script)):
            errors.append("Groovy Script step '%s': script file '%s' not found in %s "
                          "('script' holds the file name only)" % (step_id, script, script_dir))
    return errors


def warn_scripts(iflw_path, root):
    script_dir = os.path.join(resources_dir(iflw_path), SCRIPT_DIR)
    if not os.path.isdir(script_dir):
        return []
    used = {script for _, script in groovy_steps(root)}
    return ["script file '%s' in %s is not referenced by any Groovy Script step" % (f, script_dir)
            for f in sorted(os.listdir(script_dir)) if f.endswith(".groovy") and f not in used]


def find_iflw(paths):
    found = []
    for p in paths:
        if os.path.isdir(p):
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = sorted(d for d in dirnames if d != ".git")
                found += [os.path.join(dirpath, f) for f in sorted(filenames) if f.endswith(".iflw")]
        else:
            found.append(p)
    return found


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if argv else 2
    missing = [p for p in argv if not os.path.exists(p)]
    if missing:
        for p in missing:
            print("No such file or directory: %s" % p)
        return 2
    files = find_iflw(argv)
    if not files:
        print("No .iflw file found in: %s" % ", ".join(argv))
        return 2
    failed = False
    for path in files:
        errors = check_file(path)
        warnings = find_warnings(path)
        if errors:
            failed = True
            print("%s: %d error(s)" % (path, len(errors)))
            for e in errors:
                print("  - %s" % e)
        elif warnings:
            print("%s: OK, %d warning(s)" % (path, len(warnings)))
        else:
            print("%s: OK" % path)
        for w in warnings:
            print("  - warning: %s" % w)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
