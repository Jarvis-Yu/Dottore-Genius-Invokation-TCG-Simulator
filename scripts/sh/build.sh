 #!/bin/bash
if [ -d "dist" ]; then
    rm -r dist/
fi && \
./venv/bin/python scripts/py/package_file_path.py -r && \
{
    trap ctrl_c INT

    function ctrl_c() {
        echo "Build Job Canceled..."
        python scripts/py/package_file_path.py -b
        exit 1
    }

    ./venv/bin/python -m build
    ./venv/bin/python scripts/py/package_file_path.py -b
}