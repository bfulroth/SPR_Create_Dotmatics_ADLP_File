from unittest import TestCase
from Create_SPR_setup_file import spr_setup_sheet


class SetupFileTests(TestCase):

    def test_can_call_spr_setup_sheet(self):

        x = spr_setup_sheet()

