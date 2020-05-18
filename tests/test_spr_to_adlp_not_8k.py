from unittest import TestCase
from unittest.mock import MagicMock, patch
from script_spr_to_adlp_not_8k.SPR_to_ADLP import spr_create_dot_upload_file
from script_spr_to_adlp_not_8k.Cli import main
import pandas as pd
from click.testing import CliRunner
import numpy as np


class SPR_to_ADLP_not_8k_Cli(TestCase):
    """Unit tests for invoking SPR_to_ADLP Script using Click"""

    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.get_structures_smiles_from_db', return_value='Structures Here')
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.render_structure_imgs',
           return_value = MagicMock(return_value = pd.DataFrame({'IMG_PATH': ['Fake/File/Path', 'Fake/File/Path2']})))
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.spr_insert_ss_senso_images',
           return_value='Image Place Holder')
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.spr_insert_structures')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_Cli_and_adlp_df_created_Biacore1(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6) -> None:
        """
        Test that the final DataFrame for ADLP upload is created in memory.  Note that all methods related to writing
        the DataFrame to a file using Pandas and the xlsxwriter engine have been patched.

        :param mock_1: Mocks the get_structures_smiles_from_db method
        :param mock_2: Mocks the render_structure_imgs method and returns a MagicMock with a Fake DF as it's return value.
        :param mock_3: Mocks the spr_insert_ss_senso_images method
        :param mock_4: Mocks the spr_insert_structures method
        :param mock_5: Mocks the pandas.ExcelWriter method
        :param mock_6: Mocks the pandas.DataFrame.to_excel method
        :return: None
        """

        # Use the click CliRunner object for testing Click implemented Cli programs.
        runner = CliRunner()
        result = runner.invoke(main, ['--config_file', './tests/fixtures/Biacore1_Test_Files/'
                                                        '200312-1_config_affinit_Biacore1.txt', '--save_file',
                                                        'Test'])
        self.assertEqual(0, result.exit_code)

    def test_Cli_and_adlp_df_created_Biacore2(self):
        pass

    def test_Cli_and_adlp_df_created_Biacore3(self):
        pass

    def test_Cli_and_adlp_df_created_BiacoreS200(self):
        pass


class SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1(TestCase):
    """
    Tests that the final DF that contains all information, excluding images, is correct and ready for ADLP upload
    """
    # Initialize a class variable for the SPR_to_ADLP DataFrame.
    df_result = ''

    @classmethod
    @patch('os.path.join', return_value='./tests/fixtures/Biacore1_Test_Files/Save.xlsx')
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.get_structures_smiles_from_db', return_value='Structures Here')
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.render_structure_imgs',
           return_value=MagicMock(return_value=pd.DataFrame({'IMG_PATH': ['Fake/File/Path', 'Fake/File/Path2']})))
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.spr_insert_ss_senso_images',
           return_value='Image Place Holder')
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.spr_insert_structures')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def setUpClass(cls, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6, mock_7) -> None:
        """
        Sets up the class with the final DataFrame from Running the SPR_to_ADLP Script.  Subsequent methods in this class
        evaluate and verify this DataFrame for correctness.

        :param mock_1: Mocks the os.path.join method so that the script doesn't try to grab users desktop path.
        :param mock_2: Mocks the get_structures_smiles_from_db method
        :param mock_3: Mocks the render_structure_imgs method and returns a MagicMock with a Fake DF as it's return value.
        :param mock_4: Mocks the spr_insert_ss_senso_images method
        :param mock_5: Mocks the spr_insert_structures method
        :param mock_6: Mocks the pandas.ExcelWriter method
        :param mock_7: Mocks the pandas.DataFrame.to_excel method
        :return: None
        """

        config_file_path = './tests/fixtures/Biacore1_Test_Files/200312-1_config_affinit_Biacore1.txt'
        cls.df_result = spr_create_dot_upload_file(config_file=config_file_path, save_file='Test', clip=False)

    def test_final_df_correct_col_names(self):

        expected_columns = ['BROAD_ID', 'STRUCTURES', 'PROJECT_CODE', 'CURVE_VALID', 'STEADY_STATE_IMG', '1to1_IMG',
                            'TOP_COMPOUND_UM', 'RMAX_THEORETICAL', 'RU_TOP_CMPD', 'PERCENT_BINDING_TOP',
                            'KD_SS_UM', 'CHI2_SS_AFFINITY', 'FITTED_RMAX_SS_AFFINITY',
                            'KA_1_1_BINDING', 'KD_LITTLE_1_1_BINDING', 'KD_1_1_BINDING_UM',
                            'chi2_1_1_binding', 'U_VALUE_1_1_BINDING', 'FITTED_RMAX_1_1_BINDING',
                            'COMMENTS', 'FC', 'PROTEIN_RU', 'PROTEIN_MW', 'PROTEIN_ID', 'MW', 'INSTRUMENT',
                            'ASSAY_MODE', 'EXP_DATE', 'NUCLEOTIDE', 'CHIP_LOT', 'OPERATOR', 'PROTOCOL_ID',
                            'RAW_DATA_FILE', 'DIR_FOLDER', 'UNIQUE_ID', 'SS_IMG_ID', 'SENSO_IMG_ID']

        actual_columns = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result.columns)

        self.assertEqual(expected_columns, actual_columns)

    def test_final_df_correct_df_len(self):
        """Test that the DataFrame is Equal to the correct with 3 channels"""

        expected_len = 48
        actual_len = len(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result)

        self.assertEqual(expected_len, actual_len)

    def test_final_df_col_PROJECT_CODE(self):

        expected = True
        actual = (SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['PROJECT_CODE'].all() == '7279')

        self.assertEqual(expected, actual)

    def test_final_df_col_CURVE_VALID(self):

        expected = True
        actual = (SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['CURVE_VALID'].all() == '')
        
        self.assertEqual(expected, actual)
        
    def test_final_df_col_STEADY_STATE_IMG(self):
        
        expected = True
        actual = (SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['STEADY_STATE_IMG'].all() == '')
        
        self.assertEqual(expected, actual)
        
    def test_final_df_col_1to1_IMG(self):
        
        expected = True
        actual = (SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['1to1_IMG'].all() == '')
        
        self.assertEqual(expected, actual)

    def test_final_df_col_TOP_COMPUND_UM(self):

        expected = [50, 50, 50, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50,
                    20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 50, 50]

        actual = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['TOP_COMPOUND_UM'])

        self.assertEqual(expected, actual)

    def test_final_df_col_RMAX_THEORETICAL(self):

        expected = [36.84, 37.76, 37.15, 37.95, 38.9, 38.27, 36.91, 37.83, 37.22, 37.95, 38.9, 38.27, 29.56, 30.29, 
                    29.81, 38.03, 38.97, 38.35, 37.95, 38.9, 38.27, 36.84, 37.76, 37.15, 37.95, 38.9, 38.27, 37.95, 
                    38.9, 38.27, 41.44, 42.47, 41.79, 38.03, 38.97, 38.35, 36.02, 36.92, 36.32, 38.99, 39.96, 39.32, 
                    37.88, 38.82, 38.2, 36.84, 37.76, 37.15]

        actual = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['RMAX_THEORETICAL'])
        
        self.assertEqual(expected, actual)

    def test_final_df_RU_TOP_CMPD(self):

        expected = [48.78, 50.56, 49.85, 53.83, 54.91, 53.4, 54.57, 56.27, 54.58, 55.88, 55.31, 53.65, 38.85,
                    41.28, 41.21, 45.67, 51.6, 48.34, 27.93, 37.98, 37.86, 40.25, 40.41, 40.82, 46.67, 46.22,
                    46.85, 28.69, 38.59, 38.4, 40.6, 45.26, 43.74, 8.09, 19.26, 12.54, 31.95, 44.59, 36.64,
                    42.92, 53.72, 47.89, 38.61, 45.64, 44.77, 31.41, 37.33, 35.79]

        actual = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['RU_TOP_CMPD'])

        self.assertEqual(expected, actual)

    def test_final_df_PERCENT_BINDING_TOP(self):

        expected = []

        actual = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['PERCENT_BINDING_TOP'])

        self.assertEqual(expected, actual)








