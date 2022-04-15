"""Regression Test Family for PDS3 archives.

Note that EOL, label checksum tags and checksum files are not tested.
"""
import os
import shutil
import unittest

from pds.naif_pds4_bundler.__main__ import main
from pds.naif_pds4_bundler.utils import extract_comment


def compare(self):
    """Assert by comparing some products."""
    unittest.TestCase.tearDown(self)
    mis = self.pds3_dir

    all_files = []
    files = []
    with open(f"working/{self.mission}_release_{self.release}.file_list", 'r') as f:
        for line in f:
            if '.kernel_list' not in line:
                files.append(f'{self.pds3_dir}/{self.volid}/{line[:-1]}')

    #
    # Extract comments to check label insertion.
    #
    for file in files:
        if any(x in file.split('.')[-1] for x in ['bc','bsp','bds']):
            cmt = extract_comment(file)
            with open(file.split('.b')[0] + '.cmt', 'w') as c:
                for line in cmt:
                    c.write(line + '\n')
            all_files.append(file.split('.b')[0] + '.cmt')
        elif not any(x in file.split('.')[-1] for x in ['tab']):
            all_files.append(file)

    #
    # Compare the files.
    #
    for product in all_files:
        if os.path.isfile(product):
            test_product = product.replace(f"{mis}/", "../data/regression/")

            with open(product) as ff:
                fromlines = ff.read().splitlines()
                fromlines = [item for item in fromlines if ("PRODUCT_CREATION_TIME" not in item)]
                fromlines = list(map(str.rstrip, fromlines))
                while ("" in fromlines):
                    fromlines.remove("")
            with open(test_product) as tf:
                tolines = tf.read().splitlines()
                tolines = [item for item in tolines if ("PRODUCT_CREATION_TIME" not in item)]
                tolines = list(map(str.rstrip, tolines))
                while ("" in tolines):
                    tolines.remove("")
            if fromlines != tolines:
                print(f"Assertion False for: {product}")
                self.assertTrue(False)
    dirs = ["working", "staging", "kernels", mis]
    for dir in dirs:
        shutil.rmtree(dir, ignore_errors=True)
        pass


def test_msl(self):
    """Test to generate a MSL data set increment."""
    self.mission = "msl"
    self.pds3_dir = "msl-m-spice-6-v1.0"
    self.volid = "mslsp_1000"
    self.release = "29"

    os.mkdir("kernels")
    os.mkdir("staging/mslsp_1000/")
    os.mkdir("staging/mslsp_1000/catalog")
    os.mkdir("msl-m-spice-6-v1.0")

    plan = "working/msl_release_29.plan"

    config = "../config/msl.xml"
    updated_config = 'working/msl.xml'
    with open(config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "<spice_name>MSL</spice_name>" in line:
                    n.write(line)
                    n.write("<binary_endianness>LTL-IEEE</binary_endianness>\n")
                else:
                    n.write(line)

    shutil.copy2(f"../data/spiceds_{self.mission}.cat",
                 f"staging/{self.volid}/catalog/spiceds.cat"
    )
    shutil.copy2(f"../data/release_{self.mission}.cat",
                 f"staging/{self.volid}/catalog/release.cat"
    )
    shutil.copy2("../data/msl_release_28.kernel_list",
                 "working/msl_release_28.kernel_list"
    )
    shutil.copy2(
        "../data/msl_release_00.plan",
        f"working/msl_release_{self.release}.plan"
    )

    shutil.copytree("../data/msl/mslsp_1000",
                    f"{self.pds3_dir}/{self.volid}")

    main(updated_config, plan, silent=True, log=self.log)
    compare(self)
