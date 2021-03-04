class Table:
    def __init__(self, header, rows):
        self.header = header
        self.rows = rows

    def to_dict(self):
        return {
            'header': self.header,
            'rows': self.rows,
        }
