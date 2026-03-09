"""Helper module that imports from sample_module — for dependency testing."""

from sample_module import DataProcessor, find_files


class CsvExporter:
    """Exports data to CSV format."""

    def __init__(self, processor):
        self.processor = processor

    def export(self, data, output_file):
        processed = self.processor.process(data)
        lines = []
        if processed:
            lines.append(','.join(processed[0].keys()))
            for item in processed:
                lines.append(','.join(str(v) for v in item.values()))
        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))


def run():
    proc = DataProcessor('/tmp')
    files = find_files('/tmp', '.csv')
    exporter = CsvExporter(proc)
    for f in files:
        data = proc.load(f.name)
        exporter.export(data, f'/tmp/out_{f.stem}.csv')
