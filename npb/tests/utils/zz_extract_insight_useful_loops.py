#
# @author: Marc Costa Sitja (JPL)
#
# This script has been used to generate the naif-pds4-bundle
# insight_kernel_list.json configuration file from the insight
# useful_loops.csh file originally from BVS.
#
# WARNING: patterns need to be tuned and entered manually as well.
#
with open('insight_kernel_list.json', 'w+') as o:

    with open('insight_useful_loops.txt', 'r') as f:
        o.write('{\n')
        for line in f:
            if "`echo $FF | grep -c '^" in line:
                text = line.split("'")[1][1:-1]

                o.write(f'  "{text}": [\n')
                o.write('    {\n')

                if ('.bsp' in text) or ('.bc'in text) or ('.tm'in text):
                    o.write('      "mklabel_options": "",\n')
                else:
                    o.write('      "mklabel_options": "DEF_TIMES",\n')

            if 'echo "DESCRIPTION' in line:
                text = line.split('=')[-1].strip()[:-1]
                o.write(f'      "description": "{text}"\n')
                o.write('    }],\n')
#
# Please note that the last coma needs to be removed manually.
#
        o.write('}\n')
