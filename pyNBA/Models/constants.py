from nba_api.stats.library.parameters import PlayTypeNullable

SECONDS_MODEL_PARAMS = {'depth': 10, 'eval_metric': 'MAE', 'learning_rate': 0.01, 'num_boost_round': 5000}

SPS_MODEL_PARAMS = {'depth': 6, 'eval_metric': 'MAE', 'learning_rate': 0.01, 'num_boost_round': 5000}

BPS_MODEL_PARAMS = {'depth': 4, 'eval_metric': 'MAE', 'learning_rate': 0.1, 'num_boost_round': 5000}

TPS_MODEL_PARAMS = {'depth': 6, 'eval_metric': 'MAE', 'learning_rate': 0.01, 'num_boost_round': 5000}

APS_MODEL_PARAMS = {'depth': 6, 'eval_metric': 'MAE', 'learning_rate': 0.02, 'num_boost_round': 5000}

RPS_MODEL_PARAMS = {'depth': 8, 'eval_metric': 'MAE', 'learning_rate': 0.01, 'num_boost_round': 5000}

PPS_MODEL_PARAMS = {'depth': 10, 'eval_metric': 'MAE', 'learning_rate': 0.02, 'num_boost_round': 5000}

MTPS_MODEL_PARAMS = {'depth': 10, 'eval_metric': 'MAE', 'learning_rate': 0.02, 'num_boost_round': 5000}

OWNERSHIP_MODEL_PARAMS =  {
    'colsample_bytree': 0.8, 'eta': 0.01, 'eval_metric': 'mae', 'max_depth': 8,
    'n_estimators': 2000, 'subsample': 0.8, 'tree_method': 'hist'
    }
OWNERSHIP_MODEL_REGRESSORS = [
    'GAMECOUNT', 'TOTAL', 'OPPRANK_D_L20', 'START', 'VALUE', 'AVG_FP', 'L1_FP', 'MA5_FP',
    'SALARY', 'PROJECTION', 'PROJECTION_CHANGE', 'is_G', 'is_F', 'AVG_OWNERSHIP', 'L1_OWNERSHIP',
    'MA5_OWNERSHIP', 'L1P_COUNT', 'L1P_RANK', 'L1P_SB_COUNT', 'L1P_SB_RANK', 'L2P_COUNT',
    'L3P_COUNT', 'L3P_RANK', 'L3P_SB_COUNT', 'L3P_SB_RANK'
]
OWNERSHIP_MODEL_REGRESSAND = 'OWNERSHIP'

TOPSCORE_MODEL_PARAMS = {
    'eta': 0.05, 'eval_metric': 'mae', 'max_depth': 6, 'n_estimators': 5000, 'tree_method': 'hist'
    }

DEFAULT_STD = 0.35

PLAY_TYPES = [
    PlayTypeNullable.transition, PlayTypeNullable.pr_ball_handler, PlayTypeNullable.pr_roll_man, PlayTypeNullable.post_up,
    PlayTypeNullable.spot_up, PlayTypeNullable.handoff, PlayTypeNullable.cut, PlayTypeNullable.off_screen,
    PlayTypeNullable.putbacks, PlayTypeNullable.isolation
]