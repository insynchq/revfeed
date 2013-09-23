from setuptools import setup
import sys


requirements = [
  'redis',
  'sockjs-tornado>=1.0,<1.1',
]

if sys.version_info < (2, 7):
  requirements.append('argparse')


if __name__ == '__main__':
  setup(
    name='revfeed',
    version='0.0.1',
    description="Dead simple commits feed",
    packages=['revfeed'],
    entry_points=dict(console_scripts=['revfeed=revfeed:main']),
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
  )
