#
# @author: Marc Costa Sitja (JPL)
#
# This script has been used to assist the generation of the naif-pds4-bundler
# BepiColombo configuration file from the labels.
#
import glob

labels = glob.glob(
    "/Users/mcosta/workspace/bepi/20211025/bc_spice/spice_kernels/**/*.xml"
)

record = False
with open("bc_kernel_list.xml", "w") as o:
    for label in labels:
        with open(label, "r") as f:
            for line in f:
                if "<File_Area_SPICE_Kernel>" in line:
                    record = True
                if "</File_Area_SPICE_Kernel>" in line:
                    record = False
                if "<file_name>" in line and record:
                    text = line.split("<file_name>")[-1]
                    file_name = text.split("</file_name>")[0]
                    if "_v" in file_name:
                        file_name = (
                            file_name.split("_v")[0]
                            + "_v[0-9][0-9]."
                            + file_name.split(".")[-1]
                        )
                    o.write(f'        <kernel pattern="{file_name}">\n')
                    if "mpo" in file_name:
                        o.write("            <observers>\n")
                        o.write("                <observer>MPO</observer>\n")
                        o.write("            </observers>\n")
                    elif "mmo" in file_name:
                        o.write("            <observers>\n")
                        o.write("                <observer>MMO</observer>\n")
                        o.write("            </observers>\n")
                    elif "mtm" in file_name:
                        o.write("            <observers>\n")
                        o.write("                <observer>MTM</observer>\n")
                        o.write("            </observers>\n")
                if "<description>" in line and record:
                    text = line.split("<description>")[-1]
                    description = text.split("</description>")[0]
                    o.write(f"            <description>{description}\n")
                    o.write(f"            </description>\n")
                    o.write(f"        </kernel>\n")
