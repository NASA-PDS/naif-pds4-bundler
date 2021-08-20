import os
import glob
import shutil
import unittest
import spiceypy
from unittest import TestCase
from npb.main import main


class TestMars2020(TestCase):
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

        dirs = ['working', 'staging', 'mars2020', 'kernels']
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
        
        dirs = ['working', 'staging', 'kernels', 'mars2020',
                'kernels/fk', 'kernels/lsk', 'kernels/spk',  'kernels/mk']
        for dir in dirs:
            os.mkdir(dir)

        shutil.copy2('../data/kernels/lsk/naif0012.tls', 'kernels/lsk/')
        shutil.copy2('../data/kernels/fk/m2020_v04.tf', 'kernels/fk/')
        shutil.copy2('../data/kernels/mk/m2020_v01.tm', 'kernels/mk/')
        shutil.copy2('../data/kernels/mk/m2020_chronos_v01.tm', 'kernels/mk/')
        shutil.copy2('../data/kernels/spk/m2020_cruise_od138_v1.bsp', 
                     'kernels/spk/')
        shutil.copy2('../data/kernels/spk/'
                     'm2020_surf_rover_loc_0000_0089_v1.bsp', 
                     'kernels/spk/')
        
        os.chdir(os.path.dirname(__file__))

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'mars2020', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_m2020_mks_inputs_coverage(self):
        '''
        Testcase for when one of the meta-kernels does not include the SPK/CK
        that determines the coverage of the meta-kernel (implemented after
        M2020 Chronos meta-kernel generation.)
        '''
        config = '../config/mars2020.xml'
        plan = '../data/mars2020_release_00.plan'
        
        main(config, plan=plan, silent=self.silent, log=self.log)

    def test_m2020_kernel_list(self):
        '''
        Usage of kernel list instead of release plan.
        '''
        config = '../config/mars2020.xml'
        kerlist = '../data/mars2020_release_00.kernel_list'

        main(config, kerlist=kerlist, silent=self.silent, log=self.log)
        
    def test_m2020_kernel_list_dir(self):
        '''
        Usage of kernel list instead of release plan. Provided from the
        working directory with the same resulting name..
        '''
        shutil.copy2('../data/mars2020_release_00.kernel_list',
                     'working/mars2020_release_01.kernel_list', )
        
        config = '../config/mars2020.xml'
        kerlist = 'working/mars2020_release_00.kernel_list'

        with self.assertRaises(FileNotFoundError):
            main(config, kerlist=kerlist, silent=self.silent, log=self.log)

        kerlist = 'working/mars2020_release_01.kernel_list'

        main(config, kerlist=kerlist, silent=self.silent, log=self.log)

            
if __name__ == '__main__':
    unittest.main()
