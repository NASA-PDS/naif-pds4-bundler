import os
import json
import shutil
import unittest

from unittest import TestCase
from xml.etree import cElementTree as ET

from pathlib import Path

from npb.main               import main
from npb.utils.files        import etree_to_dict
from npb.classes.setup      import Setup
from npb.classes.list       import KernelList
from npb.classes.product    import Object

class TestXML(TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Unit Tests - {cls.__name__}")

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

        dirs = ['working', 'staging', 'kernels']
        for dir in dirs:
            os.mkdir(dir)

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_xml_reader_basic(self):

        shutil.copy2('../data/kernels/fk/insight_v05.tf', 'kernels/fk')
        shutil.copy2('../data/kernels/lsk/naif0012.tls', 'kernels/lsk')
        shutil.copy2('../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc',
                     'kernels/ck')
        shutil.copy2('../data/kernels/ck/insight_ida_pot_200829_201220_v1.bc',
                     'kernels/ck')
        shutil.copy2('../data/kernels/sclk/NSY_SCLKSCET.00019.tsc',
                     'kernels/sclk')

        os.mkdir('insight')

        #
        # Basic test of XML parsing.
        #
        config = Path('../config/insight.xml').read_text()
        config = etree_to_dict(ET.XML(config))
        print(json.dumps(config, indent=4))

        #
        # Dummy initialization values for Setup class
        #
        version = 'X.Y.Z'
        args = Object()

        args.config      = '../config/insight.xml'
        args.plan        = False
        args.faucet      = ''
        args.diff        = ''
        args.silent      = False
        args.verbose     = True

        setup = Setup(args, version)

        #
        # Testing of the initialisation of the List class
        #
        setup.release = '008'

        KernelList(setup, args.plan)

    def test_xml_reader_mk(self):
        '''
        Testing the initialisation of the meta-kernel
        :return:
        '''
        config = '../config/insight.xml'

        os.mkdir('staging/insight')
        os.mkdir('staging/insight/insight_spice')

        os.mkdir('kernels/fk')
        os.mkdir('kernels/sclk')
        os.mkdir('kernels/ck')
        os.mkdir('kernels/lsk')

        shutil.copy2('../data/kernels/fk/insight_v05.tf', 'kernels/fk')
        shutil.copy2('../data/kernels/lsk/naif0012.tls', 'kernels/lsk')
        shutil.copy2('../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc',
                     'kernels/ck')
        shutil.copy2('../data/kernels/ck/insight_ida_pot_200829_201220_v1.bc',
                     'kernels/ck')
        shutil.copy2('../data/kernels/sclk/NSY_SCLKSCET.00019.tsc',
                     'kernels/sclk')

        shutil.copytree('../data/insight', 'insight')

        main(config, '', 'final', silent=True, log=False, diff='')
        

if __name__ == '__main__':

    unittest.main()