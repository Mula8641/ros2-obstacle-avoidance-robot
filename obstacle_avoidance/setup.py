from glob import glob

from setuptools import find_packages, setup

package_name = "obstacle_avoidance"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.py")),
        ("share/" + package_name + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Muhammad Ali Lari",
    maintainer_email="202020144+Mula8641@users.noreply.github.com",
    description="FSM obstacle avoidance for TurtleBot3",
    license="MIT",
    entry_points={
        "console_scripts": [
            "avoidance_node = obstacle_avoidance.nodes.avoidance_node:main",
            "run_monitor = obstacle_avoidance.nodes.run_monitor:main",
        ],
    },
)
