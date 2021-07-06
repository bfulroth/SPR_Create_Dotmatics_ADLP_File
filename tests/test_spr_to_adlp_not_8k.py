"""Module for testing SPR_to_ADLP.py Script"""

# Modules for testing
from unittest import TestCase
from unittest.mock import MagicMock, patch

# Script modules
from script_spr_to_adlp_not_8k.SPR_to_ADLP import spr_create_dot_upload_file
from script_spr_to_adlp_not_8k.Cli import main
import pandas as pd
from click.testing import CliRunner
import numpy as np


class SPR_to_ADLP_not_8k_Cli(TestCase):
    """Unit tests for invoking SPR_to_ADLP Script using Click"""

    @patch('SPR_to_ADLP_Functions.common_functions.spr_binding_top_for_dot_file')
    @patch('SPR_to_ADLP_Functions.common_functions.get_structures_smiles_from_db', return_value='Structures Here')
    @patch('SPR_to_ADLP_Functions.common_functions.render_structure_imgs',
           return_value = pd.DataFrame({'IMG_PATH': ['Fake/File/Path', 'Fake/File/Path2']}))
    @patch('SPR_to_ADLP_Functions.common_functions.spr_insert_ss_senso_images',
           return_value='Image Place Holder')
    @patch('SPR_to_ADLP_Functions.common_functions.spr_insert_structures')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_Cli_and_adlp_df_created_Biacore1(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6, mock_7) -> None:
        """
        Test that the final DataFrame for ADLP upload is created in memory.  Note that all methods related to writing
        the DataFrame to a file using Pandas and the xlsxwriter engine have been patched.

        :param mock_1: Mocks the pandas.DataFrame.to_excel method
        :param mock_2: Mocks the pandas.ExcelWriter method
        :param mock_3: Mocks the spr_insert_structures method
        :param mock_4: Mocks the spr_insert_ss_senso_images method
        :param mock_5: Mocks the render_structure_imgs method and returns a MagicMock with a Fake DF as it's return value
        :param mock_6: Mocks the get_structures_smiles_from_db method
        :param mock_7: Mocks the spr_binding_top_for_dot_file. This method tested in isolation
        :return: None
        """
        # Need to provide a return value for the RU at the top concentration
        mock_7.return_value = pd.DataFrame({'Relative response (RU)': [48.78, 50.56, 49.85, 53.83, 54.91, 53.4, 54.57,
                                                                       56.27, 54.58, 55.88, 55.31, 53.65, 38.85, 41.28,
                                                                       41.21, 45.67, 51.6, 48.34, 27.93, 37.98, 37.86,
                                                                       40.25, 40.41, 40.82, 46.67, 46.22, 46.85, 28.69,
                                                                       38.59, 38.4, 40.6, 45.26, 43.74, 8.09, 19.26,
                                                                       12.54, 31.95, 44.59, 36.64, 42.92, 53.72, 47.89,
                                                                       38.61, 45.64, 44.77, 31.41, 37.33, 35.79]})

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
    @patch('SPR_to_ADLP_Functions.common_functions.spr_binding_top_for_dot_file')
    @patch('os.path.join', return_value='./tests/fixtures/Biacore1_Test_Files/Save.xlsx')
    @patch('SPR_to_ADLP_Functions.common_functions.get_structures_smiles_from_db', return_value='Structures Here')
    @patch('SPR_to_ADLP_Functions.common_functions.render_structure_imgs',
           return_value=pd.DataFrame({'IMG_PATH': ['Fake/File/Path', 'Fake/File/Path2']}))
    @patch('SPR_to_ADLP_Functions.common_functions.spr_insert_ss_senso_images',
           return_value='Image Place Holder')
    @patch('SPR_to_ADLP_Functions.common_functions.spr_insert_structures')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def setUpClass(cls, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6, mock_7, mock_8) -> None:
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
        :param mock_8: Mocks the spr_binding_top_for_dot_file. This method tested in isolation
        :return: None
        """
        # Need to provide a return value for the RU at the top concentration
        mock_8.return_value = pd.DataFrame({'Relative response (RU)': [48.78, 50.56, 49.85, 53.83, 54.91, 53.4, 54.57,
                                                                       56.27, 54.58, 55.88, 55.31, 53.65, 38.85, 41.28,
                                                                       41.21, 45.67, 51.6, 48.34, 27.93, 37.98, 37.86,
                                                                       40.25, 40.41, 40.82, 46.67, 46.22, 46.85, 28.69,
                                                                       38.59, 38.4, 40.6, 45.26, 43.74, 8.09, 19.26,
                                                                       12.54, 31.95, 44.59, 36.64, 42.92, 53.72, 47.89,
                                                                       38.61, 45.64, 44.77, 31.41, 37.33, 35.79]})

        config_file_path = './tests/fixtures/Biacore1_Test_Files/200312-1_config_affinit_Biacore1.txt'
        cls.df_result = spr_create_dot_upload_file(config_file=config_file_path, save_file='Test', clip=False,
                                                   structures=False)

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
        actual = (SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['PROJECT_CODE'] == '7279')

        self.assertEqual(expected, actual.all())

    def test_final_df_col_CURVE_VALID(self):

        expected = True
        actual = (SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['CURVE_VALID'] == '')
        
        self.assertEqual(expected, actual.all())
        
    def test_final_df_col_STEADY_STATE_IMG(self):
        
        expected = True
        actual = (SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['STEADY_STATE_IMG'] == '')
        
        self.assertEqual(expected, actual.all())
        
    def test_final_df_col_1to1_IMG(self):
        
        expected = True
        actual = (SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['1to1_IMG'] == '')
        
        self.assertEqual(expected, actual.all())

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

    def test_final_df_PERCENT_BINDING_TOP(self):

        expected = [132.41, 133.9, 134.19, 141.84, 141.16, 139.53, 147.85, 148.74, 146.64, 147.25, 142.19, 140.19,
                    131.43, 136.28, 138.24, 120.09, 132.41, 126.05, 73.6, 97.63, 98.93, 109.26, 107.02, 109.88,
                    122.98, 118.82, 122.42, 75.6, 99.2, 100.34, 97.97, 106.57, 104.67, 21.27, 49.42, 32.7, 88.7,
                    120.77, 100.88, 110.08, 134.43, 121.8, 101.93, 117.57, 117.2, 85.26, 98.86, 96.34]

        actual = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['PERCENT_BINDING_TOP'])

        self.assertEqual(expected, actual)

    def test_final_df_KD_SS_UM(self):

        expected = [4.53, 1.41, 3.8, 0.441, 0.131, 0.28, 0.228, 0.082, 0.152, 0.858, 0.268, 0.529, 10.7,
                    3.32, 4.36, 6.6, 2.42, 4.39, 33.9, 19.0, 16.5, 4.17, 1.5, 3.37, 0.705, 0.272, 0.55,
                    0.55, 4.81, 4.87, 1.84, 0.552, 1.1, 26.5, 21.3, 16.9, 11800000.0, 56.8, 2690000.0,
                    1.37, 0.552, 1.21, 2.02, 1.07, 1.47, 3.36, 1.64, 2.82]

        actual = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['KD_SS_UM'])

        self.assertEqual(expected, actual)

    def test_final_df_CHI2_SS_AFFINITY(self):

        expected = pd.Series([0.478, 0.568, 0.604, 0.12, 0.326, 0.217, 0.432, 1.25, 0.924, 0.934, 1.38, 0.458,
                                    0.337, 0.887, 0.399, 0.887, 5.15, 1.37, 0.077, 0.425, 0.142, 0.117, 0.386, 0.019,
                                    0.267, 1.98, 0.366, np.NaN, 1.91, 0.033, 0.511, 0.61, 0.681, 0.01, 0.149, 0.01,
                                    3.38, 0.272, 0.413, 0.207, 1.85, 0.579, 0.118, 1.93, 0.279, 0.104, 1.31, 0.113])

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['CHI2_SS_AFFINITY']

        result = expected.equals(actual)

        self.assertEqual(True, result)

    def test_final_df_FITTED_RMAX_SS_AFFINITY(self):

        expected = pd.Series([51.2, 50.6, 52.9, 54.9, 57.7, 55.3, 53.6, 53.0, 54.2, 55.7, 52.9, 53.5, 45.2, 42.9, 43.2,
                    49.0, 48.1, 48.7, 45.2, 53.9, 48.4, 42.2, 41.5, 42.0, 46.0, 44.3, 45.1, np.NaN, 47.3,
                    45.5, 40.9, 40.6, 41.8, 16.0, 40.8, 19.1, 17381490.8, 175.7, 4573345.7, 43.2, 44.9,
                    45.4, 40.4, 44.7, 42.2, 30.8, 34.7, 32.0])

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['FITTED_RMAX_SS_AFFINITY']

        result = expected.equals(actual)

        self.assertEqual(True, result)

    def test_final_df_KA_1_1_BINDING(self):

        expected = pd.Series([np.NaN, np.NaN, np.NaN, 541000.0, 3150000.0, 448000.0, 1270000.0, 16900000.0, 951000.0,
                              279000.0, 1680000.0, 277000.0, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                              np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                              np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                              np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN])

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['KA_1_1_BINDING']

        result = expected.equals(actual)

        self.assertEqual(True, result)

    def test_final_df_KD_LITTLE_1_1_BINDING(self):

        expected = pd.Series([np.NaN, np.NaN, np.NaN, 0.17, 0.422, 0.085, 0.203, 1.22, 0.1, 0.168, 0.378,
                              0.101, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                              np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                              np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                              np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN])

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['KD_LITTLE_1_1_BINDING']

        result = expected.equals(actual)

        self.assertEqual(True, result)

    def test_final_df_KD_1_1_BINDING_UM(self):

        expected = list(pd.Series(data=[np.NaN, np.NaN, np.NaN, 0.314, 0.134, 0.189, 0.159, 0.0719, 0.106,
                                   0.602, 0.225, 0.363, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN]))

        expected = [round(num, 3) for num in expected]
        expected = [0 if x != x else x for x in expected]

        actual = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['KD_1_1_BINDING_UM'])
        actual = [round(num, 3) for num in actual]
        actual = [0 if x != x else x for x in actual]

        self.assertEqual(expected, actual)

    def test_final_df_chi2_1_1_binding(self):

        expected = list(pd.Series(data=[np.NaN, np.NaN, np.NaN, 0.27, 0.0879, 0.452, 0.216, 0.218,
                                   0.606, 1.77, 0.791, 0.891, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN]))

        expected = [round(num, 3) for num in expected]
        expected = [0 if x != x else x for x in expected]

        actual = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['chi2_1_1_binding'])
        actual = [round(num, 3) for num in actual]
        actual = [0 if x != x else x for x in actual]

        self.assertEqual(expected, actual)

    def test_final_df_U_VALUE_1_1_BINDING(self):

        expected = ''

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['U_VALUE_1_1_BINDING'] == expected

        self.assertEqual(True, actual.all())

    def test_final_df_U_FITTED_RMAX_1_1_BINDING(self):

        expected = list(pd.Series(data=[np.NaN, np.NaN, np.NaN, 37.6, 53.0, 36.2, 37.9, 55.7, 37.5, 32.7, 45.5,
                                   33.9, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN,
                                   np.NaN]))

        expected = [round(num, 3) for num in expected]
        expected = [0 if x != x else x for x in expected]

        actual = list(SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['FITTED_RMAX_1_1_BINDING'])
        actual = [round(num, 3) for num in actual]
        actual = [0 if x != x else x for x in actual]

        self.assertEqual(actual, expected)

    def test_final_df_FC(self):

        expected = pd.Series(data=['FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr', 'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr',
                                   'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr', 'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr',
                                   'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr', 'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr',
                                   'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr', 'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr',
                                   'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr', 'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr',
                                   'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr', 'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr',
                                   'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr', 'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr',
                                   'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr', 'FC2-1Corr', 'FC3-1Corr', 'FC4-1Corr'])

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['FC']

        result = expected.equals(actual)

        self.assertEqual(True, result)

    @patch('SPR_to_ADLP_Functions.common_functions.get_predefined_comments')
    @patch('os.path.join', return_value='./tests/fixtures/Biacore1_Test_Files/Save.xlsx')
    @patch('SPR_to_ADLP_Functions.common_functions.get_structures_smiles_from_db', return_value='Structures Here')
    @patch('SPR_to_ADLP_Functions.common_functions.render_structure_imgs',
           return_value=pd.DataFrame({'IMG_PATH': ['Fake/File/Path', 'Fake/File/Path2']}))
    @patch('SPR_to_ADLP_Functions.common_functions.spr_insert_ss_senso_images',
           return_value='Image Place Holder')
    @patch('SPR_to_ADLP_Functions.common_functions.spr_insert_structures')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_get_COMMENTS_called(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6, mock_7, mock_8):
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
        :param mock_8: Mocks out the method that gets comments
        :return: None
        """

        config_file_path = './tests/fixtures/Biacore1_Test_Files/200312-1_config_affinit_Biacore1.txt'
        spr_create_dot_upload_file(config_file=config_file_path, save_file='Test', clip=False)
        self.assertEqual(1, mock_8.call_count)

    def test_final_df_PROTEIN_RU(self):

        expected = pd.Series(data=[1993.5, 2042.1, 2006.0, 1993.5, 2042.1, 2006.0, 1993.5, 2042.1, 2006.0, 1993.5,
                                   2042.1, 2006.0, 1993.5, 2042.1, 2006.0, 1993.5, 2042.1, 2006.0, 1993.5, 2042.1,
                                   2006.0, 1993.5, 2042.1, 2006.0, 1993.5, 2042.1, 2006.0, 1993.5, 2042.1, 2006.0,
                                   1993.5, 2042.1, 2006.0, 1993.5, 2042.1, 2006.0, 1993.5, 2042.1, 2006.0, 1993.5,
                                   2042.1, 2006.0, 1993.5, 2042.1, 2006.0, 1993.5, 2042.1, 2006.0])

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['PROTEIN_RU']

        result = expected.equals(actual)

        self.assertEqual(True, result)

    def test_final_df_PROTEIN_MW(self):

        expected = pd.Series(data=[26870.04, 26856.02, 26812.01, 26870.04, 26856.02, 26812.01, 26870.04, 26856.02,
                                   26812.01, 26870.04, 26856.02, 26812.01, 26870.04, 26856.02, 26812.01, 26870.04,
                                   26856.02, 26812.01, 26870.04, 26856.02, 26812.01, 26870.04, 26856.02, 26812.01,
                                   26870.04, 26856.02, 26812.01, 26870.04, 26856.02, 26812.01, 26870.04, 26856.02,
                                   26812.01, 26870.04, 26856.02, 26812.01, 26870.04, 26856.02, 26812.01, 26870.04,
                                   26856.02, 26812.01, 26870.04, 26856.02, 26812.01, 26870.04, 26856.02, 26812.01])

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['PROTEIN_MW']

        result = expected.equals(actual)

        self.assertEqual(True, result)

    def test_final_PROTEIN_ID(self):

        expected = pd.Series(data=['BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01', 'BIP-0384-01', 'BIP-0501-01',
                                   'BIP-0503-01', 'BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01', 'BIP-0384-01',
                                   'BIP-0501-01', 'BIP-0503-01', 'BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01',
                                   'BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01', 'BIP-0384-01', 'BIP-0501-01',
                                   'BIP-0503-01', 'BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01', 'BIP-0384-01',
                                   'BIP-0501-01', 'BIP-0503-01', 'BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01',
                                   'BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01', 'BIP-0384-01', 'BIP-0501-01',
                                   'BIP-0503-01', 'BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01', 'BIP-0384-01',
                                   'BIP-0501-01', 'BIP-0503-01', 'BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01',
                                   'BIP-0384-01', 'BIP-0501-01', 'BIP-0503-01'])

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['PROTEIN_ID']

        result = expected.equals(actual)

        self.assertEqual(True, result)

    def test_final_MW(self):

        expected = pd.Series(data=[496.557, 496.557, 496.557, 511.55, 511.55, 511.55, 497.524, 497.524, 497.524,
                                   511.55, 511.55, 511.55, 398.392, 398.392, 398.392, 512.535, 512.535, 512.535,
                                   511.55, 511.55, 511.55, 496.557, 496.557, 496.557, 511.55, 511.55, 511.55,
                                   511.55, 511.55, 511.55, 558.56, 558.56, 558.56, 512.535, 512.535, 512.535,
                                   485.513, 485.513, 485.513, 525.577, 525.577, 525.577, 510.565, 510.565,
                                   510.565, 496.557, 496.557, 496.557])

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['MW']

        result = expected.equals(actual)

        self.assertEqual(True, result)

    def test_final_INSTRUMENT(self):

        expected = 'Biacore1'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['INSTRUMENT'] == expected

        self.assertEqual(True, actual.all())

    def test_final_ASSAY_MODE(self):

        expected = 'Multi-Cycle'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['ASSAY_MODE'] == expected

        print(actual)

        self.assertEqual(True, actual.all())

    def test_final_EXP_DATE(self):

        expected = '2020_03_12'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['EXP_DATE'] == expected

        self.assertEqual(True, actual.all())

    def test_final_NUCLEOTIDE(self):

        expected = 'GMPPCP'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['NUCLEOTIDE'] == expected

        self.assertEqual(True, actual.all())

    def test_final_CHIP_LOT(self):

        expected = '10285867'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['CHIP_LOT'] == expected

        self.assertEqual(True, actual.all())

    def test_final_OPERATOR(self):

        expected = 'bfulroth'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['OPERATOR'] == expected

        self.assertEqual(True, actual.all())

    def test_final_PROTOCOL_ID(self):

        expected = 'KRAS_SPR_Assay_v5'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['PROTOCOL_ID'] == expected

        self.assertEqual(True, actual.all())

    def test_final_RAW_DATA_FILE(self):

        expected = '200312_7279_affinity'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['RAW_DATA_FILE'] == expected

        self.assertEqual(True, actual.all())

    def test_final_DIR_FOLDER(self):

        expected = 'Biacore1/Ben/KRAS'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result['DIR_FOLDER'] == expected

        self.assertEqual(True, actual.all())

    # def test_final_UNIQUE_ID(self):
    #
    #     expected = 'BRD-6261_1_FC2-1Corr_7279_2020_03_12_1.png'
    #
    #     actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result.loc[0, 'UNIQUE_ID']
    #
    #     self.assertEqual(expected, actual)

    def test_final_SS_IMG_ID(self):

        expected = './tests/fixtures/Biacore1_Test_Files/200312_7279_affinity_1-48_PWF/BRD-6261_1_200312_7279_affinity_1.png'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result.loc[0, 'SS_IMG_ID']

        self.assertEqual(expected, actual)

    def test_final_SENSO_IMG_ID(self):

        expected = './tests/fixtures/Biacore1_Test_Files/200312_7279_affinity_1-48_SWF/BRD-6261_1_200312_7279_affinity_1.png'

        actual = SPR_to_ADLP_not_8k_Final_Df_3_FC_1_Ref_Biacore1.df_result.loc[0, 'SENSO_IMG_ID']

        self.assertEqual(expected, actual)
















