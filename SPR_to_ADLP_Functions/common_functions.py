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

    # TODO: Make sure sorting the final df is not need at the end.
    # sort_vals = [i for i in range(0, len(df_brd_core_id))]
    # df_brd_core_id.loc[:, 'sort_col'] = pd.Series(sort_vals)

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
        raise ConnectionError("Cannot connect to resultsdb database. "
                              "Please make sure you are on the Broad Internal Network.")

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
        Draw.MolToFile(mol=m, filename=img_full_path, size=(300, 300))

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
        worksheet.set_row(row=row, height=235)

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