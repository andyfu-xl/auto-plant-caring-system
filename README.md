# System design project (8-person group)
SDP Group 20 robotics project, onboard software. For web api see repo [here](https://github.com/v-raja/power-plant-api-web).

## Project Plan

- link to general overview docs here
- [Movement](./docs/robot_movement.md)
- link to robot state docs here
- link to main managment algorithm docs here

## Working on the Project

### Dependencies
Python package dependencies are (should be at least) listed in requirements.txt
To install all listed dependencies run: 'python -m pip install -r requirements.txt'
        

### Testing

To run unit tests run pytest from the root directory with:
    'pytest'
    
### Linting

To check the code with pylint run: 'python -m pylint {file name}'
Pylint cao lint all python files run: pylint $(git ls-files '*.py') --fail-under=8
