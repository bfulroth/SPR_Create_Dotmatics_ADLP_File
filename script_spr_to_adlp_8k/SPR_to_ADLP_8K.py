import pandas as pd
import os
import re
import platform
import numpy as np
from glob import glob
import shutil
from datetime import datetime
import SPR_to_ADLP_Functions
import tempfile
from _version import __version__
import xlrd
import logging

# Get the users Home Directory
if platform.system() == "Windows":
    from pathlib import Path
    homedir = str(Path.home())
else:
    homedir = os.environ['HOME']

# Set the date to include in the file directory if a crash occures
NOW = datetime.now()
NOW = NOW.strftime('%y%m%d')

# Configure logger
logging.basicConfig(level=logging.INFO)

def rename_images(df_analysis, path_img, image_type, raw_data_file_name):
    """
    Method that renames the images in a folder.  Also adds the names of the images to the passed in df.
    :param df_analysis: Dataframe containing the steady state or kinetic fit results.
    :param path_img: Path to the folder containing the images to rename
    :param image_type: The type of image 'ss' for steady state or 'senso' for kinetic fits.
    :param raw_data_file_name: Name of the raw data file used when renaming the images.
    :return: The df_ss_senso df with the column with the image names added.
    """

    logging.info('Attempting to rename %s images...', image_type)

    # Store the current working directory
    my_dir = os.getcwd()

    # Change the Directory to the ss image folder
    os.chdir(path_img)

    # Delete legend from folder.
    ls_legend_file = [f for f in os.listdir(path_img) if re.search(r'Legend\.png', f)]
    if not len(ls_legend_file) == 0:
        legend_file_path = os.path.join(path_img, ls_legend_file[0])
        os.unlink(legend_file_path)

    # Get the image file names.
    img_files = glob('*.png')

    # Extract the order the compounds were run.
    df_analysis['Cmpd_Run_Order'] = df_analysis['Analyte 1 Solution'].str.split('_', expand=True)[1]
    df_analysis['Cmpd_Run_Order'] = df_analysis['Cmpd_Run_Order'].astype(int)
    df_analysis = df_analysis.sort_values(['Cmpd_Run_Order'])
    df_analysis = df_analysis.reset_index(drop=True)

    # Create a DataFrame with the file names.
    df_img_files = pd.DataFrame(img_files)
    df_img_files.columns = ['Original_Name']

    # Extract the compound run number and sort.
    df_img_files['File_name_chunk'] = df_img_files['Original_Name'].str.split('_', expand=True)[1]
    df_img_files['Cmpd_Run_Order'] = df_img_files['File_name_chunk'].str.split(';', expand=True)[0]
    df_img_files['Cmpd_Run_Order'] = df_img_files['Cmpd_Run_Order'].astype(int)
    df_img_files = df_img_files.sort_values(['Cmpd_Run_Order'])
    df_img_files = df_img_files.reset_index(drop=True)

    # Create a column of what we would like the name of the files to be changed to.
    # Usual format is BRD-6994_190916_7279_affinity_12.png
    # Add some randomness to the file path so that if the same cmpd on the same day was run, in a second run,
    # it would still be unique
    rand_int = np.random.randint(low=10, high=99)
    df_img_files['New_Name'] = df_analysis['Analyte 1 Solution'] + '_' + raw_data_file_name + '_' + str(rand_int) + '_' \
                               + df_img_files['Cmpd_Run_Order'].astype(str) + '.png'

    # Rename the files
    for idx, row in df_img_files.iterrows():
        ori_name = row['Original_Name']
        new_name = row['New_Name']
        os.rename(ori_name, new_name)

    # Add the image file names to the df_ss_seno DataFrame
    if image_type == 'ss':
        df_analysis['Steady_State_Img'] = df_img_files['New_Name']
    elif image_type == 'senso':
        df_analysis['Senso_Img'] = df_img_files['New_Name']

    # change the directory back to the working dir.
    os.chdir(my_dir)

    logging.info('%s Images were renamed successfully...', image_type)
    return df_analysis


def spr_create_dot_upload_file(config_file, save_file, clip, structures=False):
    """
    Function the aggregates all data from and SPR binding experiment run with compounds at dose into one Excel File.

    :arg config_file: Text file containing all of the metadata for an SPR experiment run at dose.
    :arg save_file: Name of the final Excel file.
    :arg clip: Optional flag that indicates if the setup table exists on the clipboard.
    :param structures: Optional flag that indicates if the program should attempt to insert chemical structures.
    :return None

    """
    import configparser

    # ADLP save file path
    # Note the version is saved to the file name so that data can be linked to the script version.
    save_file = save_file.replace('.xlsx', '')
    adlp_save_file_path = os.path.join(homedir, 'Desktop', save_file + '_APPVersion_' + str(__version__))
    adlp_save_file_path = adlp_save_file_path.replace('.', '_')
    adlp_save_file_path = adlp_save_file_path + '.xlsx'

    try:

        config = configparser.ConfigParser()
        config.read(config_file)

        # Get all of the file paths from the configuration file and store in variables so they are available
        if clip:
            df_cmpd_set = pd.read_clipboard()
        else:
            path_master_tbl = config.get('paths', 'path_mstr_tbl')
            df_cmpd_set = pd.read_csv(path_master_tbl)

        logging.info('Collecting metadata from configuration file...')
        path_ss_img = config.get('paths', 'path_ss_img')
        path_senso_img = config.get('paths', 'path_senso_img')
        path_ss_txt = config.get('paths', 'path_ss_txt')
        path_senso_txt = config.get('paths', 'path_senso_txt')
        path_report_pt = config.get('paths', 'path_report_pt')

        # Get the flow channels immobilized
        immobilized_fc = str(config.get('meta', 'immobilized_fc'))
        immobilized_fc = immobilized_fc.strip(" ")
        immobilized_fc = immobilized_fc.replace(' ', '')
        immobilized_fc_arr = immobilized_fc.split(',')
        immobilized_fc_arr = [int(i) for i in immobilized_fc_arr]

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

        # Get all of the immobilized protein info.
        # BIP
        fc1_protein_BIP = config.get('meta', 'fc1_protein_BIP')
        fc2_protein_BIP = config.get('meta', 'fc2_protein_BIP')
        fc3_protein_BIP = config.get('meta', 'fc3_protein_BIP')
        fc4_protein_BIP = config.get('meta', 'fc4_protein_BIP')
        fc5_protein_BIP = config.get('meta', 'fc5_protein_BIP')
        fc6_protein_BIP = config.get('meta', 'fc6_protein_BIP')
        fc7_protein_BIP = config.get('meta', 'fc7_protein_BIP')
        fc8_protein_BIP = config.get('meta', 'fc8_protein_BIP')

        # RU
        fc1_protein_RU = float(config.get('meta', 'fc1_protein_RU'))
        fc2_protein_RU = float(config.get('meta', 'fc2_protein_RU'))
        fc3_protein_RU = float(config.get('meta', 'fc3_protein_RU'))
        fc4_protein_RU = float(config.get('meta', 'fc4_protein_RU'))
        fc5_protein_RU = float(config.get('meta', 'fc5_protein_RU'))
        fc6_protein_RU = float(config.get('meta', 'fc6_protein_RU'))
        fc7_protein_RU = float(config.get('meta', 'fc7_protein_RU'))
        fc8_protein_RU = float(config.get('meta', 'fc8_protein_RU'))

        # MW
        fc1_protein_MW = float(config.get('meta', 'fc1_protein_MW'))
        fc2_protein_MW = float(config.get('meta', 'fc2_protein_MW'))
        fc3_protein_MW = float(config.get('meta', 'fc3_protein_MW'))
        fc4_protein_MW = float(config.get('meta', 'fc4_protein_MW'))
        fc5_protein_MW = float(config.get('meta', 'fc5_protein_MW'))
        fc6_protein_MW = float(config.get('meta', 'fc6_protein_MW'))
        fc7_protein_MW = float(config.get('meta', 'fc7_protein_MW'))
        fc8_protein_MW = float(config.get('meta', 'fc8_protein_MW'))

    except Exception:
        raise RuntimeError('Something is wrong with the config file. Please check.')

    # Read in the text files that have the calculated values for steady-state and kinetic analysis.
    logging.info('Reading in Steady State and Kinetic Data from Excel files on Iron...')
    try:
        def _find_cell(sh, searched_value):
            """Private function used to find the row and column of a particular value in an Excel worksheet"""
            for row in range(sh.nrows):
                for col in range(sh.ncols):
                    my_cell = sh.cell(row, col)
                    if my_cell.value == searched_value:
                        return row, col
            return -1

        # Open the ss and kinetic workbooks
        wb_ss = xlrd.open_workbook(path_ss_txt)
        sheet_ss = wb_ss.sheet_by_index(0)

        wb_senso = xlrd.open_workbook(path_senso_txt)
        sheet_senso = wb_senso.sheet_by_index(0)

        # Find the Row and Col of "Group"
        val = 'Group'

        r_ss, c_ss = _find_cell(sh=sheet_ss, searched_value=val)
        r_senso, c_senso = _find_cell(sh=sheet_senso, searched_value=val)

        df_ss_txt = pd.read_excel(path_ss_txt, skiprows=r_ss)
        df_senso_txt = pd.read_excel(path_senso_txt, skiprows=r_senso)

    except Exception:
        raise RuntimeError('Issue reading in data from either steady state or kinetic Excels files.')

    """
    Biacore 8k names the images in a different way compared to S200 and T200. Therefore, we need to rename the images
    to be consistent for Dotmatics. Unfortunately, if a crash occures during runtime then the all images are 
    renamed and the script will fail during the next attempt. Therefore, image renaming must be atomic. 
    """

    # Save images in a temporary directory in case of a crash.
    # Note that a significant amount of code is nested in this context mangager so that if a crash occurres the images
    # are returned to their original state.
    with tempfile.TemporaryDirectory() as tmp_img_dir:

        try:
            # Get the original names of the ss and senso image directories
            if platform.system() == "Windows":
                ss_img_dir_name = path_ss_img.split('\\')[-1]
                senso_img_dir_name = path_senso_img.split('\\')[-1]
            else:
                ss_img_dir_name = path_ss_img.split('/')[-1]
                senso_img_dir_name = path_senso_img.split('/')[-1]

            dir_temp_ss_img = os.path.join(tmp_img_dir, ss_img_dir_name)
            dir_temp_senso_img = os.path.join(tmp_img_dir, senso_img_dir_name)

            # Copy directories from original to temp
            shutil.copytree(path_ss_img, dir_temp_ss_img)
            shutil.copytree(path_senso_img, dir_temp_senso_img)

            # Rename the images in the original and store the new paths to the returned df_ss_txt and df_senso_txt DF's
            df_ss_txt = rename_images(df_analysis=df_ss_txt, path_img=path_ss_img, image_type='ss',
                                            raw_data_file_name=raw_data_filename)
            df_senso_txt = rename_images(df_analysis=df_senso_txt, path_img=path_senso_img,
                                            image_type='senso', raw_data_file_name=raw_data_filename)

            try:

                logging.info('Creating the main file for ADLP...')
                # Start building the final Dotmatics DataFrame
                df_final_for_dot = pd.DataFrame()

                # Start by adding the Broad ID in the correct order.
                # NB: For the 8k each compound has it's own channel so no need to replicate the BRD as is required on
                # T200 and S200
                df_final_for_dot.loc[:, 'BROAD_ID'] = df_cmpd_set['Broad ID']

                # Add structure column
                df_final_for_dot.loc[:, 'STRUCTURES'] = ''

                # Add the Project Code.  Get this from the config file.
                df_final_for_dot.loc[:, 'PROJECT_CODE'] = project_code

                #  Add an empty column called curve_valid
                df_final_for_dot.loc[:, 'CURVE_VALID'] = ''

                # Add an empty column called steady_state_img
                df_final_for_dot.loc[:, 'STEADY_STATE_IMG'] = ''

                # Add an empty column called 1to1_img
                df_final_for_dot.loc[:, '1to1_IMG'] = ''

                # Add the starting compounf_ss concentrations
                df_final_for_dot['TOP_COMPOUND_UM'] = df_cmpd_set['Test [Cpd] uM']

                # Extract the RU Max for each compound using the report point file.
                df_final_for_dot['RU_TOP_CMPD'] = SPR_to_ADLP_Functions.common_functions.spr_binding_top_for_dot_file(
                    report_pt_file=path_report_pt, df_cmpd_set=df_cmpd_set, instrument=instrument,
                    fc_used=immobilized_fc_arr)

                # Extract the steady state data and add to DataFrame
                df_ss_txt['KD_SS_UM'] = df_ss_txt['KD (M)'] * 1000000

                # Add the KD steady state
                df_final_for_dot['KD_SS_UM'] = df_ss_txt['KD_SS_UM']

                # Add the chi2_steady_state_affinity
                df_final_for_dot['CHI2_SS_AFFINITY'] = df_ss_txt['Affinity Chi² (RU²)']

                # Add the Fitted_Rmax_steady_state_affinity
                df_final_for_dot['FITTED_RMAX_SS_AFFINITY'] = df_ss_txt['Rmax (RU)']

                # Extract the sensorgram data and add to DataFrame
                # Add columns from df_senso_txt
                df_final_for_dot['KA_1_1_BINDING'] = df_senso_txt['ka']
                df_final_for_dot['KD_LITTLE_1_1_BINDING'] = df_senso_txt['kd']
                df_final_for_dot['KD_1_1_BINDING_UM'] = df_senso_txt['KD (M)'] * 1000000
                df_final_for_dot['chi2_1_1_binding'] = df_senso_txt['Kinetics Chi² (RU²)']

                # Not sure what this is???
                df_final_for_dot.loc[:, 'U_VALUE_1_1_BINDING'] = ''

                # Continue creating new columns
                df_final_for_dot['FITTED_RMAX_1_1_BINDING'] = df_senso_txt['Rmax']
                df_final_for_dot.loc[:, 'COMMENTS'] = ''

                # Add the flow channel column
                df_final_for_dot.loc[:, 'FC'] = '2-1'

                # Add protein RU
                protein_ru_dict = {1: fc1_protein_RU, 2: fc2_protein_RU, 3: fc3_protein_RU,
                                   4: fc4_protein_RU, 5: fc5_protein_RU, 6: fc6_protein_RU, 7: fc7_protein_RU,
                                   8: fc8_protein_RU}
                df_final_for_dot['PROTEIN_RU'] = df_senso_txt['Channel'].map(protein_ru_dict)

                # Add protein MW
                protein_mw_dict = {1: fc1_protein_MW, 2: fc2_protein_MW, 3: fc3_protein_MW,
                                   4: fc4_protein_MW, 5: fc5_protein_MW, 6: fc6_protein_MW, 7: fc7_protein_MW,
                                   8: fc8_protein_MW}
                df_final_for_dot['PROTEIN_MW'] = df_senso_txt['Channel'].map(protein_mw_dict)

                # Add protein BIP
                protein_bip_dict = {1: fc1_protein_BIP, 2: fc2_protein_BIP, 3: fc3_protein_BIP,
                                    4: fc4_protein_BIP, 5: fc5_protein_BIP, 6: fc6_protein_BIP, 7: fc7_protein_BIP,
                                    8: fc8_protein_BIP}
                df_final_for_dot['PROTEIN_ID'] = df_senso_txt['Channel'].map(protein_bip_dict)

                # Add the MW for each compound.
                df_final_for_dot['MW'] = df_cmpd_set['MW']

                # Continue adding columns to final DataFrame
                df_final_for_dot.loc[:, 'INSTRUMENT'] = instrument
                df_final_for_dot['ASSAY_MODE'] = 'Multi-Cycle'
                df_final_for_dot.loc[:, 'EXP_DATE'] = experiment_date
                df_final_for_dot.loc[:, 'NUCLEOTIDE'] = nucleotide
                df_final_for_dot.loc[:, 'CHIP_LOT'] = chip_lot
                df_final_for_dot.loc[:, 'OPERATOR'] = operator
                df_final_for_dot.loc[:, 'PROTOCOL_ID'] = protocol
                df_final_for_dot.loc[:, 'RAW_DATA_FILE'] = raw_data_filename
                df_final_for_dot.loc[:, 'DIR_FOLDER'] = directory_folder

                # Add the unique ID #
                df_final_for_dot['UNIQUE_ID'] = df_senso_txt['Analyte 1 Solution'] + '_' + df_final_for_dot[
                    'FC'] + '_' + project_code + \
                                                '_' + experiment_date + \
                                                '_' + df_senso_txt['Analyte 1 Solution'].str.split('_', expand=True)[1]

                # Add steady state image file path
                # Need to replace /Volumes with //Iron
                path_ss_img_edit = path_ss_img.replace('/Volumes', '//Iron')
                df_final_for_dot['SS_IMG_ID'] = path_ss_img_edit + '/' + df_ss_txt['Steady_State_Img']

                # Add sensorgram image file path
                # Need to replace /Volumes with //Iron
                path_senso_img_edit = path_senso_img.replace('/Volumes', '//Iron')
                df_final_for_dot['SENSO_IMG_ID'] = path_senso_img_edit + '/' + df_senso_txt['Senso_Img']

                # Add the Rmax_theoretical.
                # Note couldn't do this before as I needed to add protein MW and RU first.
                df_final_for_dot['RMAX_THEORETICAL'] = round((df_final_for_dot['MW'] / df_final_for_dot['PROTEIN_MW']) \
                                                             * df_final_for_dot['PROTEIN_RU'], 2)

                # Calculate Percent Binding
                df_final_for_dot['PERCENT_BINDING_TOP'] = round((df_final_for_dot['RU_TOP_CMPD'] / df_final_for_dot[
                    'RMAX_THEORETICAL']) * 100, 2)

                # Rearrange the columns for the final DataFrame (without images)
                df_final_for_dot = df_final_for_dot.loc[:, ['BROAD_ID', 'STRUCTURES', 'PROJECT_CODE', 'CURVE_VALID',
                                                            'STEADY_STATE_IMG', '1to1_IMG', 'TOP_COMPOUND_UM',
                                                            'RMAX_THEORETICAL', 'RU_TOP_CMPD', 'PERCENT_BINDING_TOP',
                                                            'KD_SS_UM', 'CHI2_SS_AFFINITY', 'FITTED_RMAX_SS_AFFINITY',
                                                            'KA_1_1_BINDING', 'KD_LITTLE_1_1_BINDING',
                                                            'KD_1_1_BINDING_UM', 'chi2_1_1_binding',
                                                            'U_VALUE_1_1_BINDING', 'FITTED_RMAX_1_1_BINDING',
                                                            'COMMENTS', 'FC', 'PROTEIN_RU', 'PROTEIN_MW',
                                                            'PROTEIN_ID', 'MW', 'INSTRUMENT', 'ASSAY_MODE',
                                                            'EXP_DATE', 'NUCLEOTIDE', 'CHIP_LOT', 'OPERATOR',
                                                            'PROTOCOL_ID', 'RAW_DATA_FILE', 'DIR_FOLDER', 'UNIQUE_ID',
                                                            'SS_IMG_ID', 'SENSO_IMG_ID']]

            except Exception:
                raise RuntimeError('Issue creating main DataFrame for Excel output file.')

            # Write the DataFrame to an Excel workbook
            try:
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
                num_data_pts = num_cpds + 1

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
                worksheet1.set_column('A:AJ', 28, cell_format)

                # Start preparing to insert the steady state and sensorgram images.
                # Get list of image files from df_ss_txt Dataframe.
                list_ss_img = df_ss_txt['Steady_State_Img'].tolist()

                # Get list of images files in the df_senso_txt DataFrame.
                list_sonso_img = df_senso_txt['Senso_Img'].tolist()

                # Create a list of tuples containing the names of the steady state image and sensorgram image.
                tuple_list_imgs = list(zip(list_ss_img, list_sonso_img))

                # Insert images into file.
                SPR_to_ADLP_Functions.common_functions.spr_insert_ss_senso_images(tuple_list_imgs, worksheet1, path_ss_img,
                                                                                  path_senso_img, biacore=instrument)
            except Exception:
                raise RuntimeError('Issue writing DataFrame to Excel file.')

        # If a crash occurs return all images files back to their original names.
        except Exception:
            # Remove the original directories
            shutil.rmtree(path_ss_img)
            shutil.rmtree(path_senso_img)

            # Copy back the image backup directories
            # Copy back the image backup directories
            shutil.copytree(dir_temp_ss_img, os.path.join(homedir, 'desktop', NOW + '_SPR_SAVED_IMGS', ss_img_dir_name))
            shutil.copytree(dir_temp_senso_img, os.path.join(homedir, 'desktop', NOW + '_SPR_SAVED_IMGS', \
                                                                                   senso_img_dir_name))

            logging.info(f"A crash occurred.  A folder named {NOW + '_SPR_SAVED_IMGS'} has be created on you desktop\n"
                         f"with the original images and their names.  To prevent an inconsistent state the image\n "
                         f"folders on Iron have been removed")
            raise RuntimeError('Dang it! A crash occurred!!')

    # Insert structure images
    SPR_to_ADLP_Functions.common_functions.manage_structure_insertion(df_cmpd_set=df_cmpd_set,
                                                                       num_fc_used=1, worksheet=worksheet1,
                                                                       structures=structures, writer=writer)
    print('\nProgram Done!')
    print("The ADLP result was saved to your desktop.")

    return df_final_for_dot
