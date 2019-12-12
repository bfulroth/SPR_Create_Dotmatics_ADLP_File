import pandas as pd
import os
import click
import platform
import numpy as np
from glob import glob

# Get the users Home Directory
if platform.system() == "Windows":
    from pathlib import Path
    homedir = str(Path.home())
else:
    homedir = os.environ['HOME']


def dup_item_for_dot_df(df, col_name, times_dup=3, sort=False):
    """
    Takes a DataFrame and a column name with items to be replicated. Sorts the list and replicates the number of
    times specified by the parameter times_dup. Copies the replicated values to the clip board.

    :param df: A DataFrame containing the column of values to be replicated.
    :param col_name: Name of the column containing values to replicate.
    :param times_dup: Number of times to replicate each value in the specified column.
    :param sort: Boolean to sort the replicated values.
    :type sort: bool
    """
    dup_list = []

    try:
        for item in df[col_name]:
            for i in range(times_dup):
                dup_list.append(item)

        a = pd.Series(dup_list)

        if sort:
            b = a.sort_values()
            return b
        else:
            return a
    except:
        print("The DataFrame does not have a " + col_name + " column.")


def spr_insert_images(tuple_list_imgs, worksheet, path_ss_img, path_senso_img):
    """
    Does the work of inserting the spr steady state and sensorgram images into the excel worksheet.
    :param tuple_list: List of tuples containing (steady state image, sensorgram image)
    :param worksheet: xlsxwriter object used to insert the images to a worksheet
    :param path_ss_img: Directory to the steady state images to insert.
    :param path_senso_img: Directory to the sensorgram images to insert.
    :return: None
    """
    # Format the rows and columns in the worksheet to fit the images.
    num_images = len(tuple_list_imgs)

    # Set height of each row
    for row in range(1, num_images + 1):
        worksheet.set_row(row=row, height=145)

    # Set the width of each column
    worksheet.set_column(first_col=3, last_col=4, width=24)

    row = 2
    for ss_img, senso_img in tuple_list_imgs:
        worksheet.insert_image('D' + str(row), path_ss_img + '/' + ss_img)
        worksheet.insert_image('E' + str(row), path_senso_img + '/' + senso_img)
        row += 1


def spr_binding_top_for_dot_file(report_pt_file, df_cmpd_set, fc_used):
    #TODO: Currently assumes that all 8 channels were used.
    """This method calculates the binding in RU at the top concentration.

        :param report_pt_file: reference to the report point file exported from the Biacore Instrument.
        :param df_cmpd_set: DataFrame containing the compound set data. This is used to extract the binding
        RU at the top concentration of compound tested.
        :param fc_used: The flow channels that were immobilized in the experiment.
        :returns Series containing the RU at the top concentration tested for each compound in the order tested.
        """

    try:
        # Read in data
        df_rpt_pts_all = pd.read_excel(report_pt_file, sheet_name='Report point table', skiprows=2)
    except:
        raise FileNotFoundError('The files could not be imported please check.')

    # Check that the NEEDED columns are in the report point file.
    cols_needed = ['Cycle', 'Channel', 'Flow cell',	'Sensorgram type', 'Name', 'Relative response (RU)',
                   'Step name', 'Analyte 1 Solution', 'Analyte 1 Concentration (µM)']

    # Convert to list
    cols_in_file = df_rpt_pts_all.columns.tolist()

    # Make sure we have the needed columns
    for col in cols_needed:
        if col not in cols_in_file:
            raise ValueError('The columns in the report point file do not match the expected names.')

    # Remove other not needed columns
    df_rpt_pts_trim = df_rpt_pts_all.loc[:, ['Cycle', 'Channel', 'Flow cell', 'Sensorgram type', 'Name',
                                             'Relative response (RU)', 'Step name', 'Analyte 1 Solution',
                                             'Analyte 1 Concentration (µM)']]

    # Filter and removed not needed rows
    df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Sensorgram type'] == 'Corrected']
    df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Name'] == 'Analyte binding late_1']
    df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Step name'] == 'Analysis']

    # Create a new column of BRD 4 digit numbers to merge
    df_rpt_pts_trim['BRD_MERGE'] = df_rpt_pts_trim['Analyte 1 Solution'].str.split('_', expand=True)[0]
    df_cmpd_set['BRD_MERGE'] = 'BRD-' + df_cmpd_set['Broad ID'].str[9:13]

    # Convert compound set concentration column to float so DataFrames can be merged.
    df_cmpd_set['Test [Cpd] uM'] = df_cmpd_set['Test [Cpd] uM'].astype('float')

    # Merge the report point DataFrame and compound set DataFrame on Top concentration which results in a new Dataframe
    # with only the data for the top concentrations run.
    # To prevent a merge error it is necessary to round sample concentration in both merged data frames.
    df_rpt_pts_trim['Analyte 1 Concentration (µM)'] = round(df_rpt_pts_trim['Analyte 1 Concentration (µM)'], 2)
    df_cmpd_set['Test [Cpd] uM'] = round(df_cmpd_set['Test [Cpd] uM'], 2)

    # Conduct the merge.
    df_rpt_pts_trim = pd.merge(left=df_rpt_pts_trim, right=df_cmpd_set,
                               left_on=['BRD_MERGE', 'Analyte 1 Concentration (µM)'],
                               right_on=['BRD_MERGE','Test [Cpd] uM'], how='inner')

    # If a compound was run more than once, such as a control, we need to drop the duplicate values.
    df_rpt_pts_trim = df_rpt_pts_trim.drop_duplicates(['Analyte 1 Solution'])

    # Need to resort the Dataframe
    # Create sorting column
    df_rpt_pts_trim['sample_order'] = df_rpt_pts_trim['Analyte 1 Solution'].str.split('_', expand=True)[1]
    df_rpt_pts_trim = df_rpt_pts_trim.sort_values(['Cycle', 'sample_order'])
    df_rpt_pts_trim = df_rpt_pts_trim.reset_index(drop=True)

    return round(df_rpt_pts_trim['Relative response (RU)'], 2)


def rename_images(df_analysis, path_img, image_type, raw_data_file_name):
    """
    Method that renames the images in a folder.  Also adds the names of the images to the passed in df.
    :param df_analysis: Dataframe containing the steady state or kinetic fit results.
    :param path_img: Path to the folder containing the images to rename
    :param image_type: The type of image 'ss' for steady state or 'senso' for kinetic fits.
    :param raw_data_file_name: Name of the raw data file used when renaming the images.
    :return: The df_ss_senso df with the column with the image names added.
    """

    # Store the current working directory
    my_dir = os.getcwd()

    # Change the Directory to the ss image folder
    os.chdir(path_img)

    # Get the image file names.
    img_files = glob('*.png')

    # Delete legend from folder.
    #TODO: Need to figure out how to delete the legend from the list of image files.

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
    return df_analysis

#Using click to manage the command line interface
@click.command()
@click.option('--config_file', prompt="Please paste the path of the configuration file", type=click.Path(exists=True),
              help="Path of the configuration file. Text file with all of the file paths and meta "
                   "data for a particular experiment.")
@click.option('--save_file', prompt="Please type the name of the ADLP result file with an .xlsx extension"
                ,help="Name of the ADLP results file which is an Excel file.")
@click.option('--clip', is_flag=True,
              help="Option to indicate that the contents of the setup file are on the clipboard.")
def spr_create_dot_upload_file(config_file, save_file, clip):
    import configparser

    # ADLP save file path.
    if platform.system() == 'Windows':
        adlp_save_file_path = homedir + '\\Desktop\\' + save_file
    else:
        adlp_save_file_path = homedir + '/' + 'desktop' + '/' + save_file

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

    except:
        raise RuntimeError('Something is wrong with the config file. Please check.')


    # Read in the text files that have the calculated values for steady-state and kinetic analysis.
    df_ss_txt = pd.read_excel(path_ss_txt)
    df_senso_txt = pd.read_excel(path_senso_txt)

    """
    Biacore 8k names the images in different way compared to S200 and T200. Therefore, we need to rename the images
    to be consistent for Dotmatics.
    """
    df_ss_txt = rename_images(df_analysis=df_ss_txt, path_img=path_ss_img, image_type='ss',
                                        raw_data_file_name=raw_data_filename)
    df_senso_txt = rename_images(df_analysis=df_senso_txt, path_img=path_senso_img,
                                        image_type='senso', raw_data_file_name=raw_data_filename)


    # Start building the final Dotmatics DataFrame
    df_final_for_dot = pd.DataFrame()

    # Start by adding the Broad ID in the correct order.
    # NB: For the 8k each compound has it's own channel so no need to replicate the BRD as is required on T200 and S200
    df_final_for_dot['BROAD_ID'] = df_cmpd_set['Broad ID']

    # Add the Project Code.  Get this from the config file.
    df_final_for_dot['PROJECT_CODE'] = project_code

    #  Add an empty column called curve_valid
    df_final_for_dot['CURVE_VALID'] = ''

    # Add an empty column called steady_state_img
    df_final_for_dot['STEADY_STATE_IMG'] = ''

    # Add an empty column called 1to1_img
    df_final_for_dot['1to1_IMG'] = ''

    # Add the starting compound concentrations
    df_final_for_dot['TOP_COMPOUND_UM'] = df_cmpd_set['Test [Cpd] uM']

    # Extract the RU Max for each compound using the report point file.
    df_final_for_dot['RU_TOP_CMPD'] = spr_binding_top_for_dot_file(report_pt_file=path_report_pt,
                                                                   df_cmpd_set=df_cmpd_set,
                                                                   fc_used=immobilized_fc_arr)

    # Extract the steady state data and add to DataFrame
    # Create new columns to sort the DataFrame as the original is out of order.
    df_ss_txt['sample_order'] = df_ss_txt['Steady_State_Img'].str.split('_', expand=True)[1]
    df_ss_txt['sample_order'] = df_ss_txt['sample_order'].str.replace('.png','')
    df_ss_txt['sample_order'] = pd.to_numeric(df_ss_txt['sample_order'])
    df_ss_txt = df_ss_txt.sort_values(by=['sample_order'])
    df_ss_txt = df_ss_txt.reset_index(drop=True)
    df_ss_txt['KD_SS_UM'] = df_ss_txt['KD'] * 1000000

    # Add the KD steady state
    df_final_for_dot['KD_SS_UM'] = df_ss_txt['KD_SS_UM']

    # Add the chi2_steady_state_affinity
    # TODO: Not sure if the squared value is usually in the file. Looks different in my downloaded file.
    df_final_for_dot['CHI2_SS_AFFINITY'] = df_ss_txt['Affinity Chi≤ (RU≤)']

    # Add the Fitted_Rmax_steady_state_affinity
    df_final_for_dot['FITTED_RMAX_SS_AFFINITY'] = df_ss_txt['Rmax']

    # Extract the sensorgram data and add to DataFrame
    df_senso_txt['sample_order'] = df_senso_txt['Senso_Img'].str.split('_', expand=True)[1]
    df_senso_txt['sample_order'] = df_senso_txt['sample_order'].str.replace('.png', '')
    df_senso_txt['sample_order'] = pd.to_numeric(df_senso_txt['sample_order'])
    df_senso_txt = df_senso_txt.sort_values(by=['sample_order'])
    df_senso_txt = df_senso_txt.reset_index(drop=True)

    # Add columns from df_senso_txt
    df_final_for_dot['KA_1_1_BINDING'] = df_senso_txt['ka']
    df_final_for_dot['KD_LITTLE_1_1_BINDING'] = df_senso_txt['kd']
    df_final_for_dot['KD_1_1_BINDING_UM'] = df_senso_txt['KD (M)'] * 1000000
    df_final_for_dot['chi2_1_1_binding'] = df_senso_txt['Kinetics Chi≤ (RU≤)']

    # Not sure what this is???
    df_final_for_dot['U_VALUE_1_1_BINDING'] = ''
    # Not sure what this is??

    # Continue creating new columns
    df_final_for_dot['FITTED_RMAX_1_1_BINDING'] = df_senso_txt['Rmax']
    df_final_for_dot.loc[:, 'COMMENTS'] = ''

    # Add the flow channel column
    df_final_for_dot.loc[:, 'FC'] = '2-1'

    # Add protein RU
    protein_ru_dict = {1: fc1_protein_RU, 2: fc2_protein_RU, 3: fc3_protein_RU,
                       4: fc4_protein_RU, 5: fc5_protein_RU, 6: fc6_protein_RU, 7: fc7_protein_RU, 8: fc8_protein_RU}
    df_final_for_dot['PROTEIN_RU'] = df_senso_txt['Channel'].map(protein_ru_dict)

    # Add protein MW
    protein_mw_dict = {1: fc1_protein_MW, 2: fc2_protein_MW, 3: fc3_protein_MW,
                       4: fc4_protein_MW, 5: fc5_protein_MW, 6: fc6_protein_MW, 7: fc7_protein_MW, 8: fc8_protein_MW}
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
    df_final_for_dot['UNIQUE_ID'] = df_senso_txt['Analyte 1 Solution'] + '_' + df_final_for_dot['FC'] + '_' + project_code + \
                                    '_' + experiment_date + \
                                    '_' + df_senso_txt['Analyte 1 Solution'].str.split('_', expand=True)[1]

    # Add steady state image file path
    # Need to replace /Volumes with //flynn
    path_ss_img_edit = path_ss_img.replace('/Volumes', '//flynn')
    df_final_for_dot['SS_IMG_ID'] = path_ss_img_edit + '/' + df_ss_txt['Steady_State_Img']

    # Add sensorgram image file path
    # Need to replace /Volumes with //flynn
    path_senso_img_edit = path_senso_img.replace('/Volumes', '//flynn')
    df_final_for_dot['SENSO_IMG_ID'] = path_senso_img_edit + '/' + df_senso_txt['Senso_Img']

    # Add the Rmax_theoretical.
    # Note couldn't do this before as I needed to add protein MW and RU first.
    df_final_for_dot['RMAX_THEORETICAL'] = round((df_final_for_dot['MW'] / df_final_for_dot['PROTEIN_MW']) \
                                           * df_final_for_dot['PROTEIN_RU'], 2)

    # Calculate Percent Binding
    df_final_for_dot['%_BINDING_TOP'] = round((df_final_for_dot['RU_TOP_CMPD'] / df_final_for_dot[
        'RMAX_THEORETICAL']) * 100, 2)

    # Rearrange the columns for the final DataFrame (without images)
    df_final_for_dot = df_final_for_dot.loc[:, ['BROAD_ID', 'PROJECT_CODE', 'CURVE_VALID', 'STEADY_STATE_IMG',
       '1to1_IMG', 'TOP_COMPOUND_UM', 'RMAX_THEORETICAL', 'RU_TOP_CMPD', '%_BINDING_TOP', 'KD_SS_UM',
       'CHI2_SS_AFFINITY', 'FITTED_RMAX_SS_AFFINITY', 'KA_1_1_BINDING',
       'KD_LITTLE_1_1_BINDING', 'KD_1_1_BINDING_UM', 'chi2_1_1_binding',
       'U_VALUE_1_1_BINDING', 'FITTED_RMAX_1_1_BINDING', 'COMMENTS', 'FC',
       'PROTEIN_RU', 'PROTEIN_MW', 'PROTEIN_ID', 'MW', 'INSTRUMENT', 'ASSAY_MODE',
       'EXP_DATE', 'NUCLEOTIDE', 'CHIP_LOT', 'OPERATOR', 'PROTOCOL_ID',
       'RAW_DATA_FILE', 'DIR_FOLDER', 'UNIQUE_ID', 'SS_IMG_ID', 'SENSO_IMG_ID']]

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
                                    ['No binding.',
                                    'Saturation reached. Fast on/off.',
                                    'Saturation reached. Fast on/off. Insolubility likely. Removed top.',
                                    'Saturation reached. Fast on/off. Insolubility likely.',
                                    'Saturation reached. Fast on/off. Low % binding.',
                                    'Saturation reached. Fast on/off. Low % binding. Insolubility likely.',
                                    'Saturation reached. Slow on. Fast off.',
                                    'Saturation reached. Slow on. Fast off. Insolubility likely.',
                                    'Saturation reached. Slow on. Slow off.',
                                    'Saturation reached. Slow on. Slow off. Insolubility likely.',
                                    'Saturation reached. Fast on. Slow off.',
                                    'Saturation reached. Fast on. Slow off. Insolubility likely.',
                                    'Saturation approached. Fast on/off.',
                                    'Saturation approached. Insolubility likely.',
                                    'Saturation approached. Fast on/off. Insolubility likely.',
                                    'Saturation approached. Low % binding.',
                                    'Saturation approached. Low % binding. Insolubility likely.',
                                    'Saturation not reached.',
                                    'Saturation not reached. Insolubility likely.',
                                    'Saturation not reached. Fast on/off.',
                                    'Saturation not reached. Fast on/off. Insolubility likely.',
                                    'Saturation not reached. Low % binding.',
                                    'Saturation not reached. Low % binding. Insolubility likely.',
                                    'Superstoichiometric binding.']})

    # Convert comments list to DataFrame
    comments_list.to_excel(writer, sheet_name='Sheet2', startcol=0, index=0)

    # For larger drop down lists > 255 characters its necessary to create a list on a seperate worksheet.
    worksheet1.data_validation('S1:S' + str(num_data_pts),
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
    spr_insert_images(tuple_list_imgs, worksheet1, path_ss_img, path_senso_img)

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    print('Program Done!')
    print("The ADLP result was saved to your desktop.")


if __name__ == '__main__':
    spr_create_dot_upload_file()
