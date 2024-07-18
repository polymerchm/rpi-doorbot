import DoorBot.Config as Config
# template strings for services and nginx
# uses .format()

API = r"""
[Unit]
Description= Flask Based API for DoorBot System
After= network.target nginx.service \
       doorbot-doorlock.service \
       doorbot-doorswitch.service \
       doorbot-reset.service \
       doorbot-updateidcache.servive \
       doorbot-reader.service

[Service]
ExecStart= {script_path}
User= {user}
Restart= on-failure


[Install]
WantedBy=multi-user.target
"""
DOORLOCK = """
[Unit]
Description= Manage Lock for DoorBot System
After= network.target nginx.service

[Service]
ExecStart= {script_path}
User= {user}
Restart= on-failure


[Install]
WantedBy=multi-user.target
"""
DOORSWITCH = """
[Unit]
Description= Manage Doorswitch for DoorBot System
After= network.target nginx.service

[Service]
ExecStart= {script_path}
User= {user}
Restart= on-failure


[Install]
WantedBy=multi-user.target
"""
RESET = """
[Unit]
Description= Forece Factory Reset for DoorBot System
After= network.target nginx.service

[Service]
ExecStart= {script_path}
User= {user}
Restart= on-failure

[Install]
WantedBy=multi-user.target
"""

UPDATEIDCACHE = """
[Unit]
Description= Update ID Cache for DoorBot System

[Service]
ExecStart= {script_path}
User= {user}
Restart= on-failure


[Install]
"""

READER = """
[Unit]
Description= Read Fob and return status for DoorBot System
After= network.target nginx.service

[Service]
ExecStart= {script_path}
User= {user}
Restart= on-failure


[Install]
WantedBy=multi-user.target
"""

NGINX_CONF = """
server {{
    listen 80 default_server;

    server_name {server_name};
    root {root_directory};
    index index.html index.htm;
    error_log  /var/log/nginx/error.log;
    
    location / {{
      root {root_directory};
      try_files $uri  $uri/index.html =404;

    }}

    location /static {{
       root {root_directory}/DoorBot;
       try_files $uri =404;
    }}

    location /api {{
      include  proxy_params; 
      proxy_pass http://127.0.0.1:5000/api;
      proxy_set_header Connection '';
      proxy_http_version 1.1;
      chunked_transfer_encoding off;
      proxy_buffering off;
      proxy_cache off;

      if ($request_method = 'OPTIONS') {{
          add_header 'Access-Control-Allow-Origin: $http_origin');
          add_header 'Access-Control-Allow-Origin: GET, POST, DELETE, PUT, PATCH, OPTIONS');
          add_header 'Access-Control-Allow-Credentials: true');
          add_header 'Vary: Origin');

      }}


       add_header 'Access-Control-Allow-Origin' "$http_origin" always;
       add_header 'Access-Control-Allow-Credentials' 'true' always;
       add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, PATCH, DELETE, OPTIONS' always;
       add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With' always;
    }}
  }}
"""
