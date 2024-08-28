import time
from tqdm import tqdm

# sleepWithLog delay execution for a given number of seconds.
def sleepWithLog(duration: float) -> None:
    update_frequency = 0.1
    for _ in tqdm(range(int(duration/update_frequency))):
        time.sleep(update_frequency)
