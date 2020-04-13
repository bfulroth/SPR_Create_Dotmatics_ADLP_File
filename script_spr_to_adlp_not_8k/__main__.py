from script_spr_to_adlp_not_8k.SPR_to_ADLP import spr_create_dot_upload_file


if __name__ == '__main__':

    # Load environmental variables
    from dotenv import load_dotenv
    load_dotenv()

    spr_create_dot_upload_file()