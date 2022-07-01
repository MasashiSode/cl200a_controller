from time import sleep

from cl200a_controller import CL200A

if __name__ == "__main__":
    luxmeter = CL200A(debug=False)

    while True:
        print(f"ev, x, y, measured_time: {luxmeter.get_ev_x_y()}")
        print(f"x, y, z, measured_time: {luxmeter.get_x_y_z()}")
        print(f"ev, u, v, measured_time: {luxmeter.get_ev_u_v()}")
        print(f"ev, tcp, Δuv, measured_time: {luxmeter.get_ev_tcp_delta_uv()}")

        sleep(1)
        print("")  # Add a blank line for readability
