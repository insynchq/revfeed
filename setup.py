from setuptools import setup

requirements = [
  'redis',
  'sockjs-tornado>=1.0,<1.1',
]


if __name__ == '__main__':
  setup(
    name='revfeed',
    version='0.0.1',
    description="Dead simple commits feed for Mercurial repos",
    packages=['revfeed'],
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
  )
