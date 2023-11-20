class Pagination:
    def __init__(self, total_items: int, offset: int = 1, limit: int = 10):
        self.total_items = total_items
        self.offset = offset
        self.limit = limit
        self.page = self.calculate_page_number()

    @property
    def total_pages(self) -> int:
        if self.limit <= 0:
            return 1  # Default to the first page if limit is non-positive
        return -(
            -self.total_items // self.limit
        )  # Ceiling division to calculate total pages

    def calculate_page_number(self):
        if self.limit <= 0:
            return 1  # Default to the first page if limit is non-positive

        page_number = (self.offset // self.limit) + 1
        return page_number
