Si_quant = 1 #обьем на SI
SBRF_quant = 1 #обьем на SBRF
LKOH_quant = 1
SNGS_quant = 1
exp_date = 22
exp_month = 3
exp_forward=1
exp_back=1

Ri = {
    'iscross_short': False,
    'quant': SBRF_quant,
    # rulez parameters
    'exp_forward' : exp_forward,
    'exp_back' : exp_back,
    'exp_day' : exp_date,
    'exp_month' : exp_month,

    #LEVEL_PARAMS
    'DESTROY_LEWEL_HIGH': 6,
    'DESTROY_LEWEL_LOW': 8,
    'KOL_Candles_HIGH': 10,
    'KOL_Candles_LOW' : 2,
    'PERSENT_HIGH' : 0.25,
    'PERSENT_LOW' : 0.45,
    'MaxR' : 8,
    'MaxL' : 8,
    'MinR': 4,
    'MinL': 6,

    #SMA PARAMS:
    'SMA': 60,

    # TR_Long_RSI parameters
    'ATR_Long1' : 20,
    'kStop_Long1' : 2,
    'kStart_Long1' : 6,
    'kPorabolic_Long' : 1700,

    # TR_Short_RSI parameters
    'ATR_Short1' : 35,
    'kStop_Short1' : 2,
    'kStart_Short1' : 1,
    'kPorabolic_Short' : 1200,

    #Максимальная просадка
    'MaxDrowDown': 1780,
    'Persent_AD_LONG': 0.45,
    'Persent_AD_SHORT':2
}

LKOH = {
    'iscross_short': False,
    'quant': LKOH_quant,
    # rulez parameters
    'exp_forward' : exp_forward,
    'exp_back' : exp_back,
    'exp_day' : exp_date,
    'exp_month' : exp_month,

    #LEVEL_PARAMS
    'DESTROY_LEWEL_HIGH': 8,
    'DESTROY_LEWEL_LOW': 4,
    'KOL_Candles_HIGH': 3,
    'KOL_Candles_LOW' : 4,
    'PERSENT_HIGH' : 0.95,
    'PERSENT_LOW' : 0.65,
    'MaxR' : 8,
    'MaxL' : 20,
    'MinR': 4,
    'MinL': 2,

    #SMA PARAMS:
    'SMA': 60,

    # TR_Long_RSI parameters
    'ATR_Long1' : 100,
    'kStop_Long1' : 2,
    'kStart_Long1' : 1,
    'kPorabolic_Long' : 700,

    # TR_Short_RSI parameters
    'ATR_Short1' : 100,
    'kStop_Short1' : 2,
    'kStart_Short1' : 10,
    'kPorabolic_Short' : 500,

    #Максимальная просадка
    'MaxDrowDown': 1251,
    'Persent_AD_LONG': 0.45,
    'Persent_AD_SHORT':2
}
SNGS = {
    'iscross_short': False,
    'quant': SNGS_quant,
    # rulez parameters
    'exp_forward' : exp_forward,
    'exp_back' : exp_back,
    'exp_day' : exp_date,
    'exp_month' : exp_month,

    #LEVEL_PARAMS
    'DESTROY_LEWEL_HIGH': 6,
    'DESTROY_LEWEL_LOW': 2,
    'KOL_Candles_HIGH': 10,
    'KOL_Candles_LOW' : 6,
    'PERSENT_HIGH' : 0.95,
    'PERSENT_LOW' : 0.65,
    'MaxR' : 3,
    'MaxL' : 3,
    'MinR': 8,
    'MinL': 8,

    #SMA PARAMS:
    'SMA': 60,

    # TR_Long_RSI parameters
    'ATR_Long1' : 20,
    'kStop_Long1' : 2,
    'kStart_Long1' : 1,
    'kPorabolic_Long' : 300,

    # TR_Short_RSI parameters
    'ATR_Short1' : 5,
    'kStop_Short1' : 2,
    'kStart_Short1' : 4,
    'kPorabolic_Short' : 600,

    #Максимальная просадка
    'MaxDrowDown': 1460,
    'Persent_AD_LONG': 0.45,
    'Persent_AD_SHORT':2
}

optimized = {'SPBFUT.SRZ3': Ri, 'SPBFUT.LKZ3': LKOH, 'SPBFUT.SNZ3': SNGS}
