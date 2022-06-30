# CL200A Controller

the library to control CL200A chroma meter/luxmeter.

All documentation can be found:

http://www.konicaminolta.com.cn/instruments/download/software/pdf/CL-200A_communication_specifications.pdf

this code is developed based on:

https://github.com/maslyankov/luxmeters-py

current code coverage can be found [here](https://github.com/MasashiSode/cl200a_controller/issues/1)

## prerequisite

the development environment are unified with pyenv and poetry. pyenv allows you to unify Python versions and poetry allows you to unify library versions.

- pyenv
- poetry

## installation

```sh
cd cl200a_controller
pip install -e .
```

## develop environment installation

```sh
cd cl200a_controller
pyenv install 3.8.10 (if needed)
make install-dev
```

## usage

connect the CL200A using USB with your computer and just run this.

```python
from time import sleep

from cl200a_controller import CL200A

if __name__ == "__main__":
    luxmeter = CL200A()

    while True:
        print(f"ev, x, y: {luxmeter.get_ev_x_y()}")
        print(f"x, y, z: {luxmeter.get_x_y_z()}")
        print(f"ev, u, v: {luxmeter.get_ev_u_v()}")
        print(f"ev, tcp, Δuv: {luxmeter.get_ev_tcp_delta_uv()}")

        sleep(1)
        print("")  # Add a blank line for readability
```

### About code formatting

This repository includes `pre-commit hooks` that automatically formats files using `black` and `isort` when you git commit. It also includes code checking with pylint.

We recommend formatting by `black` and `isort` before PR/push of the code. It is assumed that others will read the code, so if everyone can write consistent code, the work efficiency will be improved.
