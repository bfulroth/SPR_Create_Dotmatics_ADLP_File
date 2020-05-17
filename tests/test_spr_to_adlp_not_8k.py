from unittest import TestCase
from unittest.mock import MagicMock, patch
from script_spr_to_adlp_not_8k.SPR_to_ADLP import *
from script_spr_to_adlp_not_8k.Cli import main
import pandas as pd
from click.testing import CliRunner


class SPR_to_ADLP_not_8k(TestCase):

    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.get_structures_smiles_from_db', return_value='Structures Here')
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.render_structure_imgs',
           return_value = MagicMock(return_value = pd.DataFrame({'IMG_PATH': ['Fake/File/Path', 'Fake/File/Path2']})))
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.spr_insert_ss_senso_images',
           return_value='Image Place Holder')
    @patch('script_spr_to_adlp_not_8k.SPR_to_ADLP.spr_insert_structures')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_final_adlp_df_created(self, mock_1, mock_2, mock_3, mock_4, mock_5, mock_6) -> None:
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

    def test_correct_column_names(self):
        
        pass




