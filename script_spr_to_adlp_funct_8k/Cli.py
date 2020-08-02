"""
Entry point to script_spr_to_adlp_funct_8k command line script.
"""
from script_spr_to_adlp_funct_8k.SPR_to_ADLP_Funct_8K import spr_create_dot_upload_file
import click


# Using click to manage the command line interface
@click.command()
@click.option('--config_file', prompt="Please paste the path of the configuration file",
              help="Path of the configuration file. Text file with all of the file paths and meta "
                   "data for a particular experiment.")
@click.option('--save_file', prompt="Please type the name of the ADLP result file NO .xlsx extension NEEDED",
              help="Name of the ADLP results file which is an Excel file.")
@click.option('--clip', '-c', is_flag=True,
              help="Option to indicate that the contents of the setup file are on the clipboard.")
@click.option('--structures','-s', is_flag=True,
              help="Option to indicate attempting to insert structures from database.")
def main(config_file, save_file, clip, structures):
    spr_create_dot_upload_file(config_file=config_file, save_file=save_file, clip=clip, structures=structures)