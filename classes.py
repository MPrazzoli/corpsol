import pandas as pd
from datetime import datetime

# Object for Historical Fixed Rate (in Murex3 --> Published)
class historical_fixed_rate(object):
    def __init__(self, name, reference_date = None, currency = None, underlying = None):
        try:
            self.reference_date = datetime.strptime(reference_date, '%d/%m/%Y')
        except:
            self.reference_date = None
        
        self.name = name
        self.currency = currency
        self.underlying = underlying
        self.historical_fixed_rate_df = pd.DataFrame
        
# Object for Estimation and Discounting curves
class zero_curve_rate(object):
# chiedere a Mirko l'assegnazione di interp_rule e day_count
    def __init__(self, name, reference_date = None, currency = None, underlying = None, interp_rule = None, day_count = None):
        self.name = name
        try:
            self.reference_date = datetime.strptime(reference_date, '%d/%m/%Y')
        except:
            self.reference_date = None
        self.currency = currency
        self.underlying = underlying
        self.interpolation_rule = interp_rule
        self.day_count = day_count
        self.zero_curve_rate_df = pd.DataFrame