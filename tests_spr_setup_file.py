from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch
import os
from Create_SPR_setup_file import spr_setup_sheet, save_output_file
import pandas as pd


class SetupFileScriptRegularAffinity(TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        # Create a test DataFrame of the setup table.
        global df_setup_tbl
        df_setup_tbl = pd.DataFrame({'Broad ID': ['BRD-K81106261-001-01-4', 'BRD-K00024350-001-01-9', 'BRD-K00024351-001-01-9'],
                        'Comment': ['This is the control cmpd', 'This is a comment', 'This is another cmpd.'],
                        'MW': [496.557, 497.524, 497.524],
                        'Sol. (uM)': [400, 500, 10.6],
                        'Plate': ['Plate_06', 'Plate_07', 'Plate_07'],
                        'Barcode': [1172907815, 1196291078, 1196291070],
                        'BC Added': [1172907815, 1196291078, 1196291070],
                        'Well': ['H06', 'E03', 'E08'],
                        'Conc. (mM)': [10, 10, 10],
                        'Conc (uM)': [10000, 1000, 1000],
                        '384W Dest.': ['A12', 'A24', 'B12'],
                        'Total Vol. (uL)': [200, 200, 200],
                        'Test [Cpd] uM': [50, 50, 50],
                        'fold_dil': [2, 1.5, 3],
                        'num_pts': [10, 8, 6],
                        'Buffer (uL)': [190, 190, 190],
                        'Cmpd to Add (uL)': [1, 4, 4],
                        'DMSO to Add (uL)': [9, 6, 6]})

        # Export this table to a csv file for testing
        df_setup_tbl.to_csv('./Test_Files/setup_table_test.csv', index=False)

    def test_correct_headers(self) -> None:
        """
        Test that ensures that the correct headers are listed in the test DF.
        """

        ls_corr_headers = ['Broad ID', 'Comment', 'MW', 'Sol. (uM)', 'Plate', 'Barcode',
                           'BC Added', 'Well', 'Conc. (mM)', 'Conc (uM)', '384W Dest.',
                           'Total Vol. (uL)', 'Test [Cpd] uM', 'fold_dil', 'num_pts',
                           'Buffer (uL)', 'Cmpd to Add (uL)', 'DMSO to Add (uL)']

        self.assertEqual(list(df_setup_tbl.columns), ls_corr_headers)

    def test_correct_headers_from_csv(self):
        """
        Test that the correct headers are read back from the test csv file.
        """

        df_test_setup_tbl_csv = pd.read_csv('./Test_Files/setup_table_test.csv')

        self.assertEqual(list(df_test_setup_tbl_csv.columns), list(df_setup_tbl.columns))

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_spr_setup_sheet_method_input(self, mock_input1, mock_input2):
        """
        Test that confirms that the a DataFrame is returned from spr setup sheet method.
        """

        result = spr_setup_sheet()
        self.assertEqual(result.__class__, pd.DataFrame)

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_correct_column_headers(self, monkeypatch, mock_input2):
        """

        :return:
        """
        expected_headers = ['BRD', 'MW', 'CONC', 'BAR']
        df_result = spr_setup_sheet()
        self.assertEqual(expected_headers, list(df_result.columns))

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_correct_BRD_format(self, mock_input1, mock_input2):
        """
        Test that confirms that the length of the BRD's are truncated to 10 characters.
        """

        df_result = spr_setup_sheet()
        self.assertEqual(10, len(str(df_result.iloc[1]['BRD'])))

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_two_zero_conc_points_first_cmpd(self, mock_input1, mock_input2):
        """
        Test to verify that the first to concentration points are zero
        """

        df_result = spr_setup_sheet()

        zero_one = df_result.iloc[1]['CONC']
        zero_two = df_result.iloc[1]['CONC']
        self.assertEqual(0, zero_one)
        self.assertEqual(0, zero_two)

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_correct_num_points_for_10pt_curves(self, mock_input1, mock_input2):

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-6261_1']

        self.assertEqual(12, len(df_result))

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_correct_num_points_for_8pt_curves(self, mock_input1, mock_input2):

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-4350_2']

        self.assertEqual(10, len(df_result))

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_correct_num_points_for_6pt_curves(self, mock_input1, mock_input2):

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-4351_3']

        self.assertEqual(8, len(df_result))

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_correct_two_fold_dilution_10_pts(self, mock_input1, mock_input2):

        ls_corr = [0, 0, 0.09765625, 0.1953125, 0.390625, 0.78125, 1.5625, 3.125, 6.25, 12.5, 25, 50]

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-6261_1']
        con_series = list(df_result.loc[:, 'CONC'])
        self.assertEqual(ls_corr, con_series)

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_correct_1pt5_fold_dilution_8_pts(self, mock_input1, mock_input2):

        ls_corr = [0.0, 0.0, 2.9263831732967542, 4.389574759945131, 6.584362139917697,
                                      9.876543209876544, 14.814814814814817, 22.222222222222225, 33.333333333333336, 50.0]

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-4350_2']
        con_series = list(df_result.loc[:, 'CONC'])
        self.assertEqual(ls_corr, con_series)

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', './Test_Files/setup_table_test.csv'])
    def test_correct_3_fold_dilution_6_pts(self, mock_input1, mock_input2):

        ls_corr = [0.0, 0.0, 0.20576131687242802, 0.617283950617284,
                   1.851851851851852, 5.555555555555556, 16.666666666666668, 50.0]

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-4351_3']
        con_series = list(df_result.loc[:, 'CONC'])
        self.assertEqual(ls_corr, con_series)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        classmethod that removes the csv file used to test
        :return None:
        """
        os.unlink('./Test_Files/setup_table_test.csv')


class SetupFileScriptAffinity_8k(TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        # Create a test DataFrame of the setup table.
        global df_setup_tbl
        df_setup_tbl = pd.DataFrame({'Broad ID': ['BRD-K81106261-001-01-4',
                                                  'BRD-K00024350-001-01-9',
                                                  'BRD-K00024351-001-01-9',
                                                  'BRD-A00024580-001-01-9',
                                                  'BRD-K00024582-001-01-9',
                                                  'BRD-A00024581-001-01-9',
                                                  'BRD-K00024583-014-01-9',
                                                  'BRD-A00024585-001-01-9',
                                                  'BRD-A00024584-001-01-9',
                                                  'BRD-K00024344-014-01-9',
                                                  'BRD-K81106261-001-01-4',
                                                  'BRD-K00024340-014-01-9',
                                                  'BRD-K00024341-001-01-9',
                                                  'BRD-K00024349-001-01-9',
                                                  'BRD-A00024348-001-01-9',
                                                  'BRD-K00024345-001-01-9'],
                        'Comment': ['This is the control cmpd', 'This is a comment', 'This is another cmpd.', 'None',
                                    'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None',
                                    'None', 'None'],
                        'MW': [496.55699999999996,
                               497.524,
                               497.524,
                               411.431,
                               425.458,
                               411.431,
                               455.44,
                               497.524,
                               497.524,
                               457.45599999999996,
                               496.55699999999996,
                               473.45599999999996,
                               398.392,
                               525.534,
                               525.557,
                               470.455],
                        'Sol. (uM)': [400, 500, 400, 500, 400, 500, 400, 500, 400, 500, 400, 500, 400, 500, 400, 500 ],
                        'Plate': ['Plate_06', 'Plate_07', 'Plate_07', 'Plate_07', 'Plate_07', 'Plate_07', 'Plate_07',
                                  'Plate_07', 'Plate_07', 'Plate_07', 'Plate_06', 'Plate_07', 'Plate_07', 'Plate_07',
                                  'Plate_07', 'Plate_07'],
                        'Barcode': [1172907815, 1196291078, 1196291070, 1196293322, 1196293323, 1196293331, 1196293339,
                                    1196293347, 1196293324, 1196291038, 1172907815, 1196291030, 1196291046, 1196291062,
                                    1196291022, 1196291054],
                        'BC Added': [1172907815, 1196291078, 1196291070, 1196293322, 1196293323, 1196293331, 1196293339,
                                    1196293347, 1196293324, 1196291038, 1172907815, 1196291030, 1196291046, 1196291062,
                                    1196291022, 1196291054],
                        'Well': ['H06', 'E03', 'E08', 'E10', 'E11', 'E12', 'F01', 'F02', 'F03', 'E06', 'H06', 'D12', 'E01',
                                 'E02', 'E05', 'E07'],

                        'Conc. (mM)': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,10, 10, 10, 10],
                        'Conc (uM)': [10000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 10000, 10000, 10000,
                                      10000, 10000, 10000],
                        '384W Dest.': ['A12', 'A24', 'B12', 'B24', 'C12', 'C24', 'D12', 'D24', 'E12', 'E24', 'F12', 'F24',
                                       'G12', 'G24', 'H12', 'H24'],
                        'Total Vol. (uL)': [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200],
                        'Test [Cpd] uM': [50, 20, 20, 20, 20, 20, 20, 20, 20, 20, 50, 100, 100, 100, 100, 100],
                        'fold_dil': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, ],
                        'num_pts': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
                        'Buffer (uL)': [190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 190,],
                        'Cmpd to Add (uL)': [1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1, 2, 2, 2, 2, 2],
                        'DMSO to Add (uL)': [9, 6, 6, 6, 6, 6, 6, 6, 6, 6, 9, 8, 8, 8, 8, 8]})

        # Export this table to a csv file for testing
        df_setup_tbl.to_csv('./Test_Files/setup_table_test.csv', index=False)

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', './Test_Files/setup_table_test.csv'])
    def test_spr_setup_sheet_method_input(self, mock_input1, mock_input2):
        """
        Test that confirms that the a DataFrame is returned from spr setup sheet method.
        """

        result = spr_setup_sheet()
        self.assertEqual(result.__class__, pd.DataFrame)

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', './Test_Files/setup_table_test.csv'])
    def test_correct_column_headers(self, mock_input1, mock_input2):
        """

        :return:
        """
        expected_headers = ['BRD', 'MW', 'CONC', 'BAR']
        df_result = spr_setup_sheet()
        self.assertEqual(expected_headers, list(df_result.columns))

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', './Test_Files/setup_table_test.csv'])
    def test_correct_BRD_format(self, mock_input1, mock_input2):
        """
        Test that confirms that the length of the BRD's are truncated to 10 characters.
        """

        df_result = spr_setup_sheet()
        self.assertEqual(10, len(str(df_result.iloc[1]['BRD'])))

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', './Test_Files/setup_table_test.csv'])
    def test_correct_cmpd_order(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        ls_corr = ['BRD-6261_1', 'BRD-4350_2', 'BRD-4351_3', 'BRD-4580_4', 'BRD-4582_5', 'BRD-4581_6', 'BRD-4583_7',
                   'BRD-4585_8', 'BRD-4584_9', 'BRD-4344_10', 'BRD-6261_11', 'BRD-4340_12', 'BRD-4341_13', 'BRD-4349_14',
                   'BRD-4348_15', 'BRD-4345_16']

        df_result = spr_setup_sheet()
        self.assertEqual(ls_corr, list(df_result.iloc[0:16]['BRD']))


    #TODO: Left off here
    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', './Test_Files/setup_table_test.csv'])
    def test_correct_order_and_calc_off_concentrations(self, mock_input1, mock_input2):
        """
        Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
        starting concentrations.
        """

        ls_corr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0390625, 0.0390625, 0.0390625,
                   0.0390625, 0.0390625, 0.0390625, 0.0390625, 0.0390625, 0.0390625, 0.078125, 0.078125, 0.078125,
                   0.078125, 0.078125, 0.078125, 0.078125, 0.078125, 0.078125, 0.09765625, 0.09765625, 0.15625,
                   0.15625, 0.15625, 0.15625, 0.15625, 0.15625, 0.15625, 0.15625, 0.15625, 0.1953125, 0.1953125,
                   0.1953125, 0.1953125, 0.1953125, 0.1953125, 0.1953125, 0.3125, 0.3125, 0.3125, 0.3125, 0.3125,
                   0.3125, 0.3125, 0.3125, 0.3125, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625,
                   0.390625, 0.625, 0.625, 0.625, 0.625, 0.625, 0.625, 0.625, 0.625, 0.625, 0.78125, 0.78125,
                   0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.25, 1.25,
                   1.25, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
                   2.5, 2.5, 3.125, 3.125, 3.125, 3.125, 3.125, 3.125, 3.125, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                   5.0, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0,
                   10.0, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0,
                   20.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0,
                   100.0, 100.0, 100.0, 100.0, 100.0]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'CONC']

        self.assertEqual(ls_corr, list(df_result))

    @patch('Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', './Test_Files/setup_table_test.csv'])
    def test_correct_output_barcodes(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1172907815, 1196291078, 1196291070, 1196293322, 1196293323, 1196293331, 1196293339, 1196293347,
                   1196293324, 1196291038, 1172907815, 1196291030, 1196291046, 1196291062, 1196291022, 1196291054,
                   1172907815, 1196291078, 1196291070, 1196293322, 1196293323, 1196293331, 1196293339, 1196293347,
                   1196293324, 1196291038, 1172907815, 1196291030, 1196291046, 1196291062, 1196291022, 1196291054,
                   1196291078, 1196291070, 1196293322, 1196293323, 1196293331, 1196293339, 1196293347, 1196293324,
                   1196291038, 1196291078, 1196291070, 1196293322, 1196293323, 1196293331, 1196293339, 1196293347,
                   1196293324, 1196291038, 1172907815, 1172907815, 1196291078, 1196291070, 1196293322, 1196293323,
                   1196293331, 1196293339, 1196293347, 1196293324, 1196291038, 1172907815, 1172907815, 1196291030,
                   1196291046, 1196291062, 1196291022, 1196291054, 1196291078, 1196291070, 1196293322, 1196293323,
                   1196293331, 1196293339, 1196293347, 1196293324, 1196291038, 1172907815, 1172907815, 1196291030,
                   1196291046, 1196291062, 1196291022, 1196291054, 1196291078, 1196291070, 1196293322, 1196293323,
                   1196293331, 1196293339, 1196293347, 1196293324, 1196291038, 1172907815, 1172907815, 1196291030,
                   1196291046, 1196291062, 1196291022, 1196291054, 1196291078, 1196291070, 1196293322, 1196293323,
                   1196293331, 1196293339, 1196293347, 1196293324, 1196291038, 1172907815, 1172907815, 1196291030,
                   1196291046, 1196291062, 1196291022, 1196291054, 1196291078, 1196291070, 1196293322, 1196293323,
                   1196293331, 1196293339, 1196293347, 1196293324, 1196291038, 1172907815, 1172907815, 1196291030,
                   1196291046, 1196291062, 1196291022, 1196291054, 1196291078, 1196291070, 1196293322, 1196293323,
                   1196293331, 1196293339, 1196293347, 1196293324, 1196291038, 1172907815, 1172907815, 1196291030,
                   1196291046, 1196291062, 1196291022, 1196291054, 1196291078, 1196291070, 1196293322, 1196293323,
                   1196293331, 1196293339, 1196293347, 1196293324, 1196291038, 1172907815, 1172907815, 1196291030,
                   1196291046, 1196291062, 1196291022, 1196291054, 1196291078, 1196291070, 1196293322, 1196293323,
                   1196293331, 1196293339, 1196293347, 1196293324, 1196291038, 1172907815, 1172907815, 1196291030,
                   1196291046, 1196291062, 1196291022, 1196291054, 1172907815, 1172907815, 1196291030, 1196291046,
                   1196291062, 1196291022, 1196291054, 1196291030, 1196291046, 1196291062, 1196291022, 1196291054]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @classmethod
    def tearDownClass(cls) -> None:
        """
        classmethod that removes the csv file used to test
        :return None:
        """
        os.unlink('./Test_Files/setup_table_test.csv')








