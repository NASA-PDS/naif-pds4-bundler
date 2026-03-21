"""Test Family to clear previous execution."""
import os
import shutil

from pds.naif_pds4_bundler.pipeline.npb import run_pipeline
from pds.naif_pds4_bundler.utils.types.datatypes import PipelineArgs


def test_insight_basic(self):
    """Test complete clearing basic Insight archive generation.

    This method will be executed after each test function.
    """
    shutil.copy2(
        "../data/insight_release_basic.kernel_list",
        "working/insight_release_07.kernel_list",
    )
    shutil.move("insight", "insight_old")
    shutil.copytree("../data/insight", "insight")
    shutil.move("kernels", "kernels_old")
    shutil.copytree("../data/kernels", "kernels")

    with open("../data/insight.list", "r") as i:
        for line in i:
            with open(f"insight/insight_spice/{line[0:-1]}", "w"):
                pass

    config = "../config/insight.xml"
    plan = "../data/insight_release_08.plan"
    faucet = "bundle"
    run_pipeline(PipelineArgs(config=config, plan=plan, faucet=faucet,
                              silent=self.silent, log=self.log))

    #
    # Remove the files from the prior run.
    #
    run_pipeline(PipelineArgs(
        config=config,
        plan=plan,
        faucet="plan",
        silent=self.silent,
        log=self.log,
        clear="working/insight_release_08.file_list",
    ))

    #
    # Run the pipeline again.
    #
    run_pipeline(PipelineArgs(config=config, plan=plan, faucet=faucet,
                              silent=self.silent, log=self.log))

    #
    # Remove the files from the prior run and run the pipeline again.
    #
    run_pipeline(PipelineArgs(
        config=config,
        plan=plan,
        faucet=faucet,
        silent=self.silent,
        log=self.log,
        clear="working/insight_release_08.file_list",
    ))


def test_insight_error(self):
    """Test complete clearing basic Insight archive generation with error.

    Test generation of product list when there is an error in the
    execution. Also test cleaning the failed run and running the pipeline
    again. In addition, test an incorrect spice_name.
    """
    config = "../config/insight.xml"

    cwd = os.getcwd()

    plan = "../data/insight_release_08.plan"

    shutil.move("insight", "insight_old")
    shutil.copytree("../data/insight", "insight")
    shutil.move("kernels", "kernels_old")
    shutil.copytree("../data/kernels", "kernels")

    #
    # Error validating the meta-kernel
    #
    with self.assertRaises(BaseException):
        run_pipeline(PipelineArgs(config=config, silent=self.silent, log=self.log))

    os.chdir(cwd)
    #
    # Remove the files from the prior run.
    #
    run_pipeline(PipelineArgs(
        config=config,
        plan=plan,
        faucet="plan",
        silent=self.silent,
        log=self.log,
        clear="working/insight_release_08.file_list",
    ))

    #
    # Run the pipeline again.
    #
    run_pipeline(PipelineArgs(config=config, plan=plan, faucet="bundle",
                              silent=self.silent, log=self.log))


def test_clear_label_mode(self):
    """Test clear option in label mode.

    The test is implemented to check the deletion of the kernel list for
    label mode.

    Test is successful if NPB is executed without errors.
    """
    shutil.move("kernels", "kernels_old")
    shutil.copytree(
        "../data/regression/ladee_spice/spice_kernels",
        "kernels",
        ignore=shutil.ignore_patterns("*.xml", "*.csv"),
    )

    config = "../config/ladee.xml"

    run_pipeline(PipelineArgs(config=config, plan=None, faucet="labels",
                              silent=True, log=self.log))

    run_pipeline(PipelineArgs(
        config=config,
        plan="working/ladee_labels_01.plan",
        clear="working/ladee_labels_01.file_list",
        silent=True,
        log=self.log,
    ))
