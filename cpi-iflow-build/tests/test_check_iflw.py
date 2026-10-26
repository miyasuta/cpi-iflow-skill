"""Tests for scripts/check_iflw.py.

Fixtures are real .iflw files from https://github.com/miyasuta/cpi-iflow-samples
(the commit hash is part of each file name). Run from the repository root:

    python3 -m unittest discover -s tests
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, "tests", "fixtures")
SCRIPT = os.path.join(ROOT, "scripts", "check_iflw.py")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import check_iflw  # noqa: E402


def fixture(name):
    return os.path.join(FIXTURES, name)


# iFlow folders with parameters.prop / parameters.propdef, in the Git Access layout.
PARAM_FIXTURES = {
    "s03_main_e0da8c4": "S03_ExternalizedParameters",  # externalized in the UI, Configure values set
    "x02_exp_21c75ae": "X02_Sandbox",  # externalized locally (experiment I-1)
    "x02_exp_0d5db9d": "X02_Sandbox",  # the same after a Push from CPI
}

# iFlow folders with a Groovy Script step and src/main/resources/script/script1.groovy.
SCRIPT_FIXTURES = {
    "s02_main_f268336": "S02_GroovyScript",  # built in the UI
    "x02_exp_c058b69": "X02_Sandbox",  # inserted locally (experiment G-2), after a Push from CPI
}


def iflow_files(root, iflow):
    """Return (iflw, prop, propdef) paths of an iFlow folder in the Git Access layout."""
    res = os.path.join(root, iflow, "src", "main", "resources")
    iflw = os.path.join(res, "scenarioflows", "integrationflow", iflow + ".iflw")
    return iflw, os.path.join(res, "parameters.prop"), os.path.join(res, "parameters.propdef")


def copy_iflow(test, name, iflow):
    """Copy a fixture iFlow folder to a temporary directory and return its resources folder."""
    d = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, d)
    shutil.copytree(os.path.join(FIXTURES, name), d, dirs_exist_ok=True)
    return os.path.join(d, iflow, "src", "main", "resources")


def edit_file(test, path, old, new):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    test.assertIn(old, text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new, 1))


def read_fixture(name):
    with open(fixture(name), encoding="utf-8") as f:
        return f.read()


def check_text(text):
    with tempfile.NamedTemporaryFile("w", suffix=".iflw", delete=False, encoding="utf-8") as f:
        f.write(text)
        path = f.name
    try:
        return check_iflw.check_file(path)
    finally:
        os.unlink(path)


class ValidSamplesTest(unittest.TestCase):
    """Files that CPI accepted must produce no errors (no false positives)."""

    def test_s01_on_main_should_have_no_errors(self):
        self.assertEqual(check_iflw.check_file(fixture("s01_main_92c8b77.iflw")), [])

    def test_x01_sandbox_on_exp_should_have_no_errors(self):
        self.assertEqual(check_iflw.check_file(fixture("x01_exp_40a9c8b.iflw")), [])

    def test_locally_inserted_step_with_bpmndi_should_have_no_errors(self):
        self.assertEqual(check_iflw.check_file(fixture("x01_d1b_395e94c.iflw")), [])

    def test_evaluation_baseline_with_empty_certificate_cells_should_have_no_errors(self):
        # clientCertificates is a single row of empty cells in this file.
        self.assertEqual(check_iflw.check_file(fixture("x01_exp_a3c03ec.iflw")), [])

    def test_x01_sandbox_after_evaluations_should_have_no_errors(self):
        self.assertEqual(check_iflw.check_file(fixture("x01_exp_3bff3be.iflw")), [])

    def test_valid_samples_should_have_no_warnings(self):
        for name in ("s01_main_92c8b77.iflw", "x01_exp_40a9c8b.iflw",
                     "x01_exp_a3c03ec.iflw", "x01_exp_3bff3be.iflw"):
            with self.subTest(name=name):
                self.assertEqual(check_iflw.find_warnings(fixture(name)), [])


class KnownFailuresTest(unittest.TestCase):
    """Files that failed in CPI (experiments D-1, C-2, C-2b) must be detected."""

    def test_step_without_bpmndi_should_report_missing_shape_and_edges(self):
        errors = check_iflw.check_file(fixture("x01_d1_56e0a25.iflw"))
        text = "\n".join(errors)
        self.assertIn("CallActivity_Local1", text)
        self.assertIn("no BPMNShape", text)
        self.assertIn("SequenceFlow_Local1", text)
        self.assertIn("no BPMNEdge", text)
        # The existing edge still points at the End event (not re-targeted).
        self.assertTrue(any("BPMNEdge_SequenceFlow_6" in e and "targetElement" in e for e in errors), text)

    def test_unescaped_lt_in_header_table_should_be_reported(self):
        errors = check_iflw.check_file(fixture("x01_c2_a517576.iflw"))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("headerTable", errors[0])
        self.assertIn("CallActivity_5", errors[0])

    def test_unescaped_amp_in_header_table_should_be_reported(self):
        errors = check_iflw.check_file(fixture("x01_c2b_7827ffc.iflw"))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("headerTable", errors[0])


class WarningsTest(unittest.TestCase):
    """Problems that CPI accepts or that are unverified: reported as warnings, not errors."""

    def test_edge_waypoints_left_at_old_target_should_warn(self):
        # Evaluation 2 (Opus): SequenceFlow_Local1 was re-targeted to the new step,
        # but its waypoints still ended at the End event. The designer drew the
        # line to the End event; the iFlow ran correctly.
        path = fixture("x01_eval2_4992e7a.iflw")
        self.assertEqual(check_iflw.check_file(path), [])
        warnings = check_iflw.find_warnings(path)
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("BPMNEdge_SequenceFlow_Local1", warnings[0])
        self.assertIn("BPMNShape_CallActivity_Local2", warnings[0])

    def test_stale_waypoint_that_still_crosses_the_target_should_not_warn(self):
        # BPMNEdge_SequenceFlow_6 ends 59 px beyond its target in many files that
        # CPI saved, but the line passes through the target shape.
        self.assertEqual(check_iflw.find_warnings(fixture("x01_d1b_395e94c.iflw")), [])

    def test_gt_escaped_only_once_in_table_cell_should_warn(self):
        base = read_fixture("x01_exp_a3c03ec.iflw")
        self.assertIn("c&amp;gt;d", base)
        with tempfile.NamedTemporaryFile("w", suffix=".iflw", delete=False, encoding="utf-8") as f:
            f.write(base.replace("c&amp;gt;d", "c&gt;d", 1))
            path = f.name
        try:
            self.assertEqual(check_iflw.check_file(path), [])
            warnings = check_iflw.find_warnings(path)
        finally:
            os.unlink(path)
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("headerTable", warnings[0])
        self.assertIn("CallActivity_5", warnings[0])
        self.assertIn("&amp;gt;", warnings[0])


class SyntheticFailuresTest(unittest.TestCase):
    """Single, targeted corruptions of a valid sample."""

    def setUp(self):
        self.base = read_fixture("x01_exp_40a9c8b.iflw")

    def corrupt(self, old, new):
        self.assertIn(old, self.base)
        return check_text(self.base.replace(old, new, 1))

    def test_malformed_xml_should_be_reported(self):
        errors = self.corrupt("</bpmn2:process>", "")
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("not well-formed", errors[0])

    def test_duplicate_id_should_be_reported(self):
        errors = self.corrupt('id="SequenceFlow_Local1"', 'id="SequenceFlow_6"')
        self.assertTrue(any("duplicate id 'SequenceFlow_6'" in e for e in errors), errors)

    def test_incoming_not_matching_flow_target_should_be_reported(self):
        errors = self.corrupt(
            "<bpmn2:incoming>SequenceFlow_Local1</bpmn2:incoming>",
            "<bpmn2:incoming>SequenceFlow_6</bpmn2:incoming>",
        )
        text = "\n".join(errors)
        self.assertIn("EndEvent_2", text)
        self.assertIn("SequenceFlow_Local1", text)

    def test_sequence_flow_with_unknown_target_should_be_reported(self):
        errors = self.corrupt('targetRef="EndEvent_2"', 'targetRef="EndEvent_9"')
        self.assertTrue(any("EndEvent_9" in e for e in errors), errors)

    def test_missing_participant_shape_should_be_reported(self):
        errors = self.corrupt('bpmnElement="Participant_2"', 'bpmnElement="Participant_9"')
        text = "\n".join(errors)
        self.assertIn("Participant_9", text)
        self.assertIn("participant 'Participant_2' has no BPMNShape", text)

    def test_missing_message_flow_edge_should_be_reported(self):
        errors = self.corrupt('bpmnElement="MessageFlow_4"', 'bpmnElement="MessageFlow_9"')
        text = "\n".join(errors)
        self.assertIn("messageFlow 'MessageFlow_4' has no BPMNEdge", text)

    def test_edge_pointing_at_unknown_shape_should_be_reported(self):
        errors = self.corrupt(
            'sourceElement="BPMNShape_Participant_1"', 'sourceElement="BPMNShape_Participant_9"'
        )
        self.assertTrue(any("BPMNShape_Participant_9" in e for e in errors), errors)

    def test_unescaped_amp_in_client_certificates_should_be_reported(self):
        base = read_fixture("x01_exp_a3c03ec.iflw")
        old = "&lt;cell id='clientCertificate.subjectDN'&gt;&lt;/cell&gt;"
        self.assertIn(old, base)
        errors = check_text(base.replace(
            old, "&lt;cell id='clientCertificate.subjectDN'&gt;CN=a&amp;b&lt;/cell&gt;", 1))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("clientCertificates", errors[0])
        self.assertIn("MessageFlow_4", errors[0])

    def test_property_table_that_is_not_rows_and_cells_should_be_reported(self):
        errors = self.corrupt(
            "&lt;row&gt;&lt;cell id='Action'&gt;Create&lt;/cell&gt;&lt;cell id='Type'&gt;expression",
            "&lt;line&gt;&lt;cell id='Action'&gt;Create&lt;/cell&gt;&lt;cell id='Type'&gt;expression",
        )
        self.assertTrue(any("propertyTable" in e for e in errors), errors)


class ExternalizedParametersTest(unittest.TestCase):
    """{{name}} in the .iflw must be defined in parameters.prop and parameters.propdef."""

    def copy(self, name):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        shutil.copytree(os.path.join(FIXTURES, name), d, dirs_exist_ok=True)
        return iflow_files(d, PARAM_FIXTURES[name])

    def edit(self, path, old, new):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn(old, text)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(old, new, 1))

    def test_samples_with_parameters_should_have_no_errors_or_warnings(self):
        for name, iflow in PARAM_FIXTURES.items():
            with self.subTest(name=name):
                iflw = iflow_files(os.path.join(FIXTURES, name), iflow)[0]
                self.assertEqual(check_iflw.check_file(iflw), [])
                self.assertEqual(check_iflw.find_warnings(iflw), [])

    def test_iflw_without_parameters_or_parameter_files_should_have_no_errors(self):
        # S03 3ef66d2 had no parameters.prop / .propdef and was accepted by CPI.
        self.assertEqual(check_iflw.check_file(fixture("s01_main_92c8b77.iflw")), [])

    def test_name_missing_from_prop_should_be_reported(self):
        iflw, prop, _ = self.copy("x02_exp_21c75ae")
        self.edit(prop, "x02Greeting=from-prop\n", "")
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("x02Greeting", errors[0])
        self.assertIn("parameters.prop", errors[0])

    def test_name_missing_from_propdef_should_be_reported(self):
        iflw, _, propdef = self.copy("s03_main_e0da8c4")
        self.edit(propdef, "<name>s03Body</name>", "<name>s03Other</name>")
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("s03Body", errors[0])
        self.assertIn("parameters.propdef", errors[0])
        warnings = check_iflw.find_warnings(iflw)
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("s03Other", warnings[0])

    def test_unused_parameter_should_warn_but_not_fail(self):
        iflw, _, _ = self.copy("x02_exp_0d5db9d")
        self.edit(iflw, "{{x02Greeting}}", "from-iflw")
        self.assertEqual(check_iflw.check_file(iflw), [])
        warnings = check_iflw.find_warnings(iflw)
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("x02Greeting", warnings[0])
        self.assertIn("not used", warnings[0])

    def test_missing_prop_file_should_be_reported_once(self):
        iflw, prop, _ = self.copy("x02_exp_21c75ae")
        os.remove(prop)
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("parameters.prop", errors[0])
        self.assertIn("not found", errors[0])

    def test_missing_propdef_file_should_be_reported_once(self):
        iflw, _, propdef = self.copy("x02_exp_21c75ae")
        os.remove(propdef)
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("parameters.propdef", errors[0])
        self.assertIn("not found", errors[0])

    def test_empty_prop_and_propdef_files_should_report_each_name(self):
        iflw, prop, propdef = self.copy("x02_exp_21c75ae")
        for path in (prop, propdef):
            open(path, "w").close()
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 4, errors)
        text = "\n".join(errors)
        for name in ("x02Address", "x02Greeting"):
            self.assertIn(name, text)
        self.assertEqual(check_iflw.find_warnings(iflw), [])

    def test_empty_parameter_files_without_parameters_should_have_no_errors(self):
        iflw, prop, propdef = self.copy("x02_exp_21c75ae")
        self.edit(iflw, "{{x02Address}}", "/x02/sandbox")
        self.edit(iflw, "{{x02Greeting}}", "hello")
        for path in (prop, propdef):
            open(path, "w").close()
        self.assertEqual(check_iflw.check_file(iflw), [])
        self.assertEqual(check_iflw.find_warnings(iflw), [])

    def test_missing_parameter_files_without_parameters_should_have_no_errors(self):
        iflw, prop, propdef = self.copy("x02_exp_21c75ae")
        self.edit(iflw, "{{x02Address}}", "/x02/sandbox")
        self.edit(iflw, "{{x02Greeting}}", "hello")
        os.remove(prop)
        os.remove(propdef)
        self.assertEqual(check_iflw.check_file(iflw), [])

    def test_malformed_propdef_should_be_reported(self):
        iflw, _, propdef = self.copy("x02_exp_21c75ae")
        self.edit(propdef, "</parameters>", "")
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("parameters.propdef", errors[0])
        self.assertIn("not well-formed", errors[0])

    def test_prop_without_trailing_newline_should_be_read(self):
        # 0d5db9d: CPI wrote parameters.prop without a final newline.
        _, prop, _ = iflow_files(os.path.join(FIXTURES, "x02_exp_0d5db9d"), "X02_Sandbox")
        with open(prop, encoding="utf-8") as f:
            self.assertFalse(f.read().endswith("\n"))
        self.assertEqual(check_iflw.read_prop(prop),
                         {"x02Address": "/x02/externalized", "x02Greeting": "changed-locally"})

    def test_command_line_should_exit_one_for_undefined_parameter(self):
        iflw, prop, _ = self.copy("x02_exp_21c75ae")
        os.remove(prop)
        folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(iflw)))))
        result = subprocess.run([sys.executable, "-I", SCRIPT, folder], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("parameters.prop", result.stdout)


class GroovyScriptFileTest(unittest.TestCase):
    """The file named in a Groovy Script step's 'script' must exist in src/main/resources/script/."""

    def setup_iflow(self, name):
        iflow = SCRIPT_FIXTURES[name]
        res = copy_iflow(self, name, iflow)
        iflw = os.path.join(res, "scenarioflows", "integrationflow", iflow + ".iflw")
        return iflw, os.path.join(res, "script")

    def test_samples_with_groovy_step_should_have_no_errors_or_warnings(self):
        for name, iflow in SCRIPT_FIXTURES.items():
            with self.subTest(name=name):
                iflw = iflow_files(os.path.join(FIXTURES, name), iflow)[0]
                self.assertEqual(check_iflw.check_file(iflw), [])
                self.assertEqual(check_iflw.find_warnings(iflw), [])

    def test_missing_script_file_should_be_reported(self):
        iflw, script_dir = self.setup_iflow("x02_exp_c058b69")
        os.remove(os.path.join(script_dir, "script1.groovy"))
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("CallActivity_Local2", errors[0])
        self.assertIn("script1.groovy", errors[0])
        self.assertIn("not found", errors[0])

    def test_script_name_pointing_at_other_file_should_be_reported(self):
        iflw, _ = self.setup_iflow("s02_main_f268336")
        edit_file(self, iflw, "<value>script1.groovy</value>", "<value>script2.groovy</value>")
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("script2.groovy", errors[0])
        warnings = check_iflw.find_warnings(iflw)
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("script1.groovy", warnings[0])
        self.assertIn("not referenced", warnings[0])

    def test_empty_script_value_should_be_reported(self):
        # f7c70d0: the UI saved a Groovy step without a script; what Pull does with it is unverified.
        iflw, _ = self.setup_iflow("s02_main_f268336")
        edit_file(self, iflw, "<value>script1.groovy</value>", "<value/>")
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("CallActivity_5", errors[0])
        self.assertIn("no script file", errors[0])

    def test_script_value_with_path_should_be_reported(self):
        # The samples hold the file name only; script/script1.groovy is not a file in script/script/.
        iflw, _ = self.setup_iflow("x02_exp_c058b69")
        edit_file(self, iflw, "<value>script1.groovy</value>", "<value>script/script1.groovy</value>")
        errors = check_iflw.check_file(iflw)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("script/script1.groovy", errors[0])

    def test_unreferenced_groovy_file_should_warn_but_not_fail(self):
        iflw, script_dir = self.setup_iflow("x02_exp_c058b69")
        with open(os.path.join(script_dir, "unused.groovy"), "w", encoding="utf-8") as f:
            f.write("// not used\n")
        self.assertEqual(check_iflw.check_file(iflw), [])
        warnings = check_iflw.find_warnings(iflw)
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("unused.groovy", warnings[0])

    def test_iflow_without_groovy_step_or_script_folder_should_have_no_errors(self):
        iflw = iflow_files(os.path.join(FIXTURES, "x02_exp_0d5db9d"), "X02_Sandbox")[0]
        self.assertEqual(check_iflw.check_file(iflw), [])
        self.assertEqual(check_iflw.find_warnings(iflw), [])

    def test_command_line_should_exit_one_for_missing_script_file(self):
        iflw, script_dir = self.setup_iflow("s02_main_f268336")
        os.remove(os.path.join(script_dir, "script1.groovy"))
        result = subprocess.run([sys.executable, "-I", SCRIPT, iflw], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("script1.groovy", result.stdout)


class OverlappingShapesTest(unittest.TestCase):
    """Shapes of steps, events and sender/receiver must not overlap (warning only)."""

    EVAL3 = os.path.join("x01_exp_83d2f85", "X01_Sandbox", "src", "main", "resources",
                         "scenarioflows", "integrationflow", "S01_ContentModifier.iflw")

    def test_real_samples_should_have_no_overlap_warnings(self):
        paths = [fixture(n) for n in ("s01_main_92c8b77.iflw", "x01_exp_40a9c8b.iflw",
                                      "x01_d1b_395e94c.iflw", "x01_eval2_4992e7a.iflw",
                                      "x01_exp_3bff3be.iflw", "x01_exp_a3c03ec.iflw")]
        paths += [iflow_files(os.path.join(FIXTURES, n), i)[0]
                  for n, i in list(PARAM_FIXTURES.items()) + list(SCRIPT_FIXTURES.items())]
        paths.append(fixture(self.EVAL3))
        for path in paths:
            with self.subTest(path=os.path.relpath(path, FIXTURES)):
                warnings = check_iflw.find_warnings(path)
                self.assertFalse([w for w in warnings if "overlap" in w], warnings)

    def test_new_step_hidden_under_a_snapped_back_step_should_warn(self):
        # Evaluation 3 (83d2f85) moved Set evalProp (CallActivity_Local2) from x=682 to 842
        # and put the new Groovy Script 1 (CallActivity_Local3) at 682. CPI put the existing
        # shapes back, so the new step lay exactly under Set evalProp and could not be seen.
        res = copy_iflow(self, "x01_exp_83d2f85", "X01_Sandbox")
        iflw = os.path.join(res, "scenarioflows", "integrationflow", "S01_ContentModifier.iflw")
        edit_file(self, iflw,
                  '<dc:Bounds height="60.0" width="100.0" x="842.0" y="110.0"/>',
                  '<dc:Bounds height="60.0" width="100.0" x="682.0" y="110.0"/>')
        self.assertEqual(check_iflw.check_file(iflw), [])
        warnings = check_iflw.find_warnings(iflw)
        overlaps = [w for w in warnings if "overlap" in w]
        self.assertEqual(len(overlaps), 1, warnings)
        self.assertIn("BPMNShape_CallActivity_Local2", overlaps[0])
        self.assertIn("BPMNShape_CallActivity_Local3", overlaps[0])

    def test_step_overlapping_end_event_should_warn(self):
        base = read_fixture("x01_exp_40a9c8b.iflw")
        old = 'bpmnElement="EndEvent_2" id="BPMNShape_EndEvent_2">'
        self.assertIn(old, base)
        # Put the End event inside the last step's shape.
        import re
        m = re.search(r'(bpmnElement="EndEvent_2" id="BPMNShape_EndEvent_2">\s*<dc:Bounds [^>]*/>)', base)
        self.assertIsNotNone(m)
        step = re.search(r'bpmnElement="CallActivity_Local1"[^>]*>\s*<dc:Bounds height="60.0" width="100.0" '
                         r'x="([0-9.]+)" y="([0-9.]+)"/>', base)
        self.assertIsNotNone(step)
        moved = re.sub(r'x="[0-9.]+" y="[0-9.]+"', 'x="%s" y="%s"' % step.groups(), m.group(1))
        with tempfile.NamedTemporaryFile("w", suffix=".iflw", delete=False, encoding="utf-8") as f:
            f.write(base.replace(m.group(1), moved, 1))
            path = f.name
        try:
            warnings = check_iflw.find_warnings(path)
        finally:
            os.unlink(path)
        overlaps = [w for w in warnings if "overlap" in w]
        self.assertEqual(len(overlaps), 1, warnings)
        self.assertIn("BPMNShape_EndEvent_2", overlaps[0])

    def test_shapes_inside_the_process_pool_should_not_warn(self):
        # Every step lies inside Participant_Process_1; that is not an overlap.
        warnings = check_iflw.find_warnings(fixture("s01_main_92c8b77.iflw"))
        self.assertEqual(warnings, [])


class RequestReplyTest(unittest.TestCase):
    """A Request Reply step (serviceTask) and the HTTP receiver message flow from it."""

    # S05 built in the UI (receiver Participant_7, unused Participant_2 left over);
    # X05 written locally and connected to the existing Participant_2 (L-1), then
    # with a changed Address and Query (L-2).
    SAMPLES = ("s05_main_cc4ce46.iflw", "x05_exp_c3ddf1c.iflw", "x05_exp_1b378b8.iflw")

    def setUp(self):
        self.base = read_fixture("x05_exp_1b378b8.iflw")

    def corrupt(self, old, new):
        self.assertIn(old, self.base)
        return check_text(self.base.replace(old, new, 1))

    def test_request_reply_samples_should_have_no_errors_or_warnings(self):
        for name in self.SAMPLES:
            with self.subTest(name=name):
                self.assertEqual(check_iflw.check_file(fixture(name)), [])
                self.assertEqual(check_iflw.find_warnings(fixture(name)), [])

    def test_request_reply_step_without_shape_should_be_reported(self):
        errors = self.corrupt('bpmnElement="ServiceTask_5" id="BPMNShape_ServiceTask_5"',
                              'bpmnElement="ServiceTask_9" id="BPMNShape_ServiceTask_5"')
        self.assertIn("node 'ServiceTask_5' has no BPMNShape", "\n".join(errors))

    def test_request_reply_step_with_wrong_incoming_should_be_reported(self):
        errors = self.corrupt("<bpmn2:incoming>SequenceFlow_3</bpmn2:incoming>\n"
                              "            <bpmn2:outgoing>SequenceFlow_6",
                              "<bpmn2:incoming>SequenceFlow_6</bpmn2:incoming>\n"
                              "            <bpmn2:outgoing>SequenceFlow_6")
        text = "\n".join(errors)
        self.assertIn("ServiceTask_5", text)
        self.assertIn("SequenceFlow_3", text)

    def test_receiver_flow_from_unknown_step_should_be_reported(self):
        errors = self.corrupt('sourceRef="ServiceTask_5" targetRef="Participant_2"',
                              'sourceRef="ServiceTask_9" targetRef="Participant_2"')
        self.assertIn("messageFlow 'MessageFlow_8': sourceRef 'ServiceTask_9' does not exist",
                      "\n".join(errors))

    def test_receiver_flow_without_edge_should_be_reported(self):
        errors = self.corrupt('bpmnElement="MessageFlow_8" id="BPMNEdge_MessageFlow_8"',
                              'bpmnElement="MessageFlow_9" id="BPMNEdge_MessageFlow_8"')
        self.assertIn("messageFlow 'MessageFlow_8' has no BPMNEdge", "\n".join(errors))

    def test_receiver_edge_to_another_participant_should_be_reported(self):
        # The receiver flow targets Participant_2; its edge must end at that participant's shape.
        errors = self.corrupt('targetElement="BPMNShape_Participant_2"',
                              'targetElement="BPMNShape_Participant_1"')
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("BPMNEdge_MessageFlow_8", errors[0])
        self.assertIn("Participant_2", errors[0])

    def test_receiver_overlapping_the_request_reply_step_should_warn(self):
        # Move the receiver Participant_2 onto the Request Reply step.
        old = '<dc:Bounds height="140.0" width="100.0" x="900.0" y="100.0"/>'
        self.assertIn(old, self.base)
        with tempfile.NamedTemporaryFile("w", suffix=".iflw", delete=False, encoding="utf-8") as f:
            f.write(self.base.replace(old, '<dc:Bounds height="140.0" width="100.0" x="412.0" y="100.0"/>', 1))
            path = f.name
        try:
            errors = check_iflw.check_file(path)
            warnings = check_iflw.find_warnings(path)
        finally:
            os.unlink(path)
        self.assertEqual(errors, [])
        overlaps = [w for w in warnings if "overlap" in w]
        self.assertEqual(len(overlaps), 1, warnings)
        self.assertIn("BPMNShape_ServiceTask_5", overlaps[0])
        self.assertIn("BPMNShape_Participant_2", overlaps[0])


class HttpReceiverSettingsTest(unittest.TestCase):
    """Method, Authentication and Credential Name of an HTTP receiver message flow."""

    # S05 changed in the UI to OAuth2 Client Credentials and POST; X05 changed
    # locally to OAuth2 Client Credentials (N-1), then to POST (N-2).
    SAMPLES = ("s05_main_5461d27.iflw", "x05_exp_ba66a4e.iflw", "x05_exp_5b2d746.iflw")

    def setUp(self):
        self.base = read_fixture("x05_exp_5b2d746.iflw")

    def warnings_for(self, old, new):
        self.assertIn(old, self.base)
        with tempfile.NamedTemporaryFile("w", suffix=".iflw", delete=False, encoding="utf-8") as f:
            f.write(self.base.replace(old, new, 1))
            path = f.name
        try:
            self.assertEqual(check_iflw.check_file(path), [])
            return check_iflw.find_warnings(path)
        finally:
            os.unlink(path)

    def test_authentication_and_post_samples_should_have_no_errors_or_warnings(self):
        for name in self.SAMPLES:
            with self.subTest(name=name):
                self.assertEqual(check_iflw.check_file(fixture(name)), [])
                self.assertEqual(check_iflw.find_warnings(fixture(name)), [])

    def test_authentication_value_not_in_samples_should_warn(self):
        # The UI writes the display name with spaces; a guessed value must be caught.
        warnings = self.warnings_for("<value>OAuth2 Client Credentials</value>",
                                     "<value>OAuth2ClientCredentials</value>")
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("MessageFlow_8", warnings[0])
        self.assertIn("authenticationMethod 'OAuth2ClientCredentials'", warnings[0])

    def test_oauth2_client_credentials_without_credential_name_should_warn(self):
        warnings = self.warnings_for("<value>s05-oauth-client</value>", "<value/>")
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("MessageFlow_8", warnings[0])
        self.assertIn("credentialName", warnings[0])

    def test_method_not_in_samples_should_warn(self):
        warnings = self.warnings_for("<value>POST</value>", "<value>PUT</value>")
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("httpMethod 'PUT'", warnings[0])

    def test_get_without_authentication_should_not_warn(self):
        self.assertEqual(check_iflw.find_warnings(fixture("x05_exp_1b378b8.iflw")), [])


class RouterTest(unittest.TestCase):
    """A Router (exclusiveGateway), its default route and the conditions of its routes."""

    # S06 built in the UI; X07 written locally with two routes (M-1), then a third
    # route without componentVersion and cmdVariantUri (M-2).
    SAMPLES = ("s06_main_87baf40.iflw", "x07_exp_6ef7611.iflw", "x07_exp_45bac88.iflw")

    def setUp(self):
        self.base = read_fixture("x07_exp_45bac88.iflw")

    def edited(self, old, new):
        self.assertIn(old, self.base)
        with tempfile.NamedTemporaryFile("w", suffix=".iflw", delete=False, encoding="utf-8") as f:
            f.write(self.base.replace(old, new, 1))
            path = f.name
        try:
            return check_iflw.check_file(path), check_iflw.find_warnings(path)
        finally:
            os.unlink(path)

    def test_router_samples_should_have_no_errors_or_warnings(self):
        for name in self.SAMPLES:
            with self.subTest(name=name):
                self.assertEqual(check_iflw.check_file(fixture(name)), [])
                self.assertEqual(check_iflw.find_warnings(fixture(name)), [])

    def test_default_naming_a_flow_that_does_not_leave_the_router_should_be_reported(self):
        errors, _ = self.edited('default="SequenceFlow_11"', 'default="SequenceFlow_9"')
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("ExclusiveGateway_5", errors[0])
        self.assertIn("SequenceFlow_9", errors[0])

    def test_default_naming_an_unknown_flow_should_be_reported(self):
        errors, _ = self.edited('default="SequenceFlow_11"', 'default="SequenceFlow_99"')
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("SequenceFlow_99", errors[0])

    def test_route_without_condition_that_is_not_the_default_should_warn(self):
        errors, warnings = self.edited(
            "<bpmn2:conditionExpression id=\"FormalExpression_SequenceFlow_16_1792313248275\" "
            "xsi:type=\"bpmn2:tFormalExpression\">${header.X-X07-Route} = 'b'</bpmn2:conditionExpression>", "")
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("SequenceFlow_16", warnings[0])
        self.assertIn("condition", warnings[0])

    def test_router_without_default_route_should_warn(self):
        errors, warnings = self.edited('default="SequenceFlow_11" ', "")
        self.assertEqual(errors, [])
        self.assertTrue(any("ExclusiveGateway_5" in w and "default" in w for w in warnings), warnings)

    def test_default_route_with_condition_should_warn(self):
        errors, warnings = self.edited('default="SequenceFlow_11"', 'default="SequenceFlow_16"')
        self.assertEqual(errors, [])
        text = "\n".join(warnings)
        self.assertIn("SequenceFlow_16", text)  # the default route has a condition
        self.assertIn("SequenceFlow_11", text)  # a non-default route has no condition


class ExceptionSubprocessTest(unittest.TestCase):
    """Nodes, flows and shapes inside an Exception Subprocess (bpmn2:subProcess)."""

    # S04 built in the UI; X04 written locally (experiment K-1).
    SAMPLES = {"s04_main_f34d292": "S04_ExceptionSubprocess", "x04_exp_111453a": "X04_Sandbox"}

    def corrupt(self, old, new):
        """Edit a copy of the X04 sample and return (errors, warnings)."""
        res = copy_iflow(self, "x04_exp_111453a", "X04_Sandbox")
        iflw = os.path.join(res, "scenarioflows", "integrationflow", "X04_Sandbox.iflw")
        edit_file(self, iflw, old, new)
        return check_iflw.check_file(iflw), check_iflw.find_warnings(iflw)

    def test_exception_subprocess_samples_should_have_no_errors_or_warnings(self):
        for name, iflow in self.SAMPLES.items():
            path = iflow_files(os.path.join(FIXTURES, name), iflow)[0]
            with self.subTest(name=name):
                self.assertEqual(check_iflw.check_file(path), [])
                self.assertEqual(check_iflw.find_warnings(path), [])

    def test_step_inside_subprocess_without_shape_should_be_reported(self):
        errors, _ = self.corrupt('bpmnElement="CallActivity_Local2" id="BPMNShape_CallActivity_Local2"',
                                 'bpmnElement="SubProcess_Local1" id="BPMNShape_CallActivity_Local2"')
        self.assertIn("node 'CallActivity_Local2' has no BPMNShape", "\n".join(errors))

    def test_flow_inside_subprocess_without_edge_should_be_reported(self):
        errors, _ = self.corrupt('bpmnElement="SequenceFlow_Local3" id="BPMNEdge_SequenceFlow_Local3"',
                                 'bpmnElement="SequenceFlow_Local2" id="BPMNEdge_SequenceFlow_Local3"')
        self.assertIn("sequenceFlow 'SequenceFlow_Local3' has no BPMNEdge", "\n".join(errors))

    def test_wrong_incoming_inside_subprocess_should_be_reported(self):
        errors, _ = self.corrupt("<bpmn2:incoming>SequenceFlow_Local3</bpmn2:incoming>",
                                 "<bpmn2:incoming>SequenceFlow_Local2</bpmn2:incoming>")
        text = "\n".join(errors)
        self.assertIn("EndEvent_Local1", text)
        self.assertIn("SequenceFlow_Local3", text)

    def test_flow_from_subprocess_to_main_flow_should_be_reported(self):
        # The subprocess is not connected to the main flow; a flow inside it must stay inside it.
        errors, _ = self.corrupt(
            'id="SequenceFlow_Local3" sourceRef="CallActivity_Local2" targetRef="EndEvent_Local1"',
            'id="SequenceFlow_Local3" sourceRef="CallActivity_Local2" targetRef="EndEvent_2"')
        self.assertIn("sequenceFlow 'SequenceFlow_Local3': targetRef 'EndEvent_2' is in another process",
                      "\n".join(errors))

    def test_overlapping_shapes_inside_subprocess_should_warn(self):
        # Put the Content Modifier onto the Error Start event.
        errors, warnings = self.corrupt('<dc:Bounds height="60.0" width="100.0" x="431.0" y="206.0"/>',
                                        '<dc:Bounds height="60.0" width="100.0" x="311.0" y="206.0"/>')
        self.assertEqual(errors, [])
        overlaps = [w for w in warnings if "overlap" in w]
        self.assertEqual(len(overlaps), 1, warnings)
        self.assertIn("BPMNShape_StartEvent_Local1", overlaps[0])
        self.assertIn("BPMNShape_CallActivity_Local2", overlaps[0])

    def test_subprocess_overlapping_a_main_flow_step_should_warn(self):
        # Move the subprocess up onto the Groovy Script step of the main flow.
        _, warnings = self.corrupt('<dc:Bounds height="80.0" width="400.0" x="290.0" y="196.0"/>',
                                   '<dc:Bounds height="80.0" width="400.0" x="290.0" y="150.0"/>')
        overlaps = [w for w in warnings if "overlap" in w]
        self.assertTrue(any("BPMNShape_SubProcess_Local1" in w and "BPMNShape_CallActivity_Local1" in w
                            for w in overlaps), warnings)
        self.assertFalse([w for w in overlaps if "BPMNShape_SubProcess_Local1" in w
                          and ("Local2" in w or "EndEvent_Local1" in w or "StartEvent_Local1" in w)],
                         warnings)


class CommandLineTest(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True
        )

    def test_valid_file_should_exit_zero(self):
        result = self.run_script(fixture("s01_main_92c8b77.iflw"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)

    def test_invalid_file_should_exit_one(self):
        result = self.run_script(fixture("x01_c2_a517576.iflw"))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("headerTable", result.stdout)

    def test_directory_should_check_every_iflw_below_it(self):
        with tempfile.TemporaryDirectory() as d:
            sub = os.path.join(d, "a", "b")
            os.makedirs(sub)
            with open(os.path.join(sub, "x.iflw"), "w", encoding="utf-8") as f:
                f.write(read_fixture("x01_c2b_7827ffc.iflw"))
            result = self.run_script(d)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("x.iflw", result.stdout)

    def test_warnings_only_should_exit_zero_and_print_them(self):
        result = self.run_script(fixture("x01_eval2_4992e7a.iflw"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("warning", result.stdout)
        self.assertIn("BPMNEdge_SequenceFlow_Local1", result.stdout)

    def test_missing_path_should_exit_two_without_traceback(self):
        with tempfile.TemporaryDirectory() as d:
            missing = os.path.join(d, "no-such.iflw")
            result = self.run_script(missing)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("no-such.iflw", result.stdout + result.stderr)

    def test_no_iflw_found_should_exit_two(self):
        with tempfile.TemporaryDirectory() as d:
            result = self.run_script(d)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
