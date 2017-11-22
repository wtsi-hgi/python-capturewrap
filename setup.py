from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="capturewrap",
    version="1.0.1",
    packages=find_packages(exclude=["tests"]),
    url="https://github.com/wtsi-hgi/python-capturewrap",
    license="MIT",
    description="Wraps callables to capture stdout, stderr, exceptions and the return",
    long_description=read_markdown("README.md"),
    zip_safe=True
)
