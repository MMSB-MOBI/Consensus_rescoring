import sys
import argparse
import DockingPP

def args_gestion():
    parser = argparse.ArgumentParser(description = "A programm to count the number of successes after rescoring")
    parser.add_argument("--N_native", metavar = "<int>", help = "How many poses from the native ranking should we keep. If not specified, varies between 0 and top_N", type=int,required=False,default=-1)
    parser.add_argument("--score", metavar = "<str>", help = "Score type", default = "res_fr_sum")
    parser.add_argument("--list", metavar = "<file>", help = "List of complex to process", required = True)
    parser.add_argument("--zdock_results", metavar = "<dir>", help = "Directory with zdock results", required = True)
    parser.add_argument("--max_pose", metavar = "<int>", help = "Number of poses to keep (default: 2000)", default = 2000, type=int)
    parser.add_argument("--score_dir", metavar = "<dir>", help = "Directory with all scores computed", required = True)
    parser.add_argument("--top_N", metavar = "<int>", help = "topN to consider (default 10)", default = 10, type=int)
    parser.add_argument("--rmsd", metavar = "<float>", help = "RMSD cutoff (default 2.5)", default = 2.5, type=float)
    parser.add_argument("--verbose", metavar = "<dir>", help = "verbose output (deault False)", default="False",required = False)

    return parser.parse_args()

if __name__ == "__main__":
    ARGS = args_gestion()

    Results={}
    NB_SUCCESS = {}
    Poses={}

    if ARGS.N_native>-1:
        Results[ARGS.N_native]={}
        NB_SUCCESS[ARGS.N_native]=0
        Poses[ARGS.N_native]={}

    else:
        for n_native in range(ARGS.top_N+1):
            Results[n_native]={}
            NB_SUCCESS[n_native]=0
            Poses[n_native]={}

    with open(ARGS.list) as f:
        for prot in f: 
            prot=prot.strip()
            # read the docking output file 
            DH=DockingPP.loadZdock(ARGS.zdock_results + "/" + prot+".zd3.0.2.fg.fixed.out",ARGS.max_pose)
            DH.loadScores(ARGS.score_dir+"/"+prot+".tsv")

            # read the RMSD file 
            with open(ARGS.zdock_results + "/" + prot +".zd3.0.2.fg.fixed.out.rmsds") as f:
                lines=f.readlines()
            
            rmsd={L.split()[0]:L.split()[1] for L in lines}
            # Evaluation
            # get the top_N first according to the native scoring function
            original_poses = DH.getRankedPoses("original", ARGS.max_pose)
            my_list1=[pose.index for pose in original_poses[:ARGS.top_N]]

            # select the top_N first according to the specified score
            reranked_poses = DH.getRankedPoses(ARGS.score,ARGS.max_pose)
            my_list2=[pose.index for pose in reranked_poses[:ARGS.top_N]]

            if ARGS.N_native>-1:
                n_native=ARGS.N_native
                # Combine the two lists
                my_initial_list=[]
                if (n_native > 0):
                    my_initial_list=my_list1[:n_native]
                # complete poses from list2, up to top_N    
                my_added_poses=[p for p in my_list2 if p not in my_initial_list][0:(ARGS.top_N-n_native)]
                my_list_final=my_initial_list + my_added_poses

                topN_rmsd=[rmsd[str(i)] for i in my_list_final]
                NB=sum([1 for rmsd in topN_rmsd if float(rmsd)<ARGS.rmsd])
                Results[n_native][prot]=NB
                Poses[n_native][prot]=my_list_final

                if NB>0:
                    NB_SUCCESS[n_native]+=1

            else:
                for n_native in range(ARGS.top_N+1):
                    # Combine the two lists
                    my_initial_list=[]
                    if (n_native > 0):
                        my_initial_list=my_list1[:n_native]
                    # complete poses from list2, up to top_N    
                    my_added_poses=[p for p in my_list2 if p not in my_initial_list][0:(ARGS.top_N-n_native)]
                    my_list_final=my_initial_list + my_added_poses

                    topN_rmsd=[rmsd[str(i)] for i in my_list_final]
                    NB=sum([1 for rmsd in topN_rmsd if float(rmsd)<ARGS.rmsd])
                    Results[n_native][prot]=NB
                    Poses[n_native][prot]=my_list_final
                    if NB>0:
                        NB_SUCCESS[n_native]+=1

# Verbose Output :
if ARGS.verbose=="True":
    if ARGS.N_native>-1:
        n_native=ARGS.N_native
        for prot in Results[n_native].keys():
                if(Results[n_native][prot]>0):
                    print(str(n_native)+' '+prot+' '+str(Results[n_native][prot]))
    else:       
        for n_native in range(ARGS.top_N+1):
                for prot in Results[n_native].keys():
                    if(Results[n_native][prot]>0):
                        print(str(n_native)+' '+prot+' '+str(Results[n_native][prot]))
# Ultra Verbose output : give the selected poses                        
elif ARGS.verbose=="Ultra":
    if ARGS.N_native>-1:
        n_native=ARGS.N_native
        for prot in Results[n_native].keys():
                for elem in Poses[n_native][prot]:
                    print(str(n_native)+' '+prot+' '+str(elem))
    else:       
        for n_native in range(ARGS.top_N+1):
                for prot in Results[n_native].keys():
                    for elem in Poses[n_native][prot]:
                        print(str(n_native)+' '+prot+' '+str(elem))
# Non-verbose output 
else:
    if ARGS.N_native>-1:
        n_native=ARGS.N_native
        print(NB_SUCCESS[n_native])
    else:
        for n_native in range(ARGS.top_N+1):
            print(str(n_native)+' '+str(NB_SUCCESS[n_native]))

