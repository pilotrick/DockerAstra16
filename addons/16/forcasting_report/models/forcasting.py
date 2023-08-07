# -*- coding: utf-8 -*-
import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing


def forcasting_details(res, predicts_dates):
    data = pd.DataFrame(res, columns=["month_date", "sum"])
    data = data.set_index('month_date')
    try:
        model = ExponentialSmoothing(
            data, trend='add', seasonal="add", seasonal_periods=12)
        fit = model.fit()

        predictions = fit.forecast(12)
        res = dict(zip(predicts_dates, predictions.tolist()))
        return res
    except ValueError as valerr:
        model = ExponentialSmoothing(
            data, trend='add', seasonal=None, seasonal_periods=12)
        fit = model.fit()
        predictions = fit.forecast(12)
        res = dict(zip(predicts_dates, predictions.tolist()))
        return res
