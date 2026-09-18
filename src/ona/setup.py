from setuptools import setup

package_name = 'ona'

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
    description='Outside Network Area',
    license='MIT',
    entry_points={
        'console_scripts': [
            'receiver = ona.receiver:main',
            'translator = ona.translator:main',
            'uplink = ona.uplink:main',
            'briefer = ona.briefer:main',
        ],
    },
)
