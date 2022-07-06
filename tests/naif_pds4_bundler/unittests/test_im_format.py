"""Unit tests for format differences for PDS4 Information Models.

The usage of different IM will lead to changes in the format and
values of the PDS4 artifacts. This test family checks that these
changes are as expected.
"""
import os
import shutil

from pds.naif_pds4_bundler.__main__ import main


def post_setup(self):
    """Setup Test.

    This method will be executed before each test function.
    """
    self.faucet = "list"
    self.config = "../config/insight.xml"
    self.updated_config = "working/insight.xml"

    os.mkdir("kernels/lsk")
    shutil.copy2("../data/kernels/lsk/naif0012.tls", "kernels/lsk")


def test_im_format(self):
    """IM input format test.

    Tests if the IM input format in the NPB configuration file
    is adequate.

    Test is successful if the following error message is provided::

        RuntimeError: PDS4 Information Model 1.A.0.0 format from configuration is incorrect.
    """
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "<information_model>1.5.0.0</information_model>" in line:
                    n.write("<information_model>1.A.0.0" "</information_model>\n")
                else:
                    n.write(line)

    with self.assertRaises(RuntimeError):
        main(self.updated_config, faucet=self.faucet, silent=True)


def test_im_xml_incoherent(self):
    """IM input configuration incoherence test.

    Tests if the IM input in the NPB configuration file is coherent
    with other elements of the configuration.

    Test is successful if the following error message is provided::

        RuntimeError: PDS4 Information Model 1600 is incoherent with the XML Model version: http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.sch.
    """
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "<information_model>1.5.0.0</information_model>" in line:
                    n.write("<information_model>1.6.0.0</information_model>\n")
                else:
                    n.write(line)

    with self.assertRaises(RuntimeError):
        main(self.updated_config, faucet=self.faucet, silent=True)


def test_im_schema_incoherent(self):
    """Schema input configuration incoherence test.

    Tests if the schema input in the NPB configuration file is coherent
    with other elements of the configuration.

    Test is successful if the following error message is provided::

        RuntimeError: PDS4 Information Model 1500 is incoherent with the Schema location: http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1A00.xsd.
    """
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if (
                    "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                    "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd</schema_location>"
                    in line
                ):
                    n.write(
                        "<schema_location>http://pds.nasa.gov/pds4/pds/"
                        "v1 http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1A00.xsd</schema_location>\n"
                    )
                else:
                    n.write(line)

    with self.assertRaises(RuntimeError):
        main(self.updated_config, faucet=self.faucet, silent=True)


def test_im_version_ascii(self):
    """IM version test.

    Tests if the IM version in the NPB configuration file is coherent
    with other elements of the configuration.
    """
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "<information_model>1.5.0.0</information_model>" in line:
                    n.write("<information_model>1.16.0.0" "</information_model>\n")
                elif (
                    "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                    "PDS4_PDS_1500.sch</xml_model>\n" in line
                ):
                    n.write(
                        "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1G00.sch</xml_model>\n"
                    )
                elif (
                    "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                    "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd</schema_location>"
                    in line
                ):
                    n.write(
                        "<schema_location>http://pds.nasa.gov/pds4/pds/"
                        "v1 http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1G00.xsd</schema_location>\n"
                    )
                else:
                    n.write(line)

    main(self.updated_config, faucet=self.faucet, silent=True)


def test_im_version_ascii_incorrect(self):
    """IM version incoherent test.

    Tests if the IM version in the NPB configuration file is coherent
    with other elements of the configuration.

    Test is successful if the following error message is provided::

        RuntimeError: PDS4 Information Model AGBK is incoherent with the XML Model version: http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1G00.sch.
    """
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "<information_model>1.5.0.0</information_model>" in line:
                    n.write("<information_model>10.16.11.20" "</information_model>\n")
                elif (
                    "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                    "PDS4_PDS_1500.sch</xml_model>\n" in line
                ):
                    n.write(
                        "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1G00.sch</xml_model>\n"
                    )
                elif (
                    "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                    "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd</schema_location>"
                    in line
                ):
                    n.write(
                        "<schema_location>http://pds.nasa.gov/pds4/pds/"
                        "v1 http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1G00.xsd</schema_location>\n"
                    )
                else:
                    n.write(line)

    with self.assertRaises(RuntimeError):
        main(self.updated_config, faucet=self.faucet, silent=True)


def test_im_templates_16(self):
    """Test appropriate selection of templates for the IM for 1.16.0.0."""
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "<information_model>1.5.0.0</information_model>" in line:
                    n.write("<information_model>1.19.0.0</information_model>\n")
                elif (
                    "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                    "PDS4_PDS_1500.sch</xml_model>" in line
                ):
                    n.write(
                        "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1J00.sch</xml_model>\n"
                    )
                elif (
                    "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                    "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd</schema_location>"
                    in line
                ):
                    n.write(
                        "<schema_location>http://pds.nasa.gov/pds4/pds/"
                        "v1 http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1J00.xsd</schema_location>\n"
                    )
                else:
                    n.write(line)

    main(self.updated_config, faucet=self.faucet, silent=True, log=True)

    line_in_log = False
    with open("working/insight_release_01.log", "r") as log:
        for line in log:
            if (
                "Label templates will use the ones from information model 1.16.0.0."
                in line
            ):
                line_in_log = True

    self.assertTrue(line_in_log)


def test_im_templates_14(self):
    """Test appropriate selection of templates for the IM for 1.14.0.0."""
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "<information_model>1.5.0.0</information_model>" in line:
                    n.write("<information_model>1.15.0.0</information_model>\n")
                elif (
                    "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                    "PDS4_PDS_1500.sch</xml_model>" in line
                ):
                    n.write(
                        "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1F00.sch</xml_model>\n"
                    )
                elif (
                    "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                    "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd</schema_location>"
                    in line
                ):
                    n.write(
                        "<schema_location>http://pds.nasa.gov/pds4/pds/"
                        "v1 http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1F00.xsd</schema_location>\n"
                    )
                else:
                    n.write(line)

    main(self.updated_config, faucet=self.faucet, silent=True, log=True)

    line_in_log = False
    with open("working/insight_release_01.log", "r") as log:
        for line in log:
            if (
                "Label templates will use the ones from information model 1.14.0.0."
                in line
            ):
                line_in_log = True

    self.assertTrue(line_in_log)


def test_im_templates_11(self):
    """Test appropriate selection of templates for the IM for 1.11.0.0."""
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "<information_model>1.5.0.0</information_model>" in line:
                    n.write("<information_model>1.12.0.0</information_model>\n")
                elif (
                    "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                    "PDS4_PDS_1500.sch</xml_model>\n" in line
                ):
                    n.write(
                        "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1C00.sch</xml_model>\n"
                    )
                elif (
                    "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                    "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd</schema_location>"
                    in line
                ):
                    n.write(
                        "<schema_location>http://pds.nasa.gov/pds4/pds/"
                        "v1 http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1C00.xsd</schema_location>\n"
                    )
                else:
                    n.write(line)

    main(self.updated_config, faucet=self.faucet, silent=True, log=True)

    line_in_log = False
    with open("working/insight_release_01.log", "r") as log:
        for line in log:
            if (
                "Label templates will use the ones from information model 1.11.0.0."
                in line
            ):
                line_in_log = True

    self.assertTrue(line_in_log)


def test_im_templates(self):
    """Test appropriate selection of templates for the IM for 1.11.0.0."""
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "<information_model>1.5.0.0</information_model>" in line:
                    n.write("<information_model>1.11.0.0</information_model>\n")
                elif (
                    "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                    "PDS4_PDS_1500.sch</xml_model>\n" in line
                ):
                    n.write(
                        "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1B00.sch</xml_model>\n"
                    )
                elif (
                    "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                    "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd</schema_location>"
                    in line
                ):
                    n.write(
                        "<schema_location>http://pds.nasa.gov/pds4/pds/"
                        "v1 http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1B00.xsd</schema_location>\n"
                    )
                else:
                    n.write(line)

    main(self.updated_config, faucet=self.faucet, silent=True, log=True)

    line_in_log = False
    with open("working/insight_release_01.log", "r") as log:
        for line in log:
            if (
                "Label templates will use the ones from information model 1.11.0.0."
                in line
            ):
                line_in_log = True

    self.assertTrue(line_in_log)


def test_im_schema_resolution(self):
    """Test determination of xml model and schema location from IM."""
    post_setup(self)
    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "<xml_model>" in line:
                    pass
                elif "<schema_location>" in line:
                    pass
                else:
                    n.write(line)

    main(self.updated_config, faucet=self.faucet, silent=True, log=True)
