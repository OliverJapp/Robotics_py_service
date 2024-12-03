from setuptools import find_packages, setup

package_name = 'py_service'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chaos08',
    maintainer_email='u22jt21@abdn.ac.uk',
    description='Service client',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'World = py_service.World:main',
            'hive = py_service.hive:main',
            'client = py_service.shipment:main',
            'delivery = py_service.delivery:main',
            'taxi = py_service.taxi:main',
            'claw = py_service.claw:main',
        ],
    },
)
