from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch
import os
from script_spr_setup_file.Create_SPR_setup_file import spr_setup_sheet
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
        df_setup_tbl.to_csv('tests/fixtures/setup_table_test.csv', index=False)

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

        df_test_setup_tbl_csv = pd.read_csv('tests/fixtures/setup_table_test.csv')

        self.assertEqual(list(df_test_setup_tbl_csv.columns), list(df_setup_tbl.columns))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
    def test_spr_setup_sheet_method_input(self, mock_input1, mock_input2):
        """
        Test that confirms that the a DataFrame is returned from spr setup sheet method.
        """

        result = spr_setup_sheet()
        self.assertEqual(result.__class__, pd.DataFrame)

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
    def test_correct_column_headers(self, monkeypatch, mock_input2):
        """

        :return:
        """
        expected_headers = ['BRD', 'MW', 'CONC', 'BAR']
        df_result = spr_setup_sheet()
        self.assertEqual(expected_headers, list(df_result.columns))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
    def test_correct_BRD_format(self, mock_input1, mock_input2):
        """
        Test that confirms that the length of the BRD's are truncated to 10 characters.
        """

        df_result = spr_setup_sheet()
        self.assertEqual(10, len(str(df_result.iloc[1]['BRD'])))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
    def test_two_zero_conc_points_first_cmpd(self, mock_input1, mock_input2):
        """
        Test to verify that the first to concentration points are zero
        """

        df_result = spr_setup_sheet()

        zero_one = df_result.iloc[1]['CONC']
        zero_two = df_result.iloc[1]['CONC']
        self.assertEqual(0, zero_one)
        self.assertEqual(0, zero_two)

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
    def test_correct_num_points_for_10pt_curves(self, mock_input1, mock_input2):

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-6261_1']

        self.assertEqual(12, len(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
    def test_correct_num_points_for_8pt_curves(self, mock_input1, mock_input2):

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-4350_2']

        self.assertEqual(10, len(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
    def test_correct_num_points_for_6pt_curves(self, mock_input1, mock_input2):

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-4351_3']

        self.assertEqual(8, len(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
    def test_correct_two_fold_dilution_10_pts(self, mock_input1, mock_input2):

        ls_corr = [0, 0, 0.09765625, 0.1953125, 0.390625, 0.78125, 1.5625, 3.125, 6.25, 12.5, 25, 50]

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-6261_1']
        con_series = list(df_result.loc[:, 'CONC'])
        self.assertEqual(ls_corr, con_series)

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
    def test_correct_1pt5_fold_dilution_8_pts(self, mock_input1, mock_input2):

        ls_corr = [0.0, 0.0, 2.9263831732967542, 4.389574759945131, 6.584362139917697,
                                      9.876543209876544, 14.814814814814817, 22.222222222222225, 33.333333333333336, 50.0]

        df_result = spr_setup_sheet()
        df_result = df_result[df_result['BRD'] == 'BRD-4350_2']
        con_series = list(df_result.loc[:, 'CONC'])
        self.assertEqual(ls_corr, con_series)

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['n', 'tests/fixtures/setup_table_test.csv'])
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
        os.unlink('tests/fixtures/setup_table_test.csv')


class SetupFileScriptAffinity_8k(TestCase):

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_10_pt_dose.csv'])
    def test_spr_setup_sheet_method_input(self, mock_input1, mock_input2):
        """
        Test that confirms that the a DataFrame is returned from spr setup sheet method.
        """

        result = spr_setup_sheet()
        self.assertEqual(result.__class__, pd.DataFrame)

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_10_pt_dose.csv'])
    def test_correct_column_headers(self, mock_input1, mock_input2):
        """
        :return:
        """
        expected_headers = ['BRD', 'MW', 'CONC', 'BAR']
        df_result = spr_setup_sheet()
        self.assertEqual(expected_headers, list(df_result.columns))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_10_pt_dose.csv'])
    def test_correct_BRD_format(self, mock_input1, mock_input2):
        """
        Test that confirms that the length of the BRD's are truncated to 10 characters.
        """

        df_result = spr_setup_sheet()
        self.assertEqual(10, len(str(df_result.iloc[1]['BRD'])))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_10_pt_dose.csv'])
    def test_correct_cmpd_order_8_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        ls_corr = ['BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8']

        df_result = spr_setup_sheet()
        self.assertEqual(ls_corr, list(df_result.iloc[0:8]['BRD']))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_10_pt_dose.csv'])
    def test_correct_order_conc_cal_8_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
        starting concentrations.
        """

        ls_corr = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.09765625,0.0390625,0.0390625,0.0390625,0.0390625,0.0390625,
                   0.09765625,0.09765625,0.1953125,0.078125,0.078125,0.078125,0.078125,0.078125,0.1953125,0.1953125,
                   0.390625,0.15625,0.15625,0.15625,0.15625,0.15625,0.390625,0.390625,0.78125,0.3125,0.3125,0.3125,
                   0.3125,0.3125,0.78125,0.78125,1.5625,0.625,0.625,0.625,0.625,0.625,1.5625,1.5625,3.125,1.25,1.25,1.25,
                   1.25,1.25,3.125,3.125,6.25,2.5,2.5,2.5,2.5,2.5,6.25,6.25,12.5,5,5,5,5,5,12.5,12.5,25,10,10,10,10,10,25,
                   25,50,20,20,20,20,20,50,50]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'CONC']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_10_pt_dose.csv'])
    def test_correct_order_barcodes_8_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,
                   1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,
                   1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,1196295245,
                   1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,1196295245,1196295253,
                   1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,1196295245,1196295253,1196295261,
                   1206274707,1196295269,1196295277,1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,
                   1196295269,1196295277,1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,
                   1196295277,1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,
                   1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,
                   1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,
                   1196295245,1196295253,1196295261,1206274707,1196295269,1196295277]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_10_pt_dose.csv'])
    def test_correct_order_mw_8_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the molecular weights for the output file are in the correct order.
        """

        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'MW']

        ls_corr = [496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577]

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_16_cpds_10_pt_dose.csv'])
    def test_correct_cmpd_order_16_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BRD']

        ls_corr = ['BRD-6261_1','BRD-6444_2','BRD-6445_3','BRD-6447_4','BRD-6332_5','BRD-6261_6','BRD-6446_7',
                   'BRD-6443_8','BRD-6261_1','BRD-6444_2','BRD-6445_3','BRD-6447_4','BRD-6332_5','BRD-6261_6',
                   'BRD-6446_7','BRD-6443_8','BRD-6261_1','BRD-6444_2','BRD-6445_3','BRD-6447_4','BRD-6332_5',
                   'BRD-6261_6','BRD-6446_7','BRD-6443_8','BRD-6261_1','BRD-6444_2','BRD-6445_3','BRD-6447_4',
                   'BRD-6332_5','BRD-6261_6','BRD-6446_7','BRD-6443_8','BRD-6261_1','BRD-6444_2','BRD-6445_3',
                   'BRD-6447_4','BRD-6332_5','BRD-6261_6','BRD-6446_7','BRD-6443_8','BRD-6261_1','BRD-6444_2',
                   'BRD-6445_3','BRD-6447_4','BRD-6332_5','BRD-6261_6','BRD-6446_7','BRD-6443_8','BRD-6261_1',
                   'BRD-6444_2','BRD-6445_3','BRD-6447_4','BRD-6332_5','BRD-6261_6','BRD-6446_7','BRD-6443_8',
                   'BRD-6261_1','BRD-6444_2','BRD-6445_3','BRD-6447_4','BRD-6332_5','BRD-6261_6','BRD-6446_7',
                   'BRD-6443_8','BRD-6261_1','BRD-6444_2','BRD-6445_3','BRD-6447_4','BRD-6332_5','BRD-6261_6',
                   'BRD-6446_7','BRD-6443_8','BRD-6261_1','BRD-6444_2','BRD-6445_3','BRD-6447_4','BRD-6332_5',
                   'BRD-6261_6','BRD-6446_7','BRD-6443_8','BRD-6261_1','BRD-6444_2','BRD-6445_3','BRD-6447_4',
                   'BRD-6332_5','BRD-6261_6','BRD-6446_7','BRD-6443_8','BRD-6261_1','BRD-6444_2','BRD-6445_3',
                   'BRD-6447_4','BRD-6332_5','BRD-6261_6','BRD-6446_7','BRD-6443_8','BRD-6449_9','BRD-6718_10',
                   'BRD-6261_11','BRD-6922_12','BRD-6920_13','BRD-6919_14','BRD-6918_15','BRD-6261_16','BRD-6449_9',
                   'BRD-6718_10','BRD-6261_11','BRD-6922_12','BRD-6920_13','BRD-6919_14','BRD-6918_15','BRD-6261_16',
                   'BRD-6449_9','BRD-6718_10','BRD-6261_11','BRD-6922_12','BRD-6920_13','BRD-6919_14','BRD-6918_15',
                   'BRD-6261_16','BRD-6449_9','BRD-6718_10','BRD-6261_11','BRD-6922_12','BRD-6920_13','BRD-6919_14',
                   'BRD-6918_15','BRD-6261_16','BRD-6449_9','BRD-6718_10','BRD-6261_11','BRD-6922_12','BRD-6920_13',
                   'BRD-6919_14','BRD-6918_15','BRD-6261_16','BRD-6449_9','BRD-6718_10','BRD-6261_11','BRD-6922_12',
                   'BRD-6920_13','BRD-6919_14','BRD-6918_15','BRD-6261_16','BRD-6449_9','BRD-6718_10','BRD-6261_11',
                   'BRD-6922_12','BRD-6920_13','BRD-6919_14','BRD-6918_15','BRD-6261_16','BRD-6449_9','BRD-6718_10',
                   'BRD-6261_11','BRD-6922_12','BRD-6920_13','BRD-6919_14','BRD-6918_15','BRD-6261_16','BRD-6449_9',
                   'BRD-6718_10','BRD-6261_11','BRD-6922_12','BRD-6920_13','BRD-6919_14','BRD-6918_15','BRD-6261_16',
                   'BRD-6449_9','BRD-6718_10','BRD-6261_11','BRD-6922_12','BRD-6920_13','BRD-6919_14','BRD-6918_15',
                   'BRD-6261_16','BRD-6449_9','BRD-6718_10','BRD-6261_11','BRD-6922_12','BRD-6920_13','BRD-6919_14',
                   'BRD-6918_15','BRD-6261_16','BRD-6449_9','BRD-6718_10','BRD-6261_11','BRD-6922_12','BRD-6920_13',
                   'BRD-6919_14','BRD-6918_15','BRD-6261_16']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_16_cpds_10_pt_dose.csv'])
    def test_correct_order_conc_cal_16_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
        starting concentrations.
        """

        ls_corr = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.09765625,0.0390625,0.0390625,
                   0.0390625,0.0390625,0.0390625,0.09765625,0.09765625,0.1953125,0.078125,0.078125,0.078125,0.078125,
                   0.078125,0.1953125,0.1953125,0.390625,0.15625,0.15625,0.15625,0.15625,0.15625,0.390625,0.390625,
                   0.78125,0.3125,0.3125,0.3125,0.3125,0.3125,0.78125,0.78125,1.5625,0.625,0.625,0.625,0.625,0.625,
                   1.5625,1.5625,3.125,1.25,1.25,1.25,1.25,1.25,3.125,3.125,6.25,2.5,2.5,2.5,2.5,2.5,6.25,6.25,12.5,
                   5.0,5.0,5.0,5.0,5.0,12.5,12.5,25.0,10.0,10.0,10.0,10.0,10.0,25.0,25.0,50.0,20.0,20.0,20.0,20.0,20.0,
                   50.0,50.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.09765625,0.09765625,
                   0.09765625,0.09765625,0.09765625,0.09765625,0.09765625,0.09765625,0.1953125,0.1953125,0.1953125,
                   0.1953125,0.1953125,0.1953125,0.1953125,0.1953125,0.390625,0.390625,0.390625,0.390625,0.390625,
                   0.390625,0.390625,0.390625,0.78125,0.78125,0.78125,0.78125,0.78125,0.78125,0.78125,0.78125,1.5625,
                   1.5625,1.5625,1.5625,1.5625,1.5625,1.5625,1.5625,3.125,3.125,3.125,3.125,3.125,3.125,3.125,3.125,6.25,
                   6.25,6.25,6.25,6.25,6.25,6.25,6.25,12.5,12.5,12.5,12.5,12.5,12.5,12.5,12.5,25.0,25.0,25.0,25.0,25.0,
                   25.0,25.0,25.0,50.0,50.0,50.0,50.0,50.0,50.0,50.0,50.0]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'CONC']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_16_cpds_10_pt_dose.csv'])
    def test_correct_order_barcodes_16_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,
                   1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,
                   1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,1196295245,
                   1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,1196295245,1196295253,
                   1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,1196295245,1196295253,1196295261,
                   1206274707,1196295269,1196295277,1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,
                   1196295269,1196295277,1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,
                   1196295277,1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,
                   1206274707,1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,
                   1196295332,1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1206274707,1196295332,
                   1196295245,1196295253,1196295261,1206274707,1196295269,1196295277,1196295474,1196295482,1206274707,
                   1196295490,1196295522,1196295506,1196295513,1206274707,1196295474,1196295482,1206274707,1196295490,
                   1196295522,1196295506,1196295513,1206274707,1196295474,1196295482,1206274707,1196295490,1196295522,
                   1196295506,1196295513,1206274707,1196295474,1196295482,1206274707,1196295490,1196295522,1196295506,
                   1196295513,1206274707,1196295474,1196295482,1206274707,1196295490,1196295522,1196295506,1196295513,
                   1206274707,1196295474,1196295482,1206274707,1196295490,1196295522,1196295506,1196295513,1206274707,
                   1196295474,1196295482,1206274707,1196295490,1196295522,1196295506,1196295513,1206274707,1196295474,
                   1196295482,1206274707,1196295490,1196295522,1196295506,1196295513,1206274707,1196295474,1196295482,
                   1206274707,1196295490,1196295522,1196295506,1196295513,1206274707,1196295474,1196295482,1206274707,
                   1196295490,1196295522,1196295506,1196295513,1206274707,1196295474,1196295482,1206274707,1196295490,
                   1196295522,1196295506,1196295513,1206274707,1196295474,1196295482,1206274707,1196295490,1196295522,
                   1196295506,1196295513,1206274707]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_16_cpds_10_pt_dose.csv'])
    def test_correct_order_mw_16_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the molecular weights for the output file are in the correct order.
        """
        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'MW']

        ls_corr = [496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   496.55699999999996,511.55,485.51300000000003,512.535,511.55,496.55699999999996,398.392,525.577,
                   510.565,359.356,496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,
                   359.356,496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996,510.565,359.356,
                   496.55699999999996,402.421,400.405,350.346,338.336,496.55699999999996]

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_24_cpds_10_pt_dose.csv'])
    def test_correct_cmpd_order_24_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BRD']

        ls_corr = ['BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5',
                   'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3',
                   'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2',
                   'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1',
                   'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8',
                   'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5',
                   'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3',
                   'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6449_9', 'BRD-6718_10',
                   'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16',
                   'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14',
                   'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12',
                   'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10',
                   'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16',
                   'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14',
                   'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12',
                   'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10',
                   'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16',
                   'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14',
                   'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12',
                   'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10',
                   'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16',
                   'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14',
                   'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12',
                   'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16', 'BRD-6921_17', 'BRD-4344_18',
                   'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24',
                   'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22',
                   'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20',
                   'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18',
                   'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24',
                   'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22',
                   'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20',
                   'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18',
                   'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24',
                   'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22',
                   'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20',
                   'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18',
                   'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24',
                   'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22',
                   'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20',
                   'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_24_cpds_10_pt_dose.csv'])
    def test_correct_order_conc_cal_24_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
        starting concentrations.
        """

        ls_corr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.09765625,
                   0.0390625, 0.0390625, 0.0390625, 0.0390625, 0.0390625, 0.09765625, 0.09765625, 0.1953125, 0.078125,
                   0.078125, 0.078125, 0.078125, 0.078125, 0.1953125, 0.1953125, 0.390625, 0.15625, 0.15625, 0.15625,
                   0.15625, 0.15625, 0.390625, 0.390625, 0.78125, 0.3125, 0.3125, 0.3125, 0.3125, 0.3125,
                   0.78125, 0.78125, 1.5625, 0.625, 0.625, 0.625, 0.625, 0.625, 1.5625, 1.5625, 3.125, 1.25,
                   1.25, 1.25, 1.25, 1.25, 3.125, 3.125, 6.25, 2.5, 2.5, 2.5, 2.5, 2.5, 6.25, 6.25, 12.5, 5.0,
                   5.0, 5.0, 5.0, 5.0, 12.5, 12.5, 25.0, 10.0, 10.0, 10.0, 10.0, 10.0, 25.0, 25.0, 50.0, 20.0,
                   20.0, 20.0, 20.0, 20.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.09765625, 0.09765625, 0.09765625, 0.09765625, 0.09765625, 0.09765625,
                   0.09765625, 0.09765625, 0.1953125, 0.1953125, 0.1953125, 0.1953125, 0.1953125, 0.1953125,
                   0.1953125, 0.1953125, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625,
                   0.390625, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 1.5625,
                   1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 3.125, 3.125, 3.125, 3.125,
                   3.125, 3.125, 3.125, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 12.5, 12.5, 12.5, 12.5,
                   12.5, 12.5, 12.5, 12.5, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 50.0, 50.0, 50.0,
                   50.0, 50.0, 50.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 0.09765625, 0.09765625, 0.09765625, 0.09765625, 0.09765625, 0.0390625,
                   0.09765625, 0.09765625, 0.1953125, 0.1953125, 0.1953125, 0.1953125, 0.1953125, 0.078125,
                   0.1953125, 0.1953125, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625, 0.15625, 0.390625,
                   0.390625, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.3125, 0.78125, 0.78125, 1.5625,
                   1.5625, 1.5625, 1.5625, 1.5625, 0.625, 1.5625, 1.5625, 3.125, 3.125, 3.125, 3.125, 3.125,
                   1.25, 3.125, 3.125, 6.25, 6.25, 6.25, 6.25, 6.25, 2.5, 6.25, 6.25, 12.5, 12.5, 12.5, 12.5,
                   12.5, 5.0, 12.5, 12.5, 25.0, 25.0, 25.0, 25.0, 25.0, 10.0, 25.0, 25.0, 50.0, 50.0, 50.0,
                   50.0, 50.0, 20.0, 50.0, 50.0]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'CONC']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_24_cpds_10_pt_dose.csv'])
    def test_correct_order_barcodes_24_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_24_cpds_10_pt_dose.csv'])
    def test_correct_order_mw_24_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the molecular weights for the output file are in the correct order.
        """
        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'MW']

        ls_corr = [496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392,
                   525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003,
                   512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55,
                   485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996,
                   511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577,
                   496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003,
                   512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55,
                   485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996,
                   511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577,
                   496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346,
                   338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996, 402.421, 400.405,
                   350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996, 402.421,
                   400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577,
                   352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996,
                   398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577,
                   352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996,
                   398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577]

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_32_cpds_10_pt_dose.csv'])
    def test_correct_cmpd_order_32_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BRD']

        ls_corr = ['BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5',
                   'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3',
                   'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2',
                   'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1',
                   'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8',
                   'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5',
                   'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3',
                   'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6449_9', 'BRD-6718_10',
                   'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16',
                   'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14',
                   'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12',
                   'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10',
                   'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16',
                   'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14',
                   'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12',
                   'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10',
                   'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16',
                   'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14',
                   'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12',
                   'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10',
                   'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16',
                   'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12', 'BRD-6920_13', 'BRD-6919_14',
                   'BRD-6918_15', 'BRD-6261_16', 'BRD-6449_9', 'BRD-6718_10', 'BRD-6261_11', 'BRD-6922_12',
                   'BRD-6920_13', 'BRD-6919_14', 'BRD-6918_15', 'BRD-6261_16', 'BRD-6921_17', 'BRD-4344_18',
                   'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24',
                   'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22',
                   'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20',
                   'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18',
                   'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24',
                   'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22',
                   'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20',
                   'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18',
                   'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24',
                   'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22',
                   'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20',
                   'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18',
                   'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24',
                   'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22',
                   'BRD-6446_23', 'BRD-6443_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20',
                   'BRD-6261_21', 'BRD-6261_22', 'BRD-6446_23', 'BRD-6443_24', 'BRD-6449_25', 'BRD-6718_26',
                   'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32',
                   'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30',
                   'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28',
                   'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26',
                   'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32',
                   'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30',
                   'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28',
                   'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26',
                   'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32',
                   'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30',
                   'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28',
                   'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26',
                   'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32',
                   'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30',
                   'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28',
                   'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32']

        self.assertEqual(ls_corr, list(df_result))

        @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
        @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_32_cpds_10_pt_dose.csv'])
        def test_correct_order_conc_cal_32_cpds_10_pt_dose(self, mock_input1, mock_input2):
            """
            Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
            starting concentrations.
            """

            ls_corr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.09765625,
                       0.0390625, 0.0390625, 0.0390625, 0.0390625, 0.0390625, 0.09765625, 0.09765625, 0.1953125,
                       0.078125, 0.078125, 0.078125, 0.078125, 0.078125, 0.1953125, 0.1953125, 0.390625, 0.15625,
                       0.15625, 0.15625, 0.15625, 0.15625, 0.390625, 0.390625, 0.78125, 0.3125, 0.3125, 0.3125,
                       0.3125, 0.3125, 0.78125, 0.78125, 1.5625, 0.625, 0.625, 0.625, 0.625, 0.625, 1.5625, 1.5625,
                       3.125, 1.25, 1.25, 1.25, 1.25, 1.25, 3.125, 3.125, 6.25, 2.5, 2.5, 2.5, 2.5, 2.5, 6.25, 6.25,
                       12.5, 5.0, 5.0, 5.0, 5.0, 5.0, 12.5, 12.5, 25.0, 10.0, 10.0, 10.0, 10.0, 10.0, 25.0, 25.0,
                       50.0, 20.0, 20.0, 20.0, 20.0, 20.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.09765625, 0.09765625, 0.09765625, 0.09765625, 0.09765625,
                       0.09765625, 0.09765625, 0.09765625, 0.1953125, 0.1953125, 0.1953125, 0.1953125, 0.1953125,
                       0.1953125, 0.1953125, 0.1953125, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625,
                       0.390625, 0.390625, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125,
                       1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 3.125, 3.125, 3.125,
                       3.125, 3.125, 3.125, 3.125, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 12.5, 12.5, 12.5,
                       12.5, 12.5, 12.5, 12.5, 12.5, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 50.0, 50.0,
                       50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0, 0.09765625, 0.09765625, 0.09765625, 0.09765625, 0.09765625,
                       0.0390625, 0.09765625, 0.09765625, 0.1953125, 0.1953125, 0.1953125, 0.1953125, 0.1953125,
                       0.078125, 0.1953125, 0.1953125, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625, 0.15625,
                       0.390625, 0.390625, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.3125, 0.78125, 0.78125,
                       1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 0.625, 1.5625, 1.5625, 3.125, 3.125, 3.125, 3.125,
                       3.125, 1.25, 3.125, 3.125, 6.25, 6.25, 6.25, 6.25, 6.25, 2.5, 6.25, 6.25, 12.5, 12.5, 12.5,
                       12.5, 12.5, 5.0, 12.5, 12.5, 25.0, 25.0, 25.0, 25.0, 25.0, 10.0, 25.0, 25.0, 50.0, 50.0,
                       50.0, 50.0, 50.0, 20.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0, 0.0, 0.0, 0.0, 0.0, 0.0390625, 0.009765625, 0.09765625, 0.09765625, 0.09765625, 0.09765625,
                       0.09765625, 0.09765625, 0.078125, 0.01953125, 0.1953125, 0.1953125, 0.1953125, 0.1953125,
                       0.1953125, 0.1953125, 0.15625, 0.0390625, 0.390625, 0.390625, 0.390625, 0.390625, 0.390625,
                       0.390625, 0.3125, 0.078125, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.78125, 0.625,
                       0.15625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.25, 0.3125, 3.125, 3.125, 3.125,
                       3.125, 3.125, 3.125, 2.5, 0.625, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 5.0, 1.25, 12.5, 12.5,
                       12.5, 12.5, 12.5, 12.5, 10.0, 2.5, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 20.0, 5.0, 50.0, 50.0,
                       50.0, 50.0, 50.0, 50.0]

            df_result = spr_setup_sheet()
            df_result = df_result.loc[:, 'CONC']

            self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_32_cpds_10_pt_dose.csv'])
    def test_correct_order_barcodes_32_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1206274707,1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_32_cpds_10_pt_dose.csv'])
    def test_correct_order_mw_32_cpds_10_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the molecular weights for the output file are in the correct order.
        """
        df_result = spr_setup_sheet()
        df_result = df_result.loc[ :, 'MW']

        ls_corr = [496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392,
                   525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535,
                   511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003,
                   512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55,
                   485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996,
                   511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577,
                   496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392,
                   525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535,
                   511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003,
                   512.535, 511.55, 496.55699999999996, 398.392, 525.577, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577,
                   352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996,
                   398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577,
                   352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996,
                   398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996,
                   510.565, 359.356, 496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996]

        self.assertEqual(ls_corr, list(df_result))

    # TODO Next testing of 6 pt dose curves
    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_6_pt_dose.csv'])
    def test_correct_cmpd_order_8_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BRD']

        ls_corr = ['BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2',
                   'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8',
                   'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2',
                   'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8',
                   'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8']

        self.assertEqual(ls_corr, list(df_result))

        @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
        @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_6_pt_dose.csv'])
        def test_correct_order_conc_cal_8_cpds_6_pt_dose(self, mock_input1, mock_input2):
            """
            Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
            starting concentrations.
            """

            ls_corr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.625,
                       1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.25, 3.125, 3.125, 3.125, 3.125,
                       3.125, 3.125, 3.125, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 5.0, 12.5, 12.5, 12.5,
                       12.5, 12.5, 12.5, 12.5, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 20.0, 50.0, 50.0,
                       50.0, 50.0, 50.0, 50.0, 50.0]

            df_result = spr_setup_sheet()
            df_result = df_result.loc[:, 'CONC']

            self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_6_pt_dose.csv'])
    def test_correct_order_barcodes_8_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_8_cpds_6_pt_dose.csv'])
    def test_correct_order_mw_8_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the molecular weights for the output file are in the correct order.
        """
        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'MW']

        ls_corr = [496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392,
                   525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003,
                   512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55,
                   485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996,
                   511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577,
                   496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577]

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_16_cpds_6_pt_dose.csv'])
    def test_correct_cmpd_order_16_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BRD']

        ls_corr = ['BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5',
                   'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3',
                   'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2',
                   'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1',
                   'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8',
                   'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9',
                   'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15',
                   'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9',
                   'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15',
                   'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_16_cpds_6_pt_dose.csv'])
    def test_correct_order_conc_cal_16_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
        starting concentrations.
        """

        ls_corr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.625,
                   1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.25, 3.125, 3.125, 3.125, 3.125,
                   3.125, 3.125, 3.125, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 5.0, 12.5, 12.5, 12.5,
                   12.5, 12.5, 12.5, 12.5, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 20.0, 50.0, 50.0,
                   50.0, 50.0, 50.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   0.0, 0.0, 0.0, 0.0, 1.5625, 0.625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125,
                   1.25, 3.125, 3.125, 3.125, 3.125, 3.125, 3.125, 6.25, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25,
                   6.25, 12.5, 5.0, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 25.0, 10.0, 25.0, 25.0, 25.0, 25.0,
                   25.0, 25.0, 50.0, 20.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'CONC']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_16_cpds_6_pt_dose.csv'])
    def test_correct_order_barcodes_16_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_16_cpds_6_pt_dose.csv'])
    def test_correct_order_mw_16_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the molecular weights for the output file are in the correct order.
        """
        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'MW']

        ls_corr = [496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392,
                   525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003,
                   512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55,
                   485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996,
                   511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577,
                   496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44,
                   411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392,
                   525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44,
                   411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392,
                   525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44,
                   411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577]

        self.assertEqual(ls_corr, list(df_result))


    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_24_cpds_6_pt_dose.csv'])
    def test_correct_cmpd_order_24_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BRD']

        ls_corr = ['BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5',
                   'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3',
                   'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2',
                   'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1',
                   'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8',
                   'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9',
                   'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15',
                   'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9',
                   'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15',
                   'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_17',
                   'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23',
                   'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21',
                   'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19',
                   'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17',
                   'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23',
                   'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21',
                   'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19',
                   'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17',
                   'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23',
                   'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21',
                   'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_24_cpds_6_pt_dose.csv'])
    def test_correct_order_conc_cal_24_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
        starting concentrations.
        """

        ls_corr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.625, 1.5625,
                   1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.25, 3.125, 3.125, 3.125, 3.125, 3.125, 3.125,
                   3.125, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 5.0, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5,
                   12.5, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 20.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0,
                   50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5625,
                   0.625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 1.25, 3.125, 3.125, 3.125, 3.125,
                   3.125, 3.125, 6.25, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 12.5, 5.0, 12.5, 12.5, 12.5, 12.5,
                   12.5, 12.5, 25.0, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 50.0, 20.0, 50.0, 50.0, 50.0, 50.0,
                   50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5625,
                   1.5625, 0.625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 3.125, 1.25, 3.125, 3.125, 3.125,
                   3.125, 3.125, 6.25, 6.25, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 12.5, 12.5, 5.0, 12.5, 12.5, 12.5,
                   12.5, 12.5, 25.0, 25.0, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 50.0, 50.0, 20.0, 50.0, 50.0, 50.0,
                   50.0, 50.0]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'CONC']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_24_cpds_6_pt_dose.csv'])
    def test_correct_order_barcodes_24_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_24_cpds_6_pt_dose.csv'])
    def test_correct_order_mw_24_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the molecular weights for the output file are in the correct order.
        """
        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'MW']

        ls_corr = [496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392,
                   525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003,
                   512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55,
                   485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996,
                   511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577,
                   496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392,
                   525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577,
                   352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996,
                   398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997,
                   457.45599999999996, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 352.36199999999997, 457.45599999999996, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997, 457.45599999999996,
                   352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996,
                   352.36199999999997, 457.45599999999996, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 352.36199999999997, 457.45599999999996, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997,
                   457.45599999999996, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 352.36199999999997, 457.45599999999996, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997, 457.45599999999996]

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_32_cpds_6_pt_dose.csv'])
    def test_correct_cmpd_order_32_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BRD']

        ls_corr = ['BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5',
                   'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3',
                   'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2',
                   'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1',
                   'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8',
                   'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9',
                   'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15',
                   'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9',
                   'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15',
                   'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_17',
                   'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23',
                   'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21',
                   'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19',
                   'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17',
                   'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23',
                   'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21',
                   'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19',
                   'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17',
                   'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23',
                   'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21',
                   'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27',
                   'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25',
                   'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31',
                   'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29',
                   'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27',
                   'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25',
                   'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31',
                   'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29',
                   'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27',
                   'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25',
                   'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31',
                   'BRD-6261_32']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_32_cpds_6_pt_dose.csv'])
    def test_correct_order_conc_cal_32_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
        starting concentrations.
        """

        ls_corr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.625, 1.5625,
                   1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.25, 3.125, 3.125, 3.125, 3.125, 3.125, 3.125,
                   3.125, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 5.0, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5,
                   12.5, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 20.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0,
                   50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5625,
                   0.625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 1.25, 3.125, 3.125, 3.125, 3.125,
                   3.125, 3.125, 6.25, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 12.5, 5.0, 12.5, 12.5, 12.5, 12.5,
                   12.5, 12.5, 25.0, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 50.0, 20.0, 50.0, 50.0, 50.0, 50.0,
                   50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5625,
                   1.5625, 0.625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 3.125, 1.25, 3.125, 3.125, 3.125,
                   3.125, 3.125, 6.25, 6.25, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 12.5, 12.5, 5.0, 12.5, 12.5, 12.5,
                   12.5, 12.5, 25.0, 25.0, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 50.0, 50.0, 20.0, 50.0, 50.0, 50.0,
                   50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5625,
                   1.5625, 1.5625, 0.625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 3.125, 3.125, 1.25, 3.125, 3.125,
                   3.125, 3.125, 6.25, 6.25, 6.25, 2.5, 6.25, 6.25, 6.25, 6.25, 12.5, 12.5, 12.5, 5.0, 12.5, 12.5,
                   12.5, 12.5, 25.0, 25.0, 25.0, 10.0, 25.0, 25.0, 25.0, 25.0, 50.0, 50.0, 50.0, 20.0, 50.0, 50.0,
                   50.0, 50.0]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'CONC']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_32_cpds_6_pt_dose.csv'])
    def test_correct_order_barcodes_32_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_32_cpds_6_pt_dose.csv'])
    def test_correct_order_mw_32_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the molecular weights for the output file are in the correct order.
        """
        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'MW']

        ls_corr = [496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392,
                   525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003,
                   512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55,
                   485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996,
                   511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577,
                   496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44,
                   411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392,
                   525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44,
                   411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392,
                   525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44,
                   411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392,
                   525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 352.36199999999997, 457.45599999999996, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997,
                   457.45599999999996, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 352.36199999999997, 457.45599999999996, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997, 457.45599999999996,
                   352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996,
                   352.36199999999997, 457.45599999999996, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 352.36199999999997, 457.45599999999996, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997,
                   457.45599999999996, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 352.36199999999997, 457.45599999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356, 496.55699999999996,
                   402.421, 400.405, 350.346, 338.336, 496.55699999999996]

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_40_cpds_6_pt_dose.csv'])
    def test_correct_cmpd_order_40_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the compounds have been sorted correctly
        """

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BRD']

        ls_corr = ['BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6',
                   'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5',
                   'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4',
                   'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3',
                   'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1', 'BRD-6444_2',
                   'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8', 'BRD-6261_1',
                   'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7', 'BRD-6443_8',
                   'BRD-6261_1', 'BRD-6444_2', 'BRD-6445_3', 'BRD-6447_4', 'BRD-6332_5', 'BRD-6261_6', 'BRD-6446_7',
                   'BRD-6443_8', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9',
                   'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15',
                   'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9',
                   'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15',
                   'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11', 'BRD-4581_12', 'BRD-6261_13',
                   'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_9', 'BRD-4344_10', 'BRD-4583_11',
                   'BRD-4581_12', 'BRD-6261_13', 'BRD-6261_14', 'BRD-6446_15', 'BRD-6443_16', 'BRD-6921_17',
                   'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23',
                   'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21',
                   'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19',
                   'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17',
                   'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23',
                   'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21',
                   'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19',
                   'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6921_17',
                   'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21', 'BRD-6261_22', 'BRD-6921_23',
                   'BRD-4344_24', 'BRD-6921_17', 'BRD-4344_18', 'BRD-4583_19', 'BRD-4581_20', 'BRD-6261_21',
                   'BRD-6261_22', 'BRD-6921_23', 'BRD-4344_24', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27',
                   'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25',
                   'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31',
                   'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29',
                   'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27',
                   'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25',
                   'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31',
                   'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29',
                   'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25', 'BRD-6718_26', 'BRD-6261_27',
                   'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31', 'BRD-6261_32', 'BRD-6449_25',
                   'BRD-6718_26', 'BRD-6261_27', 'BRD-6922_28', 'BRD-6920_29', 'BRD-6919_30', 'BRD-6918_31',
                   'BRD-6261_32', 'BRD-6449_33', 'BRD-6718_34', 'BRD-6261_35', 'BRD-6922_36', 'BRD-6920_37',
                   'BRD-6919_38', 'BRD-6918_39', 'BRD-6261_40', 'BRD-6449_33', 'BRD-6718_34', 'BRD-6261_35',
                   'BRD-6922_36', 'BRD-6920_37', 'BRD-6919_38', 'BRD-6918_39', 'BRD-6261_40', 'BRD-6449_33',
                   'BRD-6718_34', 'BRD-6261_35', 'BRD-6922_36', 'BRD-6920_37', 'BRD-6919_38', 'BRD-6918_39',
                   'BRD-6261_40', 'BRD-6449_33', 'BRD-6718_34', 'BRD-6261_35', 'BRD-6922_36', 'BRD-6920_37',
                   'BRD-6919_38', 'BRD-6918_39', 'BRD-6261_40', 'BRD-6449_33', 'BRD-6718_34', 'BRD-6261_35',
                   'BRD-6922_36', 'BRD-6920_37', 'BRD-6919_38', 'BRD-6918_39', 'BRD-6261_40', 'BRD-6449_33',
                   'BRD-6718_34', 'BRD-6261_35', 'BRD-6922_36', 'BRD-6920_37', 'BRD-6919_38', 'BRD-6918_39',
                   'BRD-6261_40', 'BRD-6449_33', 'BRD-6718_34', 'BRD-6261_35', 'BRD-6922_36', 'BRD-6920_37',
                   'BRD-6919_38', 'BRD-6918_39', 'BRD-6261_40', 'BRD-6449_33', 'BRD-6718_34', 'BRD-6261_35',
                   'BRD-6922_36', 'BRD-6920_37', 'BRD-6919_38', 'BRD-6918_39', 'BRD-6261_40']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_40_cpds_6_pt_dose.csv'])
    def test_correct_order_conc_cal_40_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Using the test setup tbl verify that the correct concentrations are calculated and sorted given different
        starting concentrations.
        """

        ls_corr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.625, 1.5625,
                   1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.25, 3.125, 3.125, 3.125, 3.125, 3.125, 3.125,
                   3.125, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 5.0, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5,
                   12.5, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 20.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0,
                   50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5625,
                   0.625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 1.25, 3.125, 3.125, 3.125, 3.125,
                   3.125, 3.125, 6.25, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 12.5, 5.0, 12.5, 12.5, 12.5, 12.5,
                   12.5, 12.5, 25.0, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 25.0, 50.0, 20.0, 50.0, 50.0, 50.0, 50.0,
                   50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   1.5625, 1.5625, 0.625, 1.5625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 3.125, 1.25, 3.125, 3.125,
                   3.125, 3.125, 3.125, 6.25, 6.25, 2.5, 6.25, 6.25, 6.25, 6.25, 6.25, 12.5, 12.5, 5.0, 12.5, 12.5,
                   12.5, 12.5, 12.5, 25.0, 25.0, 10.0, 25.0, 25.0, 25.0, 25.0, 25.0, 50.0, 50.0, 20.0, 50.0, 50.0,
                   50.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   1.5625, 1.5625, 1.5625, 0.625, 1.5625, 1.5625, 1.5625, 1.5625, 3.125, 3.125, 3.125, 1.25, 3.125,
                   3.125, 3.125, 3.125, 6.25, 6.25, 6.25, 2.5, 6.25, 6.25, 6.25, 6.25, 12.5, 12.5, 12.5, 5.0, 12.5,
                   12.5, 12.5, 12.5, 25.0, 25.0, 25.0, 10.0, 25.0, 25.0, 25.0, 25.0, 50.0, 50.0, 50.0, 20.0, 50.0,
                   50.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                   1.5625, 1.5625, 1.5625, 1.5625, 0.625, 1.5625, 1.5625, 1.5625, 3.125, 3.125, 3.125, 3.125, 1.25,
                   3.125, 3.125, 3.125, 6.25, 6.25, 6.25, 6.25, 2.5, 6.25, 6.25, 6.25, 12.5, 12.5, 12.5, 12.5, 5.0,
                   12.5, 12.5, 12.5, 25.0, 25.0, 25.0, 25.0, 10.0, 25.0, 25.0, 25.0, 50.0, 50.0, 50.0, 50.0, 20.0,
                   50.0, 50.0, 50.0]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'CONC']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_40_cpds_6_pt_dose.csv'])
    def test_correct_order_barcodes_40_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the barcodes for the output file are in the correct order.
        """

        ls_corr = [1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1206274707, 1196295332, 1196295245, 1196295253, 1196295261, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295269, 1196295277,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295489, 1196295443, 1196295451, 1196295459, 1206274707, 1206274707, 1196295489, 1196295443,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707,
                   1196295474, 1196295482, 1206274707, 1196295490, 1196295522, 1196295506, 1196295513, 1206274707]

        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'BAR']

        self.assertEqual(ls_corr, list(df_result))

    @patch('script_spr_setup_file.Create_SPR_setup_file.save_output_file')
    @patch('builtins.input', side_effect=['y', 'tests/fixtures/spr_setup_table_40_cpds_6_pt_dose.csv'])
    def test_correct_order_mw_40_cpds_6_pt_dose(self, mock_input1, mock_input2):
        """
        Test to verify that the molecular weights for the output file are in the correct order.
        """
        df_result = spr_setup_sheet()
        df_result = df_result.loc[:, 'MW']

        ls_corr = [496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392,
                   525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55,
                   496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003, 512.535,
                   511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55, 485.51300000000003,
                   512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996, 511.55,
                   485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577, 496.55699999999996,
                   511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996, 398.392, 525.577,
                   496.55699999999996, 511.55, 485.51300000000003, 512.535, 511.55, 496.55699999999996,
                   398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44,
                   411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392,
                   525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44,
                   411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 398.392,
                   525.577, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 398.392, 525.577, 352.36199999999997, 457.45599999999996, 455.44,
                   411.431, 496.55699999999996, 496.55699999999996, 398.392, 525.577, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996,
                   352.36199999999997, 457.45599999999996, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997,
                   457.45599999999996, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 352.36199999999997, 457.45599999999996, 352.36199999999997,
                   457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997,
                   457.45599999999996, 352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996,
                   496.55699999999996, 352.36199999999997, 457.45599999999996, 352.36199999999997, 457.45599999999996,
                   455.44, 411.431, 496.55699999999996, 496.55699999999996, 352.36199999999997, 457.45599999999996,
                   352.36199999999997, 457.45599999999996, 455.44, 411.431, 496.55699999999996, 496.55699999999996,
                   352.36199999999997, 457.45599999999996, 352.36199999999997, 457.45599999999996, 455.44, 411.431,
                   496.55699999999996, 496.55699999999996, 352.36199999999997, 457.45599999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996, 510.565, 359.356,
                   496.55699999999996, 402.421, 400.405, 350.346, 338.336, 496.55699999999996]

        self.assertEqual(ls_corr, list(df_result))

    # TODO Test 6 pt 48 cmpds