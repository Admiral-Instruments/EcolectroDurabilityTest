
import asyncio
from experiment import Experiment, ExperimentError
import logging
logging.basicConfig(filename="experiment.log", level=logging.DEBUG, format="%(asctime)s %(message)s")


async def main():
    logger = logging.getLogger("experiment")
    exp = Experiment()  # note, experiment.json needs to be in the current working directory!!!
    try:
        await exp.run_experiment()
        logger.info("Experiment Finished successfully")
    except ExperimentError as err:
        logger.fatal(err)
    finally:
        await exp.stop_experiment()


if __name__ == "__main__":
    asyncio.run(main())
