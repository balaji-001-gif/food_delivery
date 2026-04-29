from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

from food_delivery import __version__ as version

setup(
    name="food_delivery",
    version=version,
    description="Food Delivery Application like Swiggy built on Frappe/ERPNext",
    author="Your Company",
    author_email="admin@yourcompany.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
