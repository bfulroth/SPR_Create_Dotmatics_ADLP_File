"""Module for testing SPR_to_ADLP_Funct_8k.py Script"""

from unittest import TestCase
from unittest.mock import patch
from script_spr_to_adlp_funct_8k.Cli import main
import pandas as pd
from click.testing import CliRunner
import numpy as np


class SPR_to_ADLP_FUNCT_8K_Cli(TestCase):
    """Unit tests for invoking SPR_to_ADLP_8K.py Script using Click"""

    df_senso_txt_test = None
    df_ss_txt_test = None
    df_ru_top_result = None

    @classmethod
    def setUpClass(cls) -> None:
        pass

    @patch('SPR_to_ADLP_Functions.common_functions.render_structure_imgs',
           return_value=pd.DataFrame({'IMG_PATH': ['Fake/File/Path', 'Fake/File/Path2']}))
    @patch('SPR_to_ADLP_Functions.common_functions.spr_insert_structures')
    @patch('SPR_to_ADLP_Functions.common_functions.spr_binding_top_for_dot_file')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_Cli_and_adlp_df_created_Biacore8k(self, mock_1, mock_2, mock_3, mock_4, mock_5) -> None:
        """
        Test that the final DataFrame for ADLP upload is created in memory.  Note that all methods related to writing
        the DataFrame to a file using Pandas and the xlsxwriter engine have been patched.

        :param mock_1: Mocks the pandas.DataFrame.to_excel method
        :param mock_2: Mocks the pandas.ExcelWriter method
        :param mock_3: Mocks the rename_images method
        :param mock_4: Mocks the spr_insert_images method
        :param mock_5: Mocks shutil.copytree method used to restore image files in the event of a crash
        :param mock_6: Mocks the shutil.rmtree method used to restore image files in the event of a crash
        :param mock_7: Mocks the spr_binding_top_for_dot_file method as this is computationally expensive
        :param mock_8: Mocks the spr_insert_structures method
        :param mock_9: Mocks the render_structure_imgs method
        :param mock_10: Mocks the get_structures_smiles_from_db method
        :return: None
        """


        # TODO Fix this test!!
        # # Define the Return value of the mocked rename_images function
        # mock_3.side_effect = [SPR_to_ADLP_8K_Cli.df_ss_txt_test, SPR_to_ADLP_8K_Cli.df_senso_txt_test]
        #
        # # Define the Return value of the mocked spr_binding_top_for_dot_file function
        # mock_7.side_effect = [SPR_to_ADLP_8K_Cli.df_ru_top_result]
        #
        # # Use the click CliRunner object for testing Click implemented Cli programs.
        runner = CliRunner()
        result = runner.invoke(main, ['--config_file',
                                      '/Users/bfulroth/GitProjects/SPR_Create_Dotmatics_ADLP_File/tests/fixtures/Biacore8k_Funct_Test_Files/200716-1_config_8K_funct.txt',
                                                            '--save_file','Test.xlsx'])
        #
        # print(result.output)
        # self.assertEqual(0, result.exit_code)