"""Module that contains common functions for SPR to ADLP aggregation scripts"""
import os
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw, AllChem
import cx_Oracle
#from sqlalchemy import create_engine, Table, MetaData, select
import sqlalchemy
import crypt


def rep_item_for_dot_df(df, col_name, times_dup=3, sort=False):
    """
    Takes a DataFrame and a column name with items to be replicated. Sorts the list and replicates the number of
    times specified by the parameter times_dup. Copies the replicated values to the clip board.

    :param df: A DataFrame containing the column of values to be replicated.
    :param col_name: Name of the column containing values to replicate.
    :param times_dup: Number of times to replicate each value in the specified column.
    :param sort: Boolean to sort the replicated values.
    :type sort: bool
    :return Series of the duplicated item either sorted or not sorted.
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
        raise RuntimeError("The DataFrame does not have a " + col_name + " column.")


def _connect(engine):
    """
    Private method that actually makes the connection to resultsdb
    :param engine: Sqlalchemy engine object
    """
    c = engine.connect()
    return c


def get_structures_smiles_from_db(df_mstr_tbl):
    """
    This method creates a connection to results db and retrieves the smiles for each BRD in the passed in df_mstr_tbl

    :param: df_mstr_tbl: SPR Setup table as a DataFrame
    :return DataFrame containing BRD, CORE ID, and SMILES
    """

    # Extract the CORE Broad ID from the df_mstr_tbl
    df_brd_core_id = df_mstr_tbl[['Broad ID']].copy()
    df_brd_core_id.loc[:, 'BROAD_CORE_ID'] = df_brd_core_id['Broad ID'].apply(lambda x: x[5:13])

    # Create a cryptographic object
    c = crypt.Crypt()

    # Connect to resultsdb database.
    try:
        host = 'cbpdb01'
        port = '1521'
        sid = 'cbplate'
        user = os.getenv('DB_USER')
        password = str(c.f.decrypt(c.token), 'utf-8')
        sid = cx_Oracle.makedsn(host, port, sid=sid)

        cstr = 'oracle://{user}:{password}@{sid}'.format(
            user=user,
            password=password,
            sid=sid
        )

        engine = sqlalchemy.create_engine(cstr,
                               pool_recycle=3600,
                               pool_size=5,
                               echo=False
                               )

        # Connect to resultsdb by calling private connection method
        conn = _connect(engine=engine)

    except Exception:
        print("\nCannot connect to resultsdb database. Structures will not be rendered. "
              "\n\nProgram proceeding without inserting structures. Please wait...")
        return None

    # Reflect Tables
    metadata = sqlalchemy.MetaData()
    structure_tbl = sqlalchemy.Table('structure', metadata, autoload=True, autoload_with=engine)

    # Get the Broad Core ID/ and SMILES from resultsdb.
    stmt = sqlalchemy.select([structure_tbl.c.broadidcore, structure_tbl.c.smiles]). \
        where(structure_tbl.c.broadidcore.in_(list(df_brd_core_id['BROAD_CORE_ID'])))

    # Execute the statement
    results = conn.execute(stmt).fetchall()

    # Close the database connection
    conn.close()

    # Turn the results into a DataFrame.
    df_struct_tbl = pd.DataFrame(results)

    # RENAME the column headers.
    df_struct_tbl.columns = ['BROAD_CORE_ID', 'SMILES']

    # Merge df_struct_tbl with df_brd_core_id such that Full BRD, CORE ID, and SMILES are in the same table
    df_merge_full_brd_smiles = pd.merge(left=df_brd_core_id, right=df_struct_tbl, on='BROAD_CORE_ID', how='left')

    return df_merge_full_brd_smiles


def render_structure_imgs(df_with_smiles, dir):
    """
    Does the work of rendering images from smiles using RDkit into a directory

    :param df_with_smiles: DataFrame contain the smiles to render
    :param dir: directory to story the images.
    :return none
    """

    # Create an image Path Column
    df_with_smiles.loc[:, 'IMG_PATH'] = ''

    # Use BRD control as a template to align molecules.
    template = Chem.MolFromSmiles('Nc1c(F)cc(C#N)c2cc[nH]c12')
    AllChem.Compute2DCoords(template)

    img_num = 0

    # Create the images from smiles in a new directory
    # TODO: Attempt to align structure doesn't fully work
    for idx, row in df_with_smiles.iterrows():

        current_smile_str = row['SMILES']
        img_name = str(img_num) + '_' + row['Broad ID'] + '.png'
        img_full_path = os.path.join(dir, img_name)

        # Generate the structure of the current molecule using the control as a template to align
        m = Chem.MolFromSmiles(current_smile_str)
        #AllChem.GenerateDepictionMatching2DStructure(m, template)
        Draw.MolToFile(mol=m, filename=img_full_path, size=(200, 200))

        # Save the image path to the DataFrame
        df_with_smiles.loc[idx, 'IMG_PATH'] = img_full_path

        img_num += 1

    return df_with_smiles


def spr_insert_structures(ls_img_struct_paths, worksheet):
    """
    Does the work of inserting the structures into the xlsxwriter workbook object.

    :param ls_img_struct_paths: list of image paths to insert.
    :param worksheet: xlsxwriter object used to insert the images to a worksheet
    :return: None
    """
    # Format the rows and columns in the worksheet to fit the images.
    num_images = len(ls_img_struct_paths)

    # Set height of each row
    for row in range(1, num_images + 1):
        worksheet.set_row(row=row, height=210)

    # Set the width of each column
    worksheet.set_column(first_col=1, last_col=1, width=45)

    row = 2
    for img in ls_img_struct_paths:
        worksheet.insert_image('B' + str(row), img)
        row += 1


def spr_insert_ss_senso_images(tuple_list_imgs, worksheet, path_ss_img, path_senso_img, biacore):
    """
    Does the work of inserting the spr steady state and sensorgram images into the excel worksheet.
    :param tuple_list: List of tuples containing (steady state image, sensorgram image)
    :param worksheet: xlsxwriter object used to insert the images to a worksheet
    :param path_ss_img: Directory to the steady state images to insert.
    :param path_senso_img: Directory to the sensorgram images to insert.
    :param biacore: Instrument used in experiment.  Images are sized differently between 8k and all other instruments.
    :return: None
    """

    # Dictionary of Excel cell format parameters for each instrument as the images are slightly different.
    if biacore == 'Biacore8K':
        cell_format = {'cell_height': 145, 'first_col': 3, 'last_col': 4, 'width': 24}
    else:
        cell_format = {'cell_height': 235, 'first_col': 4, 'last_col': 5, 'width': 58}

    # Format the rows and columns in the worksheet to fit the images.
    num_images = len(tuple_list_imgs)

    # Set height of each row
    for row in range(1, num_images + 1):
        worksheet.set_row(row=row, height=cell_format['cell_height'])

    # Set the width of each column
    worksheet.set_column(first_col=cell_format['first_col'], last_col=cell_format['last_col'],
                         width=cell_format['width'])

    row = 2
    for ss_img, senso_img in tuple_list_imgs:
        worksheet.insert_image('E' + str(row), path_ss_img + '/' + ss_img)
        worksheet.insert_image('F' + str(row), path_senso_img + '/' + senso_img)
        row += 1


def get_predefined_comments():
    """
    Method for retrieving a common list of comments to include in the SPR_to_ADLP output file.

    :param
    """
    ls_comments = pd.DataFrame({'Comments':
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

    return ls_comments


def _percent_bind_helper_filter_non_corr_data_non_8k(df, ref_fc_used_arr, fc_used):

    # Filter out non-corrected data.
    df_rpt_pts_trim = df.copy()
    df_rpt_pts_trim['FC_Type'] = df_rpt_pts_trim['Fc'].str.split(' ', expand=True)[1]
    df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['FC_Type'] == 'corr']

    ## Remove not needed flow channels
    # If the reference channel is only 3 then assume that the only immobilized channel is 4
    if (len(ref_fc_used_arr) == 1) & (ref_fc_used_arr[0] == 3):
        df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Fc'] == '4-3 corr']

    # If the reference channel is only 1 and and number of fc used is 1
    elif (len(ref_fc_used_arr) == 1) & (ref_fc_used_arr[0] == 1):
        if len(fc_used) == 1:
            if fc_used[0] == 2:
                df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Fc'] == '2-1 corr']
            elif fc_used[0] == 3:
                df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Fc'] == '3-1 corr']
            elif fc_used[0] == 4:
                df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Fc'] == '4-1 corr']

    # Ref channel is 1 and 2 channels used.
    elif (len(ref_fc_used_arr) == 1) & (len(fc_used) == 2):
        if (fc_used[0] == 2) & (fc_used[1] == 3):
            df_rpt_pts_trim = df_rpt_pts_trim[(df_rpt_pts_trim['Fc'] == '2-1 corr') |
                                              (df_rpt_pts_trim['Fc'] == '3-1 corr')]
        if (fc_used[0] == 3) & (fc_used[1] == 4):
            df_rpt_pts_trim = df_rpt_pts_trim[(df_rpt_pts_trim['Fc'] == '3-1 corr') |
                                              (df_rpt_pts_trim['Fc'] == '4-1 corr')]
        if (fc_used[0] == 2) & (fc_used[1] == 4):
            df_rpt_pts_trim = df_rpt_pts_trim[(df_rpt_pts_trim['Fc'] == '2-1 corr') |
                                              (df_rpt_pts_trim['Fc'] == '4-1 corr')]
    # If the length of ref_fc_used_arr is 2 it implies that channels 1 and 3 were used as ref's and 2 and 4 were used
    # as active as this is the only way the exp can be setup.
    elif (len(ref_fc_used_arr) == 2):
        df_rpt_pts_trim = df_rpt_pts_trim[(df_rpt_pts_trim['Fc'] == '2-1 corr') |
                                          (df_rpt_pts_trim['Fc'] == '4-3 corr')]

    # If 3 channels used than assume we want all the corrected data so no filtering done.

    return df_rpt_pts_trim


def spr_binding_top_for_dot_file(report_pt_file, df_cmpd_set, instrument, fc_used, ref_fc_used_arr=None):

    # Check that the correct instrument is specified in the configuration file.
    if (instrument != 'BiacoreS200') & (instrument != 'Biacore1') & (instrument != 'Biacore3') & \
            (instrument != 'Biacore2') & (instrument != 'Biacore8K'):
        raise ValueError('Instrument argument must be BiacoreS200, Biacore1, Biacore2, or Biacore3')

    if instrument == 'Biacore8K':
        report_pt_read_parm = {'skip': 2, 'name': 'Report point table'}
    else:
        report_pt_read_parm = {'skip': 3, 'name': 'Report Point Table'}

    try:
        # Read in data
        df_rpt_pts_all = pd.read_excel(report_pt_file, sheet_name=report_pt_read_parm['name'],
                                       skiprows=report_pt_read_parm['skip'])
    except:
        raise FileNotFoundError('The files could not be imported please check.')

    # Check that the columns in the report point file match the expected values.
    if (instrument=='Biacore1') | (instrument == 'Biacore3'):
        expected_cols = ['Cycle', 'Fc', 'Report Point', 'RelResp', 'AssayStep',
                           'CycleType', 'Sample_1_Conc', 'Sample_1_Sample']

    if (instrument == 'Biacore2') | (instrument == 'BiacoreS200'):
        expected_cols = ['Cycle', 'Fc', 'Report Point', 'RelResp [RU]',
                         'AssayStep', 'Cycle Type', 'Sample_1_Conc [µM]', 'Sample_1_Sample']

    if instrument == 'Biacore8K':
        expected_cols = ['Cycle', 'Channel', 'Flow cell',	'Sensorgram type', 'Name', 'Relative response (RU)',
                   'Step name', 'Analyte 1 Solution', 'Analyte 1 Concentration (µM)']

    for col in expected_cols:
        if col not in df_rpt_pts_all.columns.tolist():
            raise ValueError('The columns in the report point file do not match the expected names.')

    # Remove unneeded columns from DataFrame
    # For Biacore2 and BiacoreS200
    if (instrument == 'BiacoreS200') | (instrument == 'Biacore2'):

        df_rpt_pts_trim = df_rpt_pts_all.iloc[:, 1:]

        # Create Channel column for consistancy with 8k. **This is not used**
        df_rpt_pts_trim.loc[:, 'Channel'] = ''

        # Remove other not needed columns
        df_rpt_pts_trim = df_rpt_pts_trim.loc[:,
                      ['Cycle', 'Channel', 'Fc', 'Report Point',
                       'RelResp [RU]', 'AssayStep', 'Cycle Type',
                       'Sample_1_Conc [µM]', 'Sample_1_Sample']]

    # For Biacore1 or Biacore3
    if (instrument=='Biacore1') | (instrument == 'Biacore3'):

        # Create Channel column for consistancy with 8k. **This is not used**
        df_rpt_pts_all.loc[:, 'Channel'] = ''

        # Remove other not needed columns
        df_rpt_pts_trim = df_rpt_pts_all.loc[:,
                          ['Cycle', 'Channel', 'Fc', 'Report Point',
                           'RelResp','AssayStep', 'CycleType',
                           'Sample_1_Conc', 'Sample_1_Sample']]

    # For Biacore8K
    if instrument == 'Biacore8K':
        # Remove other not needed columns
        df_rpt_pts_trim = df_rpt_pts_all.loc[:,
                          ['Cycle', 'Channel', 'Flow cell', 'Name',
                           'Relative response (RU)', 'Step name', 'Sensorgram type',
                           'Analyte 1 Concentration (µM)', 'Analyte 1 Solution']]

    # Reassign columns so that there is consistent naming between BiacoreS200, Biacore1, and Biacore3, 8K.
    df_rpt_pts_trim.columns = ['Cycle', 'Channel', 'Fc', 'Report Point',
                               'RelResp [RU]', 'AssayStep', 'Cycle Type',
                               'Sample_1_Conc [µM]', 'Sample_1_Sample']


    # Filter and removed not needed rows
    # 8K
    if instrument == 'Biacore8K':
        df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Cycle Type'] == 'Corrected']
        df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Report Point'] == 'Analyte binding late_1']
        df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['AssayStep'] == 'Analysis']

    # Non-8K
    else:
        df_rpt_pts_trim = df_rpt_pts_trim[df_rpt_pts_trim['Report Point'] == 'binding']
        df_rpt_pts_trim = df_rpt_pts_trim[(df_rpt_pts_trim['AssayStep'] != 'Startup') &
                                      (df_rpt_pts_trim['AssayStep'] != 'Solvent correction')]

    # Need to filer out non-corrected data from data generated by non-8k instruments.
    if instrument != 'Biacore8K':
        df_rpt_pts_trim = _percent_bind_helper_filter_non_corr_data_non_8k(df=df_rpt_pts_trim,
                                                                       ref_fc_used_arr=ref_fc_used_arr,
                                                                       fc_used=fc_used)

    # Create a new column of BRD 4 digit numbers to merge
    df_rpt_pts_trim['BRD_MERGE'] = df_rpt_pts_trim['Sample_1_Sample'].str.split('_', expand=True)[0]
    df_cmpd_set['BRD_MERGE'] = 'BRD-' + df_cmpd_set['Broad ID'].str[9:13]

    # Convert compound set concentration column to float so DataFrames can be merged.
    df_cmpd_set['Test [Cpd] uM'] = df_cmpd_set['Test [Cpd] uM'].astype('float')

    # Merge the report point DataFrame and compound set DataFrame on Top concentration which results in a new
    # Dataframe
    # with only the data for the top concentrations run.
    # To prevent a merge error it is necessary to round sample concentration in both merged data frames.
    df_rpt_pts_trim['Sample_1_Conc [µM]'] = round(df_rpt_pts_trim['Sample_1_Conc [µM]'], 2)
    df_cmpd_set['Test [Cpd] uM'] = round(df_cmpd_set['Test [Cpd] uM'], 2)

    # Conduct the merge.
    # Note: resetting the index just in case as somtimes this causes issues. (Didn't fully explore).
    df_rpt_pts_trim = df_rpt_pts_trim.reset_index(drop=True)
    df_rpt_pts_trim = pd.merge(left=df_rpt_pts_trim, right=df_cmpd_set,
                               left_on=['BRD_MERGE', 'Sample_1_Conc [µM]'],
                               right_on=['BRD_MERGE', 'Test [Cpd] uM'], how='inner')


    # If a compound was run more than once, such as a control, we need to drop the duplicate values.
    # 8K
    if instrument == 'Biacore8K':
        df_rpt_pts_trim = df_rpt_pts_trim.drop_duplicates(['Sample_1_Sample'])
        df_rpt_pts_trim = df_rpt_pts_trim.reset_index(drop=True)
    else:
        df_rpt_pts_trim = df_rpt_pts_trim.drop_duplicates(['Fc', 'Sample_1_Sample'])
        df_rpt_pts_trim = df_rpt_pts_trim.reset_index(drop=True)

    # Need to resort the Dataframe
    # 8K
    if instrument == 'Biacore8K':
        df_rpt_pts_trim = df_rpt_pts_trim.sort_values(['Cycle', 'Channel'])
        df_rpt_pts_trim = df_rpt_pts_trim.reset_index(drop=True)

    # Non-8K
    # Create sorting column
    else:
        df_rpt_pts_trim['sample_order'] = df_rpt_pts_trim['Sample_1_Sample'].str.split('_', expand=True)[1]
        df_rpt_pts_trim = df_rpt_pts_trim.sort_values(['Cycle', 'sample_order'])
        df_rpt_pts_trim = df_rpt_pts_trim.reset_index(drop=True)

    return round(df_rpt_pts_trim['RelResp [RU]'], 2)


