# 金价监控

## 安装依赖

```bash
pip3 install -r requirements.txt
```

## 启动与管理命令

```bash
# 启动服务（后台运行）
pm2 start pm2.config.json

# 查看实时日志
pm2 logs gold-monitor

# 常用命令
pm2 status               # 查看运行状态
pm2 restart gold-monitor # 重启服务
pm2 stop gold-monitor    # 停止服务
pm2 delete gold-monitor  # 移除服务
pm2 monit                # 查看资源占用
```

## 开机自启动配置

```bash
# 生成启动脚本（只需执行一次）
pm2 startup

# 保存当前进程列表
pm2 save

# 验证启动项
launchctl list | grep pm2
```

## 日志管理（自动轮转）

```bash
# 安装日志管理插件
pm2 install pm2-logrotate

# 配置日志策略（自动压缩、保留30天）
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
pm2 set pm2-logrotate:compress true
```

## 卸载步骤

```bash
pm2 delete gold-monitor
pm2 uninstall pm2-logrotate
rm -rf ~/.pm2
```
