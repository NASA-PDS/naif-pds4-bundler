"""Unit tests for ORBNUM label generation."""
import os
import shutil

from pds.naif_pds4_bundler.__main__ import main


def post_setup(self):
    """Post Setup Test."""
    shutil.rmtree("kernels")
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


def test_pds4_orbnum_coverage_user_spk(self):
    """Test ORBNUM coverage from SPK in configuration.

    The coverage is provided by the following configuration element::

            <kernel cutoff="True">../data/kernels/spk/maven_orb_rec_210101_210401_v2.bsp</kernel>
    """
    post_setup(self)
    config = "../config/maven.xml"
    plan = "working/maven_orbnum.plan"

    with open(plan, "w") as p:
        p.write("maven_orb_rec_210101_210401_v1.orb")
        p.write("\nmaven_orb_rec_210101_210401_v1.nrb")

    main(config, plan, self.faucet, silent=self.silent)


def test_pds4_orbnum_coverage_increment_spk(self):
    """Test ORBNUM coverage from SPK with pattern in configuration.

    The coverage is provided by the following configuration element::

            <kernel cutoff="True">../data/kernels/spk/maven_orb_rec_210101_210401_v2.bsp</kernel>
    """
    post_setup(self)
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
    """Test ORBNUM coverage from SPK with pattern in configuration."""
    post_setup(self)
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
    """Test ORBNUM coverage from look-up table in configuration."""
    post_setup(self)
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
    """Test various ORBNUM coverage from look-up table in configuration."""
    post_setup(self)
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
    """Test ORBNUMs coverage from ORBNUM file itself."""
    post_setup(self)
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

    main(updated_config, plan, self.faucet, log=True, silent=self.silent)


def test_pds4_orbnum_with_former_version(self):
    """Test ORBNUM generation when multiple versions are available.

    The test checks if the correct ORBNUM file from the release list is
    used.
    """
    post_setup(self)
    config = "../config/maven.xml"
    plan = "working/maven_orbnum.plan"

    with open(plan, "w") as p:
        p.write("maven_orb_rec_210101_210401_v2.orb")

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

    main(config, plan, self.faucet, log=True, silent=self.silent)


def test_pds4_orbnum_with_former(self):
    """Test ORBNUM generation when multiple files with wrong versions.

    Test for orbnum generation when the prior file does not have an
    explicit version. Note that the orbnum file provided by the user
    does have to have a version number (and the pattern provided via
    configuration as well).
    """
    post_setup(self)
    config = "../config/maven.xml"
    plan = "working/maven_orbnum.plan"

    with open(plan, "w") as p:
        p.write("maven_orb_rec_210101_210401_v1.orb")

    with open(
        "maven/maven_spice/miscellaneous/orbnum/" "maven_orb_rec_210101_210401.orb",
        "w",
    ):
        pass

    main(config, plan, self.faucet, silent=self.silent, log=True)


def test_pds4_orbnum_blank_records(self):
    """Test an orbnum file with blank records.

    Test the generation of a label when the ORBNUM file has some incomplete
    entries (which is a real possibility.)

    In such case the record length is expanded to the adequate fixed length.
    Afterwards the ORBNUM file version is incremented, because a new file
    has just been created. The NPB log will display the following warnings::

        WARNING : -- Orbit number 13071 record has an incorrect length, the record will be expanded to cover the adequate fixed length.
        WARNING : -- Orbit number 13073 record has an incorrect length, the record will be expanded to cover the adequate fixed length.
        WARNING : -- Orbit number 13073 record is followed by 13075.
        WARNING : -- Orbnum name updated to: maven_orb_rec_210101_210401_v4.orb
    """
    post_setup(self)
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

    main(config, plan, self.faucet, silent=self.silent, log=True)


def test_pds4_orbnum_blank_records_no_former(self):
    """Test an ORBNUM file with blank records with no former versions.

    Test the generation of a label when the ORBNUM file has some incomplete
    entries (which is a real possibility.)

    In such case the record length is expanded to the adequate fixed length.
    Afterwards the ORBNUM file version is incremented based on the name
    provided in the release plan, because a new file has just been created.
    The NPB log will display the following warnings::

        WARNING : -- Orbit number 13071 record has an incorrect length, the record will be expanded to cover the adequate fixed length.
        WARNING : -- Orbit number 13073 record has an incorrect length, the record will be expanded to cover the adequate fixed length.
        WARNING : -- Orbit number 13073 record is followed by 13075.
        WARNING : -- Orbnum name updated to: maven_orb_rec_210101_210401_v4.orb
    """
    post_setup(self)
    config = "../config/maven.xml"
    plan = "working/maven_orbnum.plan"

    with open(plan, "w") as p:
        p.write("maven_orb_rec_210101_210401_v3.orb")

    main(config, plan, self.faucet, silent=self.silent, log=True)


def test_pds4_orbnum_blank_records_no_version(self):
    """Test an orbnum file with blank records.

    Test the generation of a label when the ORBNUM file has some incomplete
    entries (which is a real possibility.)

    In such case the record length is expanded to the adequate fixed length.
    Afterwards the ORBNUM file version is incremented based on the name
    provided in the release plan, because a new file has just been created.
    The NPB log will display the following warnings::

        WARNING : -- Orbit number 13071 record has an incorrect length, the record will be expanded to cover the adequate fixed length.
        WARNING : -- Orbit number 13073 record has an incorrect length, the record will be expanded to cover the adequate fixed length.
        WARNING : -- Orbit number 13073 record is followed by 13075.
        WARNING : -- Orbnum name updated to: maven_orb_rec_210101_210401_v2.orb
    """
    post_setup(self)
    config = "../config/maven.xml"
    updated_config = "working/maven.xml"
    plan = "working/maven_orbnum.plan"

    with open(config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "<pattern>maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].orb" in line:
                    n.write(
                        "<pattern>maven_orb_rec_[0-9]{6}_[0-9]{6}.orb</pattern>\n"
                    )
                else:
                    n.write(line)

    with open(plan, "w") as p:
        p.write("maven_orb_rec_210101_210401.orb")

    main(updated_config, plan, self.faucet, silent=self.silent, log=True)


def test_pds3_orbnum_files(self):
    """Test all the types of NASA and ESA PDS3 data sets ORBNUM files."""
    post_setup(self)
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
                "    <author>NAIF, JPL</author>\n"
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

    main(updated_config, plan, self.faucet, silent=self.silent, log=True)


def test_pds4_orbnum_eol_line_feed(self):
    """Test generation of ORBNUM files with LF End-of-Line."""
    post_setup(self)
    config = "../config/maven.xml"
    updated_config = "working/maven.xml"
    plan = "working/maven_orbnum.plan"

    with open(config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "<end_of_line>CRLF</end_of_line>" in line:
                    n.write("<end_of_line>LF</end_of_line>\n")
                #
                # Remove the explicit directory from the configuration file.
                #
                elif "templates_directory" in line:
                    pass
                else:
                    n.write(line)

    with open(plan, "w") as p:
        p.write("maven_orb_rec_210101_210401_v1.orb")

    main(updated_config, plan, self.faucet, log=True, silent=self.silent)


def test_pds4_orbnum_generated_list(self):
    """Test inclusion of ORBNUM in kernel list.

    Test ORBNUM file generation with automatic plan generation, when the
    plan is not provided by the user.
    """
    post_setup(self)
    config = "../config/maven.xml"

    shutil.copy(
        "../data/misc/orbnum/maven_orb_rec_210101_210401_v1.orb", "misc/orbnum/"
    )

    main(config, faucet=self.faucet, silent=self.silent, log=True)


def test_pds4_orbnum_multiple_files(self):
    """Test ORBNUM coverage for multiple files.

    Update the configuration file to use kernel patterns to determine
    coverage for different ORBNUM files.
    """
    post_setup(self)
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
                        "maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].bsp</kernel>"
                    )
                else:
                    n.write(line)

    shutil.copy2("../data/maven_release_orbnum.plan", "working/")

    plan = "working/maven_release_orbnum.plan"

    shutil.copy2(
        "kernels/spk/maven_orb_rec_210101_210401_v2.bsp",
        "kernels/spk/maven_orb_rec_210101_210401_v1.bsp",
    )
    shutil.copy2(
        "kernels/spk/maven_orb_rec_210101_210401_v2.bsp",
        "kernels/spk/maven_orb_rec_210101_210402_v1.bsp",
    )
    shutil.copy2(
        "../data/misc/orbnum/maven_orb_rec_210101_210401_v1.orb",
        "misc/orbnum/maven_orb_rec_210101_210402_v1.orb",
    )

    main(updated_config, plan=plan, faucet="bundle", log=True, silent=self.silent)


def test_pds4_orbnum_multiple_files_incorrect_spk(self):
    """Test incorrect ORBNUM coverage.

    This test ensures that the coverage is incorrectly calculated for
    two ORBNUM files due to the configuration file.
    """
    post_setup(self)
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

    main(config, plan=plan, faucet="bundle", log=True, silent=self.silent)


def test_pds4_orbnum_multiple_files_in_spk_dir(self):
    """Test ORBNUM with input files in SPK directory."""
    post_setup(self)
    config = "../config/maven.xml"

    updated_config = "working/maven.xml"
    with open(config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "<orbnum_directory>misc/orbnum" "</orbnum_directory>" in line:
                    n.write("<orbnum_directory>kernels/spk</orbnum_directory>")
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
