import pandas as pd
import os
from glob import glob
import platform
import tempfile
import shutil
from datetime import datetime
import re
import xlrd
import numpy as np
import SPR_to_ADLP_Functions
from _version import __version__

# Get the users Home Directory
if platform.system() == "Windows":
    from pathlib import Path
    homedir = str(Path.home())
else:
    homedir = os.environ['HOME']

# Set the date to include in the file directory for images if a crash occurs
NOW = datetime.now()
NOW = NOW.strftime('%y%m%d')


def spr_displacement_top_conc(report_pt_file, df_cmpd_set):
    """This method calculates the binding in RU at the top concentration.

        :param report_pt_file: reference to the report point file exported from the Biacore Instrument.
        :param df_cmpd_set: DataFrame containing the compound set data. This is used to extract the binding
        RU at the top concentration of compound tested.
        :returns Series containing the RU at the top concentration tested for each compound in the order tested.
        """
    try:
        # Read in data
        df_rpt_pts_all = pd.read_excel(report_pt_file, sheet_name='Report point table', skiprows=2)
    except:
        raise FileNotFoundError('The files could not be imported please check.')

    # TODO: Check that the columns in the report point file match the expected values.
    # Trim the df to only the columns we need.
    df_rpt_pts_trim = df_rpt_pts_all[['Cycle', 'Channel', 'Flow cell', 'Sensorgram type', 'Name','Step purpose',
                                      'Relative response (RU)', 'A-B-A 1 Concentration (µM)' ,
                                      'A-B-A 1 Flanking solution']]

    # Remove not needed rows.
    df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Step purpose'] == 'Analysis']
    df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Sensorgram type'] == 'Corrected']
    df_rpt_pts_trim = df_rpt_pts_trim[(df_rpt_pts_trim['Name'] == 'A-B-A binding late_1')]

    # Create a new column of BRD 4 digit numbers to merge
    df_rpt_pts_trim['BRD_MERGE'] = df_rpt_pts_trim['A-B-A 1 Flanking solution'].str.split('_', expand=True)[0]
    df_cmpd_set['BRD_MERGE'] = 'BRD-' + df_cmpd_set['Broad ID'].str[9:13]

    # Convert compound set concentration column to float so DataFrames can be merged.
    df_cmpd_set['Test [Cpd] uM'] = df_cmpd_set['Test [Cpd] uM'].astype('float')

    # Merge the report point DataFrame and compound set DataFrame on Top concentration which results in a new Dataframe
    # with only the data for the top concentrations run.
    # To prevent a merge error it is necessary to round sample concentration in both merged data frames.
    df_rpt_pts_trim['A-B-A 1 Concentration (µM)'] = round(df_rpt_pts_trim['A-B-A 1 Concentration (µM)'], 2)
    df_cmpd_set['Test [Cpd] uM'] = round(df_cmpd_set['Test [Cpd] uM'], 2)

    # Conduct the merge.
    df_rpt_pts_trim = pd.merge(left=df_rpt_pts_trim, right=df_cmpd_set,
                               left_on=['BRD_MERGE', 'A-B-A 1 Concentration (µM)'],
                               right_on=['BRD_MERGE','Test [Cpd] uM'], how='inner')

    # If a compound was run more than once, such as a control, we need to drop the duplicate values.
    df_rpt_pts_trim = df_rpt_pts_trim.drop_duplicates(['A-B-A 1 Flanking solution', 'A-B-A 1 Concentration (µM)'])

    # Need to resort the Dataframe
    df_rpt_pts_trim = df_rpt_pts_trim.sort_values(['Channel'])
    df_rpt_pts_trim = df_rpt_pts_trim.reset_index(drop=True)

    series_percent_disp_top = round(df_rpt_pts_trim['Relative response (RU)'].apply(lambda x: x*-1), 2)

    return series_percent_disp_top


def calc_max_theory_disp(file_path, fc_used_arr):
    """
    This method takes a report point file from a Biacore 8k instrument and extracts the blank/ zero concentration
    values. These only contain competitor protein and not compound. These values represent the maximum amount that
    a compound could theoretically displace a binding partner from the immobilized protein. The values are returned
    in the order they were run on the instrument.

    :param file_path: path to report point file
    :param fc_used_arr: integer array of the flow channels used.
    :return: Series containing all of the max displacement values in order.
    """

    try:
        df_report_pt = pd.read_excel(file_path, sheet_name='Report point table', skiprows=2)

    except:
        raise FileNotFoundError('The files could not be imported please check.')

    # Filter out all columns not needed
    df_report_pt_trim = df_report_pt[
        ['Cycle', 'Channel', 'Flow cell', 'Sensorgram type', 'Name', 'Relative response (RU)', 'A-B-A 1 Concentration (µM)'
            , 'A-B-A 1 Flanking solution']]

    # For each FC immobilized create a new DataFrame and filter for that FC.
    # Create a list with all of the flow channel filtered DataFrames.
    ls_max_theory = []

    for fc in fc_used_arr:
        df_filter = df_report_pt_trim.copy()
        df_filter = df_filter[(df_filter['Channel'] == fc) & (df_filter['Sensorgram type'] == 'Corrected') &
                              (df_filter['Name'] == 'A-B-A binding late_1')]

        # Filter to only the blank injections.
        df_filter = df_filter[df_filter['A-B-A 1 Concentration (µM)'] == 0]

        blanks_list = df_filter['Relative response (RU)'].tolist()

        avg_blanks_per_fc = [sum(blanks_list[i: i + 2]) / 2 for i in range(0,len(blanks_list), 2)]

        ls_max_theory = ls_max_theory + avg_blanks_per_fc

    ls_max_theory_neg = [i * -1 for i in ls_max_theory]

    return pd.Series(ls_max_theory_neg)


def rename_images(df, path_img, image_type, raw_data_file_name):
    """
    Method that renames the images in a folder.  Also adds the names of the images to the passed in df.
    :param df: Dataframe containing the steady state or kinetic fit results.
    :param path_img: Path to the folder containing the images to rename
    :param image_type: The type of image eight 'ss' for steady state or 'senso' for kinetic fits.
    :param raw_data_file_name: Name of thee raw data file used when renaming the images.
    :return: The df passed in with the column with the image names added.
    """

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

    # Sort df_ss_senso
    df_ss_senso = df.sort_values(['Channel'])
    df_ss_senso = df_ss_senso.reset_index(drop=True)

    # Create a DataFrame with the file names.
    df_img_files = pd.DataFrame(img_files)
    df_img_files.columns = ['Original_Name']

    # Extract the channel number and sort.
    df_img_files['Channel'] = df_img_files['Original_Name'].str.split('-', expand=True)[0]
    df_img_files['Channel'] = df_img_files['Channel'].astype(int)

    # Sort on Channel
    df_img_files = df_img_files.sort_values(['Channel'])
    df_img_files = df_img_files.reset_index(drop=True)

    # Create a column of what we would like the name of the files to be changed to.
    # Usual format is BRD-6994_s_190916_7279_function_12
    # Add some randomness to the file path so that if the same cmpd on the same day was run, in a second run,
    # it would still be unique
    rand_int = np.random.randint(low=10, high=99)
    df_img_files['New_Name'] = df_ss_senso['A-B-A 1 Solution'] + '_' + raw_data_file_name + '_' + str(rand_int) + '_' \
                               + df_img_files['Channel'].astype(str) + '.png'

    # Rename the files
    for idx, row in df_img_files.iterrows():
        ori_name = row['Original_Name']
        new_name = row['New_Name']
        os.rename(ori_name, new_name)

    # Add the image file names to the df_ss_seno DataFrame
    if image_type == 'ss':
        df_ss_senso['Steady_State_Img'] = df_img_files['New_Name']
    elif image_type == 'senso':
        df_ss_senso['Senso_Img'] = df_img_files['New_Name']

    # change the directory back to the working dir.
    os.chdir(my_dir)
    return df_ss_senso


def spr_create_dot_upload_file(config_file, save_file, clip):
    """
    This program aggregates all of the data from and SPR Dose Functional assay into one Excel file for ADLP upload.

    :param config_file: Path of the configuration file containing the paths to the needed files and meta data for a particular experiment.
    :param save_file: Path of the saved ADLP Excel file. This is saved to the users desktop.
    :param clip: Option that indicates that the contents of the SPR setup table are on the clipboard.

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

        path_ss_img = config.get('paths', 'path_ss_img')
        path_senso_img = config.get('paths', 'path_senso_img')
        path_ss_txt = config.get('paths', 'path_ss_txt')
        path_senso_txt = config.get('paths', 'path_senso_txt')
        path_report_pt = config.get('paths', 'path_report_pt')

        # Get all of the metadata variables
        num_fc_used = config.get('meta','num_fc_used')

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
        fc2_protein_MW = float(config.get('meta','fc2_protein_MW'))
        fc3_protein_MW = float(config.get('meta','fc3_protein_MW'))
        fc4_protein_MW = float(config.get('meta','fc4_protein_MW'))
        fc5_protein_MW = float(config.get('meta', 'fc5_protein_MW'))
        fc6_protein_MW = float(config.get('meta', 'fc6_protein_MW'))
        fc7_protein_MW = float(config.get('meta', 'fc7_protein_MW'))
        fc8_protein_MW = float(config.get('meta', 'fc8_protein_MW'))

        # Get meta data for the protein floated
        protein_floated_BIP = config.get('meta', 'protein_floated_BIP')
        protein_floated_conc_uM = float(config.get('meta', 'protein_floated_conc_uM'))
        protein_floated_MW = float(config.get('meta', 'protein_floated_MW'))

    except Exception:
        raise RuntimeError('Something is wrong with the config file. Please check.')

    # Read in the text files that have the calculated values for steady-state and kinetic analysis.
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
    to be consistent for Dotmatics.
    """
    # Save images in a temporary directory in case of a crash.
    # Note that a significant amount of code is nested in this context mangager so that if a crash occurs the images
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

            # Create a temporary backup directory for both ss and senso images
            dir_temp_ss_img = os.path.join(tmp_img_dir, ss_img_dir_name)
            dir_temp_senso_img = os.path.join(tmp_img_dir, senso_img_dir_name)

            # Copy directories from original to temp
            shutil.copytree(path_ss_img, dir_temp_ss_img)
            shutil.copytree(path_senso_img, dir_temp_senso_img)

            # Rename the images in the original and store the new paths to the returned df_ss_txt and df_senso_txt DF's
            df_ss_txt = rename_images(df=df_ss_txt, path_img=path_ss_img, image_type='ss',
                                      raw_data_file_name=raw_data_filename)
            df_senso_txt = rename_images(df=df_senso_txt, path_img=path_senso_img,
                                         image_type='senso', raw_data_file_name=raw_data_filename)

            try:
                # Start building the final Dotmatics DataFrame
                df_final_for_dot = pd.DataFrame()

                # NB: For the 8k each row of a 96 well testing plate corresponds to compound which corresponds to 1 flow channel.
                df_final_for_dot['BROAD_ID'] = df_cmpd_set['Broad ID']

                # Add structure column
                df_final_for_dot.loc[:, 'STRUCTURES'] = ''

                # Add the Project Code.  Get this from the config file.
                df_final_for_dot['PROJECT_CODE'] = project_code

                #  Add an empty column called curve_valid
                df_final_for_dot.loc[:, 'CURVE_VALID'] = ''

                # Add an empty column called steady_state_img
                df_final_for_dot.loc[:, 'STEADY_STATE_IMG'] = ''

                # Add an empty column called 1to1_img
                df_final_for_dot.loc[:, '1to1_IMG'] = ''

                # Add the starting compound concentrations
                df_final_for_dot['TOP_COMPOUND_UM'] = df_cmpd_set['Test [Cpd] uM']

                # Calculate Max theoretical displacement
                # Average of the 2 blanks for each flow cell
                df_final_for_dot['MAX_THEORETICAL_DISP_RU'] = calc_max_theory_disp(path_report_pt, immobilized_fc_arr)

                # Get the percent displacement at the top conc for each flow channel using the report point file.
                percent_disp = pd.Series(spr_displacement_top_conc(report_pt_file=path_report_pt, df_cmpd_set=df_cmpd_set))

                # Extract the RU Max for each compound using the report point file.
                df_final_for_dot['RU_TOP_CMPD'] = df_final_for_dot['MAX_THEORETICAL_DISP_RU'] - percent_disp

                # Calculate percent displacement at top conc.
                df_final_for_dot['DISP_TOP_CMPD'] = round(((df_final_for_dot['RU_TOP_CMPD']/
                                                            df_final_for_dot['MAX_THEORETICAL_DISP_RU'])*100), 2)

                """
                Add info from ss and senso text files
                """

                # Add steady state analysis parameters to the final DataFrame.
                df_ss_txt['IC50_UM'] = df_ss_txt['KD (M)'] * 1000000

                # Add the KD steady state
                df_final_for_dot['IC50_UM'] = df_ss_txt['IC50_UM']

                # Add the kinetic results to the final df.
                df_final_for_dot['KA_1_1_BINDING'] = df_senso_txt['ka (1/Ms)']
                df_final_for_dot['KD_LITTLE_1_1_BINDING'] = df_senso_txt['kd (1/s)']
                df_final_for_dot['KD_1_1_BINDING_UM'] = df_senso_txt['KD (M)'] * 1000000

                # Continue creating new columns
                df_final_for_dot['COMMENTS'] = ''

                # Rename the flow channels and add the flow channel column
                df_final_for_dot.loc[:, 'FC'] = '2-1'

                # Add protein RU
                protein_ru_dict = {1: fc1_protein_RU, 2: fc2_protein_RU, 3: fc3_protein_RU,
                                   4: fc4_protein_RU, 5: fc5_protein_RU, 6: fc6_protein_RU, 7: fc7_protein_RU,
                                   8: fc8_protein_RU}
                df_final_for_dot['PROTEIN_RU'] = df_senso_txt['Channel'].map(protein_ru_dict)

                # Add protein MW
                protein_mw_dict = {1: fc1_protein_MW, 2: fc2_protein_MW, 3: fc3_protein_MW,
                                   4: fc4_protein_MW, 5: fc5_protein_MW, 6: fc6_protein_MW,
                                   7: fc7_protein_MW, 8: fc8_protein_MW}
                df_final_for_dot['PROTEIN_MW'] = df_senso_txt['Channel'].map(protein_mw_dict)

                # Add protein BIP
                protein_bip_dict = {1: fc1_protein_BIP, 2 : fc2_protein_BIP, 3: fc3_protein_BIP,
                                    4: fc4_protein_BIP, 5: fc5_protein_BIP, 6: fc6_protein_BIP,
                                    7: fc7_protein_BIP, 8: fc8_protein_BIP}
                df_final_for_dot['PROTEIN_ID'] = df_senso_txt['Channel'].map(protein_bip_dict)

                # Add columns for protein floated meta data.
                df_final_for_dot['PROTEIN_FLOATED_ID'] = protein_floated_BIP
                df_final_for_dot['PROTEIN_FLOATED_CONC_UM'] = protein_floated_conc_uM
                df_final_for_dot['PROTEIN_FLOATED_MW'] = protein_floated_MW

                # Add the MW for each compound. Uses the step table.
                df_final_for_dot['MW'] = df_cmpd_set['MW']

                # Continue adding columns to final DataFrame
                df_final_for_dot.loc[:, 'INSTRUMENT'] = instrument
                df_final_for_dot.loc[:, 'EXP_DATE'] = experiment_date
                df_final_for_dot.loc[:, 'NUCLEOTIDE'] = nucleotide
                df_final_for_dot.loc[:, 'CHIP_LOT'] = chip_lot
                df_final_for_dot.loc[:, 'OPERATOR'] = operator
                df_final_for_dot.loc[:, 'PROTOCOL_ID'] = protocol
                df_final_for_dot.loc[:, 'RAW_DATA_FILE'] = raw_data_filename
                df_final_for_dot.loc[:, 'DIR_FOLDER'] = directory_folder

                # Add the unique ID #
                rand_int = np.random.randint(low=10, high=99)
                df_final_for_dot['UNIQUE_ID'] = df_ss_txt['A-B-A 1 Solution'] + '_' + df_final_for_dot['FC'] + '_' \
                                                + project_code + '_' + experiment_date + '_' + str(rand_int) + '_' + \
                                                df_ss_txt['Steady_State_Img'].str.split('_').str[-1]

                # Add steady state image file path
                # Need to replace /Volumes with //flynn
                path_ss_img_edit = path_ss_img.replace('/Volumes', '//Iron')
                df_final_for_dot['SS_IMG_ID'] = path_ss_img_edit + '/' + df_ss_txt['Steady_State_Img']

                # Add sensorgram image file path
                # Need to replace /Volumes with //Iron
                path_senso_img_edit = path_senso_img.replace('/Volumes', '//Iron')
                df_final_for_dot['SENSO_IMG_ID'] = path_senso_img_edit + '/' + df_senso_txt['Senso_Img']

                # Rearrange the columns for the final DataFrame (without images)
                df_final_for_dot = df_final_for_dot.loc[:, ['BROAD_ID', 'STRUCTURES', 'PROJECT_CODE', 'CURVE_VALID',
                                                            'STEADY_STATE_IMG', '1to1_IMG', 'TOP_COMPOUND_UM',
                                                            'MAX_THEORETICAL_DISP_RU', 'RU_TOP_CMPD', 'DISP_TOP_CMPD',
                                                            'IC50_UM', 'KA_1_1_BINDING', 'KD_LITTLE_1_1_BINDING',
                                                            'KD_1_1_BINDING_UM', 'COMMENTS', 'FC', 'PROTEIN_RU',
                                                            'PROTEIN_MW', 'PROTEIN_ID','PROTEIN_FLOATED_ID',
                                                            'PROTEIN_FLOATED_CONC_UM', 'PROTEIN_FLOATED_MW',
                                                            'MW', 'INSTRUMENT', 'EXP_DATE', 'NUCLEOTIDE', 'CHIP_LOT',
                                                            'OPERATOR', 'PROTOCOL_ID', 'RAW_DATA_FILE', 'DIR_FOLDER',
                                                            'UNIQUE_ID', 'SS_IMG_ID', 'SENSO_IMG_ID']]

            except Exception:
                raise RuntimeError('Issue creating main DataFrame for Excel output file.')

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
                comments_list = pd.DataFrame({'Comments':
                                                ['No displacement.',
                                                 'Normal curve.',
                                                 'Greater than 50% displacement. Partial Saturation.',
                                                 'Greater than 50% displacement. Curve does not saturate.',
                                                 'Normal curve. Below 50% Displacement.',
                                                 'Below 50% Displacement.',
                                                 'Positive displacement',
                                                 'Issues with compound.',
                                                 'Poor fit. IC50 not reported.',
                                                 'Issues at top concentration',
                                                 'Mark for retest.'
                                               ]})

                # Convert comments list to DataFrame
                comments_list.to_excel(writer, sheet_name='Sheet2', startcol=0, index=0)

                # For larger drop down lists > 255 characters its necessary to create a list on a seperate worksheet.
                worksheet1.data_validation('O1:N' + str(num_data_pts),
                                                    {'validate': 'list',
                                                     'source': '=Sheet2!$A$2:$A$' + str(len(comments_list) + 1)
                                                     })

                # Freeze the top row of the excel worksheet.
                worksheet1.freeze_panes(1, 0)

                # Add a cell format object to align text center.
                cell_format = workbook.add_format()
                cell_format.set_align('center')
                cell_format.set_align('vcenter')
                worksheet1.set_column('A:AI', 28, cell_format)

                # Start preparing to insert the steady state and sensorgram images.
                # Get list of image files from df_ss_txt Datafßrame.
                list_ss_img = df_ss_txt['Steady_State_Img'].tolist()

                # Get list of images files in the df_senso_txt DataFrame.
                list_sonso_img = df_senso_txt['Senso_Img'].tolist()

                # Create a list of tuples containing the names of the steady state image and sensorgram image.
                tuple_list_imgs = list(zip(list_ss_img, list_sonso_img))

                # Insert images into file.
                SPR_to_ADLP_Functions.common_functions.spr_insert_ss_senso_images(tuple_list_imgs, worksheet1, path_ss_img,
                                                                                path_senso_img, biacore='Biacore8K')
            except Exception:
                raise RuntimeError('Issue writing DataFrame to Excel file.')

        # If a crash occurs return all images files back to their original names.
        except Exception:
            # Remove the original directories
            shutil.rmtree(path_ss_img)
            shutil.rmtree(path_senso_img)

            # Copy back the image backup directories
            shutil.copytree(dir_temp_ss_img, os.path.join(homedir, 'desktop', NOW + '_SPR_SAVED_IMGS', ss_img_dir_name))
            shutil.copytree(dir_temp_senso_img, os.path.join(homedir, 'desktop', NOW + '_SPR_SAVED_IMGS',
                                                             senso_img_dir_name))
            raise RuntimeError('Dang it! A crash occurred!!\n'
                               'IMPORTANT: The original image names have been saved to your desktop in folder ' +
                               NOW + '_SPR_SAVED_IMGS\n'
                               'Please copy back these original images to the Iron server.')

    # Insert structure images
    # Render the smiles into png images in a temp directory
    with tempfile.TemporaryDirectory() as tmp_img_dir:

        # This line gets all the smiles from the database
        df_struct_smiles = SPR_to_ADLP_Functions.common_functions.get_structures_smiles_from_db(
            df_mstr_tbl=df_cmpd_set)

        # Issue with connecting to resultsdb, then skip inserting structures.
        if df_struct_smiles is not None:

            # Render the structure images
            df_with_paths = SPR_to_ADLP_Functions.common_functions.render_structure_imgs(
                df_with_smiles=df_struct_smiles, dir=tmp_img_dir)

            # Create an list of the images paths in order
            ls_img_paths = SPR_to_ADLP_Functions.common_functions.rep_item_for_dot_df(df=df_with_paths,
                                                                                      col_name='IMG_PATH',
                                                                                      times_dup=1)

            # Insert the structures into the Excel workbook object
            SPR_to_ADLP_Functions.common_functions.spr_insert_structures(ls_img_struct_paths=ls_img_paths,
                                                                         worksheet=worksheet1)

            # Save the writer object inside the context manager.
            writer.save()

        else:
            # Save the writer object inside the context manager.
            writer.save()

    print('Program Done!')
    print("The ADLP result was saved to your desktop.")
