import os
import typing
from PyQt5 import QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget,QPushButton,QLineEdit,QVBoxLayout,QApplication,QMainWindow,QFileDialog,QProgressBar,QStatusBar,QDialog
import sys
from qtawesome import icon
import pycurl
import io
from fkdm.config.styles import global_styles
from fkdm.dialogs.settings import SettingsDialog
from io import BytesIO
from fkdm.config import settings

kb = 1024

pycurl_custom_headers = [
    f"User-Agent: {settings.DEFAULT_USER_AGENT}",
]


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
        self.setStyleSheet(global_styles)
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
    

    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.show()

    def get_valid_name(self,url):
        file_name = url.split("/")[-1]
        if '?' in file_name:
            file_name = file_name.split('?')[0]
        
        max_file_name_length = 255
        if len(file_name) > max_file_name_length:
            file_name = file_name[:max_file_name_length]
        
        return file_name
    


    def progress_callback(self,download_total, downloaded, upload_total, uploaded):
        
        if downloaded == download_total:
            print("Download is 100% complete")
        
        print(downloaded,download_total)
        return 0


    def browse_location(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self,"select download location",options=options)
        if folder_path:
            self.save_directory_input.setText(folder_path)

    def download_file(self):
        print("Download button clicked")
        self.settings.setValue("save_location",self.save_directory_input.text())
        self.settings.sync()
        url = self.url_input.text()
        save_location = self.save_directory_input.text()
        buffer = BytesIO()
        if not url:
            return

        self.progress_bar.setValue(0)

        file_name = self.get_valid_name(url)
        file_path = os.path.join(save_location, file_name)
        
        try:
            
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.PROGRESSFUNCTION, self.progress_callback)
            curl.setopt(pycurl.XFERINFOFUNCTION, self.status_download_progress)
            curl.setopt(pycurl.FOLLOWLOCATION, True)
            curl.setopt(pycurl.NOPROGRESS, 0)
            with open(file_path, 'wb') as file:
                curl.setopt(pycurl.WRITEFUNCTION, file.write)
                curl.setopt(pycurl.HTTPHEADER, pycurl_custom_headers)
                curl.perform()
                print('Status: %d' % curl.getinfo(curl.RESPONSE_CODE))

            curl.close()
                
                
            print(f"Downloaded file to '{file_path}' successfully.")
        except Exception as e:
            print(f"Error downloading file: {e}")


    def status_download_progress(self, download_t, download_d, upload_t, upload_d):
        #print(f"Downloaded {download_d} of {download_t} bytes")
        self.status_bar.showMessage(f"Downloading {round(download_d/kb,1)} kb of {download_t} bytes")



    
    
    

def runApp():
    app = QApplication(sys.argv)
    fkdm = FkdmApp()
    fkdm.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    runApp()
