# fooStrat <img src="meta/img/logo.png" align="right" height=140/>
Statistical analysis and strategy development for football data

<p align="center">
  <img width="500" height="400" src="meta/img/architecture.png">
</p>


**Core**

> Data sourcing ```1_data_sourcing```

> Restore data ```2_restoration```

> Update data ```3_processing```

> Compute all factors ```4_features```

> Factor evaluation```5_evaluation```

> Model building ```6_modelling```

> Signal generation ```7_signals```


**Utilities**

> Utillity functions required to perform data cleaning, calculations etc. ```foostrat.servicers```

> Daily ETL Process ```job_schedule.py```

> Cloud access via ```from fooStrat.processing import fp_cloud```


