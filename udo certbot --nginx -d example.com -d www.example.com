[0;1;32m●[0m nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (]8;;file://lamponubuntu4004/usr/lib/systemd/system/nginx.service/usr/lib/systemd/system/nginx.service]8;;; [0;1;32menabled[0m; preset: [0;1;32menabled[0m)
     Active: [0;1;32mactive (running)[0m since Sun 2025-03-23 20:15:00 UTC; 2s ago
       Docs: ]8;;man:nginx(8)man:nginx(8)]8;;
    Process: 389276 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
    Process: 389278 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
   Main PID: 389279 (nginx)
      Tasks: 2 (limit: 1110)
     Memory: 3.0M (peak: 3.1M)
        CPU: 27ms
     CGroup: /system.slice/nginx.service
             ├─[0;38;5;245m389279 "nginx: master process /usr/sbin/nginx -g daemon on; master_process on;"[0m
             └─[0;38;5;245m389280 "nginx: worker process"[0m

Mar 23 20:15:00 lamponubuntu4004 systemd[1]: Starting nginx.service - A high performance web server and a reverse proxy server...
Mar 23 20:15:00 lamponubuntu4004 systemd[1]: Started nginx.service - A high performance web server and a reverse proxy server.
