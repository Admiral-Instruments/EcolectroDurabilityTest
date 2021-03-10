# Copyright (c) 2021 Admiral Instruments

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from signal import *
import asyncio
from experiment import Experiment, ExperimentError
import logging




async def main():
    logger = logging.getLogger("experiment")
    exp = Experiment()  # note, experiment.json needs to be in the current working directory!!!
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(exp.run_experiment())
        logger.info("Experiment Finished successfully")

        async def cleanup():
            await exp.stop_experiment()
        
        #for sig in (SIGABRT, SIGBREAK, SIGILL, SIGINT, SIGSEGV, SIGTERM):
        #    signal(sig, cleanup)

    except BaseException as err:
        logger.fatal(str(err) + " Aborting Experiment.")
    finally:
        loop.run_until_complete(exp.stop_experiment())


if __name__ == "__main__":
    asyncio.run(main())
