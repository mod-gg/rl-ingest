import logging
import dlt
import argparse
from octanegg import Octane

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class OctaneLoader:
    """
    class to retrieve rocket league games based on a set of inputs and load them into a database
    """

    def __init__(self):
        pass

    def extract(self, **kwargs):
        """
        extracts rlcs games from the octane client and brings them into a python object
        kwargs are the arguments passed into the command line to select specific games to extract
        we `yield` from this function to create a generator according to dlt best practices
        """
        with Octane() as client:
            page = 1
            try:
                while True:
                    logging.info(f"Retrieving page {page}")
                    current_page_games = client.get_games(**kwargs, page=page)
                    if not current_page_games:  # no more games
                        break
                    yield current_page_games
                    page += 1
            except Exception:
                logging.error("Exception occurred", exc_info=True)

        logging.info("Games Obtained")

    def load(self, source_octane_games):
        """
        creates a dlt pipeline to take the nested json files and return a suite of tables in the db
        db credentials are stored in local config TODO: move into github secrets
        """
        dlt_pipeline = dlt.pipeline(
            pipeline_name="rocket-league-pipeline",
            dataset_name="rocket-league",
            destination="postgres",
            # full_refresh=True, # only use this to create one-off schemas
        )
        try:
            dlt_pipeline.run(
                source_octane_games,
                table_name="source_octane_games",
                write_disposition="replace",
            )
        except Exception:
            logging.error("Exception occurred", exc_info=True)
        logging.info("Load Complete")

    def run(self, **kwargs):
        source_octane_games = self.extract(**kwargs)
        self.load(source_octane_games)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", type=str)
    parser.add_argument("--after", type=str)
    parser.add_argument("--before", type=str)
    args = parser.parse_args()
    logging.info(f"Retrieving games with arguments {vars(args)}")
    octane_loader = OctaneLoader()
    octane_loader.run(**vars(args))
