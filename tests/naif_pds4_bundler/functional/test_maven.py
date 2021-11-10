"""Functional Test Family for MAVEN Archive Generation."""
import os
import shutil
import unittest
from unittest import TestCase

from naif_pds4_bundler.__main__ import main


class TestMAVEN(TestCase):
    """Functional Test Family Class for MAVEN Archive Generation."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Functional Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ["working", "staging", "final", "kernels", "misc", "maven"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.verbose = False
        cls.silent = True
        cls.log = True

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ["working", "staging"]
        for dir in dirs:
            os.mkdir(dir)

        shutil.copytree("../data/kernels", "kernels")
        shutil.copytree("../data/maven", "maven")

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "final", "kernels", "misc", "maven"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        try:
            os.remove("maven_orbnum.plan")
        except BaseException:
            pass

    def generate_mks(self, directory="working"):
        """Generate test MKs."""
        shutil.copy2("../data/kernels/lsk/naif0012.tls", "working/")
        with open(f"{directory}/maven_2015_v09.tm", "w") as p:
            p.write("KPL/MK\n"
                    "\\begindata\n"
                    f"PATH_VALUES = ( '{os.getcwd()}' )\n"
                    "PATH_SYMBOLS = ( 'KERNELS' )\n"
                    "KERNELS_TO_LOAD = ('$KERNELS/../data/kernels/lsk/naif0012.tls')\n"
                    "\\begintext")
        with open(f"{directory}/maven_2020_v06.tm", "w") as p:
            p.write("KPL/MK\n"
                    "\\begindata\n"
                    f"PATH_VALUES = ( '{os.getcwd()}' )\n"
                    "PATH_SYMBOLS = ( 'KERNELS' )\n"
                    "KERNELS_TO_LOAD = ('$KERNELS/../data/kernels/lsk/naif0012.tls')\n"
                    "\\begintext")

    def test_maven_mks_input(self):
        """Test MKs provided as input.

        Test the generation of MK labels with MKs provided as inputs.

        The first run will provide the following error message::
           RuntimeError: No kernels present in (...)maven_2015_v09.tm. Please review MK generation.

        The second run will be successful.

        The test is successful if the conditions described above are met.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven.plan"

        shutil.copy2("../data/maven_release_24.kernel_list", "working/")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<coverage_kernels>" in line:
                        n.write("<mk_inputs>")
                        n.write("   <file>working/maven_2015_v09.tm</file>\n")
                        n.write("   <file>working/maven_2020_v06.tm</file>\n")
                        n.write("</mk_inputs>")
                        n.write("<coverage_kernels>")
                    else:
                        n.write(line)

        with open("working/maven_2015_v09.tm", "w") as p:
            p.write("KPL/MK\n")
        with open("working/maven_2020_v06.tm", "w") as p:
            p.write("KPL/MK\n")

        with open("working/maven.plan", "w") as p:
            p.write("mvn_sclkscet_00088.tsc")

        with self.assertRaises(RuntimeError):
            main(
                updated_config,
                plan=plan,
                silent=self.silent,
                verbose=self.verbose,
                log=self.log
            )

        main(
            updated_config,
            clear="working/maven_release_25.file_list",
            silent=self.silent,
            verbose=self.verbose,
            log=self.log
        )

        self.generate_mks()

        main(
            updated_config,
            plan=plan,
            silent=self.silent,
            verbose=self.verbose,
            log=self.log
        )

    def test_maven_mks_list(self):
        """Test MKs provided in release plan to be generated by NPB.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/maven.xml"
        plan = "working/maven.plan"
        faucet = "bundle"

        with open("working/maven.plan", "w") as p:
            p.write("mvn_sclkscet_00088.tsc\n")
            p.write("maven_2015_v09.tm\n")
            p.write("maven_2020_v06.tm")

        main(
            config,
            plan=plan,
            faucet=faucet,
            silent=self.silent,
            verbose=self.verbose,
            log=self.log
        )

    def test_maven_mks_list_in_kernels(self):
        """Test MKs provided in release plan and provided as inputs.

        The MKs are not present in the configuration file but are present in
        the input kernels directory.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/maven.xml"
        plan = "working/maven.plan"
        faucet = "bundle"

        with open("working/maven.plan", "w") as p:
            p.write("mvn_sclkscet_00088.tsc\n")
            p.write("maven_2015_v09.tm\n")
            p.write("maven_2020_v06.tm")

        self.generate_mks(directory="kernels/mk")

        main(
            config,
            plan=plan,
            faucet=faucet,
            silent=self.silent,
            verbose=self.verbose,
            log=self.log
        )

    def test_maven_mks_list_config_in_kernels(self):
        """Test MKs provided in release plan and provided as double inputs.

        The MKs are both present in the configuration file and are present in
        the input ``kernels_directory``. The files specified by the
        configuration file are not present and NPB uses the ones under the
        ``kernels_directory``.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven.plan"
        faucet = "bundle"

        with open("working/maven.plan", "w") as p:
            p.write("mvn_sclkscet_00088.tsc\n")
            p.write("maven_2015_v09.tm\n")
            p.write("maven_2020_v06.tm")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<coverage_kernels>" in line:
                        n.write("<mk_inputs>")
                        n.write("   <file>working/maven_2015_v09.tm</file>\n")
                        n.write("   <file>working/maven_2020_v06.tm</file>\n")
                        n.write("</mk_inputs>")
                        n.write("<coverage_kernels>")
                    else:
                        n.write(line)

        self.generate_mks(directory="kernels/mk")

        main(
            updated_config,
            plan=plan,
            faucet=faucet,
            silent=self.silent,
            verbose=self.verbose,
            log=self.log
        )

    def test_maven_mks_list_config_in_kernels_and_config(self):
        """Test MKs provided in release plan and provided as dobule inputs.

        The MKs are both present in the configuration file and are present in
        the input ``kernels_directory``. The files in the release plan that
        point to the ``kernels_directory`` will be ignored.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/maven.xml"
        updated_config = "working/maven.xml"
        plan = "working/maven.plan"
        faucet = "bundle"

        with open("working/maven.plan", "w") as p:
            p.write("mvn_sclkscet_00088.tsc\n")
            p.write("maven_2015_v09.tm\n")
            p.write("maven_2020_v06.tm")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<coverage_kernels>" in line:
                        n.write("<mk_inputs>")
                        n.write("   <file>working/maven_2015_v09.tm</file>\n")
                        n.write("   <file>working/maven_2020_v06.tm</file>\n")
                        n.write("</mk_inputs>")
                        n.write("<coverage_kernels>")
                    else:
                        n.write(line)

        self.generate_mks()
        self.generate_mks(directory="kernels/mk")

        main(
            updated_config,
            plan=plan,
            faucet=faucet,
            silent=self.silent,
            verbose=self.verbose,
            log=self.log
        )

    def test_maven_no_mk(self):
        """Test to generate the first release with no MK inputs.

        No meta-kernels are generated because the meta-kernel includes
        the year pattern ``YEAR``.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/maven.xml"
        plan = "working/maven.plan"
        faucet = "staging"

        with open("working/maven.plan", "w") as p:
            p.write("mvn_sclkscet_00088.tsc")

        main(
            config,
            plan=plan,
            faucet=faucet,
            silent=self.silent,
            verbose=self.verbose,
            log=self.log
        )

    def test_maven_generate_mk(self):
        """Test automatic generation of when specifying MK name in plan.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/maven.xml"
        plan = "working/maven.plan"
        faucet = "staging"

        with open("working/maven.plan", "w") as p:
            p.write("mvn_sclkscet_00088.tsc")
            p.write("maven_2021_v99.tm")

        main(
                config,
                plan=plan,
                faucet=faucet,
                silent=self.silent,
                verbose=self.verbose,
                log=self.log
            )


if __name__ == "__main__":

    unittest.main()