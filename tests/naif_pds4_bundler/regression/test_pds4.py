"""Regression Test Family for PDS4 archives."""
import glob
import os
import shutil

from pds.naif_pds4_bundler.__main__ import main


def compare(self):
    """Assert results by comparing certain products."""
    mis = self.mission

    #
    # Compare the files.
    #
    files = glob.glob(f"{mis}/{mis}_spice/**/*.xml", recursive=True)
    files += glob.glob(f"{mis}/{mis}_spice/**/*.csv", recursive=True)
    files += glob.glob(f"{mis}/{mis}_spice/**/*.html", recursive=True)
    files += glob.glob(f"{mis}/{mis}_spice/**/*.tm", recursive=True)
    files += glob.glob(f"{mis}/{mis}_spice/**/*.txt", recursive=True)
    for product in files:
        if os.path.isfile(product):
            test_product = product.replace(f"{mis}/", "../data/regression/")

            with open(product) as ff:
                fromlines = ff.read().splitlines()
                fromlines = [
                    item
                    for item in fromlines
                    if ("checksum" not in item)
                    and ("file_size" not in item)
                    and ("object_length" not in item)
                ]
                fromlines = [item for item in fromlines if "checksum" not in item]
            with open(test_product) as tf:
                tolines = tf.read().splitlines()
                tolines = [
                    item
                    for item in tolines
                    if ("checksum" not in item)
                    and ("file_size" not in item)
                    and ("object_length" not in item)
                ]

            if fromlines != tolines:
                print(f"Assertion False for: {product}")
                self.assertTrue(False)
    dirs = ["working", "staging", "kernels", mis]
    for dir in dirs:
        shutil.rmtree(dir, ignore_errors=True)

        pass


def post_setup(self):
    """Ensures release and creation date time is fixed for the test."""
    self.config = f"../config/{self.mission}.xml"
    self.updated_config = f"working/{self.mission}.xml"

    with open(self.config, "r") as c:
        with open(self.updated_config, "w") as n:
            for line in c:
                if "</readme>" in line:
                    n.write("</readme>\n")
                    n.write("<release_date>2021-06-25</release_date>\n")
                    n.write(
                        "<creation_date_time>"
                        "2021-06-25T08:00:00</creation_date_time>\n"
                    )
                #
                # Remove line from M2020 configuration file
                #
                elif "<release_date>2021-08-20</release_date>" in line:
                    n.write("")
                elif "<spice_name>TGO</spice_name>" in line:
                    n.write("<spice_name>TGO</spice_name>\n")
                    n.write("<release_date>2021-06-25</release_date>\n")
                    n.write(
                        "<creation_date_time>"
                        "2021-06-25T08:00:00</creation_date_time>\n"
                    )
                else:
                    n.write(line)


def test_insight(self):
    """Test to generate the INSIGHT archive."""
    self.mission = "insight"
    post_setup(self)

    plan = "../data/insight_release_08.plan"

    shutil.copy2(
        "../data/insight_release_basic.kernel_list",
        "working/insight_release_07.kernel_list",
    )
    shutil.copytree("../data/insight", "insight")
    shutil.copytree("../data/kernels", "kernels")

    #
    # Remove the MK used for other tests. MK will be generated
    # by NPB.
    #
    os.remove("kernels/mk/insight_v08.tm")

    main(
        self.updated_config, plan, silent=self.silent, log=self.log
    )
    compare(self)


def test_ladee(self):
    """Test to generate the LADEE archive."""
    self.mission = "ladee"
    post_setup(self)

    os.makedirs("ladee")
    shutil.copytree(
        "../data/regression/ladee_spice/spice_kernels",
        "kernels",
        ignore=shutil.ignore_patterns("*.xml", "*.csv"),
    )

    main(self.updated_config, silent=self.silent, log=self.log)
    compare(self)


def test_kplo(self):
    """Test to generate the KPLO archive (non-PDS archive)."""
    self.mission = "kplo"
    post_setup(self)

    os.makedirs("kplo")
    shutil.copytree(
        "../data/regression/kplo_spice/spice_kernels",
        "kernels",
        ignore=shutil.ignore_patterns("*.xml", "*.csv"),
    )

    main(self.updated_config, silent=self.silent, log=self.log)
    compare(self)


def test_m2020(self):
    """Test to generate two releases of the M2020 archive.

    This test is implemented to test the generation of an archive that
    already has an existing miscellaneous collection.

    The MKs are provided as inputs with the configuration file.
    """
    self.mission = "mars2020"
    post_setup(self)

    os.makedirs("mars2020")
    shutil.copytree(
        "../data/regression/mars2020_spice/spice_kernels",
        "kernels",
        ignore=shutil.ignore_patterns("*.xml", "*.csv"),
    )

    plan = '../data/mars2020_release_01.plan'

    main(self.updated_config, plan=plan, silent=self.silent, log=self.log)

    updated_config = 'working/mars2020_release_02.xml'

    with open(self.updated_config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "<file>kernels/mk/m2020_v01.tm</file>" in line:
                    n.write("<file>kernels/mk/m2020_v02.tm</file>\n")
                elif "<file>kernels/mk/m2020_chronos_v01.tm</file>" in line:
                    n.write("")
                else:
                    n.write(line)

    plan = '../data/mars2020_release_02.plan'
    main(updated_config, plan=plan, silent=self.silent, log=self.log)

    updated_config = 'working/mars2020_release_03.xml'
    mk_inputs = False
    with open(self.updated_config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "mk_inputs" in line and not mk_inputs:
                    mk_inputs = True
                elif "mk_inputs" in line and mk_inputs:
                    mk_inputs = False
                elif not mk_inputs:
                    n.write(line)

    plan = "../data/mars2020_release_03.plan"
    shutil.copy2("../data/kernels/sclk/m2020_168_sclkscet_refit_v03.tsc",
                 "kernels/sclk/m2020_168_sclkscet_refit_v03.tsc")
    main(updated_config, plan=plan, silent=self.silent, log=self.log)
    compare(self)


def test_em16(self):
    """Test to generate the ESA SPICE Service ExoMars2016 archive."""
    self.mission = "em16"
    post_setup(self)

    shutil.copytree(
        "../data/regression/em16_spice/spice_kernels",
        "kernels",
        ignore=shutil.ignore_patterns("*.xml", "*.csv"),
    )
    shutil.copytree("../data/em16", "em16")

    plan = '../data/em16_release_04.plan'

    main(self.updated_config, plan=plan, silent=self.silent, log=self.log)
    compare(self)
