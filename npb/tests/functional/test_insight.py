import os
import glob
import shutil
import unittest
import spiceypy
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

        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            
        cls.silent = True
        cls.log = True

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")
        
        os.chdir(os.path.dirname(__file__))

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        if os.path.exists('staging'):
            os.remove('staging')

    def test_insight_basic(self):
        '''
        Test complete pipeline with basic Insight data (no binary kernels,
        no SCLK).

        '''
        config = '../config/insight.xml'
        plan = '../data/insight_release_26.plan'
        faucet = 'final'

        os.makedirs('working', mode=0o777, exist_ok=True)
        os.makedirs('staging', mode=0o777, exist_ok=True)
        shutil.copy2('../data/insight_release_basic.kernel_list',
                     'working/insight_release_07.kernel_list')
        shutil.rmtree('insight', ignore_errors=True)
        shutil.copytree('../data/insight', 'insight')
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.copytree('../data/kernels', 'kernels')
        
        with open('../data/insight.list', 'r') as i:
            for line in i:
                with open(f'insight/insight_spice/{line[0:-1]}', 'w'):
                    pass

        main(config, plan, faucet, silent=self.silent, log=self.log)

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
        
        os.makedirs('staging', mode=0o777)
        os.makedirs('working', mode=0o777)
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,
                         'working')
        shutil.copytree('../data/insight', 'insight')
    

        main(config, plan, faucet, silent=self.silent, log=self.log, diff='')

    def test_insight_diff_previous_all(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area.
        '''

        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.makedirs('staging', mode=0o777)
        os.makedirs('working', mode=0o777)
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file,
                         'working')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=self.silent, log=self.log, diff='all')

    def test_insight_diff_previous_files(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area.
        '''

        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.makedirs('staging', mode=0o777)
        os.makedirs('working', mode=0o777)
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=self.silent, log=self.log, 
             diff='files')

    def test_insight_diff_previous_log(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area.
        '''
        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.makedirs('staging', mode=0o777)
        os.makedirs('working', mode=0o777)
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')
        shutil.copytree('../data/insight', 'insight')

        main(config, plan, faucet, silent=self.silent, log=self.log, diff='log')

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

        os.makedirs('staging', mode=0o777)
        os.makedirs('working', mode=0o777)
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        os.makedirs('insight/insight_spice/spice_kernels/sclk', mode=0o777)
        shutil.copy2('../data/insight/insight_spice/spice_kernels/sclk/'
                     'marcob_fake_v01.xml',
                     'insight/insight_spice/spice_kernels/sclk')
        with open(f'insight/insight_spice/spice_kernels/sclk/'
                f'marcob_fake_v01.tsc', 'w'):
            pass

        main(config, plan, faucet, silent=self.silent, log=self.log, diff='all')

    def test_insight_files_in_staging(self):
        '''
        Testcase in which products are already present in the staging
        directory. The log provides error messages but the process is not
        stopped. Process is finished before moving all files to the final
        area.
        
        The testcase also tests the obtention of checksums from already existing
        labels.
        '''

        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.makedirs('working', mode=0o777)
        shutil.copytree('../data/kernels', 'kernels')
        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')
        shutil.copytree('../data/insight', 'staging')

        #
        # The files that are added on top of the staging area need to have
        # their coverage extracted. Those are the files provided in the
        # insight_08.list.
        #
        with open('../data/insight.list', 'r') as i:
            for line in i:
                with open(f'staging/insight_spice/{line[0:-1]}', 'w'):
                    pass
        
        shutil.copy2('../data/kernels/sclk/NSY_SCLKSCET.00019.tsc',
            'staging/insight_spice/spice_kernels/sclk/nsy_sclkscet_00019.tsc')

        shutil.copy2('../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc',
                     'staging/insight_spice/spice_kernels/ck/')
        shutil.copy2('../data/kernels/ck/insight_ida_enc_200829_201220_v1.xml',
                     'staging/insight_spice/spice_kernels/ck/')
        
        shutil.copy2('../data/kernels/ck/insight_ida_pot_200829_201220_v1.bc',
                     'staging/insight_spice/spice_kernels/ck/')
        shutil.copy2('../data/kernels/ck/insight_ida_pot_200829_201220_v1.xml',
                     'staging/insight_spice/spice_kernels/ck/')
        
        shutil.copy2('../data/kernels/mk/insight_v08.tm',
                     'staging/insight_spice/spice_kernels/mk/')
        
        os.makedirs('insight', mode=0o777)

        main(config, plan, faucet, silent=self.silent, log=self.log)

    def test_insight_previous_spiceds(self):
        '''
        Testcase for when the spiceds file is not provided
        via configuration but the previous version is  available.

        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        print(os.getcwd())

        os.makedirs('staging', mode=0o777, exist_ok=True)
        os.makedirs('working', mode=0o777, exist_ok=True)
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.copytree('../data/kernels', 'kernels', )
        shutil.copytree('../data/insight', 'insight')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<spiceds>../data/spiceds_test.html</spiceds>' in line:
                        n.write('        <spiceds> </spiceds>\n')
                    else:
                        n.write(line)

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        main(updated_config, plan, faucet, silent=self.silent, log=self.log, 
             diff='all')

    def test_insight_start_finish(self):
        '''
        Testcase providing increment start and finish times via
        configuration.
        '''

        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'
        
        os.makedirs('staging', mode=0o777)
        os.makedirs('working', mode=0o777)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/insight', 'insight')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '</readme>' in line:
                        n.write('</readme>\n'
                                '<release_date>2021-04-04</release_date>\n'
                                '<increment_start>2021-04-03T20:53:00Z'
                                '</increment_start>\n'
                                '<increment_finish>'
                                '2021-04-23T20:53:00Z</increment_finish>\n')
                    else:
                        n.write(line)

        main(updated_config, plan, faucet, silent=self.silent, log=self.log, 
             diff='')

    def test_insight_incorrect_times(self):
        '''
        Testcase providing increment start and finish times via
        configuration.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'staging'

        os.makedirs('staging', mode=0o777)
        os.makedirs('working', mode=0o777)
        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/insight', 'insight')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<mission_start>2018-05-05T11:05:00Z</mission_start>' \
                            in line:
                        n.write('        '
                                '<mission_start>2018-05-05T11:05:00'
                                '</mission_start>\n')
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=self.silent, log=self.log,
                 diff='')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '</readme>' in line:
                        n.write('        </readme>\n'
                                '        <release_date>2021</release_date>\n')
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=self.silent, log=self.log,
                 diff='')

    def test_insight_mk_input(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = 'working/insight.plan'
        faucet = 'staging'

        os.makedirs('working', mode=0o777)
        os.makedirs('staging', mode=0o777)
        shutil.copytree('../data/kernels', 'kernels')
        os.makedirs('insight', mode=0o777)

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '        <coverage_kernels>' in line:
                        n.write('        <mk_inputs>\n'
                                '            <file>working/insight_2021_v08.tm'
                                '</file>\n'
                                '        </mk_inputs>\n'
                                '        <coverage_kernels>\n')
                    else:
                        n.write(line)

        with open('working/insight_2021_v08.tm', 'w') as p:
            p.write('test')

        with open('working/insight.plan', 'w') as p:
            p.write('nsy_sclkscet_00019.tsc')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=self.silent, 
                 log=self.log, diff='all')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<file> </file>' in line:
                        n.write('            <file>../data/insight_v08.tm'
                                '</file>\n')
                    else:
                        n.write(line)

        os.remove('working/insight_release_08.kernel_list')

        main(updated_config, plan, faucet, silent=self.silent, log=self.log, 
             diff='all')
        

    def test_insight_mks_input(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = 'working/insight.plan'
        faucet = 'staging'
        
        os.makedirs('working', mode=0o777)
        os.makedirs('staging', mode=0o777)
        shutil.copytree('../data/kernels', 'kernels')
        os.makedirs('insight', mode=0o777)

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '        <coverage_kernels>' in line:
                        n.write('        <mk_inputs>\n'
                                '<file>working/insight_v08.tm</file>\n'
                                '<file>working/insight_v09.tm</file>\n'
                                '        </mk_inputs>\n'
                                '        <coverage_kernels>\n')
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

        with self.assertRaises(spiceypy.utils.exceptions.SpiceFILEREADFAILED):
            main(updated_config, plan, faucet, silent=self.silent, log=self.log, 
             diff='all')
            
    def test_insight_mks_inputs_coverage(self):
        '''
        Testcase for when one of the meta-kernels does not include the SPK/CK
        that determines the coverage of the meta-kernel (implemented after
        M2020 Chronos meta-kernel generation.).
        
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_00.plan'
        faucet = 'final'

        dirs = ['working', 'staging', 'insight']
        for dir in dirs:
            os.makedirs(dir, 0o766, exist_ok=True)
        
        shutil.copy2('../data/insight_release_basic.kernel_list',
                     'working/insight_release_07.kernel_list')
        shutil.rmtree('insight')
        shutil.copytree('../data/insight', 'insight')
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.copytree('../data/kernels', 'kernels')
        os.remove('kernels/mk/insight_v08.tm')
        shutil.copy2('../data/insight_v00.tm',
                     'working/insight_v00.tm')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '        <coverage_kernels>' in line:
                        n.write('        <mk_inputs>\n'
                                '<file>working/insight_v00.tm</file>\n'
                                '        </mk_inputs>\n'
                                '        <coverage_kernels>\n')
                    else:
                        n.write(line)

        main(updated_config, plan, faucet, silent=self.silent, log=self.log)

    def test_insight_mks_coverage_in_final(self):
        '''
        Testcase for when one of the meta-kernels does not include the SPK/CK
        that determines the coverage of the meta-kernel (implemented after
        M2020 Chronos meta-kernel generation.).

        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_00.plan'
        faucet = 'final'

        dirs = ['working', 'staging', 'insight']
        for dir in dirs:
            os.makedirs(dir, 0o766, exist_ok=True)

        shutil.copy2('../data/insight_release_basic.kernel_list',
                     'working/insight_release_07.kernel_list')
        shutil.rmtree('insight')
        shutil.copytree('../data/insight', 'insight')
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.copytree('../data/kernels', 'kernels')
        shutil.copy2('../data/insight_v08.tm',
                     'working/insight_v08.tm')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '        <coverage_kernels>' in line:
                        n.write('        <mk_inputs>\n'
                                '<file>working/insight_v08.tm</file>\n'
                                '        </mk_inputs>\n'
                                '        <coverage_kernels>\n')
                    else:
                        n.write(line)
                        
        main(updated_config, plan, faucet, silent=self.silent, log=self.log)
        print('')

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

        os.makedirs('staging', mode=0o777)
        os.makedirs('working', mode=0o777)
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
            main(updated_config, plan, faucet, silent=self.silent, log=self.log,
                 diff='all')

    def test_insight_no_readme(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'final'

        os.makedirs('working', mode=0o777)
        os.makedirs('staging', mode=0o777)

        shutil.copytree('../data/kernels', 'kernels')

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        os.makedirs('insight')

        main(config, plan, faucet, silent=self.silent, log=self.log, diff='all')
        
    def test_insight_no_kernels(self):
        '''
        Testcase for when the no kernels are provided as an input but an
        updated spiceds file is.
        '''
        config = '../config/insight.xml'
        faucet = 'final'

        os.makedirs('working', mode=0o777)
        os.makedirs('staging', mode=0o777)
        os.makedirs('kernels', mode=0o777)

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        os.makedirs('insight')

        main(config, plan=False, faucet=faucet, silent=self.silent, 
             log=self.log, diff='all')
        
    def test_insight_no_kernels_with_bundle(self):
        '''
        Testcase for when the no kernels are provided as an input but an
        updated spiceds file is.
        '''
        config = '../config/insight.xml'
        faucet = 'final'

        os.makedirs('working', mode=0o777)
        os.makedirs('staging', mode=0o777)
        os.makedirs('kernels', mode=0o777)

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        shutil.copytree('../data/insight', 'insight')

        main(config, plan=False, faucet=faucet, silent=self.silent, 
             log=self.log, diff='all')
        
    def test_insight_only_cheksums(self):
        '''
        Testcase for when the no inputs are provided at all but checksums
        are generated.
        '''
        config = '../config/insight.xml'
        updated_config = 'working/maven.xml'
        faucet = 'final'

        os.makedirs('working', mode=0o777)
        os.makedirs('staging', mode=0o777)
        os.makedirs('kernels', mode=0o777)

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        shutil.copytree('../data/insight', 'insight')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<spiceds>../data/spiceds_insight.html</spiceds>' in line:
                        n.write('            '
                                '<spiceds> </spiceds>\n')
                    else:
                        n.write(line)

        main(updated_config, plan=False, faucet=faucet, silent=self.silent, 
             log=self.log, diff='all')

    def test_insight_null_run(self):
        '''
        Testcase for when the no inputs are provided at all but checksums
        the checksum of the run is generated..
        '''
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        faucet = 'final'

        os.makedirs('working', mode=0o777, exist_ok=True)
        os.makedirs('staging', mode=0o777, exist_ok=True)
        shutil.rmtree('kernels', onerror=True)
        os.makedirs('kernels', mode=0o777, exist_ok=True)

        for file in glob.glob('../data/insight_release_0[0-7].kernel_list'):
            shutil.copy2(file, 'working')

        shutil.copytree('../data/insight', 'insight')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<spiceds>../data/spiceds_insight.html</spiceds>' in line:
                        n.write('            '
                                '<spiceds> </spiceds>\n')
                    else:
                        n.write(line)

        main(updated_config, plan=False, faucet=faucet, silent=self.silent, 
             log=self.log, diff='all')

            
if __name__ == '__main__':
    unittest.main()
