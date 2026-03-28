import requests, csv, os, json, subprocess, getpass, sys, base64
from urllib.parse import quote

# --- 基础配置 ---
EXE_NAME = "cfst.exe"
CONFIG_FILE = "config.txt"
CSV_FILE = "result.csv"
SPEED_URL = "https://speed.cloudflare.com/__down?bytes=99999999"

# --- 订阅转换与短链配置 ---
CONVERTER_API = "https://subapi.dayutian.com/sub"
CONFIG_TEMPLATE = "https://raw.githubusercontent.com/cutethotw/ClashRule/main/GeneralClashRule.ini"
SHORTENER_API = "https://suo.yt/short"

def get_config():
    """获取并缓存域名、Token 和密码"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                c = json.load(f)
                # 显示当前记忆的配置
                print(f"\n✨ 当前配置:")
                print(f"   域名: {c.get('domain')}")
                print(f"   Token: {c.get('token')}")
                
                if input("\n按回车继续，重新输入配置按 [N]: ").strip().upper() != 'N':
                    return c['domain'], c['token'], c['password']
        except:
            pass

    print("\n" + "=="*10 + " 身份初始化 " + "=="*10)
    domain = input("1. 输入你的上传域名 (例如 xxx.workers.dev): ").strip()
    # 自动处理用户输入可能带有的 http 前缀
    domain = domain.replace("https://", "").replace("http://", "").strip("/")
    
    token = input("2. 输入你的专属 Token: ").strip()
    print("3. 输入管理员密码 (输入时不显示): ", end="", flush=True)
    password = getpass.getpass("")
    
    config_data = {"domain": domain, "token": token, "password": password}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    
    return domain, token, password

def run_cfst():
    """执行优选测速"""
    if not os.path.exists(EXE_NAME):
        print(f"\n❌ 错误：在当前目录下找不到 {EXE_NAME}"); return False

    print("\n" + "="*10 + " 优选参数设置 " + "="*10)
    ipt = input("1. 类型: [1]IPv4 [2]IPv6 (默认1): ") or "1"
    f_path = "ipv6.txt" if ipt == "2" else "ip.txt"
    
    if not os.path.exists(f_path):
        with open(f_path, "w") as f: f.write("104.16.0.0/16" if ipt == "1" else "2606:4700::/32")

    threads = input("2. 线程数 -n (默认 200): ") or "200"
    tl_ms = input("3. 延迟上限 ms -tl (默认 350): ") or "350"
    sl_mb = input("4. 速度下限 MB/s -sl (默认 1): ") or "1"
    dn_count = input("5. 结果数量 -dn (默认 10): ") or "10"

    cmd = [EXE_NAME, "-f", f_path, "-url", SPEED_URL, "-n", threads, "-tl", tl_ms, "-sl", sl_mb, "-dn", dn_count, "-o", CSV_FILE]
    print(f"\n🚀 启动优选测速...\n")
    try:
        subprocess.run(cmd)
        return True
    except: return False

def main():
    domain, token, password = get_config()
    if not run_cfst(): return

    # 读取测速结果
    ips = []
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, encoding='utf-8-sig') as f:
                reader = csv.reader(f); next(reader, None)
                for row in reader:
                    if row: ips.append(row[0].strip())
        except: pass

    if not ips:
        print("\n💡 未找到符合条件的 IP。"); input(); return

    # 1. 同步 IP 到指定的 Worker 域名
    print(f"\n📡 正在同步到 {domain}...")
    try:
        r = requests.post(f"https://{domain}/update-ip?token={token}", 
                          json={"password": password, "ips": ips}, timeout=15)
        
        if r.status_code == 200:
            # 2. 构造基础订阅链接
            base_sub_url = f"https://{domain}/?token={token}"
            
            # 3. 构造 Clash 完整转换长链接
            clash_long_url = (
                f"{CONVERTER_API}?target=clash&new_name=true"
                f"&url={quote(base_sub_url, safe='')}"
                f"&insert=false&config={quote(CONFIG_TEMPLATE, safe='')}"
                f"&emoji=true&list=false&xudp=false&udp=false&tfo=false&expand=true&scv=false&fdn=false"
            )
            
            # 4. 生成 suo.yt 短链接
            print("🔗 正在请求 suo.yt 生成短链接...")
            clash_short_url = "短链生成失败"
            try:
                b64_long_url = base64.b64encode(clash_long_url.encode('utf-8')).decode('utf-8')
                payload = {"longUrl": b64_long_url, "shortKey": ""}
                headers = {
                    'User-Agent': 'Mozilla/5.0',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Referer': 'https://suo.yt/'
                }
                short_res = requests.post(SHORTENER_API, data=payload, headers=headers, timeout=10)
                if short_res.status_code == 200:
                    res_json = short_res.json()
                    if res_json.get("Code") == 1:
                        clash_short_url = res_json.get("ShortUrl")
            except:
                pass

            # 最终展示输出
            print("\n" + "🎉" + "=="*25 + "🎉")
            print(f"✅ 【同步与转换成功】")
            
            print(f"\n1️⃣  通用订阅地址 (V2Ray/Base64):")
            print(f"\033[1;36m{base_sub_url}\033[0m")
            
            print(f"\n2️⃣  Clash 专用短链接 (suo.yt):")
            print(f"\033[1;32m{clash_short_url}\033[0m")

            print(f"\n3️⃣  Clash 转换长链接 (备份用):")
            print(f"{clash_long_url}")
            
            print("\n" + "🎉" + "=="*25 + "🎉")
            print(f"提示：当前数据已同步至域名: {domain}")
            
        else:
            print(f"\n❌ 同步失败，域名或 Token 有误: {r.text}")
    except Exception as e:
        print(f"\n⚠️ 网络错误: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断运行。")
    except Exception as e:
        print(f"\n致命错误: {e}")
    
    print("\n" + "-"*50)
    input("执行完毕，按回车键退出脚本...")