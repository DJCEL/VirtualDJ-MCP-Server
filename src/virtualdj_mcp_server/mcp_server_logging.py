import logging
from typing import Literal
import os

from .mcp_server_config import MCP_SERVER_DEBUG, MCP_SERVER_LOG_FOLDER, MCP_SERVER_LOG_FILENAME

def configure_mcp_server_log(level: Literal["DEBUG","INFO","WARNING","ERROR","CRITICAL"] = "INFO") -> None:
            filepath = f"{MCP_SERVER_LOG_FOLDER}/{MCP_SERVER_LOG_FILENAME}"
            if not os.path.exists(MCP_SERVER_LOG_FOLDER):
                os.makedirs(MCP_SERVER_LOG_FOLDER)
            
            FORMAT = '%(asctime)s - %(message)s'
            handlers = list[logging.Handler] = []
            
            file_handler = logging.FileHander(filename=filepath)
            file_handler.setLevel(level)
            formatter = logging.Formatter(FORMAT)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
            
            if not handlers:
               handlers.append(logging.StreamHandler())

            logging.basicConfig(filename=filepath, level=level, format=FORMAT)

            #logging.basicConfig(level=level, format=FORMAT, handlers=handlers)
#------------------------------------------------------------------------------------
def get_mcp_server_log(name: str) -> logging.Logger:
        return logging.getLogger(str)
#------------------------------------------------------------------------------------
def save_mcp_server_log(msg: str, level: Literal["DEBUG","INFO","WARNING","ERROR","CRITICAL"] = "INFO", logger: logging.Logger = None, name: str = "__name__") -> None:
        if MCP_SERVER_DEBUG == False:
            return
        
        if logger is None:
            logger = get_client_log(name)

        if level == logging.INFO:
            logger.info(msg)
#------------------------------------------------------------------------------------
def close_mcp_server_log():
        logging.shutdown()