"""Run dev tasks locally"""
import sys
from duty import duty

python_exe = sys.executable

@duty
def lint(ctx, path="QWeb"):
    """
    Check code quality
    Arguments:
        ctx: The context instance (passed automatically)
        path: path of folder/file to check
    """
    ctx.run(f"{python_exe} -m flake8 {path}", title="Checking code quality: flake8", capture=False)
    ctx.run(f"{python_exe} -m pylint {path}", title="Checking code quality: pylint", capture=False)


@duty
def unit_tests(ctx):
    """
    Runs unit tests
    Args:
        ctx: The context instance (passed automatically)
    """
    ctx.run([f"{python_exe}", "-m", "pytest", "-v", "--junit-xml", "unittests.xml","--cov", "QWeb"], title="Unit tests", capture=False)

@duty
def acceptance_tests(ctx, browser="chrome"):
    """
    Runs robot Acceptance tests
    Args:
        ctx: The context instance (passed automatically)
        browser: browser name [chrome (default), gc, firefox, ff]
    """
    ctx.run(f"{python_exe} -m robot -v BROWSER:{browser} --exitonfailure -e jailed -e PROBLEM_IN_WINDOWS -e FLASK "
            "-e WITH_DEBUGFILE -e PROBLEM_IN_FIREFOX -e PROBLEM_IN_MACOS -e RESOLUTION_DEPENDENCY test/Acceptance",
            title="Acceptance tests", capture=False)

@duty
def kw_docs(ctx):
    """
    Generates updated keyword docs
    Args:
        ctx: The context instance (passed automatically)
    """
    ctx.run([f"{python_exe}", "-m", "robot.libdoc", "-F", "REST", "QWeb", "./docs/QWeb.html"], title="Generating keyword documentation")

@duty
def create_dist(ctx):
    """
    Creates distribution packages
    Args:
        ctx: The context instance (passed automatically)
    """
    ctx.run(f"{python_exe} setup.py sdist bdist_wheel", title="Creating packages to ./dist", capture=False)
