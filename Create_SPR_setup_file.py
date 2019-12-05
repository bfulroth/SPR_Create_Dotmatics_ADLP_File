import pandas as pd
from datetime import datetime
import os
import click
import platform


# Get the users Home Directory
if platform.system() == "Windows":
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
    # Determine at runtime if the user wants to format the file for a Biacore 8k run.
    process_for_8k = False
    if click.confirm('Do you want to format the file for Biacore 8K?'):
        process_for_8k = True

    try:
        if clip:
            df_setup_ori = pd.read_clipboard()
        else:
            file = click.prompt("Paste the path to the setup table", type=click.Path(exists=True))
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

        # Need to sort the DF if flag b8k is true.
        # TODO: Limited to only 8 compounds.  If > 8 all zeros are sorted to the beginning. Need to change.
        if process_for_8k:

            """
            Need to sort the df for 8k input such that each cmpd is grouped for 8 needles and sorted by conc. 
            Stategy: 
            1. Add a row number column. 
            2. Add logic that address two zero conc. pts for each cmpd run.
            3. Sort by zero conc., row number, concentration.
            """
            # add column for sorting
            final_df['sort_val'] = [i for i in range(len(final_df))]
            final_df['sort_zero'] = ""

            zero_num = 2
            zero_count = 1

            # TODO: Logic only works if you use two blank injections for zero points.  Need to make more genaralized
            for i in range(zero_num):
                for index, row in final_df.iterrows():
                    if row['CONC'] == 0:
                        if (index % 2 == 0) & (i == 0):
                            final_df.loc[index, 'sort_zero'] = zero_count
                            zero_count += 1
                        elif (index % 2 != 0) & (i != 0):
                            final_df.loc[index, 'sort_zero'] = zero_count
                            zero_count += 1

            final_df = final_df.sort_values(['sort_zero', 'CONC', 'sort_val'])
            del final_df['sort_zero']
            del final_df['sort_val']

    except RuntimeError:
        print("Something is wrong. Check the original file.")
        raise

    # Truncate the year in the file name.
    now = datetime.now()
    now = now.strftime('%y%m%d')

    try:
        if platform.system() == 'Windows':
            final_df.to_excel('\\\iron\\tdts_users\\SPR Setup Files\\' + now + '_spr_setup_affinity.xlsx')
        else:
            final_df.to_excel('/Volumes/tdts_users/SPR Setup Files/' + now + '_spr_setup_affinity.xlsx')
        print('Setup file has been placed on Iron in folder: SRP Setup Files')
    except:
        print('Issue connecting to Iron. Mount drive and try again.')
        print('')
        if platform.system() == 'Windows':
            path_desk = homedir + '\\Desktop\\' + now + '_spr_setup_affinity.xlsx'
            final_df.to_excel(path_desk)
        else:
            final_df.to_excel(homedir + '/Desktop/' + now + '_spr_setup_affinity.xlsx')
        print('File created on desktop.')


if __name__ == '__main__':
    spr_setup_sheet()