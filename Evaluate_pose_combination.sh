echo "Compute Number of successes with each scoring function after combination with ZDOCK poses (Figure 2)"

echo "frequency_set Score N_ZDOCK NB_success" > NB_success_combination.txt
for N in 50 100 1000 2000
do
    for SCORE in contact_average contact_sum residue_average residue_sum
    do
    python $SRC_DIR/Compute_NB_success.py --score $SCORE --list $SRC_DIR/listBM.txt  --zdock_results $ZDOCK_DIR/results/ --max_pose 2000 --all_scores Scores_Freq_top$N/  --rmsd 2.5 > result.temp
    awk -v header="$N $SCORE" '{print header" "$0}' result.temp 
    done
done >> NB_success_combination.txt



