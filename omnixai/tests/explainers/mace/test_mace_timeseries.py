import os
import unittest
import numpy as np
import pandas as pd
from omnixai.utils.misc import set_random_seed
from omnixai.data.timeseries import Timeseries
from omnixai.explainers.timeseries.counterfactual.mace import MACEExplainer


def load_timeseries():
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../datasets")
    df = pd.read_csv(os.path.join(data_dir, "timeseries.csv"))
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
    df = df.rename(columns={"horizontal": "values"})
    df = df.set_index("timestamp")
    df = df.drop(columns=["anomaly"])
    return df


def train_detector(train_df):
    threshold = np.percentile(train_df["values"].values, 90)

    def _detector(ts: Timeseries):
        scores = []
        for x in ts.values:
            anomaly_scores = np.sum((x > threshold).astype(int))
            scores.append(anomaly_scores / x.shape[0])
        return np.array(scores)

    return _detector


class TestMACETimeseries(unittest.TestCase):

    def setUp(self) -> None:
        df = load_timeseries()
        self.train_df = df.iloc[:9150]
        self.test_df = df.iloc[9150:9300]
        self.detector = train_detector(self.train_df)
        print(self.detector(Timeseries.from_pd(self.test_df)))

    def test(self):
        set_random_seed()
        explainer = MACEExplainer(
            training_data=Timeseries.from_pd(self.train_df),
            predict_function=self.detector,
            threshold=0.001
        )
        explanations = explainer.explain(Timeseries.from_pd(self.test_df))
        explanations.plotly_plot()


if __name__ == "__main__":
    unittest.main()
