"""Compare-tool: impport gui classes from module dependent on toolkit
So that the main program doesn't need to know which toolkit is used
"""
from toolkit import toolkit
if toolkit == 'qt':
    from qt_gui import MainWindow, AskOpenFilesGui, ShowComparisonGui, show_dialog
elif toolkit == 'wx':
    from wx_gui import MainWindow, AskOpenFilesGui, ShowComparisonGui, show_dialog
