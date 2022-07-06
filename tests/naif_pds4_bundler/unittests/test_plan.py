"""Unit tests for the Release Plan generation."""
import os
import shutil

from pds.naif_pds4_bundler.__main__ import main


def post_setup(self):
    """Post setup Test."""
    dirs = [
        "working",
        "staging",
        "insight",
        "mars2020",
        "kernels",
        "kernels/fk",
        "kernels/sclk",
        "kernels/ik",
        "kernels/lsk",
        "kernels/ck",
        "kernels/spk",
        "kernels/pck",
        "kernels/mk",
    ]
    for dir in dirs:
        try:
            shutil.move(dir, f"{dir}_old")
        except BaseException:
            pass
        os.mkdir(dir)


def test_pds4_insight_plan(self):
    """Basic test for InSight kernel list generation.

    Implemented following the generation of the kernel list for InSight
    release 8.
    """
    post_setup(self)
    config = "../config/insight.xml"
    plan = ""
    faucet = "list"

    shutil.copy2("../data/kernels/fk/insight_v05.tf", "kernels/fk")
    shutil.copy2("../data/kernels/lsk/naif0012.tls", "kernels/lsk")
    shutil.copy2("../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc", "kernels/ck")
    shutil.copy2("../data/kernels/ck/insight_ida_pot_200829_201220_v1.bc", "kernels/ck")

    shutil.copy2(
        "../data/insight_release_empty.kernel_list",
        "working/insight_release_07.kernel_list",
    )

    main(config, plan, faucet, silent=True, log=True)

    new_file = ""
    with open("working/insight_release_08.plan", "r") as f:
        for line in f:
            new_file += line

    old_file = ""
    with open("../data/insight_release_test.plan", "r") as f:
        for line in f:
            old_file += line

    self.assertEqual(old_file.split("\n")[9:], new_file.split("\n")[9:])


def test_pds4_mars2020_no_plan(self):
    """Basic test for M2020 kernel plan generation.

    Implemented for the generation of the first M2020 release. The
    particularity of this test is that it includes two meta-kernels provided
    as inputs.
    """
    post_setup(self)
    config = "../config/mars2020.xml"
    faucet = "list"
    last_filename = ""
    with open("../data/mars2020_release_10.kernel_list", "r") as f:
        for line in f:
            if last_filename and "MAPPING" in line:
                os.remove(last_filename)
                filename = os.sep.join(last_filename.split(os.sep)[0:-1])
                filename += f'/{line.split("=")[-1].strip()}'
                with open(f"{filename}", "w") as fp:
                    fp.flush()
                    pass
            if "FILE             = spice_kernels" in line:
                filename = f"kernels/{line.split('= spice_kernels/')[-1]}"
                filename = filename[:-1]
                with open(f"{filename}", "w") as fp:
                    fp.flush()
                    pass
                last_filename = filename

    main(config, faucet=faucet, silent=True, log=True)

    new_file = ""
    with open("working/mars2020_release_01.plan", "r") as f:
        for line in f:
            new_file += line

    old_file = ""
    with open("../data/mars2020_release_10.plan", "r") as f:
        for line in f:
            if "m2020_168_sclkscet_00007.tsc" not in line:
                old_file += line

    self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])
