import yaml
import logging
import sys
import base64

def load_config(config_path):
    """安全加载配置文件"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            logging.info(f"Loaded config from {config_path}")
            return config
    except Exception as e:
        logging.critical(f"Config load failed: {str(e)}")
        sys.exit(1)


def get_base64_credentials(app_id: str, app_secret: str):
    """生成 Base64 编码的认证信息"""
    credentials = f"{app_id}:{app_secret}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()
    return base64_credentials

