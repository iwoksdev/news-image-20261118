#!/usr/bin/env python3
"""Write the entry image to the output directory.

Copies entry.png (the image summing up 18 November 2026 world news)
to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
No network, no clock, no randomness: a plain byte-for-byte copy.
"""

import os
import shutil
import sys

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def main() -> int:
    if not os.path.isfile(SOURCE):
        print(f"error: entry image not found: {SOURCE}", file=sys.stderr)
        return 1

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if os.path.exists(output_dir) and not os.path.isdir(output_dir):
        print(f"error: output path exists and is not a directory: {output_dir}",
              file=sys.stderr)
        return 1
    os.makedirs(output_dir, exist_ok=True)

    destination = os.path.join(output_dir, "entry.png")
    shutil.copyfile(SOURCE, destination)

    # Confirm the copy landed whole before reporting success.
    if os.path.getsize(destination) != os.path.getsize(SOURCE):
        print("error: copied file size does not match entry.png",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
