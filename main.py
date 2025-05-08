# -*- coding: utf-8 -*-
import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('twitter_manager.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger("Main")
    
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"应用程序崩溃: {str(e)}", exc_info=True)
        QMessageBox.critical(None, "致命错误", f"应用程序遇到错误:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()