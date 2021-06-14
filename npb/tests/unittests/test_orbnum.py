"""Functional tests for the List generator.
"""
import os
import shutil
import unittest

from unittest import TestCase
from npb.main import main


class TestPlan(TestCase):
    """
    Test family for the plan generation.
    The data sources are contained in the::

        data/

    directory.

    """

    def test_pds4_maven_orbnum_coverage_user_spk(self):
        """
        Test for meta-kernel configuration loading error cases.
        """
        config = '../config/maven.xml'
        faucet = 'staging'
        plan = 'maven_orbnum.plan'

        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.rmtree('misc', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/misc', 'misc')
        os.mkdir('working')

        with open(plan, 'w') as p:
            p.write('maven_orb_rec_210101_210401_v1.orb')
            p.write('\nmaven_orb_rec_210101_210401_v1.nrb')

        #
        # Test preparation
        #
        dirs = ['staging', 'maven']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        main(config, plan, faucet, silent=True)

        #
        # Cleanup test facility
        #
        dirs = ['working', 'staging', 'maven', 'kernels', 'misc']
        #for dir in dirs:
        #   shutil.rmtree(dir, ignore_errors=True)

        return None

    def test_pds4_maven_orbnum_coverage_increment_spk(self):
        '''
         Testcase for when the readme file is not present.
         '''
        config = '../config/maven.xml'
        updated_config = 'working/maven.xml'
        faucet = 'staging'
        plan = 'maven_orbnum.plan'

        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.rmtree('misc', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/misc', 'misc')
        os.mkdir('working')

        with open(plan, 'w') as p:
            p.write('maven_orb_rec_210101_210401_v2.bsp')
            p.write('\nmaven_orb_rec_210101_210401_v1.orb')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<kernel>../data/kernels/spk/' \
                       'maven_orb_rec_210101_210401_v2.bsp</kernel>' in line:
                        n.write('                '
                                '<kernel>maven_orb_rec_[0-9]{6}_[0-9]{6}_'
                                'v[0-9].bsp</kernel>\n')
                    else:
                        n.write(line)

        #
        # Test preparation
        #
        dirs = ['staging', 'maven']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        main(updated_config, plan, faucet, silent=True)

        #
        # Cleanup test facility
        #
        dirs = ['working', 'staging', 'maven', 'kernels', 'misc']
        #for dir in dirs:
        #   shutil.rmtree(dir, ignore_errors=True)

        return None

    def test_pds4_maven_orbnum_coverage_archived_spk(self):

        '''
         Testcase for when the readme file is not present.
         '''
        config = '../config/maven.xml'
        updated_config = 'working/maven.xml'
        faucet = 'staging'
        plan = 'maven_orbnum.plan'

        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.rmtree('misc', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/misc', 'misc')
        os.mkdir('working')

        with open(plan, 'w') as p:
            p.write('\nmaven_orb_rec_210101_210401_v1.orb')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<kernel>../data/kernels/spk/' \
                       'maven_orb_rec_210101_210401_v2.bsp</kernel>' in line:
                        n.write('                '
                                '<kernel>maven_orb_rec_[0-9]{6}_[0-9]{6}_'
                                'v[0-9].bsp</kernel>\n')
                    else:
                        n.write(line)

        #
        # Test preparation
        #
        dirs = ['staging', 'maven', 'maven/maven_spice',
                'maven/maven_spice/spice_kernels',
                'maven/maven_spice/spice_kernels/spk']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)


        shutil.copy2('../data/kernels/spk/maven_orb_rec_210101_210401_v2.bsp',
                     'maven/maven_spice/spice_kernels/spk/')

        main(updated_config, plan, faucet, silent=True)

        #
        # Cleanup test facility
        #
        dirs = ['working', 'staging', 'maven', 'kernels', 'misc']
        for dir in dirs:
           shutil.rmtree(dir, ignore_errors=True)

        return None


    def test_pds4_maven_orbnum_coverage_lookup_table(self):
        '''
         Testcase for when the readme file is not present.
         '''
        config = '../config/maven.xml'
        updated_config = 'working/maven.xml'
        faucet = 'staging'
        plan = 'maven_orbnum.plan'

        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.rmtree('misc', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/misc', 'misc')
        os.mkdir('working')

        with open(plan, 'w') as p:
            p.write('\nmaven_orb_rec_210101_210401_v1.orb')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<kernel>../data/kernels/spk/' \
                       'maven_orb_rec_210101_210401_v2.bsp</kernel>' in line:
                        n.write(
                            '<lookup_table>\n'
                            '  <file name='
                            '"maven_orb_rec_210101_210401_v1.orb">\n'
                            '     <start>2021-01-01T00:00:00.000Z</start>\n'
                            '     <finish>2021-04-01T01:00:00.000Z</finish>\n'
                            '  </file>\n'
                            '</lookup_table>\n')
                    else:
                        n.write(line)

        #
        # Test preparation
        #
        dirs = ['staging', 'maven']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        main(updated_config, plan, faucet, silent=True)

        #
        # Cleanup test facility
        #

        dirs = ['working', 'staging', 'maven', 'kernels', 'misc']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        return None


    def test_pds4_maven_orbnum_coverage_estimate(self):
        """
        Test for meta-kernel configuration loading error cases.
        """
        config = '../config/maven.xml'
        updated_config = 'working/maven.xml'
        faucet = 'staging'
        plan = 'maven_orbnum.plan'

        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.rmtree('misc', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/misc', 'misc')
        os.mkdir('working')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<kernel>../data/kernels/spk/' \
                       'maven_orb_rec_210101_210401_v2.bsp</kernel>' in line:
                        n.write('')
                    else:
                        n.write(line)

        with open(plan, 'w') as p:
            p.write('maven_orb_rec_210101_210401_v1.orb')

        #
        # Test preparation
        #
        dirs = ['staging', 'maven']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        main(updated_config, plan, faucet, silent=True)

        #
        # Cleanup test facility
        #
        dirs = ['working', 'staging', 'maven', 'kernels', 'misc']
        for dir in dirs:
           shutil.rmtree(dir, ignore_errors=True)

        return None

    def test_pds3_orbnum_files(self):

        config = '../config/maven.xml'
        updated_config = 'working/maven.xml'
        faucet = 'staging'
        plan = 'maven_orbnum.plan'

        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.rmtree('misc', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/misc', 'misc')
        os.mkdir('working')

        orbnum_list = ['cas_v40.orb',
                      'clem.orb',
                      'dawn_vesta_iau_v05.nrb',
                      'grail_v02.nrb',
                      'juno_rec_orbit_v08.orb',
                      'lro_v45.nrb',
                      'm01_ext64.nrb',
                      'mgs_ext26_v2.nrb',
                      'mro_psp58.nrb',
                      'msgr_040803_150430_150430_od431sc_2.orb',
                      'ormm_merged_00966.orb',
                      'orvm_t19___________00001.orb',
                      'vco_v05.orb',
                      'vo1_rcon.orb',
                      'vo2_rcon.orb']

        orbnum_config = ''
        with open(plan, 'w') as p:
            for file in orbnum_list:
                p.write(f'{file}\n')
                orbnum_config += \
                  f'<orbnum pattern="{file}">\n' \
                   "    <event_detection_frame>\n" \
                   "        <spice_name>IAU_MARS</spice_name>\n" \
                   "        <description>Mars body-fixed frame</description>\n" \
                   "    </event_detection_frame>\n" \
                   "    <header_start_line>1</header_start_line >\n" \
                   "    <pck>\n" \
                   "        <kernel_name>pck0010.tpc</kernel_name>\n" \
                   "        <description>IAU 2009 report</description>\n" \
                   "    </pck>\n" \
                   "    <coverage>\n" \
                   "    </coverage>\n" \
                   "</orbnum>\n"

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<kernel>../data/kernels/spk/' \
                       'maven_orb_rec_210101_210401_v2.bsp</kernel>' in line:
                        n.write('')
                    elif '</orbit_number_file>' in line:
                        n.write(orbnum_config)
                        n.write('</orbit_number_file>')
                    else:
                        n.write(line)

        #
        # Test preparation
        #
        dirs = ['staging', 'maven']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        main(updated_config, plan, faucet, silent=True)

        #
        # Cleanup test facility
        #
        dirs = ['working', 'staging', 'maven', 'kernels', 'misc']
        for dir in dirs:
           shutil.rmtree(dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()