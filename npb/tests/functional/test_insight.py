import os
import glob
import shutil
import unittest
from unittest import TestCase
from npb.main import main


class TestINSIGHT(TestCase):
    '''
    Test Family for INSIGHT archive generation. 
    '''

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.
         
        '''
        print(f"NPB - Functional Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_insight_basic(self):
        '''
        Test complete pipeline with basic Insight data (no binary kernels,
        no SCLK).

        '''
        config = '../config/insight.xml'
        plan = '../data/insight_release_26.plan'
        faucet = 'final'

        os.mkdir('working')
        os.mkdir('staging')
        shutil.copy2('../data/insight_release_basic.kernel_list',
                     'working/insight_release_07.kernel_list')
        shutil.copytree('../data/insight', 'insight')
        shutil.copytree('../data/kernels', 'kernels')

        with open('../data/insight.list', 'r') as i:
            for line in i:
                with open(f'insight/insight_spice/{line[0:-1]}', 'w'):
                    pass

        main(config, plan, faucet, silent=False, log=True, diff='all')

    def test_insight_diff_previous_none(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The reporting of diff files is set to none; therefore
        only the files that are diff'ed by default are reported.
        The pipeline stops before copying the previous increment files
        to the staging area.
        '''

        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'
        
        os.mkdir('staging')
        os.mkdir('working')
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,
                         'working')
        shutil.copytree('../data/insight', 'insight')


        main(config, plan, faucet, silent=False, log=True, diff='')

    def test_insight_diff_previous_all(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area.
        '''

        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.mkdir('staging')
        os.mkdir('working')
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,
                         'working')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=False, log=True, diff='all')

    def test_insight_diff_previous_files(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area.
        '''

        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.mkdir('staging')
        os.mkdir('working')
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=False, log=True, diff='files')

    def test_insight_diff_previous_log(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area.
        '''
        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.mkdir('staging')
        os.mkdir('working')
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=False, log=True, diff='log')

    def test_insight_diff_templates(self):
        '''
        Testcase in which products are compared with the templates to
        generate the products and to similar kernels; the final directory
        files are not present. The pipeline stops before copying the
        previous increment files to the staging area.
        '''
        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.mkdir('staging')
        os.mkdir('working')
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        os.mkdir('insight')
        os.mkdir('insight/insight_spice')
        os.mkdir('insight/insight_spice/spice_kernels')
        os.mkdir('insight/insight_spice/spice_kernels/sclk')
        shutil.copy2('../data/insight/insight_spice/spice_kernels/sclk/'
                     'marcob_fake_v01.xml',
                     'insight/insight_spice/spice_kernels/sclk')
        with open(
                f'insight/insight_spice/spice_kernels/sclk/'
                f'marcob_fake_v01.tsc', 'w'):
            pass

        main(config, plan, faucet, silent=False, log=True, diff='all')

    def test_insight_files_in_staging(self):
        '''
        Testcase in which products are already present in the staging
        directory. The log provides error messages but the process is not
        stopped. Process is finished before moving all files to the final
        area.
        '''

        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.mkdir('working')
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')
        shutil.copytree('../data/insight', 'staging')
        with open('../data/insight.list', 'r') as i:
            for line in i:
                with open(f'staging/insight_spice/{line[0:-1]}', 'w'):
                    pass
        with open('../data/insight_08.list', 'r') as i:
            for line in i:
                with open(f'staging/insight_spice/{line[0:-1]}', 'w'):
                    pass

        os.mkdir('insight')

        main(config, plan, faucet, silent=False, log=True, diff='all')

    def test_insight_no_spiceds(self):
        '''
        Testcase for when the spiceds file is not provided
        via configuration and the previous version is not available.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        shutil.copytree('../data/kernels', 'kernels')
        
        os.mkdir('staging')
        os.mkdir('working')
        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<spiceds>../data/spiceds_test.html</spiceds>' in line:
                        n.write('        <spiceds></spiceds>\n')
                    else:
                        n.write(line)

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=False, log=True,
                 diff='all')

    def test_insight_previous_spiceds(self):
        '''
        Testcase for when the spiceds file is not provided
        via configuration but the previous version is  available.

        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.mkdir('staging')
        os.mkdir('working')
        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/insight', 'insight')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<spiceds>../data/spiceds_test.html</spiceds>' in line:
                        n.write('        <spiceds></spiceds>\n')
                    else:
                        n.write(line)

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        main(updated_config, plan, faucet, silent=False, log=True, diff='all')

    def test_insight_start_finish(self):
        '''
        Testcase providing increment start and finish times via
        configuration.
        '''

        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'
        
        os.mkdir('staging')
        os.mkdir('working')

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/insight', 'insight')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

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

    def test_insight_incorrect_times(self):
        '''
        Testcase providing increment start and finish times via
        configuration.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.mkdir('staging')
        os.mkdir('working')
        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/insight', 'insight')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

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

    def test_insight_no_readme(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'final'
        
        os.mkdir('working')
        os.mkdir('staging')
        
        shutil.copytree('../data/kernels', 'kernels')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        os.mkdir('insight')

        main(config, plan, faucet, silent=False, log=True, diff='all')

    def test_insight_mk_input(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = 'working/insight.plan'
        faucet = 'staging'

        os.mkdir('working')
        os.mkdir('staging')
        shutil.copytree('../data/kernels', 'kernels')
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
            shutil.copy2(file, 'working')

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

    def test_insight_mks_input(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = 'working/insight.plan'
        faucet = 'staging'
        
        os.mkdir('working')
        os.mkdir('staging')
        shutil.copytree('../data/kernels', 'kernels')
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
            shutil.copy2(file, 'working')

        main(updated_config, plan, faucet, verbose=True, log=True, diff='all')


if __name__ == '__main__':
    unittest.main()
