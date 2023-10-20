 #!/bin/bash
rm -r dist/ && \
python scripts/py/package_file_path.py -r && \
{
    ./venv/bin/python -m build
    python scripts/py/package_file_path.py -b
}