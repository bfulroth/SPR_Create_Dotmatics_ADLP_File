"""
Entry point to SPR_to_ADLP.py command line script.
"""

from script_spr_to_adlp_not_8k.SPR_to_ADLP import spr_create_dot_upload_file
import click

# Using click to manage the command line interface
@click.command()
@click.option('--config_file', prompt="Please paste the path of the configuration file", type=click.Path(exists=True),
              help="Path of the configuration file. Text file with all of the file paths and meta "
                   "data for a particular experiment.")
@click.option('--save_file', prompt="Please type the name of the ADLP result file with an .xlsx extension"
                ,help="Name of the ADLP results file which is an Excel file.")
@click.option('--clip', is_flag=True,
              help="Option to indicate that the contents of the setup file are on the clipboard.")
def main(config_file, save_file, clip):
    spr_create_dot_upload_file(config_file=config_file, save_file=save_file, clip=clip)