import pandas as pd
from datetime import datetime
import os
import click
from sys import platform


# Get the users Home Directory
if platform == "win32":
    from pathlib import Path

    homedir = str(Path.home())
else:
    homedir = os.environ['HOME']


@click.command()
@click.option('--clip', is_flag=True, help='Option to indicate that the contents of the setup file is on the clipboard')
def spr_setup_sheet(clip):
    """
    Creates the setup file necessary to run a dose response protocol on a Biacore instrument.

    :param clip: Optional flag to indicate that the contents of the setup file are on the clipboard.
    """

    try:
        if clip:
            df_setup_ori = pd.read_clipboard()
        else:
            file = input("Please paste the path to the setup file: ")
            df_setup_ori = pd.read_csv(file)
    except:
        raise ImportError("Issues reading contents of file.")

    try:
        # Trim the sheet down to only the columns we need for the SPR setup sheet.
        df_setup_trim = df_setup_ori.loc[:, ['Broad ID','MW', 'Barcode', 'Test [Cpd] uM', 'fold_dil', 'num_pts']]

        # Start building the setup sheet.
        # Store the dimensions of the DataFrame in variables that are used later in the method.
        nRows, nCols = df_setup_trim.shape

        # Create empty list used to build up the final DataFrame.
        brd_list = []
        mw_list = []
        bar_list = []
        conc_list = []

        # Inner method uses the original DataFrame to construct each column of the setup sheet.
        def create_lists(header, list):

            if header == 'Broad ID':
                unique_brd = 1
                for cmpd in range(nRows):
                    value = df_setup_trim.iloc[cmpd][header]

                    for i in range(int(df_setup_trim.iloc[cmpd]['num_pts']) + 2):

                        # As the SPR field limit is only 15 characters trim the BRD's
                        if len(value) == 22:
                            v = value[:3] + '-' + value[9:13] + '_' + str(unique_brd)
                            list.append(v)
                        else:
                            v = value + '_' + str(unique_brd)
                            list.append(v)
                    unique_brd += 1
            else:
                for cmpd in range(nRows):
                    value = df_setup_trim.iloc[cmpd][header]
                    for i in range(int(df_setup_trim.iloc[cmpd]['num_pts']) + 2):
                        list.append(value)

        # Inner method needed to create the dose response column.
        def dose_conc_list():

            for cmpd in range(nRows):

                # empty list to store each concentration in the dose response
                dose_list = []

                # Include two blank injections for each compound
                dose_list.append(0)
                dose_list.append(0)

                top = df_setup_trim.iloc[cmpd]['Test [Cpd] uM']  #store top dose in a variable.

                for i in range(int(df_setup_trim.iloc[cmpd]['num_pts'])):
                    dose_list.append(top)
                    top = top / float(df_setup_ori.iloc[cmpd]['fold_dil']) # use value in original DataFrame to determine
                    # the fold of dilution.
                dose_list.sort(reverse=False)

                # Want one final concentration list.  So add each concentration in the dose_list to the final conc_list.
                for c in dose_list:
                    conc_list.append(c)

        # Create the columns in the setup sheet
        create_lists(header='Broad ID', list=brd_list)
        create_lists(header='MW', list=mw_list)
        dose_conc_list()
        create_lists(header='Barcode', list=bar_list)

        # Create the final DataFrame from all of the lists.
        final_df = pd.DataFrame({'BRD': brd_list, 'MW': mw_list, 'CONC': conc_list, 'BAR': bar_list})

        # Reorder the columns
        final_df = final_df.loc[:, ['BRD', 'MW', 'CONC', 'BAR']]

    except RuntimeError:
        print("Something is wrong. Check the original file.")
        raise

    # Truncate the year in the file name.
    now = datetime.now()
    now = now.strftime('%y%m%d')

    try:
        if platform == 'win32':
            final_df.to_excel('\\Volumes\\tdts_users\\SPR Setup Files\\' + now + '_spr_setup_affinity.xlsx')
        else:
            final_df.to_excel('/Volumes/tdts_users/SPR Setup Files/' + now + '_spr_setup_affinity.xlsx')
        print('Setup file has been placed on Iron in folder: SRP Setup Files')
    except:
        print('Issue connecting to Iron. Mount drive and try again.')
        print('')

        if platform == 'win32':
            final_df.to_excel(homedir + '\\Users\\Desktop')
        else:
            final_df.to_excel(homedir + '/Desktop/' + now + '_spr_setup_affinity.xlsx')
        print('File created on desktop.')


if __name__ == '__main__':
    spr_setup_sheet()