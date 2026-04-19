import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def get_authenticator():
    config = {
        'credentials': {
            'usernames': {
                'admin': {
                    'email': 'admin@example.com',
                    'name': 'Admin',
                    'password': '$2b$12$tMDHCr4rOHbCMHJBDalcXOXMo1sFBm7vVsKM3l3XVZlPBJwVBMiKy'
                },
                'kullanici': {
                    'email': 'kullanici@example.com',
                    'name': 'Kullanıcı',
                    'password': '$2b$12$tMDHCr4rOHbCMHJBDalcXOXMo1sFBm7vVsKM3l3XVZlPBJwVBMiKy'
                }
            }
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'akademik_asistan_key',
            'name': 'akademik_asistan_cookie'
        },
        'pre-authorized': {
            'emails': []
        }
    }

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )
    return authenticator