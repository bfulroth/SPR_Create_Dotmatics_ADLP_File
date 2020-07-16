import pandas as pd
import os
import platform
import argparse
from datetime import datetime

# Get the users Home Directory
if platform.system() == "Windows":
    from pathlib import Path

    homedir = str(Path.home())
else:
    homedir = os.environ['HOME']

# Use argparse to parse the arguments instead of click.
parser = argparse.ArgumentParser(description='Script for Creating an SPR setup file.')
parser.add_argument("-c", "--clip", action='store_true', default=False)
parser.add_argument("--b8k", action='store_true', default=False)


def main(args=None):
    """Creates the setup file necessary to run an ABA functional assay protocol on a Biacore S200 or 8k instrument.

     :param clip: Contents of the setup file are on the clipboard.
     :param b8k: Boolean to indicate data format in for 8k or not.
     :type clip: bool
    """

    # Extract the command line arguments
    args = parser.parse_args(args=args)

    if args.clip:
        df_setup = pd.read_clipboard()

    else:
        file = input('Enter setup file path: ')
        df_setup = pd.read_csv(file)

    try:
        # Read in the DataFrame.
        # Trim the sheet down to only the columns we need for the SPR setup sheet.
        df_setup_trim = df_setup[['Broad ID','MW', 'Barcode', 'Test [Cpd] uM', 'fold_dil', 'num_pts']]

        # Start building the setup sheet.
        # Store the dimensions of the DataFrame in variables that are used later in the method.
        nRows, nCols = df_setup_trim.shape

        # Create empty list used to build up the final DataFrame.
        sample_sol_list = []
        flank_sol_list = []
        mw_list = []
        bar_list = []
        conc_list = []

        # Inner method uses the original DataFrame to construct the sample solution column.
        def create_sample_sol_list(header, list):

            for cmpd in range(nRows):
                value = df_setup_trim.iloc[cmpd][header]

                for i in range(int(df_setup_trim.iloc[cmpd]['num_pts']) + 2):

                    # As the SPR field limit is only 15 characters trim the BRD's
                    if len(value) == 22:
                        v = value[:3] + '-' + value[9:13] + '_' + 's'
                        list.append(v)
                    else:
                        v = value + '_' + 's' + '_' + 's'
                        list.append(v)

        # Inner method uses the original DataFrame to construct the flanking solution column.
        def create_flank_sol_list(header, list):

            phase_A_group_num = 1
            for cmpd in range(nRows):

                value = df_setup_trim.iloc[cmpd][header]

                for i in range(int(df_setup_trim.iloc[cmpd]['num_pts']) + 2):

                    # As the SPR field limit is only 15 characters trim the BRD's
                    if len(value) == 22:
                        v = value[:3] + '-' + value[9:13] + '_'
                    else:
                        v = value + '_'

                    # If we are formatting for 8K
                    if args.b8k:
                        v = v + str(phase_A_group_num)
                        list.append(v)

                    else:
                        v = v + str(phase_A_group_num)
                        list.append(v)
                        phase_A_group_num += 1

                # Reset the appended num for another compound
                if args.b8k:
                    phase_A_group_num += 1
                else:
                    phase_A_group_num = 1

        # Inner method needed to create the dose response column.
        def create_dose_conc_list():

            for cmpd in range(nRows):
                # empty list to store each concentration in the dose response
                dose_list = []

                # Include two blank injections for each compound
                dose_list.append(0)
                dose_list.append(0)

                top = df_setup_trim.iloc[cmpd]['Test [Cpd] uM'] #store top dose in a variable.

                for i in range(int(df_setup_trim.iloc[cmpd]['num_pts'])):
                    dose_list.append(top)
                    top = top / int(df_setup_trim.iloc[cmpd]['fold_dil']) # use value in original DataFrame to determine
                    # the fold of dilution.
                dose_list.sort(reverse=False)

                # Want one final concentration list.  So add each concentration in the dose_list to the final conc_list.
                for c in dose_list:
                    conc_list.append(c)

            # Inner method used to create the mw or bc columns.
        def create_mw_or_bc_list(header, list):

            for cmpd in range(nRows):
                value = df_setup_trim.iloc[cmpd][header]
                for i in range(int(df_setup_trim.iloc[cmpd]['num_pts']) + 2):
                    list.append(value)

        # Create the columns in the setup sheet by calling the inner methods above.
        create_sample_sol_list(header='Broad ID', list=sample_sol_list)
        create_flank_sol_list(header='Broad ID', list=flank_sol_list)
        create_dose_conc_list()
        create_mw_or_bc_list(header='MW', list=mw_list)
        create_mw_or_bc_list(header='Barcode', list=bar_list)

        # Create the final DataFrame from all of the lists.
        final_df = pd.DataFrame({'Sample Solution': sample_sol_list, 'Flanking Solution (A)': flank_sol_list,
                                 'CONC': conc_list, 'MW': mw_list, 'BAR': bar_list})

        # Reorder the columns
        final_df = final_df.loc[:, ['Sample Solution', 'Flanking Solution (A)', 'CONC', 'MW', 'BAR']]

        # Need to sort the DF if flag b8k is true.
        if args.b8k:

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

            #TODO: Logic only works if you use to blank injections for zero points.  Need to make more genaralized
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

        now = datetime.now()

        # Truncate the year in the file name.
        now = now.strftime('%y%m%d')

        try:
            final_df.to_excel('/Volumes/tdts_users/SPR Setup Files/' + now + '_spr_setup_ABA.xlsx')
            print('Setup file has been placed on Iron server in folder: SRP Setup Files')
        except:
            print('Issue connecting to Iron server. Mount drive and try again.')
            print('')

            final_df.to_excel(os.path.join(homedir, 'Desktop', now + '_spr_setup_ABA.xlsx'))
            print('File created on desktop.')

    except:
        print("Something is wrong. Check the original file.")