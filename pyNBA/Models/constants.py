from nba_api.stats.library.parameters import PlayTypeNullable

OWNERSHIP_MODEL_PARAMS =  {
    'colsample_bytree': 1, 'eta': 0.01, 'eval_metric': 'mae', 'max_depth': 8,
    'n_estimators': 2000,'subsample': 0.8, 'tree_method': 'hist'
    }
OWNERSHIP_MODEL_REGRESSORS = [
    'GAMECOUNT', 'OPPRANK_D_L20', 'START', 'VALUE', 'AVG_FP', 'L1_FP', 'MA5_FP',
    'SALARY', 'SALARY_CHANGE', 'PROJECTION', 'PROJECTION_CHANGE', 'is_G', 'is_F',
    'L1P_RANK', 'L1P_SB_COUNT', 'L1P_SB_RANK',
    'L3P_COUNT', 'L3P_RANK', 'L3P_SB_COUNT', 'L3P_SB_RANK'
]
OWNERSHIP_MODEL_REGRESSAND = 'OWNERSHIP'
OWNERSHIP_PRIMARY_COLS = ['DATE', 'SLATEID', 'PLAYER_ID']

VARIANCE_MODEL_PARAMS =  {
    'colsample_bytree': 1, 'eta': 0.01, 'eval_metric': 'mae', 'max_depth': 8,
    'n_estimators': 2000, 'subsample': 0.8, 'tree_method': 'hist'
    }
VARIANCE_MODEL_REGRESSORS = [
    'PROJECTION_DIFF', 'SALARY', 'AVG_SALARY', 'PROJECTION', 'AVG_PROJECTION', 'PROJECTION_CHANGE',
    'STD_FP', 'MIN_FP', 'MAX_FP', 'AVG_ABS_RES', 'L1_ABS_RES', 'START', 'COUNT_GP', 'PCT_IN_ROLE'
]
VARIANCE_MODEL_REGRESSAND = 'ABS_RES'
VARIANCE_PRIMARY_COLS = ['DATE', 'PLAYER_ID']

PLAY_TYPES = [
    PlayTypeNullable.transition, PlayTypeNullable.pr_ball_handler, PlayTypeNullable.pr_roll_man, PlayTypeNullable.post_up,
    PlayTypeNullable.spot_up, PlayTypeNullable.handoff, PlayTypeNullable.cut, PlayTypeNullable.off_screen,
    PlayTypeNullable.putbacks, PlayTypeNullable.isolation
]