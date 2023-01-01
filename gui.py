from toolkit import toolkit
if toolkit == 'qt':
    from qt_gui_new import MainWindow, AskOpenFilesGui, ShowComparisonGui, show_dialog
elif toolkit == 'wx':
    from wx_gui_new import MainWindow, AskOpenFilesGui, ShowComparisonGui, show_dialog
