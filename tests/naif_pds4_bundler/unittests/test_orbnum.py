"""Functional tests for the List generator.
"""
import os
import shutil
import unittest
from unittest import TestCase

from naif_pds4_bundler.__main__ import main


class TestOrbnum(TestCase):
    """
    Test family for the plan generation.
    """

    @classmethod
    def setUpClass(cls):
        """
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ["working", "staging", "final", "kernels", "misc", "maven"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.faucet = "staging"
        cls.silent = True

    def setUp(self):
        """
        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ["working", "staging", "maven"]
        for dir in dirs:
            os.mkdir(dir)

        shutil.copytree("../data/kernels", "kernels")
        shutil.copytree("../data/misc", "misc")

        dirs = [
            "maven/maven_spice",
            "maven/maven_spice/spice_kernels",
            "maven/maven_spice/spice_kernels/spk",
            "maven/maven_spice/miscellaneous",
            "maven/maven_spice/miscellaneous/orbnum",
        ]
        for dir in dirs:
            os.mkdir(dir)

    def tearDown(self):
        """
        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "final", "kernels", "misc", "maven"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        try:
            os.remove("working/maven_orbnum.plan")
        except:
            pass

    def test_pds4_orbnum_coverage_user_spk(self):
        """
        Test for meta-kernel configuration loading error cases.
        """
        config = "../config/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401_v1.orb")
            p.write("\nmaven_orb_rec_210101_210401_v1.nrb")

        main(config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_coverage_increment_spk(self):
        """
        Testcase for when the readme file is not present.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401_v2.bsp")
            p.write("\nmaven_orb_rec_210101_210401_v1.orb")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if (
                        '<kernel cutoff="True">../data/kernels/spk/'
                        "maven_orb_rec_210101_210401_v2.bsp</kernel>" in line
                    ):
                        n.write(
                            "                "
                            '<kernel cutoff="True">maven_orb_rec_[0-9]{6}_[0-9]{6}_'
                            "v[0-9].bsp</kernel>\n"
                        )
                    else:
                        n.write(line)

        main(updated_config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_coverage_archived_spk(self):
        """
        Testcase for when the readme file is not present.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(plan, "w") as p:
            p.write("\nmaven_orb_rec_210101_210401_v1.orb")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if (
                        '<kernel cutoff="True">../data/kernels/spk/'
                        "maven_orb_rec_210101_210401_v2.bsp</kernel>" in line
                    ):
                        n.write(
                            '<kernel cutoff="True">maven_orb_rec_[0-9]{6}_[0-9]{6}_'
                            "v[0-9].bsp</kernel>\n"
                        )
                    else:
                        n.write(line)

        shutil.copy2(
            "../data/kernels/spk/maven_orb_rec_210101_210401_v2.bsp",
            "maven/maven_spice/spice_kernels/spk/",
        )

        main(updated_config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_coverage_lookup_table(self):
        """
        Testcase for when the readme file is not present.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(plan, "w") as p:
            p.write("\nmaven_orb_rec_210101_210401_v1.orb")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if (
                        '<kernel cutoff="True">../data/kernels/spk/'
                        "maven_orb_rec_210101_210401_v2.bsp</kernel>" in line
                    ):
                        n.write(
                            "<lookup_table>\n"
                            "  <file name="
                            '"maven_orb_rec_210101_210401_v1.orb">\n'
                            "     <start>2021-01-01T00:00:00.000Z</start>\n"
                            "     <finish>2021-04-01T01:00:00.000Z</finish>\n"
                            "  </file>\n"
                            "</lookup_table>\n"
                        )
                    else:
                        n.write(line)

        main(updated_config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_coverage_lookup_table_multiple(self):
        """
        Testcase for when the readme file is not present.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(plan, "w") as p:
            p.write("\nmaven_orb_rec_210101_210401_v1.orb")
            p.write("\nmaven_orb_rec_210101_210402_v1.orb")

        shutil.copy(
            "../data/misc/orbnum/maven_orb_rec_210101_210401_v1.orb",
            "misc/orbnum/maven_orb_rec_210101_210402_v1.orb",
        )

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if (
                        '<kernel cutoff="True">../data/kernels/spk/'
                        "maven_orb_rec_210101_210401_v2.bsp</kernel>" in line
                    ):
                        n.write(
                            "<lookup_table>\n"
                            "  <file name="
                            '"maven_orb_rec_210101_210401_v1.orb">\n'
                            "     <start>2021-01-01T00:00:00.000Z</start>\n"
                            "     <finish>2021-04-01T01:00:00.000Z</finish>\n"
                            "  </file>\n"
                            "  <file name="
                            '"maven_orb_rec_210101_210402_v1.orb">\n'
                            "     <start>2021-01-01T00:00:00.000Z</start>\n"
                            "     <finish>2021-04-02T01:00:00.000Z</finish>\n"
                            "  </file>\n"
                            "</lookup_table>\n"
                        )
                    else:
                        n.write(line)

        main(updated_config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_coverage_estimate(self):
        """
        Test for meta-kernel configuration loading error cases.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if (
                        '<kernel cutoff="True">../data/kernels/spk/'
                        "maven_orb_rec_210101_210401_v2.bsp</kernel>" in line
                    ):
                        n.write("")
                    else:
                        n.write(line)

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401_v1.orb")

        main(updated_config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_with_former_version(self):
        """
        Test for meta-kernel configuration loading error cases.
        """
        config = "../config/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401_v2.orb")

        #
        # Test preparation
        #
        with open(
            "maven/maven_spice/miscellaneous/orbnum/"
            "maven_orb_rec_210101_210401_v1.orb",
            "w",
        ):
            pass
        with open(
            "maven/maven_spice/miscellaneous/orbnum/"
            "maven_orb_rec_210101_2105401_v2.orb",
            "w",
        ):
            pass

        main(config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_with_former(self):
        """
        Test for orbnum generation when the prior file does not have an
        explicit version. Note that the orbnum file provided by the user
        does have to have a version number (and the pattern provided via
        configuration as well).
        """
        config = "../config/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401_v1.orb")

        with open(
            "maven/maven_spice/miscellaneous/orbnum/" "maven_orb_rec_210101_210401.orb",
            "w",
        ):
            pass

        main(config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_blank_records(self):
        """
        Test an orbnum file with blank records.
        """
        config = "../config/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401_v3.orb")

        with open(
            "maven/maven_spice/miscellaneous/orbnum/"
            "maven_orb_rec_210101_210401_v1.orb",
            "w",
        ):
            pass
        with open(
            "maven/maven_spice/miscellaneous/orbnum/"
            "maven_orb_rec_210101_2105401_v2.orb",
            "w",
        ):
            pass

        main(config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_blank_records_no_former(self):
        """
        Test an orbnum file with blank records.
        """
        config = "../config/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401_v3.orb")

        main(config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_blank_records_no_version(self):
        """
        Test an orbnum file with blank records.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if (
                        "<orbnum pattern="
                        '"maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].orb">' in line
                    ):
                        n.write(
                            "<orbnum pattern=" '"maven_orb_rec_[0-9]{6}_[0-9]{6}.orb">'
                        )
                    else:
                        n.write(line)

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401.orb")

        main(updated_config, plan, self.faucet, silent=self.silent)

    def test_pds3_orbnum_files(self):

        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven_orbnum.plan"

        orbnum_list = [
            "cas_v40.orb",
            "clem.orb",
            "dawn_vesta_iau_v05.nrb",
            "grail_v02.nrb",
            "juno_rec_orbit_v08.orb",
            "lro_v45.nrb",
            "m01_ext64.nrb",
            "mgs_ext26_v2.nrb",
            "mro_psp58.nrb",
            "msgr_040803_150430_150430_od431sc_2.orb",
            "ormm_merged_00966.orb",
            "orvm_t19___________00001.orb",
            "vco_v05.orb",
            "vo1_rcon.orb",
            "vo2_rcon.orb",
        ]

        orbnum_config = ""
        with open(plan, "w") as p:
            for file in orbnum_list:
                p.write(f"{file}\n")
                orbnum_config += (
                    f"<orbnum>\n"
                    f"    <pattern>{file}</pattern>\n"
                    "    <event_detection_frame>\n"
                    "        <spice_name>IAU_MARS</spice_name>\n"
                    "        <description>Mars body-fixed frame</description>\n"
                    "    </event_detection_frame>\n"
                    "    <header_start_line>1</header_start_line >\n"
                    "    <pck>\n"
                    "        <kernel_name>pck0010.tpc</kernel_name>\n"
                    "        <description>IAU 2009 report</description>\n"
                    "    </pck>\n"
                    "</orbnum>\n"
                )

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if (
                        '<kernel cutoff="True">../data/kernels/spk/'
                        "maven_orb_rec_210101_210401_v2.bsp</kernel>" in line
                    ):
                        n.write("")
                    elif "</orbit_number_file>" in line:
                        n.write(orbnum_config)
                        n.write("</orbit_number_file>")
                    else:
                        n.write(line)

        main(updated_config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_eol_line_feed(self):
        """
        Test for meta-kernel configuration loading error cases.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven_orbnum.plan"

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<information_model>1.5.0.0</information_model>" in line:
                        n.write("<information_model>1.16.0.0" "</information_model>")
                    elif "/PDS4_PDS_1500" in line:
                        n.write(line.replace("/PDS4_PDS_1500", "/PDS4_PDS_1G00"))
                    else:
                        n.write(line)

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401_v1.orb")

        main(updated_config, plan, self.faucet, silent=self.silent)

    def test_pds4_orbnum_generated_list(self):
        """
        Test orbnum file generation with automatic plan generation
        (plan is not provided by the user.)
        """
        config = "../config/maven.xml"

        shutil.copy(
            "../data/misc/orbnum/maven_orb_rec_210101_210401_v1.orb", "misc/orbnum/"
        )

        main(config, faucet=self.faucet, silent=self.silent)

    def test_pds4_orbnum_multiple_files(self):
        """
        Test orbnum file generation with mulitple orbnum files in list.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if (
                        '<kernel cutoff="True">../data/kernels/spk/'
                        "maven_orb_rec_210101_210401_v2.bsp</kernel>" in line
                    ):
                        n.write(
                            '<kernel cutoff="True">kernels/spk/'
                            "maven_orb_rec[0-9]{6}_[0-9]{6}_v[0-9].bsp</kernel>"
                        )
                    else:
                        n.write(line)

        shutil.copy("../data/maven_release_orbnum.plan", "working/")

        plan = "working/maven_release_orbnum.plan"

        shutil.copy(
            "kernels/spk/maven_orb_rec_210101_210401_v2.bsp",
            "kernels/spk/maven_orb_rec_210101_210401_v1.bsp",
        )
        shutil.copy(
            "kernels/spk/maven_orb_rec_210101_210401_v2.bsp",
            "kernels/spk/maven_orb_rec_210101_210402_v1.bsp",
        )
        shutil.copy(
            "../data/misc/orbnum/maven_orb_rec_210101_210401_v1.orb",
            "misc/orbnum/maven_orb_rec_210101_210402_v1.orb",
        )

        main(updated_config, plan=plan, faucet="bundle", silent=self.silent)

    def test_pds4_orbnum_multiple_files_incorrect_spk(self):
        """
        Test orbnum file generation with mulitple orbnum files in list.
        """
        config = "../config/maven.xml"

        shutil.copy("../data/maven_release_orbnum.plan", "working/")

        plan = "working/maven_release_orbnum.plan"

        shutil.copy(
            "kernels/spk/maven_orb_rec_210101_210401_v2.bsp",
            "kernels/spk/maven_orb_rec_210101_210401_v1.bsp",
        )
        shutil.copy(
            "kernels/spk/maven_orb_rec_210101_210401_v2.bsp",
            "kernels/spk/maven_orb_rec_210101_210402_v1.bsp",
        )
        shutil.copy(
            "../data/misc/orbnum/maven_orb_rec_210101_210401_v1.orb",
            "misc/orbnum/maven_orb_rec_210101_210402_v1.orb",
        )

        main(config, plan=plan, faucet="bundle", silent=self.silent)

    def test_pds4_orbnum_multiple_files_in_spk_dir(self):
        """
        Test orbnum file generation with mulitple orbnum files in list.
        """
        config = "../config/maven.xml"

        updated_config = "working/maven.xml"
        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<orbnum_directory>misc/orbnum" "</orbnum_directory>" in line:
                        n.write("<orbnum_directory>kernels/spk" "</orbnum_directory>")
                    elif (
                        '<kernel cutoff="True">../data/kernels/spk/'
                        "maven_orb_rec_210101_210401_v2.bsp</kernel>" in line
                    ):
                        n.write(
                            '<kernel cutoff="True">kernels/spk/'
                            "maven_orb_rec_[0-9][0-9][0-9][0-9][0-9][0-9]_"
                            "[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9]."
                            "bsp</kernel>"
                        )
                    else:
                        n.write(line)

        shutil.copy("../data/maven_release_orbnum.plan", "working/")

        plan = "working/maven_release_orbnum.plan"

        shutil.copy(
            "kernels/spk/maven_orb_rec_210101_210401_v2.bsp",
            "kernels/spk/maven_orb_rec_210101_210401_v1.bsp",
        )
        shutil.copy(
            "kernels/spk/maven_orb_rec_210101_210401_v2.bsp",
            "kernels/spk/maven_orb_rec_210101_210402_v1.bsp",
        )
        shutil.copy(
            "../data/misc/orbnum/maven_orb_rec_210101_210401_v1.orb",
            "kernels/spk/maven_orb_rec_210101_210402_v1.orb",
        )
        shutil.copy(
            "../data/misc/orbnum/maven_orb_rec_210101_210401_v1.orb",
            "kernels/spk/maven_orb_rec_210101_210401_v1.orb",
        )

        main(updated_config, plan=plan, faucet="bundle", silent=self.silent, log=True)


if __name__ == "__main__":
    unittest.main()
