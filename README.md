Finding Edge in Daily Fantasy Basketball
================
Brandon Shimiaie

Documentation [WIP]
---------------------------------------

https://github.com/bshim1108/pyNBA/blob/master/Documentation/Documentation.pdf

Example: Projecting Points Per Second
---------------------------------------

# Problem Definition

Use historical boxscores to predict an NBA player's Points Per Second (PPS) in a single game. In conjunction with the predicted NBA player's Seconds Played (SP) will be used to predict the total points of a player in a single game.

Setup

``` r
# for data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pyNBA.Data.data import QueryData
from pyNBA.Models.helpers import CleanData
import math

# for features
from pyNBA.Models.features import FeatureCreation
from pyNBA.Models.cluster import Cluster, Evaluate
from sklearn.feature_selection import SelectFromModel
from sklearn.feature_selection import RFE

# for plotting
import matplotlib.pyplot as plt
import seaborn as sns
from research import Helpers
from statsmodels.graphics.api import abline_plot

# for statistical tests
from scipy.stats import shapiro
import pingouin as pg

# for machine learning
from sklearn import model_selection, preprocessing, ensemble, neighbors, linear_model, svm, neural_network, metrics
import xgboost as xgb
from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split

# for explainer
from lime import lime_tabular

# misc
import warnings
warnings.filterwarnings('ignore')
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:90% !important; }</style>"))
```

# Factor Determination
Determine the factors that influence a player's Points Per Second (PPS).

- Historical PPS
    - Season average
    - Recent performances (hot streaks)
    - Home vs. Away
    - Start vs. Bench
    - Rest
    - Historical Attempts Per Second (APS) and Points Per Second (PPS)


- Defense
    - Defensive PPS allowed
        - Starters vs. Bench players
        - By position
        - By cluster
    - Vegas game total

        
- Injuries
    - APS of players playing vs average APS of team
    - Player PPS/APS by starting lineup
