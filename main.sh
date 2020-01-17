COMPLEX_LIST="/home/chilpert/Data/Docking/list_complex.txt"
ZDOCK_DATA="/home/chilpert/Data/Docking/zdock_data/decoys_bm4_zd3.0.2_6deg_fixed"
OUTDIR="/home/chilpert/Test/Docking"
LAUNCH_DIR=$(pwd)

ZDOCK_RESULTS=$ZDOCK_DATA/results
PDBS=$ZDOCK_DATA/input_pdbs

# do it once :
# python Compute_scores_Zdock.py

set -e

mkdir -p $OUTDIR

#Reformat
cd $PDBS
for file in `ls *.pdb.ms `
do

	cut -c1-55 $file > ${file%%.ms}

done

cd $LAUNCH_DIR

SCORES_DIR=$OUTDIR/all_scores
mkdir -p $SCORES_DIR

#python Compute_scores_Zdock.py $COMPLEX_LIST $ZDOCK_RESULTS $PDBS $SCORES_DIR

# Sans Clustering 
echo "== Number of success without clustering"
for score in res_fr_sum  con_fr_sum  res_mean_fr con_mean_fr
do
	echo score is $score 	
	for N in 0 1 2 3 4 5 6 7 8 9 10
	do
	res=`python Compute_NB_success.py -N $N --score $score --list_complex $COMPLEX_LIST --zdock_results $ZDOCK_RESULTS --all_scores $SCORES_DIR`
	echo N=$N $res
	done 
done > $OUTDIR/nb_success_without_clustering.txt


echo "== Number of success with BSAS clustering"

# Avec Clustering  BSAS 
for maxD in 3 
do
echo maxD=$maxD

for N in 0 1 2 3 4 5 6 7 8 9 10
do
res=`python Combine_BSAS_clusters.py -N $N --score res_fr_sum --maxD $maxD --list_complex $COMPLEX_LIST --zdock_results $ZDOCK_RESULTS --all_scores $SCORES_DIR`
echo N=$N $res
done 

done > $OUTDIR/nb_success_with_BSAS.txt


# End of Table 


#Avec Clustering : script : Combine_clusters_rescored.py : pour chaque cluster, on attribue un nouveau score (=rang moyen) et l’on ré-ordonne les clusters selon ce rang. (rankCluster)
#echo 'res_fr_sum'
#for N in 0 1 2 3 4 5 6 7 8 9 10
#do
#res=`python Combine_clusters_rescored.py -N $N -score res_fr_sum`
#echo $N $res
#done
# IS THIS PART USEFUL ? Script doesn't exist and no redirection


echo "== Number of success with BSAS rescored clustering"

for score2 in original_rank res_fr_sum
do
echo $score2
for N in 0 1 2 3 4 5 6 7 8 9 10
do
res=`python Combine_clusters_rescored_choice.py -N $N --pose_score res_fr_sum --cluster_score $score2 --list_complex $COMPLEX_LIST --zdock_results $ZDOCK_RESULTS --all_scores $SCORES_DIR`
echo N=$N $res
done 
done > $OUTDIR/nb_success_rescored_BSAS.txt

echo "== Number of success with BSAS rescored clustering and filter size"

echo 'res_fr_sum'
for size in 0 2 5 10 20 30 
do
for N in 0 1 2 3 4 5 6 7 8 9 10
do
res=`python Combine_clusters_filter_size.py -N $N --pose_score res_fr_sum --size $size --list_complex $COMPLEX_LIST --zdock_results $ZDOCK_RESULTS --all_scores $SCORES_DIR`
echo size=$size N=$N $res
done
done  > $OUTDIR/nb_success_rescored_BSAS_filter_size.txt



echo 'res_fr_sum'
for N in 0 1 2 3 4 5 6 7 8 9 10
do
res=`python Combine_clusters_order_size.py -N $N -score res_fr_sum`
echo size=$size N=$N $res
done  > Table5.txt
