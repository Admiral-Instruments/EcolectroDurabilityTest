from experiment import Experiment

import asyncio

async def main():
    test = Experiment()
    await test.run_experiment()

if __name__ == "__main__":
    asyncio.run(main())
