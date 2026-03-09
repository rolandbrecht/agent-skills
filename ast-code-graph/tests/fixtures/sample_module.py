"""Sample Python module for testing build-graph.py."""

import os
import json
from pathlib import Path


class DataProcessor:
    """Processes data files."""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)

    def load(self, filename):
        filepath = self.base_dir / filename
        with open(filepath) as f:
            return json.load(f)

    def process(self, data):
        return [self.transform(item) for item in data]

    def transform(self, item):
        return {k: v.strip() if isinstance(v, str) else v for k, v in item.items()}


class DataExporter(DataProcessor):
    """Exports processed data."""

    def export(self, data, output_file):
        processed = self.process(data)
        with open(output_file, 'w') as f:
            json.dump(processed, f, indent=2)


def find_files(directory, extension='.json'):
    """Find all files with a given extension."""
    return list(Path(directory).rglob(f'*{extension}'))


def main():
    processor = DataProcessor('/tmp/data')
    files = find_files('/tmp/data')
    for f in files:
        data = processor.load(f.name)
        result = processor.process(data)
        print(f'Processed {len(result)} items from {f.name}')


if __name__ == '__main__':
    main()
