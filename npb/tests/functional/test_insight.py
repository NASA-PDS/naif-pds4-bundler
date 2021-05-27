"""
This test is used to compare labels with the test labels.
"""
import os
import glob
import shutil
import unittest

from unittest import TestCase
from npb.main import main

class TestInsight(TestCase):

    def test_insight_basic(self):
        '''
        Test complete pipeline with basic Insight data (no binary kernels,
        no SCLK).

        '''

        config = '../config/insight.xml'
        plan   = '../data/insight_release_26.plan'
        faucet = 'final'

        dirs = ['working', 'staging']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)
        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copy2('../data/insight_release_basic.kernel_list',
                    'working/insight_release_07.kernel_list')

        shutil.copytree('../data/insight', 'insight')
        shutil.copytree('../data/kernels', 'kernels_ladee')

        with open('../data/insight.list', 'r') as i:
            for line in i:
                with open(f'insight/insight_spice/{line[0:-1]}', 'w') as fp:
                    pass

        main(config, plan, faucet, verbose=True, log=True, diff='all')

        #
        # Cleanup test facility
        #
        #dirs = ['working', 'staging', 'insight', 'kernels']
        #for dir in dirs:
        #    shutil.rmtree(dir, ignore_errors=True)


    def test_insight_diff_previous_none(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The reporting of diff files is set to none; therefore
        only the files that are diff'ed by default are reported.
        The pipeline stops before copying the previous increment files
        to the staging area.
        '''

        config = '../config/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        for file in glob.glob('data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,
                        'working')
        os.mkdir('staging')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=False, log=True, diff='')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_insight_diff_previous_all(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area.
        '''

        config = '../config/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,
                        'working')
        os.mkdir('staging')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=False, log=True, diff='all')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_insight_diff_previous_files(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area.
        '''

        config = '../config/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,
                        'working')
        os.mkdir('staging')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=False, log=True, diff='files')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_insight_diff_previous_log(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area.
        '''

        config = '../config/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,
                        'working')
        os.mkdir('staging')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=False, log=True, diff='log')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_insight_diff_templates(self):
        '''
        Testcase in which products are compared with the templates to
        generate the products and to similar kernels; the final directory
        files are not present. The pipeline stops before copying the
        previous increment files to the staging area.
        '''

        config = '../config/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,'working')
        os.mkdir('staging')
        os.mkdir('insight')
        os.mkdir('insight/insight_spice')
        os.mkdir('insight/insight_spice/spice_kernels')
        os.mkdir('insight/insight_spice/spice_kernels/sclk')
        shutil.copy2('../data/insight/insight_spice/spice_kernels/sclk/'
                     'marcob_fake_v01.xml',
                     'insight/insight_spice/spice_kernels/sclk')
        with open(
            f'insight/insight_spice/spice_kernels/sclk/marcob_fake_v01.tsc',
            'w') as fp:
            pass

        main(config, plan, faucet, silent=False, log=True, diff='all')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_insight_files_in_staging(self):
        '''
        Testcase in which products are already present in the staging
        directory. The log provides error messages but the process is not
        stopped. Process is finished before moving all files to the final
        area.
        '''

        config = '../config/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,'working')
        shutil.copytree('../data/insight', 'staging')
        with open('../data/insight.list', 'r') as i:
            for line in i:
                with open(f'staging/insight_spice/{line[0:-1]}', 'w') as fp:
                    pass
        with open('../data/insight_08.list', 'r') as i:
            for line in i:
                with open(f'staging/insight_spice/{line[0:-1]}', 'w') as fp:
                    pass


        os.mkdir('insight')

        main(config, plan, faucet, silent=False, log=True, diff='all')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_insight_no_spiceds(self):
        '''
        Testcase for when the spiceds file is not provided
        via configuration and the previous version is not available.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<spiceds>../data/spiceds_test.html</spiceds>' in line:
                        n.write('        <spiceds></spiceds>\n')
                    else:
                        n.write(line)

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,'working')


        os.mkdir('insight')

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=False, log=True,
                 diff='all')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_insight_previous_spiceds(self):
        '''
        Testcase for when the spiceds file is not provided
        via configuration but the previous version is  available.

        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        shutil.copytree('../data/insight', 'insight')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<spiceds>../data/spiceds_test.html</spiceds>' in line:
                        n.write('        <spiceds></spiceds>\n')
                    else:
                        n.write(line)

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,'working')

        main(updated_config, plan, faucet, silent=False, log=True, diff='all')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)
        return


    def test_insight_start_finish(self):
        '''
        Testcase providing increment start and finish times via
        configuration.
        '''

        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        shutil.copytree('../data/insight', 'insight')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,'working')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<release_date></release_date>' in line:
                        n.write('        '
                                '<release_date>2021-04-04</release_date>\n')
                    elif '<increment_start></increment_start>' in line:
                        n.write('        '
                                '<increment_start>2021-04-03T20:53:00Z'
                                '</increment_start>\n')
                    elif '<increment_finish></increment_finish>' in line:
                        n.write('        '
                                '<increment_finish>'
                                '2021-04-23T20:53:00Z</increment_finish>\n')
                    else:
                        n.write(line)

        main(updated_config, plan, faucet, silent=False, log=True, diff='')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)
        return


    def test_insight_incorrect_times(self):
        '''
        Testcase providing increment start and finish times via
        configuration.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        shutil.copytree('../data/insight', 'insight')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,'working')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<increment_finish></increment_finish>' in line:
                        n.write('        '
                                '<increment_finish>2021-04-23T20:53:00'
                                '</increment_finish>\n')
                    elif '<increment_finish></increment_finish>' in line:
                        n.write('        '
                                '<increment_finish>2021-04-23T20:53:00Z'
                                '</increment_finish>\n')
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=False, log=True,
                 diff='')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<increment_finish></increment_finish>' in line:
                        n.write('        '
                                '<increment_finish>2021-04-23T20:53:00Z'
                                '</increment_finish>\n')
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=False, log=True,
                 diff='')


        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<release_date></release_date>' in line:
                        n.write('        <release_date>2021</release_date>\n')
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=False, log=True,
                 diff='')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)
        return


    def test_insight_no_readme(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'final'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,'working')


        os.mkdir('insight')

        main(config, plan, faucet, silent=False, log=True, diff='all')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_insight_mk_input(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config         = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan           = 'working/insight.plan'
        faucet         = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        os.mkdir('staging')
        os.mkdir('insight')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<file></file>' in line:
                        n.write('            '
                                '<file>working/insight_2021_v08.tm</file>\n')
                    else:
                        n.write(line)

        with open('working/insight_2021_v08.tm', 'w') as p:
            p.write('test')

        with open('working/insight.plan', 'w') as p:
            p.write('nsy_sclkscet_00019.tsc')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,'working')

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=False, log=True,
                 diff='all')


        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<file></file>' in line:
                        n.write('            <file>../data/insight_v08.tm'
                                '</file>\n')
                    else:
                        n.write(line)

        os.remove('working/insight_release_08.kernel_list')

        main(updated_config, plan, faucet, silent=False, log=True, diff='all',
             verbose=True)

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_insight_mks_input(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config         = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan           = 'working/insight.plan'
        faucet         = 'staging'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('working')
        os.mkdir('staging')
        os.mkdir('insight')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<file></file>' in line:
                        n.write('            '
                                '<file>working/insight_v08.tm</file>\n')
                        n.write('            '
                                '<file>working/insight_v09.tm</file>\n')
                    else:
                        n.write(line)

        with open('working/insight_v08.tm', 'w') as p:
            p.write('test')
        with open('working/insight_v09.tm', 'w') as p:
            p.write('test')

        with open('working/insight.plan', 'w') as p:
            p.write('nsy_sclkscet_00019.tsc')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,'working')

        main(updated_config, plan, faucet, verbose=True, log=True, diff='all')

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

if __name__ == '__main__':

    unittest.main()