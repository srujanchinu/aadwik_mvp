import os,json,subprocess,shutil
from pathlib import Path
BLENDER_EXE=Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
FFMPEG_EXE=Path(r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffmpeg.exe")
FFPROBE_EXE=Path(r"C:\ffmpeg-n9.0-latest-win64-gpl-9.0\bin\ffprobe.exe")
BASE=Path(__file__).resolve().parent; SCENE_SCRIPT=BASE/'aadwik_blender_scene.py'
class LocalVideoProvider:
 def generate_video(self,prompt,output_path,aspect_ratio='16:9',style=None,**kwargs):
  out=Path(output_path); work=out.parent/(out.stem+'_v6'); frames=work/'rendered_frames'
  if work.exists(): shutil.rmtree(work)
  frames.mkdir(parents=True,exist_ok=True)
  plan = {
   'title': kwargs.get('title', 'Aadwik Production'),
   'prompt': prompt,
   'scenes': kwargs.get('scenes') or [
    {
     'location': 'forest',
     'emotion': 'curious',
     'action': prompt
    }
   ]
  }
  plan_path=work/'production_plan.json'; plan_path.write_text(json.dumps(plan,indent=2),encoding='utf-8')
  width,height=(640,360) if aspect_ratio=='16:9' else (360,640); fps=int(kwargs.get('fps',8))
  duration = float(kwargs.get("duration_minutes", 1))
  cmd=[str(BLENDER_EXE),'-b','-P',str(SCENE_SCRIPT),'--','--plan',str(plan_path),'--out',str(frames),'--width',str(width),'--height',str(height),'--fps',str(fps),'--duration',str(duration)]
  r=subprocess.run(cmd,cwd=str(BASE),capture_output=True,text=True,timeout=1800); print(r.stdout); print(r.stderr or '')
  if r.returncode!=0: raise RuntimeError('Blender failed:\n'+r.stderr[-7000:])
  pngs=sorted(frames.glob('frame_*.png'))
  if not pngs: raise RuntimeError('V6 connected 3D route produced no PNG frames.')
  norm=work/'sequence'; norm.mkdir()
  for i,p in enumerate(pngs,1): shutil.copy2(p,norm/f'frame_{i:06d}.png')
  ff=[str(FFMPEG_EXE),'-y','-framerate',str(fps),'-i',str(norm/'frame_%06d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
  q=subprocess.run(ff,capture_output=True,text=True,timeout=900)
  if q.returncode!=0: raise RuntimeError('FFmpeg failed:\n'+q.stderr[-5000:])
  probe=subprocess.run([str(FFPROBE_EXE),'-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,duration','-of','json',str(out)],capture_output=True,text=True)
  if probe.returncode!=0: raise RuntimeError('FFprobe validation failed.')
  data=json.loads(probe.stdout); streams=data.get('streams',[])
  if not streams: raise RuntimeError('Final MP4 has no video stream.')
  print(f'[AADWIK V6] MP4: {out} | frames={len(pngs)} | fps={fps} | {width}x{height}')
  return str(out)
local_video_provider=LocalVideoProvider(); video_provider=local_video_provider; VideoProvider=LocalVideoProvider


