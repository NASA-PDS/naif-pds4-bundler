import os
import shutil
import glob
from subprocess import Popen, PIPE, list2cmdline


def slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, 
                  start_time, stop_time, timetype="UTC"):
    '''
    This script creates a new SPICE kernel data set cropped between two dates.
    The intended usage of this tool is to support the testing of 
    naif-pds4-bundle.

    Note that this tool requires the NAIF utilities CKSLICER and SPKMERGE
    to be setup in the system and to be included in the PATH.

    The tool is based on the 'SKD SLICER TOOL' by Ricardo Valles (ESS/ESAC)

    :param kernels_dir: 
    :param out_kernels_dir: 
    :param lsk_file: 
    :param sclk_file: 
    :param start_time: 
    :param stop_time: 
    :param timetype: 
    :return: 
    '''
    #
    # Remove out_kernels_dir if exist, and create it again
    #
    if os.path.isdir(out_kernels_dir):
        shutil.rmtree(out_kernels_dir)
    os.mkdir(out_kernels_dir)

    #
    # List all kernels
    #
    skd_files = list(glob.iglob(kernels_dir + '/**/*', recursive=True))

    # Check contents file by file
    for filename in skd_files:

        if not 'former_versions' in filename:
            output_filename = filename.replace(kernels_dir, out_kernels_dir)

            if os.path.isdir(filename):
                os.mkdir(output_filename)
            else:
                extension = str(os.path.splitext(filename)[1]).lower()
                if extension == ".bc":
                    #
                    #  If it is a CK kernel, run ckslicer
                    #
                    ckslicer(lsk_file, sclk_file, filename, output_filename, 
                             start_time, stop_time, timetype)
                elif extension == ".bsp":
                    #
                    #  Its a SPK kernel, run spkmerge
                    #
                    spkmerge(lsk_file, filename, output_filename, start_time, 
                             stop_time)
                elif not extension == ".lbl":
                    #
                    # Copy kernel to destination
                    #
                    shutil.copyfile(filename, output_filename)
                    
    return


def ckslicer(lsk_file, sclk_file, input_ck, output_ck, start_time, stop_time, 
             timetype="UTC", naif_id=None):

    #
    # Check if ck_file exists and remove it
    #
    if os.path.isfile(output_ck):
        os.remove(output_ck)

    #
    # Prepare params for CKSLICER
    #
    params = ['ckslicer',
              '-lsk', lsk_file,
              '-sclk', sclk_file,
              '-inputck', input_ck,
              '-outputck ', output_ck,
              '-timetype', timetype,
              '-start', start_time,
              '-stop', stop_time]
    if naif_id:
        params.extend(['-id', naif_id])

    print("ckslicer Command ->")
    print(list2cmdline(params))
    print(" ")

    #
    # Run CKSLICER 
    #
    p = Popen(params, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()

    print("ckslicer Results ->")
    print(output.decode("utf-8"))
    print(" ")

    #
    # Return process output
    #
    return {'returnCode': p.returncode, 
            'stdout': output.decode("utf-8"), 
            'stderr': err.decode("utf-8")}


def spkmerge(lsk_file, input_spk, output_spk, start_time, stop_time):

    #
    # Check if ck_file exists and remove it
    #
    if os.path.isfile(output_spk):
        os.remove(output_spk)
    
    #
    # Prepare SPK Merge setup file
    #
    spk_dir = os.path.dirname(output_spk)
    spk_merge_setup_file = os.path.join(spk_dir, "spk_mrg.setup")
    spk_merge_setup = open(spk_merge_setup_file, 'w+')
    spk_merge_setup.write(f"LEAPSECONDS_KERNEL     = {lsk_file}\n")
    spk_merge_setup.write(f"SPK_KERNEL             = {output_spk}\n")
    spk_merge_setup.write(f"   SOURCE_SPK_KERNEL   = {input_spk}\n")
    spk_merge_setup.write(f"      BEGIN_TIME       = {start_time}\n")
    spk_merge_setup.write(f"      END_TIME         = {stop_time}\n")
    spk_merge_setup.close()

    #
    # Prepare params for SPKMERGE
    #
    params = ['spkmerge', spk_merge_setup_file]

    print("spkmerge Command ->")
    print(list2cmdline(params))
    print(" ")

    #
    # Run SPKMERGE
    #
    p = Popen(params, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()

    print("spkmerge Results ->")
    print(output.decode("utf-8"))
    print(" ")

    #
    # Remove SPK Merge setup file
    #
    if os.path.isfile(spk_merge_setup_file):
        os.remove(spk_merge_setup_file)

    #
    # Return process output
    #
    return {'returnCode': p.returncode, 
            'stdout': output.decode("utf-8"), 
            'stderr': err.decode("utf-8")}