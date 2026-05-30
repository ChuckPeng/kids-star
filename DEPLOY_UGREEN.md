# Kids-Star 绿联云部署指南

## 前提

绿联云需开启 SSH（设置 → 网络服务 → SSH），已安装 Docker。

## 快速部署

### 1. SSH 登录绿联云

```bash
ssh root@<你的绿联云IP>
```

### 2. 创建目录并下载文件

```bash
mkdir -p /volume1/docker/kids-star && cd /volume1/docker/kids-star

# 下载 docker-compose.prod.yml
wget https://raw.githubusercontent.com/ChuckPeng/kids-star/main/docker-compose.prod.yml

# 创建 .env 配置
cat > .env << 'EOF'
POSTGRES_DB=kids_star
POSTGRES_USER=kids_star
POSTGRES_PASSWORD=改成一个强密码
SECRET_KEY=改成一个随机字符串至少32位
EOF
```

### 3. 拉取镜像并启动

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### 4. 检查运行状态

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs app
```

### 5. 访问

浏览器打开 `http://<绿联云IP>` 即可访问 Kids-Star

---

## 更新

```bash
cd /volume1/docker/kids-star
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## 备用：U盘导入（无外网）

如果绿联云无法访问 GitHub，下载以下文件到 U 盘插入绿联云：

1. `docker-compose.prod.yml`
2. `.env`

然后在绿联云 Docker 应用中手动导入 compose 文件启动。
