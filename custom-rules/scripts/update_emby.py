import re

def generate_loon_rules():
    try:
        with open('urls.txt', 'r') as f:
            content = f.read()

        # 正则提取域名，支持带端口的情况
        # 匹配 http(s):// 之后到第一个 / 或 : 之前的字符
        domains = re.findall(r'https?://([^:/ \n\r]+)', content)

        # 去重并排序
        unique_domains = sorted(list(set(domains)))

        with open('Emby.lsr', 'w', encoding='utf-8') as f:
            f.write("# Emby Rules for Loon\n")
            f.write("# Generated from urls.txt\n\n")
            for domain in unique_domains:
                if domain:
                    # 逻辑：如果只有一级子域名(如 a.com)，用 DOMAIN-SUFFIX
                    # 如果是多级子域名(如 a.b.com)，用 DOMAIN
                    if domain.count('.') > 1:
                        f.write(f"DOMAIN,{domain}\n")
                    else:
                        f.write(f"DOMAIN-SUFFIX,{domain}\n")
        print("Successfully updated Emby.lsr")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_loon_rules()
