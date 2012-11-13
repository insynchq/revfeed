from setuptools import setup
import os.path


requirements_path = os.path.join(os.path.dirname("requirements.txt"),
                                 'requirements.txt')
with open(requirements_path) as f:
    install_requires = f.readlines()

setup(
    name='revfeed',
    version='0.0.0',
    packages=['revfeed'],
    author="Mark Steve Samson",
    author_email="hello@marksteve.com",
    description="Watch your commits in style",
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'revfeed_update_db=revfeed:update_db',
            'revfeed_run_server=revfeed:run_server',
            ],
        },
    include_package_data=True,
    zip_safe=False,
    )
