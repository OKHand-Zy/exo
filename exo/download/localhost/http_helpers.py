from aiohttp import web
from exo.helpers import DEBUG, terminal_link
from exo.download.localhost.http_server import app as http_app

async def start_http_servers(ips, http_app, port=52525):
  """
  在指定的IP地址上啟動HTTP服務器
  Args:
      ips (list): IP地址列表
      http_app (web.Application): aiohttp應用實例
      port (int, optional): 服務器監聽端口. 默認為 52525
  Returns:
      list: 運行器列表
  """
  runners = []
  sites = []
  try:
      if DEBUG >= 0: print(f"Local HTTP endpoint served at:")
      for ip in ips:
          runner = web.AppRunner(http_app)
          await runner.setup()
          site = web.TCPSite(runner, ip, port)
          await site.start()
          runners.append(runner)
          sites.append(site)
          http_endpoint = f"http://{ip}:{port}"
          if DEBUG >= 0: print(f" - {terminal_link(http_endpoint)}")
  except Exception as e:
      print(f"Failed to start local HTTP server on {ip}: {e}")
  
  return runners, sites

async def cleanup_http_servers(runners, sites):
  """
  優雅地關閉所有HTTP服務器
  
  Args:
      runners (list): web.AppRunner列表
      sites (list): web.TCPSite列表
  """
  # 首先停止所有站點
  for site in sites:
    try:
      await site.stop()
      if DEBUG >= 1:
        print(f"Site {site} stopped successfully")
    except Exception as e:
      print(f"Error stopping http site {site}: {e}")
  
  # 然後清理運行器
  for runner in runners:
    try:
      await runner.cleanup()
      if DEBUG >= 1:
        print(f"Runner {runner} cleaned up successfully")
    except Exception as e:
      print(f"Error cleaning up runner {runner}: {e}")
