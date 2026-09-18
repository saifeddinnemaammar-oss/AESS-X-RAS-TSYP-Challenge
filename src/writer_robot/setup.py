from setuptools import setup

package_name = 'writer_robot'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Team',
    maintainer_email='team@example.com',
    description='Writer robot',
    license='MIT',
    entry_points={
        'console_scripts': [
            'explorer = writer_robot.explorer:main',
            'event_detector = writer_robot.event_detector:main',
            'beacon_dropper = writer_robot.beacon_dropper:main',
        ],
    },
)
