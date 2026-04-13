from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'tb3_yolo_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # ADD THIS LINE TO INCLUDE LAUNCH FILES:
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        # ADD THIS LINE TO INCLUDE YOUR BEST.PT WEIGHTS:
        (os.path.join('share', package_name, 'weights'), glob('weights/*.pt')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='YOLOv8 Object Detection for Turtlebot3',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # ADD THIS LINE TO MAKE THE PYTHON SCRIPT EXECUTABLE:
            'yolo_node = tb3_yolo_vision.yolo_node:main'
        ],
    },
)