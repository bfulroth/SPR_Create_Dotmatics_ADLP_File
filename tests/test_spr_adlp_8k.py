"""Module for testing SPR_to_ADLP_8K.py Script"""

from unittest import TestCase
from unittest.mock import patch
from script_spr_to_adlp_8k.Cli import main
import pandas as pd
from click.testing import CliRunner


class SPR_to_ADLP_8K_Cli(TestCase):
    """Unit tests for invoking SPR_to_ADLP_8K.py Script using Click"""

    df_senso_txt_test = None
    df_ss_txt_test = None
    df_ru_top_result = None

    @classmethod
    def setUpClass(cls) -> None:
        """Class used to setup objects needed to test the main method."""

        cls.df_ss_txt_test = pd.read_excel('./tests/fixtures/Biacore8k_Test_Files/SS_DF_After_IMG_Rename.xlsx')

        cls.df_senso_txt_test = pd.read_excel('./tests/fixtures/Biacore8k_Test_Files/SENSO_DF_After_IMG_Rename.xlsx')

        cls.df_ru_top_result = pd.DataFrame({'Relative response (RU)': [35.83, 36.49, 36.34, 34.89, 35.17, 36.48,
                                                                        36.19, 33.92, 23.81, 20.23, 63.57, 22.11,
                                                                        22.66, 59.98, 53.59, 28.1, 49.93, 40.9,
                                                                        75.32, 50.51, 47.63, 83.6, 28.59, 36.58,
                                                                        52.61, 12.46, 15.19, 16.84, 28.72, 26.97,
                                                                        18.81, 30.92, 28.53, 32.5, 31.72, 16.22,
                                                                        26.1, 77.67, 35.74, 18.94, 24.05, 32.55,
                                                                        35.72, 44.11, 51.18, 63.29, 17.97, 17.97,
                                                                        35.83, 36.49, 36.34, 34.89, 35.17, 36.48,
                                                                        36.19, 33.92, 23.81, 20.23, 63.57, 22.11,
                                                                        22.66, 59.98, 53.59, 28.1, 49.93, 40.9,
                                                                        75.32, 50.51, 47.63, 83.6, 28.59, 36.58,
                                                                        52.61, 12.46, 15.19, 16.84, 28.72, 26.97,
                                                                        18.81, 30.92, 28.53, 32.5, 31.72, 16.22, 26.1,
                                                                        77.67, 35.74, 18.94, 24.05, 32.55, 35.72,
                                                                        44.11, 51.18, 63.29, 17.97, 17.97]})

    @patch('SPR_to_ADLP_Functions.common_functions.spr_binding_top_for_dot_file')
    @patch('shutil.rmtree')
    @patch('shutil.copytree')
    @patch('SPR_to_ADLP_Functions.common_functions.manage_structure_insertion')
    @patch('SPR_to_ADLP_Functions.common_functions.spr_insert_ss_senso_images', return_value='Image Place Holder')
    @patch('script_spr_to_adlp_8k.SPR_to_ADLP_8K.rename_images')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_Cli_and_adlp_df_created_Biacore8k(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6, mock_7,
                                               mock_8) -> None:
        """
        Test that the final DataFrame for ADLP upload is created in memory.  Note that all methods related to writing
        the DataFrame to a file using Pandas and the xlsxwriter engine have been patched.

        :param mock_1: Mocks the pandas.DataFrame.to_excel method
        :param mock_2: Mocks the pandas.ExcelWriter method
        :param mock_3: Mocks the rename_images method
        :param mock_4: Mocks the spr_insert_images method
        :param mock_5: Mocks the manage_structure_insertion method
        :param mock_6: Mocks the shutil.copytree method used to restore image files in the event of a crash
        :param mock_7: Mocks the shutil.rmtree method used to restore image files in the event of a crash
        :param mock_8: Mocks the spr_binding_top_for_dot_file method as this is computationally expensive
        :return: None
        """

        # Define the Return value of the mocked rename_images function
        mock_3.side_effect = [SPR_to_ADLP_8K_Cli.df_ss_txt_test, SPR_to_ADLP_8K_Cli.df_senso_txt_test]

        # Define the Return value of the mocked spr_binding_top_for_dot_file function
        mock_8.side_effect = [SPR_to_ADLP_8K_Cli.df_ru_top_result]

        # Use the click CliRunner object for testing Click implemented Cli programs.
        runner = CliRunner()
        result = runner.invoke(main, ['--config_file',
                                      './tests/fixtures/Biacore8k_Test_Files/200708_8K_Config.txt',
                                                            '--save_file','Test.xlsx'])

        print(result.output)
        self.assertEqual(0, result.exit_code)