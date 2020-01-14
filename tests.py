from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch
import pytest
import click
from click.testing import CliRunner
import os
from Create_SPR_setup_file import spr_setup_sheet, save_output_file
import pandas as pd


class SetupFileScriptTests(TestCase):

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
                        'Test [Cpd] uM': [50, 20, 20],
                        'fold_dil': [2, 2, 2],
                        'num_pts': [10, 10, 10],
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

        result = spr_setup_sheet()
        self.assertEqual(result.__class__, pd.DataFrame)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        classmethod that removes the csv file used to test
        :return None:
        """
        os.unlink('./Test_Files/setup_table_test.csv')








