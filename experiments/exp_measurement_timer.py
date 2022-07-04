import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

from cl200a_controller import CL200A


class MeasurementTimer:
    def __init__(self, luxmeter):
        self._luxmeter = luxmeter

    def measure_periodically(self, period: float = 1, end_time: int = 10) -> pd.DataFrame:
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
        df_output["time_diff"] = df_output["time_diff"].apply(lambda x: x.total_seconds())

        return df_output

    def _run_measure_thread(self, output_list: List):
        job_thread = threading.Thread(
            target=self._perform_measurement, kwargs={"output_list": output_list}
        )
        job_thread.start()

    # pylint: disable=invalid-name
    # the names ev, y, z are used in the documentation
    def _perform_measurement(self, output_list: List):
        ev, x, y, measured_time = self._luxmeter.get_ev_x_y()
        output_dict = {"measured_time": str(measured_time), "ev": ev, "x": x, "y": y}
        print(output_dict)
        output_list.append(output_dict)


def main():
    luxmeter = CL200A(debug=False)
    output_dir = Path("results/")
    while True:
        name = input("please enter export name: ")
        now = datetime.now()
        output_name = output_dir / (now.strftime("%Y%m%d_%H%M%S") + "_" + name + ".csv")
        measurement_timer = MeasurementTimer(luxmeter=luxmeter)
        df_output = measurement_timer.measure_periodically(period=1, end_time=10)
        df_output.to_csv(output_name)


if __name__ == "__main__":
    main()
