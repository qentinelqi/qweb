import os, sys

is_gh_action = False
if (len(sys.argv) > 1) and sys.argv[1] == "--github":
    is_gh_action = True

serial_str = "{\n"
parallel_str = ""
last_parallel = ""
basename = ""
acceptance_path = None
for root, dirs, files in os.walk(os.getcwd()):
    basename = os.path.basename(root)
    if basename == "acceptance":
        acceptance_path = root
    if basename in ("serial", "parallel"):
        # invert to descending alphabetical order for shorter total exec time
        for f in files[::-1]:
            if os.path.splitext(f)[-1] != ".robot":
                continue
            name = f.split(".")[0].replace("_", " ").title()
            # pabot 5+ requires using full suite name (either original or new name) 
            # with ordering if top suite is renamed with --name
            # Because name in gh action has python version with '.' 
            # we need to use the original name
            if is_gh_action:
                name = f"{acceptance_path}.{basename.title()}.{name}"
            if basename == "serial":    
                serial_str += f"--suite {name}\n"
            else:
                parallel_str += f"--suite {name}\n"

if acceptance_path is None:
    raise OSError("Couldn't find directory: 'acceptance'")
serial_str += "}\n"

# gh runners can run out of resources
# if serial and parallel tests run concurrently
if is_gh_action:
    serial_str += f"#WAIT\n"

order_str = serial_str + parallel_str

# print the contents in gh action just in case
if is_gh_action:
    print(f"order_str:\n{order_str}")

with open(os.path.join(acceptance_path, ".pabot_order"), "w") as f:
    f.write(order_str)