import asyncio
import time
import warnings

'''
    GLOBAL DEFINITIONS
'''
TICK_FREQUENCY = 20 # Ticks per second

async def tick():
    # Record initial time before code execution
    time_initial = time.time()

    '''
        BEGIN MAIN THREAD
    '''

    for i in range(9999999):
        pass

    # Record time after code execution and compare difference to ticks.
    time_post = time.time()
    time_difference = time_post - time_initial
    if time_difference < (1/TICK_FREQUENCY):
        time.sleep((1/TICK_FREQUENCY) - time_difference) # pause execution until the tick is done
    else:
        warnings.warn(f'Couldn\'t keep up! Running {time_difference} behind expected interval of {TICK_FREQUENCY} ticks per second.', RuntimeWarning)
    

async def main():
    while True:
        print('owo')
        await tick()

asyncio.run(main())


