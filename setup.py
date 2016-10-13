from setuptools import setup, find_packages

install_requires = [
    "Django==1.10",
    "django-extensions==1.7.3",
    "eventlet==0.19.0",
    "greenlet==0.4.10",
    "gunicorn==19.4.5",
    "psycopg2==2.6.2",
    "six==1.10.0",
    "etvnet_user_api",
]


extras_require = dict(
    test=[]
)

dependency_links = [
    'http://letmein:please@pypi.etvnet.com/simple/etv_syslog/',
    'http://letmein:please@pypi.etvnet.com/simple/etvnet_user_api/',
    'http://letmein:please@pypi.etvnet.com/simple/pika/',
]

setup(
    name="mtvil.partnerstat",
    version="1.0",
    author="Matvil Corp",
    packages=find_packages("", exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requires,
    extras_require=extras_require,
    dependency_links=dependency_links,
)
