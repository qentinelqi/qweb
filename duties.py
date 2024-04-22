"""Run dev tasks locally"""
import sys
from platform import system
from duty import duty

python_exe = sys.executable

@duty
def format(ctx, path="QWeb"):
    """
    Automatic formatting of files
    Arguments:
        ctx: The context instance (passed automatically)
        path: path of folder/file to check
    """
    ctx.run(f"{python_exe} -m ruff format {path}", title="Autoformatting files: ruff", capture=False)

@duty
def typing(ctx, path="QWeb"):
    """
    Check code typing
    Arguments:
        ctx: The context instance (passed automatically)
        path: path of folder/file to check
    """
    ctx.run(f"{python_exe} -m mypy --show-error-codes {path}", title="Checking code typing", capture=False)

@duty
def lint(ctx, path="QWeb"):
    """
    Check code quality
    Arguments:
        ctx: The context instance (passed automatically)
        path: path of folder/file to check
    """
    ctx.run(f"{python_exe} -m ruff {path}", title="Checking code quality: ruff", capture=False)
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
def acceptance_tests(ctx,
                     browser="chrome",
                     exitonfailure="True",
                     listener=None):
    """
    Runs robot Acceptance tests
    Args:
        ctx: The context instance (passed automatically)
        browser: Browser name (use fullname instead of shorthand), [chrome, firefox, edge, safari]
                    Default: chrome
        exitonfailure: Stop tests upon first failing test. True/False
                    Default: True
        listener: Path to listener to use temporarily, for example notification purposes
                    Default: None
                          
    """
    def remove_extra_whitespaces(string: str) -> str:
        return " ".join(string.split())

    cmd_exit_on_failure = ""
    if exitonfailure.lower() == "true":
        cmd_exit_on_failure = "--exitonfailure"

    listener_cmd = ""
    if listener:
        listener_cmd = f" --listener {listener}"

    os = system().upper()
    if os == "DARWIN":
        os = "MACOS"
 
    excludes = [
        f"PROBLEM_IN_{os}",
        f"PROBLEM_IN_{browser.upper()}",
        "FLASK",
        "RESOLUTION_DEPENDENCY",
        "jailed",
        "WITH_DEBUGFILE"
    ]
    cmd_excludes = f'-e {" -e ".join(excludes)}'


    cmd_str = remove_extra_whitespaces(
               f" {python_exe} -m pabot.pabot"
               f" --ordering test/acceptance/.pabot_suite_order"
               f" --name Acceptance"
               f" {listener_cmd}"
               f" {cmd_exit_on_failure}"
               f" -v BROWSER:{browser}"
               f" {cmd_excludes}"
               f" test/acceptance"
            )
    print(cmd_str)
    ctx.run(cmd_str, title="Acceptance tests", capture=False)

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
