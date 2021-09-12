# AdventOfCodeTools
## Usage
This tool should help Advent of Code participant by automating basic tasks. It runs with three scripts:
1. **Browser Add-on** (only tested with firefox). This Add-on will automatically detect which exercises are open and
fetch the necessary input. It also submits solutions through the browser.

    To install this Add-on in your browser, add  ```src/add-on/manifest.json``` as an Add-on to your browser.

2. **Server**: The server runs locally on your machine. It is necessary to set up a communication between browser and the solution script.
The server should be started **before** opening the Advent of Code exercises. This script can be called upon ```src/advent-of-code-tools.py```, where ```path``` defines the Advent of Code projects path. A directory ```template``` is expected in the project root directory, which will be copied every time a new exercise got opened.
An example can be found in ```src/adventofcode```.

    ```
    python advent-of-code-tools.py server [path]
    ```
   
    Paths within the project can be configured in ```src/config ```

3. **Script runner**: This script runs your solutions. If all your test cases match, you can automatically submit your
solution to Advent of Code's website from the console (which happens through the local server mentioned before).
     
    ```
    python advent-of-code-tools.py run [path] [year] [day] -- [command]
    ```

    Note:  ```command``` is being executed within the ```part-1``` or ```part-2``` directory. If you choose to code in Python
    for example, the value of ```command``` would be  ```python -u main.py```. The  ```-u``` parameter is necessary to force stdout to be unbuffered.
    Only the last row of the scripts std output will be recognized as the exercise's solution.
    
    ```
    python advent-of-code-tools.py run [path] [year] [day] -- python -u main.py
    ```
    
    Example inputs and outputs can be found in the ```examples``` directory. This can be changed in ```src/config```.
