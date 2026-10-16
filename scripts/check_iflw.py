#!/usr/bin/env python3
"""Minimal consistency check for SAP Cloud Integration .iflw files.

Run it after every local edit, before pushing to the Git repository:

    python3 scripts/check_iflw.py <file.iflw | directory> [...]

A directory is searched recursively for *.iflw files.
Exit code: 0 = no errors, 1 = errors found,
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
- headerTable/propertyTable values, after the one level of unescaping done by
  the XML parser, parse as <row><cell id='...'>...</cell></row> fragments.

Which bpmndi gaps actually make a Pull fail is not known, so every element is
checked strictly. Uses the Python standard library only.
"""

import os
import sys
import xml.etree.ElementTree as ET

BPMN2 = "http://www.omg.org/spec/BPMN/20100524/MODEL"
BPMNDI = "http://www.omg.org/spec/BPMN/20100524/DI"
IFL = "http:///com.sap.ifl.model/Ifl.xsd"

# Table-type ifl:property values that hold an escaped XML fragment.
TABLE_KEYS = ("headerTable", "propertyTable")

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


def check_tables(root):
    errors = []
    for owner in root.iter():
        ext = owner.find(q(BPMN2, "extensionElements"))
        if ext is None:
            continue
        for prop in ext.findall(q(IFL, "property")):
            key = (prop.findtext("key") or "").strip()
            if key not in TABLE_KEYS:
                continue
            value = prop.findtext("value") or ""
            if not value.strip():
                continue
            where = "%s '%s', %s" % (local(owner.tag), owner.get("id"), key)
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
        if errors:
            failed = True
            print("%s: %d error(s)" % (path, len(errors)))
            for e in errors:
                print("  - %s" % e)
        else:
            print("%s: OK" % path)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
