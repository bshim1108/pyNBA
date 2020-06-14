from pyNBA.DFS.constants import Site


class FPCalculator(object):
    def __init__(self, site):
        self.site = site

    def calculate_fantasy_points(self, season, pts, reb, ast, tov, blk, stl, tpm=None):
        if self.site == Site.FANDUEL:
            if int(season.split('-')[0]) < 2017:
                return pts + 1.2*reb + 1.5*ast - 1*tov + 2*blk + 2*stl
            else:
                return pts + 1.2*reb + 1.5*ast - 1*tov + 3*blk + 3*stl

        elif self.site == Site.DRAFTKINGS:
            fp = pts + 0.5*tpm + 1.25*reb + 1.5*ast - 0.5*tov + 2*blk + 2*stl
            doubles = [i for i in [pts, reb, ast, blk, stl] if i >= 10]
            if len(doubles) < 2:
                return fp
            elif len(doubles) == 2:
                return fp + 1.5
            else:
                return fp + 3

        else:
            raise Exception('invald site')
