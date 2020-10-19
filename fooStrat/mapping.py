import pandas as pd

# division mapping
competition = {'E0':'England Premier League',
               'E1':'England Championship League',
               'E2':'England Football League One',
               'E3':'England Football League Two',
               'EC':'England National League',
               'SC0':'Scottish Premiership',
               'SC1':'Scottish Championship',
               'SC2':'Scottish League One',
               'SC3':'Scottish League Two',
               'D1':'German Bundesliga',
               'D2':'German 2. Bundesliga',
               'SP1':'Spain La Liga',
               'SP2':'Spain Segunda Division',
               'I1':'Italy Serie A',
               'I2':'Italy Serie B',
               'F1':'France Ligue 1',
               'F2':'France Ligue 2',
               'N1':'Dutch Eredivisie',
               'B1':'Belgian First Division A',
               'P1':'Portugal',
               'T1':'Turkey Süper Lig',
               'G1':'Greek Super League',
               'Argentina Superliga':'Argentina Superliga',
               'Austria Tipico Bundesliga':'Austria Tipico Bundesliga',
               'Brazil Serie A':'Brazil Serie A',
               'China Super League':'China Super League',
               'Denmark Superliga':'Denmark Superliga',
               'Finland Veikkausliiga':'Finland Veikkausliiga',
               'Ireland Premier Division':'Ireland Premier Division',
               'Japan J-League':'Japan J-League',
               'Japan J1 League':'Japan J1 League',
               'Mexico Liga MX':'Mexico Liga MX',
               'Norway Eliteserien':'Norway Eliteserien',
               'Poland Ekstraklasa':'Poland Ekstraklasa',
               'Romania Liga 1':'Romania Liga 1',
               'Russia Premier League':'Russia Premier League',
               'Sweden Allsvenskan':'Sweden Allsvenskan',
               'Switzerland Super League':'Switzerland Super League',
               'USA MLS':'USA MLS'}
# ml_map = pd.DataFrame(list(competition.items()), columns=['Div', 'Competition'])
ml_map = pd.read_csv('./data/mapping/leagues.csv', encoding = "ISO-8859-1", delimiter=";")


# odds mapping
# home win
oh = ['B365H', 'BSH', 'BWH', 'GBH', 'IWH', 'LBH', 'PSH', 'PH', 'SOH', 'SBH', 'SJH', 'SYH',
      'VCH', 'WHH', 'BbMxH', 'BbAvH', 'MaxH', 'AvgH']
# away win
oa = ['B365A', 'BSA', 'BWA', 'GBA', 'IWA', 'LBA', 'PSA', 'PA', 'SOA', 'SBA', 'SJA', 'SYA',
      'VCA', 'WHA', 'BbMxA', 'BbAvA', 'MaxA', 'AvgA']
# draw
od = ['B365D', 'BSD', 'BWD', 'GBD', 'IWD', 'LBD', 'PSD', 'PD', 'SOD', 'SBD', 'SJD', 'SYD',
      'VCD', 'WHD', 'BbMxD', 'BbAvD', 'MaxD', 'AvgD']
# above 2.5
atp5 = ['BbMx>2.5', 'BbAv>2.5', 'GB>2.5', 'B365>2.5', 'P>2.5', 'Max>2.5', 'Avg>2.5']
# below 2.5
btp5 = ['BbMx<2.5', 'BbAv<2.5', 'GB<2.5', 'B365<2.5', 'P<2.5', 'Max<2.5', 'Avg<2.5']
odds_fields = {'odds_home_win':oh,
               'odds_away_win':oa,
               'odds_draw_win':od,
               'odds_under_25_goal':btp5,
               'odds_above_25_goal': atp5}

# symmetric odds map
owsy = ['B365_win', 'BS_win', 'BW_win', 'GB_win', 'IW_win', 'LB_win',
        'PS_win', 'P_win', 'SO_win', 'SB_win', 'SJ_win', 'SY_win',
        'VC_win', 'WH_win', 'BbMx_win', 'BbAv_win', 'Max_win', 'Avg_win']
odsy = ['B365_draw', 'BS_draw', 'BW_draw', 'GB_draw', 'IW_draw', 'LB_draw',
        'PS_draw', 'P_draw', 'SO_draw', 'SB_draw', 'SJ_draw', 'SY_draw',
        'VC_draw', 'WH_draw', 'BbMx_draw', 'BbAv_draw', 'Max_draw', 'Avg_draw']

home_boo = [1 for x in range(len(oh))] + [-1 for x in range(len(oa))] + [0 for x in range(len(od))]
odds_fields_neutral = pd.DataFrame({'field': oh + oa + od,
                                    'home': home_boo,
                                    'field_neutral': owsy + owsy + odsy})



