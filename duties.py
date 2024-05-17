"""Run dev tasks locally"""
import sys
import subprocess
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
    ctx.run(f"{python_exe} -m ruff check {path}", title="Checking code quality: ruff", capture=False)
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
                     parallel="True",
                     on_http_server="False",
                     suite=None,
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
    listener_cmd = ""
    if listener:
        listener_cmd = f" --listener {listener}"


    cmd_exit_on_failure = ""
    if exitonfailure.lower() == "true":
        cmd_exit_on_failure = "--exitonfailure"
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

    
    if os == "MACOS" or parallel.capitalize() == "False": 
        # on MACOS we always need to run tests in a single process
        # https://developer.apple.com/documentation/webkit/about_webdriver_for_safari#2957226
        cmd_str = f"{python_exe} -m robot"
    else:
        ctx.run(f"{python_exe} test/acceptance/pabot_suite_ordering.py", nofail=True)
        cmd_str = (
                f"{python_exe} -m pabot.pabot"
                f" --ordering test/acceptance/.pabot_order"
                f" --name Acceptance"
            )
        
    if suite is not None:
        cmd_str += f" -s {suite}"

    cmd_str += (
               f" {listener_cmd}"
               f" {cmd_exit_on_failure}"
               f" -v BROWSER:{browser}"
               f" -v ON_HTTP_SERVER:{on_http_server}"
               f" {cmd_excludes}"
               f" test/acceptance")
    print(f"Running cmd:\n{cmd_str}\n")
    if on_http_server.capitalize() == "True":
        proc = subprocess.Popen([python_exe, '-m', 'http.server', '-b', '127.0.0.1', '-d', 'test/resources', '8000'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        ctx.run(cmd_str, title="Acceptance tests", capture=False)
        proc.terminate()
    else:
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
