# Sudoku-Solver
An automatic solver for the mobile game [Sudoku - The Clean One](https://play.google.com/store/apps/details?id=ee.dustland.android.dustlandsudoku).
   
It reads the sudoku and send touches through the [ppadb library](https://pypi.org/project/pure-python-adb/) and processes the image using [OpenCv](https://pypi.org/project/opencv-python/)'s [pattern recognition](https://docs.opencv.org/master/d4/dc6/tutorial_py_template_matching.html).
   
If you want to use it on your phone you will need to adapt the main file (sudoku.py) to match the size of your screen (Maybe the numbers images too).