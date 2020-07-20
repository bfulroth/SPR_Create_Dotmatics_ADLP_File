import pandas as pd
import os
import platform
import argparse
from datetime import datetime
from _version import __version__
import numpy as np

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

    # Determine at runtime if the user wants to format the file for a Biacore 8k run.
    process_for_8k = False

    # TODO: How to test using click?
    # Ask user if they want the output table to be formatted for the 8K
    while True:
        process_for_8k_confirm = input("Do you want to format the file for Biacore 8K [y/N]?")

        if (process_for_8k_confirm == 'y') | (process_for_8k_confirm == 'Y'):
            process_for_8k = True
            print('Process for 8K:', process_for_8k)

        if ((process_for_8k_confirm == 'y') |
                (process_for_8k_confirm == 'Y') |
                (process_for_8k_confirm == 'n') |
                (process_for_8k_confirm == 'N')):
            break

    try:
        if args.clip:
            df_setup_ori = pd.read_clipboard()
        else:
            # TODO: How to test using click?
            # file = click.prompt("Paste the path to the setup table", type=click.Path(exists=True))
            file = input('Paste the path to the setup table: ')
            df_setup_ori = pd.read_csv(file)
    except:
        raise ImportError("Issues reading contents of file.")



    # If process_for_8k is True, preform checks of the current supported scenarios.
    if process_for_8k:
        if not len(df_setup_ori) % 8 == 0:
            print("This script currently only supports runs using all 8 needles.\n")
            print("Exiting program... Please try again.")
            raise RuntimeError

        if (len(df_setup_ori) > 32) & (int(df_setup_ori.iloc[1]['num_pts']) == 10):
            print('Currently this script supports processing one 384W plate at a time.')
            print("Exiting program... Please try again.")
            raise RuntimeError

        if (len(df_setup_ori) > 48) & (int(df_setup_ori.iloc[1]['num_pts']) == 6):
            print('Currently this script supports processing one 384W plate at a time.')
            print("Exiting program... Please try again.")
            raise RuntimeError

    try:
        # Read in the DataFrame.
        # Trim the sheet down to only the columns we need for the SPR setup sheet.
        df_setup_trim = df_setup_ori.loc[:, ['Broad ID', 'MW', 'Barcode', 'Test [Cpd] uM', 'fold_dil', 'num_pts']]

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
                    if process_for_8k:
                        v = v + str(phase_A_group_num)
                        list.append(v)

                    else:
                        v = v + str(phase_A_group_num)
                        list.append(v)
                        phase_A_group_num += 1

                # Reset the appended num for another compound
                if process_for_8k:
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
        if process_for_8k:

            """
            Need to sort the df for 8k input such that each cmpd is grouped for 8 needles and sorted by conc. 
            Stategy: 
            1. Add a row number column. 
            2. Add logic that address two zero conc. pts for each cmpd run.
            3. Sort by zero conc., row number, concentration.
            """
            # Variables needed to reorganize compound titrations for 8k.
            num_pts_curve = int(df_setup_ori.iloc[1]['num_pts'])
            num_active_needles = 8
            total_pts_per_pass = num_pts_curve * num_active_needles

            # add column for sorting
            final_df.loc[:, 'sort_zero'] = ''

            # Variables needed to keep track of where a zero is located in original df
            zero_num = 2
            zero_count = 1

            for i in range(zero_num):
                for index, row in final_df.iterrows():
                    if row['CONC'] == 0:
                        if (index % 2 == 0) & (i == 0):
                            final_df.loc[index, 'sort_zero'] = zero_count
                            zero_count += 1
                        elif (index % 2 != 0) & (i != 0):
                            final_df.loc[index, 'sort_zero'] = zero_count
                            zero_count += 1
                    else:
                        final_df.loc[index, 'sort_zero'] = np.nan

            # Create a copy of the final df so that the final_df is preserved.
            df_zeros = final_df.copy()
            df_zeros = df_zeros.dropna(how='any', subset=['sort_zero'])

            df_zeros = df_zeros.sort_values(['sort_zero'])
            df_zeros = df_zeros.reset_index(drop=True)

            # Create a list to store the sorted DataFrames of zero concentration.
            ls_df_zeros = []

            row_start = 0
            row_end = num_active_needles

            # Group into df's of 8 rows each corresponding to the 8 needles.
            for i in range(0, int(len(df_zeros)), num_active_needles):
                df_active = df_zeros.iloc[row_start:row_end, :]
                df_active = df_active.reset_index(drop=True)
                del df_active['sort_zero']
                ls_df_zeros.append(df_active)
                row_start += 8
                row_end += 8

            # At this point the blanks ordered are placed into separate DF's of length 8 for the 8 needles of the 8k.
            # Now the non-blank concentrations must be handled...
            df_non_zero = final_df[final_df['sort_zero'].isna()].copy()
            df_non_zero.loc[:, 'sort_non_zero'] = ''
            df_non_zero = df_non_zero.reset_index(drop=True)

            # As done with the blanks, split DF into groups of 8 for the 8 needles
            ls_dfs_non_zeros = []
            row_start = 0
            row_end = total_pts_per_pass

            # Create a list of DataFrames separated by each pass of the 8k head.
            for i in range(0, int(len(df_non_zero)), total_pts_per_pass):
                df_active = df_non_zero.iloc[row_start:row_end, :]
                df_active = df_active.reset_index(drop=True)
                ls_dfs_non_zeros.append(df_active)
                row_start += total_pts_per_pass
                row_end += total_pts_per_pass

            # For each df in the non zero df list..
            # Pull out the df and label the sorting column so that sorting can be done.
            ls_dfs_non_zeros_sorted = []

            for df_active in ls_dfs_non_zeros:

                non_zero_count = 1
                row_count = 0
                needle_num = 1

                for i in range(0, num_pts_curve):

                    for j in range(0, int(len(df_active)), num_pts_curve):
                        df_active.loc[row_count, 'sort_non_zero'] = non_zero_count
                        non_zero_count += 1
                        row_count += num_pts_curve

                    row_count = i + 1

                # Sort based on the newly created 'sort_non_zero' column
                df_active = df_active.sort_values(['sort_non_zero'])
                df_active = df_active.reset_index(drop=True)

                # Remove the columns needed for sorting
                del df_active['sort_zero']
                del df_active['sort_non_zero']

                # Append the sorted group of 8 compound titrations to the list of dfs
                ls_dfs_non_zeros_sorted.append(df_active)

            # Need to paste all the zero and non-zero df's together in the right order.
            if ((len(df_setup_ori) == 8) & (num_pts_curve == 10)) | ((len(df_setup_ori) == 8) & (num_pts_curve == 6)):
                final_df = pd.concat([ls_df_zeros[0], ls_df_zeros[1],
                                      ls_dfs_non_zeros_sorted[0]])

            elif ((len(df_setup_ori) == 16) & (num_pts_curve == 10)) | (
                    (len(df_setup_ori) == 16) & (num_pts_curve == 6)):
                final_df = pd.concat([ls_df_zeros[0], ls_df_zeros[2], ls_dfs_non_zeros_sorted[0],
                                      ls_df_zeros[1], ls_df_zeros[3], ls_dfs_non_zeros_sorted[1]])

            elif ((len(df_setup_ori) == 24) & (num_pts_curve == 10)) | (
                    (len(df_setup_ori) == 24) & (num_pts_curve == 6)):
                final_df = pd.concat([ls_df_zeros[0], ls_df_zeros[3], ls_dfs_non_zeros_sorted[0],
                                      ls_df_zeros[1], ls_df_zeros[4], ls_dfs_non_zeros_sorted[1],
                                      ls_df_zeros[2], ls_df_zeros[5], ls_dfs_non_zeros_sorted[2]])

            elif ((len(df_setup_ori) == 32) & (num_pts_curve == 10)) | (
                    (len(df_setup_ori) == 32) & (num_pts_curve == 6)):
                final_df = pd.concat([ls_df_zeros[0], ls_df_zeros[4], ls_dfs_non_zeros_sorted[0],
                                      ls_df_zeros[1], ls_df_zeros[5], ls_dfs_non_zeros_sorted[1],
                                      ls_df_zeros[2], ls_df_zeros[6], ls_dfs_non_zeros_sorted[2],
                                      ls_df_zeros[3], ls_df_zeros[7], ls_dfs_non_zeros_sorted[3]])

            elif (len(df_setup_ori) == 40) & (num_pts_curve == 6):
                final_df = pd.concat([ls_df_zeros[0], ls_df_zeros[5], ls_dfs_non_zeros_sorted[0],
                                      ls_df_zeros[1], ls_df_zeros[6], ls_dfs_non_zeros_sorted[1],
                                      ls_df_zeros[2], ls_df_zeros[7], ls_dfs_non_zeros_sorted[2],
                                      ls_df_zeros[3], ls_df_zeros[8], ls_dfs_non_zeros_sorted[3],
                                      ls_df_zeros[4], ls_df_zeros[9], ls_dfs_non_zeros_sorted[4]])

            elif (len(df_setup_ori) == 48) & (num_pts_curve == 6):
                final_df = pd.concat([ls_df_zeros[0], ls_df_zeros[6], ls_dfs_non_zeros_sorted[0],
                                      ls_df_zeros[1], ls_df_zeros[7], ls_dfs_non_zeros_sorted[1],
                                      ls_df_zeros[2], ls_df_zeros[8], ls_dfs_non_zeros_sorted[2],
                                      ls_df_zeros[3], ls_df_zeros[9], ls_dfs_non_zeros_sorted[3],
                                      ls_df_zeros[4], ls_df_zeros[10], ls_dfs_non_zeros_sorted[4],
                                      ls_df_zeros[5], ls_df_zeros[11], ls_dfs_non_zeros_sorted[5]])

            final_df = final_df.reset_index(drop=True)

    except RuntimeError:
        print("Something is wrong. Check the original file.")
        raise

        # Save the file to the desktop
    save_output_file(df_final=final_df)

    return final_df


def save_output_file(df_final):
    # Truncate the year in the file name.
    now = datetime.now()
    now = now.strftime('%y%m%d')

    # Save file path for server Iron
    save_file_path_iron = os.path.join('iron', 'tdts_users', 'SPR Setup Files',
                                       now + '_spr_setup_funct_APPVersion_' + str(__version__))

    save_file_path_iron = save_file_path_iron.replace('.', '_')
    save_file_path_iron = save_file_path_iron + '.xlsx'

    # Backup save file path for Desktop
    save_file_path_desk = os.path.join(homedir, 'Desktop', now + '_spr_setup_funct_APPVersion_' + str(__version__))
    save_file_path_desk = save_file_path_desk.replace('.', '_')
    save_file_path_desk = save_file_path_desk + '.xlsx'

    try:
        df_final.to_excel(save_file_path_iron)
        print('Setup file has been placed on Iron in folder: SRP Setup Files')
    except:
        print('Issue connecting to Iron. Mount drive and try again.')
        print('')
        df_final.to_excel(save_file_path_desk)
        print('File created on desktop.')