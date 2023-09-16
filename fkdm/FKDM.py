import os
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget,QPushButton,QLineEdit,QVBoxLayout,QApplication,QMainWindow,QFileDialog,QProgressBar,QStatusBar
import sys
from qtawesome import icon
import pycurl
from sys import stderr as STREAM

if __package__ is None:
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(path))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))
    
    __package__ = 'fkdm'
    import fkdm

kb = 1024


class FkdmApp(QMainWindow):


    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings("Fkdm","Fkdm")
        self.initUI()
        

    
    def initUI(self):
        self.setWindowTitle("Fkdm - Free yet simple and very fast downloader manager")
        self.setGeometry(100, 100, 600, 200)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # URL textfield
        main_layout = QVBoxLayout(main_widget)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL text...")
        main_layout.addWidget(self.url_input)
        self.save_directory_input = QLineEdit()
        self.save_directory_input.setReadOnly(True)

        self.save_directory_input.setText(self.settings.value("save_location"))
        self.save_directory_input.setPlaceholderText("Choose save location...")
        main_layout.addWidget(self.save_directory_input)

        # create a button to select save location
        browse_button = QPushButton(icon('fa.folder-open',color='black'),'Browse',self)
        browse_button.clicked.connect(self.browse_location)
        main_layout.addWidget(browse_button)

        # create a button to handle download
        download_button = QPushButton(icon("fa.download",color="black"),"Download",self)
        download_button.clicked.connect(self.download_file)
        main_layout.addWidget(download_button)

        # add progress bar
        self.progress_bar = QProgressBar(self)
        main_layout.addWidget(self.progress_bar)
        
        # status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    

    def get_valid_name(self,url):
        file_name = url.split("/")[-1]
        if '?' in file_name:
            file_name = file_name.split('?')[0]
        
        max_file_name_length = 255
        if len(file_name) > max_file_name_length:
            file_name = file_name[:max_file_name_length]
        
        return file_name
    

    def update_progress(self,total,current,_,__):
        if total > 0:
            progress = int((current/total)*100)
            self.progress_bar.setValue(progress)
            self.status_bar.showMessage(f"Downloading {progress}%")


    def browse_location(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self,"select download location",options=options)
        if folder_path:
            self.save_directory_input.setText(folder_path)

    def download_file(self):
        self.settings.setValue("save_location",self.save_directory_input.text())
        self.settings.sync()
        url = self.url_input.text()
        save_location = self.save_directory_input.text()

        if not url:
            return

        self.progress_bar.setValue(0)

        file_name = self.get_valid_name(url)
        file_path = os.path.join(save_location, file_name)

        try:
            with open(file_path, 'wb') as file:
                curl = pycurl.Curl()
                curl.setopt(curl.URL, url)
                curl.setopt(curl.WRITEDATA, file)
                curl.setopt(curl.FOLLOWLOCATION, 1)
                curl.setopt(curl.NOPROGRESS, False)
                curl.setopt(curl.XFERINFOFUNCTION, self.status_download_progress)
                curl.setopt(curl.PROGRESSFUNCTION, self.update_progress)
                curl.perform()
                curl.close()
            self.progress_bar.setValue(100)
            self.status_bar.showMessage("Download completed")
            self.url_input.setText("")
        except Exception as e:
            print(f"Error downloading file: {e}")

    def status_download_progress(self, download_t, download_d, upload_t, upload_d):
        self.status_bar.showMessage(f"Downloading {download_d} of {download_t} bytes")

    

def runApp():
    app = QApplication(sys.argv)
    fkdm = FkdmApp()
    fkdm.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    runApp()
