from aiohttp import web
import os
from pathlib import Path
from datetime import datetime

routes = web.RouteTableDef()
CACHE_DIR = os.path.expanduser('~/.cache/exo')
Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

@routes.get('/files/{filename}')
async def download_file(request):
  filename = request.match_info['filename']
  file_path = os.path.join(CACHE_DIR, filename)
  
  if not os.path.exists(file_path):
      return web.json_response({"error": "File not found"}, status=404)
  
  return web.FileResponse(file_path)

@routes.get('/files')
async def list_files(request):
  files = []
  for entry in os.scandir(CACHE_DIR):
      if entry.is_file():
          stat = entry.stat()
          files.append({
              'name': entry.name,
              'size': stat.st_size,
              'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
          })
  return web.json_response({'files': files})

@routes.get('/models')
async def list_folders(request):
  """列出所有可用資料夾"""
  folders = []
  for entry in os.scandir(CACHE_DIR):
      if entry.is_dir() and not entry.name.startswith('.'):
          folder_size = sum(
              f.stat().st_size for f in Path(entry.path).rglob('*') if f.is_file()
          )
          folders.append({
              'name': entry.name,
              'size': folder_size,
              'modified': datetime.fromtimestamp(entry.stat().st_mtime).isoformat()
          })
  return web.json_response({'models': folders})

@routes.get('/models/{foldername}/files')
async def list_folder_files(request):
  """列出資料夾內所有檔案"""
  foldername = request.match_info['foldername']
  folder_path = os.path.join(CACHE_DIR, foldername)
  
  if not os.path.exists(folder_path):
      return web.json_response({"error": "Folder not found"}, status=404)
      
  if not os.path.isdir(folder_path):
      return web.json_response({"error": "Not a valid folder"}, status=400)

  files = []
  for root, dirs, filenames in os.walk(folder_path):
      # Skip hidden directories
      dirs[:] = [d for d in dirs if not d.startswith('.')]
      # Skip hidden files
      for filename in filenames:
          if filename.startswith('.'):
              continue
          file_path = os.path.join(root, filename)
          rel_path = os.path.relpath(file_path, folder_path)
          files.append({
              'name': rel_path,
              'size': os.path.getsize(file_path),
              'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
          })
  
  return web.json_response({'files': files})

app = web.Application()
app.add_routes(routes)