"""
Module for testing SPR to ADLP functions that may be used across similar scripts.
"""

from unittest import TestCase
import pandas as pd

# Import functions for testing
from SPR_to_ADLP_Functions.common_functions import rep_item_for_dot_df


class TestReplicateItemFunct(TestCase):
    """
    Test class that tests the rep_item_for_dot_df function.
    """

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

    def test_dup_item_default_3(self):
        """
        Test replicating the BRD 3x which is the default, not sorted.
        """

        result = rep_item_for_dot_df(df=df_setup_tbl, col_name='Broad ID')

        ans = pd.Series(['BRD-K81106261-001-01-4', 'BRD-K81106261-001-01-4', 'BRD-K81106261-001-01-4',
               'BRD-K00024350-001-01-9', 'BRD-K00024350-001-01-9', 'BRD-K00024350-001-01-9',
               'BRD-K00024351-001-01-9', 'BRD-K00024351-001-01-9', 'BRD-K00024351-001-01-9'])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_item_1x(self):
        """
        Test replicating the BRD 1x, not sorted.
        """

        result = rep_item_for_dot_df(df=df_setup_tbl, col_name='Broad ID', times_dup=1)

        ans = pd.Series(['BRD-K81106261-001-01-4', 'BRD-K00024350-001-01-9', 'BRD-K00024351-001-01-9'])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_item_2x(self):
        """
        Test replicating the BRD 1x, not sorted.
        """

        result = rep_item_for_dot_df(df=df_setup_tbl, col_name='Broad ID', times_dup=2)

        ans = pd.Series(['BRD-K81106261-001-01-4', 'BRD-K81106261-001-01-4',
                         'BRD-K00024350-001-01-9', 'BRD-K00024350-001-01-9',
                         'BRD-K00024351-001-01-9', 'BRD-K00024351-001-01-9'])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_float_item_default_3(self):
        """
        Test replicating a series of floats by the default number, not sorted.
        """

        result = pd.Series(rep_item_for_dot_df(df=df_setup_tbl, col_name='MW'))

        ans = pd.Series([496.557, 496.557, 496.557,
                          497.524, 497.524, 497.524,
                          497.524, 497.524, 497.524])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_float_item_default_3_sorted(self):
        """
        Test replicating a series of floats by the default number, sorted.
        """

        result = pd.Series(rep_item_for_dot_df(df=df_setup_tbl, col_name='Sol. (uM)', sort=True))

        ans = pd.Series([10.6, 10.6, 10.6, 400, 400, 400, 500, 500, 500])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_item_fail_no_column(self):
        """
        Test that the function raises a runtime error if the column is not found.
        """

        with self.assertRaises(RuntimeError):
            result = pd.Series(rep_item_for_dot_df(df=df_setup_tbl, col_name='Test', sort=True))




