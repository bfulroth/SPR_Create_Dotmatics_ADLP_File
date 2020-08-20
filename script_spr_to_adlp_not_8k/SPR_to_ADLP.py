import pandas as pd
import platform
import tempfile
import configparser
import os
import logging

import SPR_to_ADLP_Functions
from _version import __version__

# Get the users Home Directory
if platform.system() == "Windows":
    from pathlib import Path
    homedir = str(Path.home())
else:
    homedir = os.environ['HOME']

# Configure logger
logging.basicConfig(level=logging.INFO)


def spr_create_dot_upload_file(config_file, save_file, clip, structures=False):
    """
    Function the aggregates all data from and SPR binding experiment run with compounds at dose into one Excel File.

    :arg config_file: Text file containing all of the metadata for an SPR experiment run at dose.
    :arg save_file: Name of the final Excel file.
    :arg clip: Optional flag that indicates if the setup table exists on the clipboard.
    :param structures: Optional flag that indicates if the program should attempt to insert chemical structures.
    :return None

    """

    # ADLP save file path
    # Note the version is saved to the file name so that data can be linked to the script version.
    save_file = save_file.replace('.xlsx', '')
    adlp_save_file_path = os.path.join(homedir, 'Desktop', save_file + '_APPVersion_' + str(__version__))
    adlp_save_file_path = adlp_save_file_path.replace('.', '_')
    adlp_save_file_path = adlp_save_file_path + '.xlsx'

    try:
        logging.info('Collecting metadata from configuration file...')
        config = configparser.ConfigParser()
        config.read(config_file)

        # Get all of the file paths from the configuration file and store in variables so they are available
        if clip:
            df_cmpd_set = pd.read_clipboard()
        else:
            path_master_tbl = config.get('paths', 'path_mstr_tbl')
            df_cmpd_set = pd.read_csv(path_master_tbl)

        path_ss_img = config.get('paths', 'path_ss_img')
        path_senso_img = config.get('paths', 'path_senso_img')
        path_ss_txt = config.get('paths', 'path_ss_txt')
        path_senso_txt = config.get('paths', 'path_senso_txt')
        path_report_pt = config.get('paths', 'path_report_pt')

        # Get all of the metadata variables
        num_fc_used = config.get('meta','num_fc_used')

        # Get the reference channel
        ref_fc_used = str(config.get('meta', 'ref_fc_used'))
        ref_fc_used = ref_fc_used.strip(" ")
        ref_fc_used = ref_fc_used.replace(' ', '')
        ref_fc_used_arr = ref_fc_used.split(',')
        ref_fc_used_arr = [int(i) for i in ref_fc_used_arr]

        # Get the flow channels immobilized
        immobilized_fc = str(config.get('meta', 'immobilized_fc'))
        immobilized_fc = immobilized_fc.strip(" ")
        immobilized_fc = immobilized_fc.replace(' ', '')
        immobilized_fc_arr = immobilized_fc.split(',')
        immobilized_fc_arr = [int(i) for i in immobilized_fc_arr]

        if int(num_fc_used) != len(immobilized_fc_arr):
            raise RuntimeError ('The number of flow channels used is not equal to the number of immobilized flow '
                                'channels.')

        # Continue collecting variables from the configuration file.
        experiment_date = config.get('meta','experiment_date')
        project_code = config.get('meta','project_code')
        operator = config.get('meta','operator')
        instrument = config.get('meta','instrument')
        protocol = config.get('meta','protocol')
        chip_lot = config.get('meta','chip_lot')
        nucleotide = config.get('meta','nucleotide')
        raw_data_filename = config.get('meta','raw_data_filename')
        directory_folder = config.get('meta','directory_folder')

        if immobilized_fc_arr[0] == 2 and int(num_fc_used) == 1:
            fc2_protein_BIP = config.get('meta','fc2_protein_BIP')
            fc2_protein_RU = float(config.get('meta','fc2_protein_RU'))
            fc2_protein_MW = float(config.get('meta','fc2_protein_MW'))

        elif immobilized_fc_arr[0] == 4 and int(num_fc_used) == 1:
            fc4_protein_BIP = config.get('meta', 'fc4_protein_BIP')
            fc4_protein_RU = float(config.get('meta', 'fc4_protein_RU'))
            fc4_protein_MW = float(config.get('meta', 'fc4_protein_MW'))

        else:
            fc2_protein_BIP = config.get('meta', 'fc2_protein_BIP')
            fc2_protein_RU = float(config.get('meta', 'fc2_protein_RU'))
            fc2_protein_MW = float(config.get('meta', 'fc2_protein_MW'))
            fc3_protein_BIP = config.get('meta','fc3_protein_BIP')
            fc3_protein_RU = float(config.get('meta','fc3_protein_RU'))
            fc3_protein_MW = float(config.get('meta','fc3_protein_MW'))
            fc4_protein_BIP = config.get('meta','fc4_protein_BIP')
            fc4_protein_RU = float(config.get('meta','fc4_protein_RU'))
            fc4_protein_MW = float(config.get('meta','fc4_protein_MW'))
        logging.info('Finished collecting metadata from configuration file. Proceeding...')
    except:
        raise RuntimeError('Something is wrong with the config file. Please check.')

    logging.info('Creating the ADLP File...')
    # Start building the final Dotmatics DataFrame
    df_final_for_dot = pd.DataFrame()

    # Start by adding the Broad ID in the correct order.
    num_fc_used = int(num_fc_used)
    df_final_for_dot['BROAD_ID'] = pd.Series(SPR_to_ADLP_Functions.common_functions.rep_item_for_dot_df(df_cmpd_set, col_name='Broad ID',
                                                                 times_dup=num_fc_used))

    # Add structure column
    df_final_for_dot.loc[:, 'STRUCTURES'] = ''

    # Add the Project Code.  Get this from the config file.
    df_final_for_dot.loc[:, 'PROJECT_CODE'] = project_code

    #  Add an empty column called curve_valid
    df_final_for_dot.loc[:, 'CURVE_VALID'] = ''

    # Add an empty column called steady_state_img
    df_final_for_dot.loc[:, 'STEADY_STATE_IMG'] = ''

    # Add an empty column called 1to1_img
    df_final_for_dot.loc[:,  '1to1_IMG'] = ''

    # Add the starting compound concentrations
    df_final_for_dot.loc[:, 'TOP_COMPOUND_UM'] = pd.Series(
        SPR_to_ADLP_Functions.common_functions.rep_item_for_dot_df(df_cmpd_set, col_name='Test [Cpd] uM',
                                                                   times_dup=num_fc_used))

    # Extract the RU Max for each compound using the report point file.
    df_final_for_dot['RU_TOP_CMPD'] = SPR_to_ADLP_Functions.common_functions.spr_binding_top_for_dot_file(
        report_pt_file=path_report_pt,
        df_cmpd_set=df_cmpd_set,
        instrument=instrument,
        fc_used=immobilized_fc_arr,
        ref_fc_used_arr=ref_fc_used_arr)

    # Extract the steady state data and add to DataFrame
    # Read in the steady state text file into a DataFrame
    logging.info('Reading data from steady state fit file...')
    df_ss_txt = pd.read_csv(path_ss_txt, sep='\t')

    # Create new columns to sort the DataFrame as the original is out of order.
    df_ss_txt['sample_order'] = df_ss_txt['Image File'].str.split('_', expand=True)[1]
    df_ss_txt['sample_order'] = pd.to_numeric(df_ss_txt['sample_order'])
    df_ss_txt['fc_num'] = pd.to_numeric(df_ss_txt['Curve'].str[3])
    df_ss_txt = df_ss_txt.sort_values(by=['sample_order', 'fc_num'])
    df_ss_txt = df_ss_txt.reset_index(drop=True)
    df_ss_txt['KD_SS_UM'] = round(df_ss_txt['KD (M)'] * 1000000, 3)

    # Add the KD steady state
    df_final_for_dot['KD_SS_UM'] = df_ss_txt['KD_SS_UM']

    # Add the chi2_steady_state_affinity
    df_final_for_dot['CHI2_SS_AFFINITY'] = round(df_ss_txt['Chi² (RU²)'], 3)

    # Add the Fitted_Rmax_steady_state_affinity
    df_final_for_dot['FITTED_RMAX_SS_AFFINITY'] = df_ss_txt['Rmax (RU)']

    # Extract the sensorgram data and add to DataFrame
    # Read in the sensorgram data into a DataFrame
    logging.info('Reading data from kinetic fit file...')
    df_senso_txt = pd.read_csv(path_senso_txt, sep='\t')
    df_senso_txt['sample_order'] = df_senso_txt['Image File'].str.split('_', expand=True)[1]
    df_senso_txt['sample_order'] = pd.to_numeric(df_senso_txt['sample_order'])
    df_senso_txt['fc_num'] = pd.to_numeric(df_senso_txt['Curve'].str[3])
    df_senso_txt = df_senso_txt.sort_values(by=['sample_order', 'fc_num'])
    df_senso_txt = df_senso_txt.reset_index(drop=True)

    # Add columns from df_senso_txt
    df_final_for_dot['KA_1_1_BINDING'] = df_senso_txt['ka (1/Ms)']
    df_final_for_dot['KD_LITTLE_1_1_BINDING'] = round(df_senso_txt['kd (1/s)'], 3)
    df_final_for_dot['KD_1_1_BINDING_UM'] = df_senso_txt['KD (M)'] * 1000000
    df_final_for_dot['chi2_1_1_binding'] = df_senso_txt['Chi² (RU²)']

    df_final_for_dot.loc[:, 'U_VALUE_1_1_BINDING'] = ''

    # Continue creating new columns
    df_final_for_dot['FITTED_RMAX_1_1_BINDING'] = df_senso_txt['Rmax (RU)']
    df_final_for_dot['COMMENTS'] = ''

    # Rename the flow channels and add the flow channel column
    df_senso_txt['FC'] = df_senso_txt['Curve'].apply(lambda x: x.replace('c', 'C'))
    df_senso_txt['FC'] = df_senso_txt['FC'].apply(lambda x: x.replace('=', ''))
    df_senso_txt['FC'] = df_senso_txt['FC'].apply(lambda x: x.replace(' ', ''))
    df_final_for_dot['FC'] = df_senso_txt['FC']

    # Protein RU, MW, and BIP to corresponding columns
    if immobilized_fc_arr[0] == 2 and int(num_fc_used) == 1:
        protein_ru_dict = {'FC2-1Corr': fc2_protein_RU}
        protein_mw_dict = {'FC2-1Corr': fc2_protein_MW}
        protein_bip_dict = {'FC2-1Corr': fc2_protein_BIP}

    elif immobilized_fc_arr[0] == 4 and int(num_fc_used) == 1:
        protein_ru_dict = {'FC4-3Corr': fc4_protein_RU}
        protein_mw_dict = {'FC4-3Corr': fc4_protein_MW}
        protein_bip_dict = {'FC4-3Corr': fc4_protein_BIP}

    else:
        protein_ru_dict = {'FC2-1Corr': fc2_protein_RU, 'FC3-1Corr': fc3_protein_RU, 'FC4-1Corr': fc4_protein_RU,
                           'FC4-3Corr': fc4_protein_RU}
        protein_mw_dict = {'FC2-1Corr': fc2_protein_MW, 'FC3-1Corr': fc3_protein_MW, 'FC4-1Corr': fc4_protein_MW,
                           'FC4-3Corr': fc4_protein_MW}
        protein_bip_dict = {'FC2-1Corr': fc2_protein_BIP, 'FC3-1Corr': fc3_protein_BIP, 'FC4-1Corr': fc4_protein_BIP,
                            'FC4-3Corr': fc4_protein_BIP}

    df_final_for_dot['PROTEIN_RU'] = df_final_for_dot['FC'].map(protein_ru_dict)
    df_final_for_dot['PROTEIN_MW'] = df_final_for_dot['FC'].map(protein_mw_dict)
    df_final_for_dot['PROTEIN_ID'] = df_final_for_dot['FC'].map(protein_bip_dict)

    # Add the MW for each compound.
    df_final_for_dot['MW'] = round(pd.Series(SPR_to_ADLP_Functions.
                                             common_functions.rep_item_for_dot_df(df_cmpd_set, col_name='MW',
                                                                                  times_dup=num_fc_used)), 3)

    # Continue adding columns to final DataFrame
    df_final_for_dot['INSTRUMENT'] = instrument
    df_final_for_dot['ASSAY_MODE'] = 'Multi-Cycle'
    df_final_for_dot['EXP_DATE'] = experiment_date
    df_final_for_dot['NUCLEOTIDE'] = nucleotide
    df_final_for_dot['CHIP_LOT'] = chip_lot
    df_final_for_dot['OPERATOR'] = operator
    df_final_for_dot['PROTOCOL_ID'] = protocol
    df_final_for_dot['RAW_DATA_FILE'] = raw_data_filename
    df_final_for_dot['DIR_FOLDER'] = directory_folder

    # Add the unique ID #
    df_final_for_dot['UNIQUE_ID'] = df_senso_txt['Sample'] + '_' + df_final_for_dot['FC'] + '_' + project_code + \
                                    '_' + experiment_date + \
                                    '_' + df_senso_txt['Image File'].str.split('_', expand=True)[5]

    # Add steady state image file path
    # Need to replace /Volumes with //Iron
    path_ss_img_edit = path_ss_img.replace('/Volumes', '//Iron')
    df_final_for_dot['SS_IMG_ID'] = path_ss_img_edit + '/' + df_ss_txt['Image File']

    # Add sensorgram image file path
    # Need to replace /Volumes with //Iron
    path_senso_img_edit = path_senso_img.replace('/Volumes', '//Iron')
    df_final_for_dot['SENSO_IMG_ID'] = path_senso_img_edit + '/' + df_senso_txt['Image File']

    # Add the Rmax_theoretical.
    # Note couldn't do this before as I needed to add protein MW and RU first.
    df_final_for_dot['RMAX_THEORETICAL'] = round((df_final_for_dot['MW'] / df_final_for_dot['PROTEIN_MW']) \
                                           * df_final_for_dot['PROTEIN_RU'], 2)

    # Calculate Percent Binding

    df_final_for_dot['PERCENT_BINDING_TOP'] = round((df_final_for_dot['RU_TOP_CMPD'] /
                                                     df_final_for_dot['RMAX_THEORETICAL']) * 100, 2)

    # Rearrange the columns for the final DataFrame (without images)
    df_final_for_dot = df_final_for_dot.loc[:, ['BROAD_ID', 'STRUCTURES', 'PROJECT_CODE', 'CURVE_VALID',
                                                'STEADY_STATE_IMG', '1to1_IMG', 'TOP_COMPOUND_UM',
                                                'RMAX_THEORETICAL', 'RU_TOP_CMPD', 'PERCENT_BINDING_TOP',
                                                'KD_SS_UM', 'CHI2_SS_AFFINITY', 'FITTED_RMAX_SS_AFFINITY',
                                                'KA_1_1_BINDING', 'KD_LITTLE_1_1_BINDING', 'KD_1_1_BINDING_UM',
                                                'chi2_1_1_binding', 'U_VALUE_1_1_BINDING', 'FITTED_RMAX_1_1_BINDING',
                                                'COMMENTS', 'FC', 'PROTEIN_RU', 'PROTEIN_MW', 'PROTEIN_ID', 'MW',
                                                'INSTRUMENT', 'ASSAY_MODE', 'EXP_DATE', 'NUCLEOTIDE', 'CHIP_LOT',
                                                'OPERATOR', 'PROTOCOL_ID', 'RAW_DATA_FILE', 'DIR_FOLDER', 'UNIQUE_ID',
                                                'SS_IMG_ID', 'SENSO_IMG_ID']]

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(adlp_save_file_path, engine='xlsxwriter')

    # Convert the DataFrame to an XlsxWriter Excel object.
    df_final_for_dot.to_excel(writer, sheet_name='Sheet1', startcol=0, index=None)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet1 = writer.sheets['Sheet1']

    # Add a drop down list of comments.
    # Calculate the number of rows to add the drop down menu.
    num_cpds = len(df_cmpd_set.index)
    num_data_pts = (num_cpds * 3) + 1

    # Write the comments to the comment sheet.
    comments_list = SPR_to_ADLP_Functions.common_functions.get_predefined_comments()

    # Convert comments list to DataFrame
    comments_list.to_excel(writer, sheet_name='Sheet2', startcol=0, index=0)

    # For larger drop down lists > 255 characters its necessary to create a list on a seperate worksheet.
    worksheet1.data_validation('T1:T' + str(num_data_pts),
                                    {'validate': 'list',
                                     'source': '=Sheet2!$A$2:$A$' + str(len(comments_list) + 1)
                                     })

    # Freeze the top row of the excel worksheet.
    worksheet1.freeze_panes(1, 0)

    # Add a cell format object to align text center.
    cell_format = workbook.add_format()
    cell_format.set_align('center')
    cell_format.set_align('vcenter')
    worksheet1.set_column('A:AK', 25, cell_format)

    # Start preparing to insert the steady state and sensorgram images.
    # Get list of image files from df_ss_txt Dataframe.
    list_ss_img = df_ss_txt['Image File'].tolist()

    # Get list of images files in the df_senso_txt DataFrame.
    list_sonso_img = df_senso_txt['Image File'].tolist()

    # Create a list of tuples containing the names of the steady state image and sensorgram image.
    tuple_list_imgs = list(zip(list_ss_img, list_sonso_img))

    # Insert steady-state and sensogram images into file.
    SPR_to_ADLP_Functions.common_functions.spr_insert_ss_senso_images(tuple_list_imgs, worksheet1, path_ss_img,
                                                                      path_senso_img, biacore=instrument)
    # Insert structure images
    SPR_to_ADLP_Functions.common_functions.manage_structure_insertion(df_cmpd_set=df_cmpd_set,
                                                                       num_fc_used=num_fc_used, worksheet=worksheet1,
                                                                       structures=structures, writer=writer)
    print('\nProgram Done!')
    print("The ADLP result was saved to your desktop.")
    return df_final_for_dot