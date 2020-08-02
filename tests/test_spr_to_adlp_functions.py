"""
Module for testing SPR to ADLP functions that may be used across similar scripts.
"""

from unittest import TestCase
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, Table, MetaData, select
import pandas as pd
import numpy as np
from cryptography.fernet import Fernet

# Import functions for testing
from SPR_to_ADLP_Functions.common_functions import rep_item_for_dot_df, get_structures_smiles_from_db, \
    spr_binding_top_for_dot_file


class TestReplicateItemFunct(TestCase):
    """
    Test class that tests the rep_item_for_dot_df function.
    """

    @classmethod
    def setUpClass(cls) -> None:

        # Create a test DataFrame of the setup table.
        cls.df_setup_tbl = pd.DataFrame({'Broad ID': ['BRD-K81106261-001-01-4', 'BRD-K00024350-001-01-9', 'BRD-K00024351-001-01-9'],
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

        result = rep_item_for_dot_df(df=TestReplicateItemFunct.df_setup_tbl, col_name='Broad ID')

        ans = pd.Series(['BRD-K81106261-001-01-4', 'BRD-K81106261-001-01-4', 'BRD-K81106261-001-01-4',
               'BRD-K00024350-001-01-9', 'BRD-K00024350-001-01-9', 'BRD-K00024350-001-01-9',
               'BRD-K00024351-001-01-9', 'BRD-K00024351-001-01-9', 'BRD-K00024351-001-01-9'])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_item_1x(self):
        """
        Test replicating the BRD 1x, not sorted.
        """

        result = rep_item_for_dot_df(df=TestReplicateItemFunct.df_setup_tbl, col_name='Broad ID', times_dup=1)

        ans = pd.Series(['BRD-K81106261-001-01-4', 'BRD-K00024350-001-01-9', 'BRD-K00024351-001-01-9'])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_item_2x(self):
        """
        Test replicating the BRD 1x, not sorted.
        """

        result = rep_item_for_dot_df(df=TestReplicateItemFunct.df_setup_tbl, col_name='Broad ID', times_dup=2)

        ans = pd.Series(['BRD-K81106261-001-01-4', 'BRD-K81106261-001-01-4',
                         'BRD-K00024350-001-01-9', 'BRD-K00024350-001-01-9',
                         'BRD-K00024351-001-01-9', 'BRD-K00024351-001-01-9'])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_float_item_default_3(self):
        """
        Test replicating a series of floats by the default number, not sorted.
        """

        result = pd.Series(rep_item_for_dot_df(df=TestReplicateItemFunct.df_setup_tbl, col_name='MW'))

        ans = pd.Series([496.557, 496.557, 496.557,
                          497.524, 497.524, 497.524,
                          497.524, 497.524, 497.524])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_float_item_default_3_sorted(self):
        """
        Test replicating a series of floats by the default number, sorted.
        """

        result = pd.Series(rep_item_for_dot_df(df=TestReplicateItemFunct.df_setup_tbl, col_name='Sol. (uM)', sort=True))

        ans = pd.Series([10.6, 10.6, 10.6, 400, 400, 400, 500, 500, 500])

        self.assertEqual(result.all(), ans.all())
        self.assertEqual(len(result), len(ans))

    def test_dup_item_fail_no_column(self):
        """
        Test that the function raises a runtime error if the column is not found.
        """

        with self.assertRaises(RuntimeError):
            result = pd.Series(rep_item_for_dot_df(df=TestReplicateItemFunct.df_setup_tbl, col_name='Test', sort=True))


class TestGetStructSmilesDB(TestCase):

    df_setup_tbl = None
    results_from_db = None

    @classmethod
    def setUpClass(cls) -> None:
        # Create a test DataFrame of the setup table.

        cls.df_setup_tbl = pd.DataFrame(
            {'Broad ID': ['BRD-K81106261-001-01-4', 'BRD-K00024350-001-01-9', 'BRD-K00024351-001-01-9'],
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

        # Create a results DataFrame that simulates a database query from smiles
        cls.results_from_db = pd.DataFrame({'broadcoreid' : ['81106261', '00024350', '00024351'],
                                            'smiles' : ['smile1', 'smile2', 'smile3']})

    @patch('SPR_to_ADLP_Functions.common_functions._connect')
    @patch('pandas.DataFrame')
    @patch('sqlalchemy.create_engine')
    @patch('sqlalchemy.MetaData')
    @patch('sqlalchemy.Table')
    @patch('sqlalchemy.select')
    def test_1_connection_attempt_to_db(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6):
        """
        Test that one connection attempt to resultsdb is made when retrieving smiles
        :param mock_1: Mocks the sqlalchemy select call
        :param mock_2: Mocks the sqlalchemy Table call
        :param mock_3: Mocks the MetaData call
        :param mock_4: Mocks the sqlalchemy create_engine call
        :param mock_5: Mocks pandas DataFrame method that converts query results to a DataFrame
        :param mock_6: Mocks the _connect method that take a engine as a parameter and makes a db connection attempt.
        """

        # Mock the Crypt class that is needed to decrypt the database password.
        with patch('crypt.Crypt') as MockCrypt:
            MockCrypt.return_value.f.return_value = Fernet(b't43ZD1fHNQ9CZTkPDDP_1wCHmZ50C8o2vxKpmTNsgo8=')
            MockCrypt.return_value.f.decrypt.return_value = b'test'

            # Mock the results returned from the DB query.  As mocking a sqlalchemy query is difficult, the result as
            # a DataFrame object is returned from mock5 instead.
            mock_5.return_value = TestGetStructSmilesDB.results_from_db
            get_structures_smiles_from_db(df_mstr_tbl=TestGetStructSmilesDB.df_setup_tbl)

            # Assert that one connect attempt to the database was made.
            self.assertEqual(1, mock_6.call_count)
    
    # TODO: Need to create a results object composed of a dictionary of core id and smiles.
    # TODO: Cannot mock results = conn.execute(stmt).fetchall() after multiple attempts (5 hr)
    @patch('SPR_to_ADLP_Functions.common_functions._connect')
    @patch('pandas.DataFrame')
    @patch('sqlalchemy.create_engine')
    @patch('sqlalchemy.MetaData')
    @patch('sqlalchemy.Table')
    @patch('sqlalchemy.select')
    def test_correct_obj_returned(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6):
        """
        Test that a DataFrame object is returned.

        :param mock_1: Mocks the sqlalchemy select call
        :param mock_2: Mocks the sqlalchemy Table call
        :param mock_3: Mocks the MetaData call
        :param mock_4: Mocks the sqlalchemy create_engine call
        :param mock_5: Mocks pandas DataFrame method that converts query results to a DataFrame
        :param mock_6: Mocks the _connect method that take a engine as a parameter and makes a db connection attempt.
        """

        # Mock the Crypt class that is needed to decrypt the database password.
        with patch('crypt.Crypt') as MockCrypt:
            MockCrypt.return_value.f.return_value = Fernet(b't43ZD1fHNQ9CZTkPDDP_1wCHmZ50C8o2vxKpmTNsgo8=')
            MockCrypt.return_value.f.decrypt.return_value = b'test'

            # Mock the results returned from the DB query.
            mock_5.return_value = TestGetStructSmilesDB.results_from_db
            result = get_structures_smiles_from_db(df_mstr_tbl=TestGetStructSmilesDB.df_setup_tbl)

            self.assertEqual(result.__class__, pd.core.frame.DataFrame)

    @patch('SPR_to_ADLP_Functions.common_functions._connect')
    @patch('pandas.DataFrame')
    @patch('sqlalchemy.create_engine')
    @patch('sqlalchemy.MetaData')
    @patch('sqlalchemy.Table')
    @patch('sqlalchemy.select')
    def test_correct_results(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6):
        """
        Test that the returned DataFrame is as expected.

        :param mock_1: Mocks the sqlalchemy select call
        :param mock_2: Mocks the sqlalchemy Table call
        :param mock_3: Mocks the MetaData call
        :param mock_4: Mocks the sqlalchemy create_engine call
        :param mock_5: Mocks pandas DataFrame method that converts query results to a DataFrame
        :param mock_6: Mocks the _connect method that take a engine as a parameter and makes a db connection attempt.
        """

        # Mock the Crypt class that is needed to decrypt the database password.
        with patch('crypt.Crypt') as MockCrypt:
            MockCrypt.return_value.f.return_value = Fernet(b't43ZD1fHNQ9CZTkPDDP_1wCHmZ50C8o2vxKpmTNsgo8=')
            MockCrypt.return_value.f.decrypt.return_value = b'test'

            # Mock the results returned from the DB query.
            mock_5.return_value = TestGetStructSmilesDB.results_from_db
            result = get_structures_smiles_from_db(df_mstr_tbl=TestGetStructSmilesDB.df_setup_tbl)

            # Test columns
            expected_cols = ['Broad ID', 'BROAD_CORE_ID', 'SMILES']
            result_cols = result.columns
            self.assertEqual(expected_cols, list(result_cols))

            # Test Broad ID
            expected_ids = ['BRD-K81106261-001-01-4', 'BRD-K00024350-001-01-9', 'BRD-K00024351-001-01-9']
            result_ids = result['Broad ID'].tolist()
            self.assertEqual(expected_ids, result_ids)

            # Test BROAD_CORE_ID
            expected_core_ids = ['81106261', '00024350', '00024351']
            result_core_ids = result['BROAD_CORE_ID'].tolist()
            self.assertEqual(expected_core_ids, result_core_ids)

            # Test SMILES
            expected_smiles = ['smile1', 'smile2', 'smile3']
            result_smiles = result['SMILES'].tolist()
            self.assertEqual(expected_smiles, result_smiles)


class TestInsertSSandSensoImages(TestCase):

    def test_(self):
        pass


class TestRUatTopConcNot_8K(TestCase):
    """
    Class that tests spr_binding_top_for_dot_file() method in isolation for a Biacore T200 Instrument
    """

    # Class variables
    report_path = None
    df_cmpd_set = None
    instrument = None
    fc_used = None
    ref_fc_used_arr = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        Class that creates the parameters needed for testing the spr_binding_top_for_dot_file() method
        :return: None
        """

        #Create parameters for method testing
        cls.report_path = './tests/fixtures/Biacore1_Test_Files/200312_7279_affinity_rp.xls'
        cls.df_cmpd_set = pd.read_csv('./tests/fixtures/Biacore1_Test_Files/200312_setup_table.csv')
        cls.instrument = 'Biacore1'
        cls.fc_used = [1, 2, 3]
        cls.ref_fc_used_arr=[1]

    def test_bind_RU_TOP_ref_1_immob_2_3_4_correct_RU(self):

        expected = [48.78, 50.56, 49.85, 53.83, 54.91, 53.4, 54.57, 56.27, 54.58, 55.88, 55.31, 53.65, 38.85, 41.28,
                    41.21, 45.67, 51.6, 48.34, 27.93, 37.98, 37.86, 40.25, 40.41, 40.82, 46.67, 46.22, 46.85, 28.69,
                    38.59, 38.4, 40.6, 45.26, 43.74, 8.09, 19.26, 12.54, 31.95, 44.59, 36.64, 42.92, 53.72, 47.89,
                    38.61, 45.64, 44.77, 31.41, 37.33, 35.79]

        result = spr_binding_top_for_dot_file(report_pt_file=TestRUatTopConcNot_8K.report_path,
                                              df_cmpd_set=TestRUatTopConcNot_8K.df_cmpd_set,
                                              instrument=TestRUatTopConcNot_8K.instrument,
                                              fc_used=TestRUatTopConcNot_8K.fc_used,
                                              ref_fc_used_arr=TestRUatTopConcNot_8K.ref_fc_used_arr)
        ls_result = list(result)
        self.assertEqual(expected, ls_result)


class TestRUatTopConc8K(TestCase):
    """
    Class that tests spr_binding_top_for_dot_file() method in isolation for the Biacore 8K instrument
    """

    # Class variables
    report_path = None
    df_cmpd_set = None
    instrument = None
    fc_used = None
    ref_fc_used_arr = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        Class that creates the parameters needed for testing the spr_binding_top_for_dot_file() method
        :return: None
        """

        #Create parameters for method testing
        cls.report_path = './tests/fixtures/Biacore8k_Test_Files/20200708_7324_affinity_report_pt.xlsx'
        cls.df_cmpd_set = pd.read_csv('./tests/fixtures/Biacore8k_Test_Files/20200708_setup.csv')
        cls.instrument = 'Biacore8K'
        cls.fc_used = [1, 2, 3, 4, 5, 6, 7, 8]
        cls.ref_fc_used_arr=None

    def test_binding_RU_TOP(self):

        expected = [46.1, 17.67, 20.97, 14.17, 11.27, 0.91, 10.95, 5.94, 19.83, 14.1, 9.48, 10.85, 4.81,
                    12.92, 8.01, 8.75, 44.17, 13.72, 6.08, 13.62, 4.74, 4.94, 6.49, 10.07, 6.79, 7.91,
                    8.0, 16.21, 14.26, 11.69, 9.7, 7.51, 41.88, 5.04, 15.88, 8.89, 12.02, 12.17, 10.06,
                    17.38, 17.63, 9.98, 9.56, 13.47, 8.06, 19.52, 16.53, 7.13, 45.27, 25.32, 14.11, 17.88,
                    5.47, 4.26, 10.77, 15.67, 11.78, 33.63, 15.05, 13.38, 13.93, 19.45, 11.8, 17.57, 42.03,
                    11.84, 13.99, 9.44, 22.29, 7.0, 9.27, 15.99, 19.83, 18.91, 12.84, 10.5, 6.59, 6.09,
                    6.85, 10.12, 44.24, 8.61, 6.31, 10.48, 15.76, 9.21, 23.89, 3.79, 19.64, 0.63, 14.2,
                    12.74, 26.4, 22.73, 10.59, 4.83]

        result = spr_binding_top_for_dot_file(report_pt_file=TestRUatTopConc8K.report_path,
                                              df_cmpd_set=TestRUatTopConc8K.df_cmpd_set,
                                              instrument=TestRUatTopConc8K.instrument, fc_used=TestRUatTopConc8K.fc_used,
                                              ref_fc_used_arr=TestRUatTopConc8K.ref_fc_used_arr)
        ls_result = list(result)
        self.assertEqual(expected, ls_result)








