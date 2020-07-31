"""
Entry point to SPR_to_ADLP.py command line script.
"""
from script_spr_to_adlp_8k.SPR_to_ADLP_8K import spr_create_dot_upload_file
import click


# Using Click to manage the command line interface
@click.command()
@click.option('--config_file', prompt="Please paste the path of the configuration file", type=click.Path(exists=True))
@click.option('--save_file', prompt="Please type the name of the ADLP result file NO .xlsx extension NEEDED")
@click.option('--clip', is_flag=True, help="Option to indicate that the contents of the setup file are on the clipboard.")
@click.option('--structures', is_flag=True, help="Option to indicate attempting to insert structures from database.")
def main(config_file, save_file, clip, structures):
    spr_create_dot_upload_file(config_file=config_file, save_file=save_file, clip=clip, structures=structures)