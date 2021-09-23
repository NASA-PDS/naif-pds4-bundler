#
# @author: Marc Costa Sitja (JPL)
#
# This script has been used to generate the naif-pds4-bundler
# insight_kernel_list.json configuration file from the insight
# useful_loops.csh file originally from BVS.
#
# WARNING: patterns need to be tuned and entered manually as well.
#
with open("maven_kernel_list.xml", "w+") as o:

    with open("useful_loops.csh", "r") as f:
        o.write("{\n")
        for line in f:
            if "`echo $FF | grep -c '^" in line:
                text = line.split("'")[1][1:-1]

                o.write(f'  <kernel pattern="{text}">\n')

                if (".bsp" in text) or (".bc" in text) or (".tm" in text):
                    o.write(f"      <mklabel_options></mklabel_options>\n")
                else:
                    o.write("      <mklabel_options>DEF_TIMES</mklabel_options>\n")

            if 'echo "DESCRIPTION' in line:
                text = line.split("=")[-1].strip()[:-1]
                o.write(
                    f"      <description>{text}\n      </description>\n  </kernel>\n"
                )
