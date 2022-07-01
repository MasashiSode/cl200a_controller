import threading
import time
from datetime import datetime
from typing import Dict, List

import pandas as pd

from cl200a_controller import CL200A


class MeasurementTimer:
    def __init__(self, luxmeter):
        self._luxmeter = luxmeter

    def measure_periodically(self, period: float = 1, end_time: int = 10):
        if period < 1:
            raise ValueError("Period must be greater than or equal to 1")

        output_list: List[Dict] = []
        for _ in range(end_time):
            self._run_measure_thread(output_list)
            time.sleep(period)

        df_output = pd.DataFrame(output_list)
        df_output["measured_time"] = df_output["measured_time"].apply(
            lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")
        )
        df_output["time_diff"] = df_output["measured_time"].diff()

        return df_output

    def _run_measure_thread(self, output_list):
        job_thread = threading.Thread(
            target=self._perform_measurement, kwargs={"output_list": output_list}
        )
        job_thread.start()

    # pylint: disable=invalid-name
    # the names ev, y, z are used in the documentation
    def _perform_measurement(self, output_list):
        ev, x, y, measured_time = self._luxmeter.get_ev_x_y()
        output_dict = {"measured_time": str(measured_time), "ev": ev, "x": x, "y": y}
        print(output_dict)
        output_list.append(output_dict)


if __name__ == "__main__":
    luxmeter_ = CL200A(debug=False)
    measurement_timer = MeasurementTimer(luxmeter=luxmeter_)
    df = measurement_timer.measure_periodically(period=1, end_time=10)
    print(df)
