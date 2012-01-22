from setuptools import setup, find_packages

setup(name="nvda_update_ws",
    author="Rui Batista",
    author_email="ruiandrebatista@gmail.com",
    packages=find_packages(),
    install_requires=["web.py", "elixir"])
