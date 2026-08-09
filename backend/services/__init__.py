def __init__(self) -> None:
    """
    Initialize the Market Data Service.
    """

    self.logger = get_logger(self.__class__.__name__)

    self.output_directory = Path("data/raw/stocks")

    self.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )