from setuptools import setup, find_namespace_packages

with open("README.md", "r") as f:
    long_description = f.read()
with open("requirements.txt") as f:
    requirements = f.read().splitlines()
setup(
    name="MemoMind",
    version="1.0.0",
    author="Code Cobras",
    author_email="camyray1992@gmail.com",
    description="Personal Assistant Bot",
    long_description=long_description,
    packages=find_namespace_packages(),
    url="https://github.com/BonesetterB/Team_Project_bot.git"
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6<=3.10.5'
    install_requires=requirements,
    entry_points={'console_scripts': ['memo = memomind.main:main']}
)
