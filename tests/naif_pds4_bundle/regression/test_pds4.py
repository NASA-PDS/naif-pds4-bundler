import os
import shutil
import unittest
import glob
from unittest import TestCase
from naif_pds4_bundle.__main__ import main  


class TestPDS4(TestCase):
    '''
    Note that EOL, label checksum tags and checksum files are not tested.
    '''
    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Regression Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ['working', 'staging', 'kernels', 'insight', 'ladee', 'kplo',
                'dart']
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
        
        dirs = ['working', 'staging', 'kernels', 'insight', 'ladee', 'kplo',
                'dart']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)
        mis = self.mission

        #
        # Compare the files. 
        #
        files = glob.glob(f'{mis}/{mis}_spice/**/*.xml', recursive=True)
        files += glob.glob(f'{mis}/{mis}_spice/**/*.csv', recursive=True)
        files += glob.glob(f'{mis}/{mis}_spice/**/*.html', recursive=True)
        files += glob.glob(f'{mis}/{mis}_spice/**/*.tm', recursive=True)
        files += glob.glob(f'{mis}/{mis}_spice/**/*.txt', recursive=True)
        for product in files:
            if os.path.isfile(product):
                test_product = product.replace(f'{mis}/','../data/regression/')
                
                with open(product) as ff:
                    fromlines = ff.read().splitlines()
                    fromlines = [item for item in fromlines if 
                                 ('checksum' not in item) and 
                                 ('file_size' not in item)]
                    fromlines = [item for item in fromlines if 'checksum' not in item]
                with open(test_product) as tf:
                    tolines = tf.read().splitlines()
                    tolines = [item for item in tolines if 
                                 ('checksum' not in item) and 
                                 ('file_size' not in item)]

                if fromlines != tolines:
                    print(f'Assertion False for: {product}')
                    self.assertTrue(False) 
        dirs = ['working', 'staging', 'kernels', mis]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

            pass
        
    def post_setUp(self):

        self.config = f'../config/{self.mission}.xml'
        self.updated_config = f'working/{self.mission}.xml'

        dirs = ['working', 'staging', self.mission]
        for dir in dirs:
            os.makedirs(dir, 0o766, exist_ok=True)

        with open(self.config, 'r') as c:
            with open(self.updated_config, 'w') as n:
                for line in c:
                    if '</readme>' in line:
                        n.write('        </readme>\n')
                        n.write('        <release_date>2021-06-25'
                                '</release_date>\n')
                        n.write('        <creation_date_time>'
                                '2021-06-25T08:00:00</creation_date_time>\n')
                    else:
                        n.write(line)

    def test_insight(self):
        '''
        Test to generate the DART archive. This test includes multiple
        targets and spacecrafts.
        '''
        self.mission = 'insight' 
        self.post_setUp()
        
        plan = '../data/insight_release_08.plan'

        shutil.copy2('../data/insight_release_basic.kernel_list',
                     'working/insight_release_07.kernel_list')
        shutil.rmtree('insight')
        shutil.copytree('../data/insight', 'insight')
        
        try:
            shutil.copytree('../data/kernels', 'kernels')
        except:
            pass

        main(self.updated_config, plan, silent=self.silent, log=self.log)

    def test_ladee(self):
        '''
        Test to generate the LADEE archive.
        '''
        self.mission = 'ladee'
        self.post_setUp()

        shutil.copytree('../data/regression/ladee_spice/spice_kernels', 
                        'kernels',
                        ignore=shutil.ignore_patterns('*.xml','*.csv'))

        main(self.updated_config, silent=self.silent, log=self.log)
        
    def test_kplo(self):
        '''
        Test to generate the KPLO archive (non-PDS archive).
        '''
        self.mission = 'kplo'
        self.post_setUp()

        shutil.copytree('../data/regression/kplo_spice/spice_kernels', 
                        'kernels',
                        ignore=shutil.ignore_patterns('*.xml','*.csv'))

        main(self.updated_config, silent=self.silent, log=self.log)

#    def test_dart(self):
#        '''
#        Test to generate the DART archive. This test includes multiple
#        targets and spacecrafts.
#        '''
#        config = '../config/dart.xml'
#
#        shutil.copytree('/Users/mcosta/workspace/dart/DART/kernels/','kernels',
#                        ignore=shutil.ignore_patterns('*.xml','*.csv'))
#
#        main(config, silent=False, verbose=False, log=True, diff='files')
#        print('')
                
if __name__ == '__main__':
    unittest.main()