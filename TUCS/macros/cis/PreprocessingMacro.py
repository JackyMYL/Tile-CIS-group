import os
import argparse

parser = argparse.ArgumentParser(description=
'Creates a list of channels automatically qualified \n\
for recalibration for a given IOV. The macro is designed \n\
to used prior to performing a bulk reprocessing but \n\
could be useful for any CIS recalibration',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--IOVs', action='store', nargs='*', type=int, required=True, 
                    default=0, help=
'Enter the IOVs that are being used for the reprocessing. \n\
They must be six-digit integers separated with spaces.')

args=parser.parse_args()
iovlist=args.IOVs
print iovlist
if len(iovlist)==0:
	raise Exception('\
\n \n ERROR: You must enter at least one IOV. This is going to fail. \n')

for iov in iovlist:        
        call="""python macros/cis/StudyFlag.py --date '-28 days' --ldate {0} --region --qflag 'DB Deviation' \
             --exclude --printopt 'Only_Chosen_Flag' --output 'Preprocessing Check {0}' --preprocessing""".format(iov)
        print call
        os.system(call)
