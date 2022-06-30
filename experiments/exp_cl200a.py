from time import sleep

from cl200a_controller import CL200A

if __name__ == "__main__":
    luxmeter = CL200A(debug=True)

    while True:
        print(f"ev, x, y: {luxmeter.get_ev_x_y()}")
        print(f"x, y, z: {luxmeter.get_x_y_z()}")
        print(f"ev, u, v: {luxmeter.get_ev_u_v()}")
        print(f"ev, tcp, Δuv: {luxmeter.get_ev_tcp_delta_uv()}")

        sleep(1)
        print("")  # Add a blank line for readability
