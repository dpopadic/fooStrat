


df0 = res.query("field=='goal_superiority'").reset_index(drop=True)
df1 = expand_field_single(data=df0)







tmp6_1 = df1.query("div=='E0' & season=='2005'")
tmp6_1.team.unique()

res.query("div=='E0' & season=='2019' & team=='liverpool'")
