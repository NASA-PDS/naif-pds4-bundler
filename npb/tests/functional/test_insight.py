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

        config = 'data/insight.json'
        plan   = 'data/insight_release_26.plan'

        #
        # Debugging does not work while using coverage.
        # See: https://github.com/microsoft/vscode-python/issues/693
        #
        #cov = coverage.Coverage()
        #cov.start()

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)

        os.mkdir('working')
        shutil.copy2('data/insight_release_basic.kernel_list',
                     'working/insight_release_07.kernel_list')
        os.mkdir('staging')
        os.mkdir('staging/insight')
        os.mkdir('staging/insight/insight_spice')

        shutil.copytree('data/insight', 'insight')
        with open('data/insight.list', 'r') as i:
            for line in i:
                with open(f'insight/insight_spice/{line[0:-1]}', 'w') as fp:
                    pass

        main(config, plan, silent=False, log=True)

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)

        #cov.stop()
        #cov.save()
        #
        #cov.html_report()


    def test_insight_diff_previous(self):
        '''
        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment files
        to the staging area.
        '''

        config = 'data/insight_release_08.json'
        plan   = 'data/insight_release_08.plan'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)

        os.mkdir('working')
        for file in glob.glob('data/insight_release_[0-9][0-9].kernel_list'):
            shutil.copy2(file,
                        'working')
        os.mkdir('staging')
        os.mkdir('staging/insight')
        os.mkdir('staging/insight/insight_spice')
        shutil.copytree('data/insight', 'insight')
        for file in glob.glob('data/insight_release_[0-9][0-9].kernel_list'):
            shutil.copy2(file,
                        'working')

        main(config, plan, silent=False, log=True)

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)


    def test_insight_diff_similar(self):
        '''
        Testcase in which products are compared with similar products from
        the previous increment (not the same products as with the previous
        testcase) The pipeline stops before copying the previous
        increment files
        to the staging area.
        '''


    def test_insight_diff_templates(self):
        '''
        Testcase in which products are compared with the templates to
        generate the products. The pipeline stops before copying the previous
        increment files
        to the staging area.
        '''

        config = 'data/insight_release_08.json'
        plan   = 'data/insight_release_08.plan'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)

        os.mkdir('working')
        for file in glob.glob('data/insight_release_[0-9][0-9].kernel_list'):
            shutil.copy2(file,
                        'working')
        os.mkdir('staging')
        os.mkdir('staging/insight')
        os.mkdir('staging/insight/insight_spice')
        os.mkdir('insight')

        main(config, plan, silent=False, log=True)

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)


    def test_insight_files_in_staging(self):
        '''
        Testcase in which products are already present in the staging
        directory. The log provides error messages but the process is not
        stopped. Process is finished before moving all files to the final
        area.
        '''

        config = 'data/insight_release_08.json'
        plan   = 'data/insight_release_08.plan'


        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)

        os.mkdir('working')
        for file in glob.glob('data/insight_release_[0-9][0-9].kernel_list'):
            shutil.copy2(file,
                        'working')
        os.mkdir('staging')
        os.mkdir('staging/insight')
        os.mkdir('staging/insight/insight_spice')
        os.mkdir('insight')

        main(config, plan, silent=False, log=True)

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        #cov.stop()
        #cov.save()
        #
        #cov.html_report()


if __name__ == '__main__':

    unittest.main()