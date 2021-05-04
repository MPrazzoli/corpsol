from math import *
import numpy as np
import pandas as pd
from QuantLib import *
from datetime import date, datetime
from classes import historical_fixed_rate, zero_curve_rate

# Ammortamento Francese
def ammortamento_francese(df,amortization_rate,tenor,rate_totali,notional):
    t = (1 + amortization_rate / (12 / tenor)) ** rate_totali
    rata_fra = round(notional * t * (amortization_rate / (12 / tenor)) / (t - 1),2)
    Residuo_fra = notional
    Estinto_fra = 0
    tot_I_fra = 0
    plan_fra = np.array
    plan_fra = [[0,0,0,0,0, Residuo_fra]]
    rate_fra = range(0, rate_totali)
    for count in rate_fra:
        Int_quota_fra = round(Residuo_fra * (amortization_rate*(tenor/12)),2)
        Cap_quota_fra = (rata_fra - Int_quota_fra)
        tot_I_fra = (tot_I_fra + Int_quota_fra)
        Residuo_fra = (Residuo_fra - Cap_quota_fra)
        Estinto_fra = (Estinto_fra + Cap_quota_fra)
        Tot_fra = (Int_quota_fra + Cap_quota_fra)
    plan.append([Int_quota_fra, Cap_quota_fra, Tot_fra, tot_I_fra, Estinto_fra, Residuo_fra])
    index = ['Quota Interesse','Quota Capitale','Rata','Interessi Totali','Debito Estinto','Debito Residuo']
    df_fra = pd.DataFrame(plan_fra)
    df_fra.columns = index
    df1_fra = pd.concat([df,df_fra], axis=1)
    df2_fra = pd.concat([df,df_fra['Debito Residuo']], axis=1)[:-1]
    return (df2_fra)

# Ammortamento Italiano
def ammortamento_italiano(df,amortization_rate,tenor,rate_totali, notional):
    Residuo_ita = notional
    tot_I_ita = 0
    Estinto_ita = 0
    Tot_ita = 0
    plan_ita = np.array
    plan_ita = [[0,0,0,0,0,Residuo_ita]]
    rate_ita = range(0,rate_totali)
    for count in rate_ita:
        Int_quota_ita = round(Residuo_ita*amortization_rate/(12/tenor),2)
        Cap_quota_ita = round((notional/rate_totali),2)
        tot_I_ita = (tot_I_ita + Int_quota_ita)
        Residuo_ita = (Residuo_ita - Cap_quota_ita)
        Estinto_ita = (Estinto_ita + Cap_quota_ita)
        Tot_ita = (Int_quota_ita + Cap_quota_ita)
        plan_ita.append([Int_quota_ita,Cap_quota_ita,Tot_ita,tot_I_ita,Estinto_ita,Residuo_ita])
    index = ['Quota Interesse','Quota Capitale','Rata','Interessi Totali','Debito Estinto','Debito Residuo']
    df_ita = pd.DataFrame(plan_ita)
    df_ita.columns=index
    df1_ita = pd.concat([df,df_ita],axis=1)
    df2_ita = pd.concat([df,df_ita['Debito Residuo']],axis=1)[:-1]
    return (df2_ita)

# Ammortamento Bullet
def ammortamento_bullet(df,amortization_rate,tenor,rate_totali, notional):
    Residuo_bullet = notional
    tot_I_bullet = 0
    plan_bullet = np.array
    plan_bullet = [[0,0,Residuo_bullet]]
    rate_bullet = range(0,rate_totali)
    for count in rate_bullet:
        Int_quota_bullet = round(Residuo_bullet*amortization_rate/(12/tenor),2)
        tot_I_bullet = (tot_I_bullet+Int_quota_bullet)
        plan_bullet.append([Int_quota_bullet,tot_I_bullet,Residuo_bullet])
    index = ['Quota Interesse','Interessi Totali','Debito Residuo']
    df_bullet = pd.DataFrame(plan_bullet)
    df_bullet.columns = index
    df1_bullet = pd.concat([df,df_bullet],axis=1)
    df2_bullet = pd.concat([df,df_bullet['Debito Residuo']],axis=1)
    df2_bullet = df2_bullet[:-1]
    return (df2_bullet)

# market data function to fetch Historical Fixed Rate (in Murex3 --> Published), Estimation curve and Discount curve and put everything in one dictionary
def market_data(path):
    historical_fixed_rates = historical_fixed_rate(name = "HISTORICAL RATE")
    historical_fixed_rates.historical_fixed_rate_df = pd.read_excel(path, sheet_name='fixings')
    estimation_curve = zero_curve_rate(name = 'ESTIMATION')
    estimation_curve.zero_curve_rate_df = pd.read_excel(path, sheet_name='estimation')
    discount_curve = zero_curve_rate(name = 'DISCOUNT')
    discount_curve.zero_curve_rate_df = pd.read_excel(path, sheet_name='discount')
    market_data_dict = {'ESTIMATION': estimation_curve, 'DISCOUNT': discount_curve, 'HISTORICAL': historical_fixed_rates}
    return(market_data_dict)

# funzione per convertire le Date quantlib in numeri ATTENZIONE RESTITUISCE SEMPRE UNA LISTA!!!
def date_to_ordinal(date_to_convert):
    date_number = []
    if type(date_to_convert) == QuantLib.Date:
        date_convert = datetime(date_to_convert.year(),date_to_convert.month(),date_to_convert.dayOfMonth())
        date_number.append(date_convert.toordinal())
    else:
        for i, d in enumerate(date_to_convert):
            date_convert = datetime(d.year(), d.month(), d.dayOfMonth())
            date_number.append(date_convert.toordinal())
    return date_number

# funzione per l'interpolazione
def rate_interpoletor(interpolation_type, x_interpolation, y_interpolation, date_to_interpolate):
    interpolation_object = interpolation_type(x_interpolation, y_interpolation)
    rate_interpolated = interpolation_object(date_to_interpolate, allowExtrapolation=True)
    return rate_interpolated

# ESTIMATION RATE FUNCTION
def estimation_rate_function(dataframe_curve, date_fixing_start, date_fixing_end, ref_date): # da passare i fixed rate !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    date_curve_number = date_to_ordinal( dataframe_curve['DATE'])      
    date_fixing_start_number = date_to_ordinal(date_fixing_start)
    date_fixing_end_number = date_to_ordinal(date_fixing_end)
    ref_date_number = date_to_ordinal(ref_date)
    rate_start = []
    for date in date_fixing_start_number:
        rate = rate_interpoletor(KrugerCubic, list(date_curve_number), list(dataframe_curve['RATE']), date)
        rate_start.append(rate)
    discount_start = []
    for i, rate in enumerate(rate_start):
        discount_start.append(exp(-rate / 100 * ((date_fixing_start_number[i] - ref_date_number[0]) / 365))) # convenzione curva di estimation dell'EURIBOR è act/365
    rate_end = []
    for date in date_fixing_end_number:
        rate_end.append(rate_interpoletor(KrugerCubic, list(date_curve_number), list(dataframe_curve['RATE']), date))
    discount_end = []
    for i, rate in enumerate(rate_end):
        discount_end.append(exp(-rate / 100 * ((date_fixing_end_number[i] - ref_date_number[0]) / 365)))
    estimated_rate = []
    for i, date in enumerate(date_fixing_start_number):
        if date <= ref_date_number[0] : 
            estimated_rate.append(0) # bisogna mettere il rate che fa riferimento al sottostante !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        else:
            estimated_rate.append((discount_start[i] / discount_end[i] - 1) / ((date_fixing_end_number[i] - date) / 360)) # convenzione per i discount dell'EURIBOR è act/360
    return estimated_rate

# DISCOUNT RATE FUNCTION
def discount_rate_function(dataframe_curve, ref_date, dataframe_schedule):
    date_curve_number = date_to_ordinal(dataframe_curve['DATE'])
    end_date_number = date_to_ordinal(dataframe_schedule['enddate'])
    ref_date_number = date_to_ordinal(ref_date)
    settlement_date_number = date_to_ordinal(dataframe_schedule['startdate'][0])
    rate_list = [] 
    for date in end_date_number:
        rate_list.append(rate_interpoletor(KrugerCubic, list(date_curve_number), list(dataframe_curve['RATE']), date))
    settlement_date_rate = rate_interpoletor(KrugerCubic, list(date_curve_number), list(dataframe_curve['RATE']), settlement_date_number[0])
    discount_list = []
    for i, rate_curve in enumerate(rate_list):
        discount_list.append(exp(-rate_curve/ 100 * (end_date_number[i] - ref_date_number[0])/ 365))
    discount_settlement = exp(-settlement_date_rate/ 100 * ((settlement_date_number[0] - ref_date_number[0]) / 365))
    discount_rates = []
    for discount in discount_list:
        discount_rates.append(discount / discount_settlement)
    return discount_rates