import os
from glob import glob
from setuptools import setup

package_name = 'core'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='AESS-X-RAS',
    maintainer_email='robotics@team.com',
    description='ROS 2 package for The Living Map Writer Robot',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'odom_bridge = living_map_core.odom_bridge:main'
        ],
    },
)