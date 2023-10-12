
qlineEditSyles = """
    QLineEdit {
        padding: 6px;
    }
    QLineEdit[readOnly="true"] {
        background-color: #fff;

    }
    
"""

qPushButtonStyles = """
    QPushButton {
        padding: 10px;
        text-transform: uppercase;
    }

    QPushButton:hover {
        color: white;
        background-color:black;
    }


"""

qProgressBarStyles = """
    QProgressBar {
        border: 1px solid #000;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #000;
        width: 10px;
    }
"""


global_styles = """
    {qlineEditSyles}
    {qPushButtonStyles}
    {qProgressBarStyles}
""".format(qlineEditSyles=qlineEditSyles,qPushButtonStyles=qPushButtonStyles,qProgressBarStyles=qProgressBarStyles)