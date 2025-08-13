import os, sys

suite_name = ""
if (len(sys.argv) > 1):
    print(f"suite_name: {suite_name}")
    suite_name = sys.argv[1]

serial_str = "{\n"
parallel_str = ""
last_parallel = ""
acceptance_path = None
for root, dirs, files in os.walk(os.getcwd()):
    if os.path.basename(root) == "acceptance":
        acceptance_path = root
    if os.path.basename(root) in ("serial", "parallel"):
        # invert to descending alphabetical order for shorter total exec time
        for f in files[::-1]:
            if os.path.splitext(f)[-1] != ".robot":
                continue
            name = f.split(".")[0].replace("_", " ").title()
            if os.path.basename(root) == "serial":
                if suite_name:
                    serial_str += f"--suite Test.Acceptance.Serial.{name}\n"
                else:
                    serial_str += f"--suite {name}\n"
            else:
                if suite_name:
                    parallel_str += f"--suite Test.Acceptance.Parallel.{name}\n"
                else:
                    parallel_str += f"--suite {name}\n"

if acceptance_path is None:
    raise OSError("Couldn't find directory: 'acceptance'")
serial_str += "}\n"
if (len(sys.argv) > 1):
    serial_str += f"#WAIT\n"

order_str = serial_str + parallel_str

print(f"order_str:\n{order_str}")

with open(os.path.join(acceptance_path, ".pabot_order"), "w") as f:
    f.write(order_str)