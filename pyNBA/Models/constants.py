SECONDS_MODEL_PARAMS = {'depth': 10, 'eval_metric': 'MAE', 'learning_rate': 0.01, 'num_boost_round': 5000}

SPS_MODEL_PARAMS = {'depth': 6, 'eval_metric': 'MAE', 'learning_rate': 0.01, 'num_boost_round': 5000}

BPS_MODEL_PARAMS = {'depth': 4, 'eval_metric': 'MAE', 'learning_rate': 0.1, 'num_boost_round': 5000}

TPS_MODEL_PARAMS = {'depth': 6, 'eval_metric': 'MAE', 'learning_rate': 0.01, 'num_boost_round': 5000}

APS_MODEL_PARAMS = {'depth': 6, 'eval_metric': 'MAE', 'learning_rate': 0.02, 'num_boost_round': 5000}

RPS_MODEL_PARAMS = {'depth': 8, 'eval_metric': 'MAE', 'learning_rate': 0.01, 'num_boost_round': 5000}

PPS_MODEL_PARAMS = {'depth': 10, 'eval_metric': 'MAE', 'learning_rate': 0.02, 'num_boost_round': 5000}

MTPS_MODEL_PARAMS = {'depth': 10, 'eval_metric': 'MAE', 'learning_rate': 0.02, 'num_boost_round': 5000}

OWNERSHIP_MODEL_PARAMS = {
    'colsample_bytree': 0.9, 'eta': 0.02, 'eval_metric': 'mae', 'max_depth': 8, 'n_estimators': 2000,
    'subsample': 0.9, 'tree_method': 'hist'
    }

TOPSCORE_MODEL_PARAMS = {
    'eta': 0.05, 'eval_metric': 'mae', 'max_depth': 6, 'n_estimators': 5000, 'tree_method': 'hist'
    }

DEFAULT_STD = 0.35
