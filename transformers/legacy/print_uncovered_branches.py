import polars as pl
import sys

if __name__ == '__main__':
    
    df_train = pl.scan_parquet(sys.argv[1])
    df_test = pl.scan_parquet(sys.argv[2])

    train_inst_addr = df_train.select(pl.col('inst_addr').unique()).collect(streaming=True)['inst_addr'] 
    uncovered_branches = df_test.filter(~pl.col('inst_addr').is_in(train_inst_addr))

    num_test_entries = df_test.select(pl.col('inst_addr').count()).collect(streaming=True)[0, 'inst_addr']
    num_uncovered_entries = uncovered_branches.select(pl.col('inst_addr').count()).collect(streaming=True)[0, 'inst_addr']
 
    uncovered_branch_names = uncovered_branches.select(pl.col('inst_rel_addr').unique()).collect(streaming=True)
    num_uncovered_branches = uncovered_branch_names.select(pl.count())[0, 'count']
    num_test_branches = df_test.select(pl.col('inst_addr').unique().count()).collect(streaming=True)[0, 'inst_addr']

    print(f'The test trace contains {num_test_entries} entries, of which {num_uncovered_entries} ({num_uncovered_entries / num_test_entries * 100:.2f}%) correspond to branches not encountered in training!')
    print(f'The test trace contains {num_test_branches} unique branches, of which {num_uncovered_branches} ({num_uncovered_branches / num_test_branches * 100:.2f}%) have not been encountered in training!')
    print('Uncovered branches:')
    print(uncovered_branch_names)
