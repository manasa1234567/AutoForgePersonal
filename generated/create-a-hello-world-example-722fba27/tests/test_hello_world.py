import subprocess
import sys
import os

def test_hello_world_output():
    # Run the hello_world.py script and capture its output
    result = subprocess.run([sys.executable, "hello_world.py"], capture_output=True, text=True)
    
    # The output should be exactly 'Hello World' with no trailing newline or extra spaces
    # Allowing for the typical newline after print by stripping
    output = result.stdout.strip()

    assert result.returncode == 0, f"Script exited with non-zero code {result.returncode}"
    assert output == "Hello World", f"Output was '{output}' instead of 'Hello World'"

    # No errors to stderr
    assert result.stderr == ""
