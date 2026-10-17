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


def iflow_files(root, iflow):
    """Return (iflw, prop, propdef) paths of an iFlow folder in the Git Access layout."""
    res = os.path.join(root, iflow, "src", "main", "resources")
    iflw = os.path.join(res, "scenarioflows", "integrationflow", iflow + ".iflw")
    return iflw, os.path.join(res, "parameters.prop"), os.path.join(res, "parameters.propdef")


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
