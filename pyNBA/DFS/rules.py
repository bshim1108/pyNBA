
class FPCalculator(object):

    @staticmethod
    def calculate_draftkings_fp(pts, reb, ast, tov, blk, stl, tpm, dd_td_pct=None):
        fp = pts + 0.5*tpm + 1.25*reb + 1.5*ast - 0.5*tov + 2*blk + 2*stl
        doubles = [i for i in [pts, reb, ast, blk, stl] if i >= 10]
        if dd_td_pct is not None:
            dd_pct = dd_td_pct[0]
            td_pct = dd_td_pct[1]
            return fp + 1.5*(dd_pct) + 3*(td_pct)
        else:
            doubles = [i for i in [pts, reb, ast, blk, stl] if i >= 10]
            if len(doubles) < 2:
                return fp
            elif len(doubles) == 2:
                return fp + 1.5
            else:
                return fp + 4.5

    @staticmethod
    def calculate_fanduel_fp(season, pts, reb, ast, tov, blk, stl):
        if int(season.split('-')[0]) < 2017:
            return pts + 1.2*reb + 1.5*ast - 1*tov + 2*blk + 2*stl
        else:
            return pts + 1.2*reb + 1.5*ast - 1*tov + 3*blk + 3*stl
