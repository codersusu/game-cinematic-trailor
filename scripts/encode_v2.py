"""Encode complete Cycles frames with sound and readable title/attribution overlays.

Use --prepare-overlays to inspect graphics without starting a movie encode.
Use --dry-run to validate frame completeness and print the planned output.
"""
from pathlib import Path
import argparse
import os
import json
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/python'))
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

CREDIT = ('Character: Rain Rig (CC-BY 4.0), Blender Foundation, '
          'https://studio.blender.org/characters/rain/v3/ . '
          'License: https://creativecommons.org/licenses/by/4.0/ . '
          'Adapted materials, pose and animation. Environment scans: Poly Haven, CC0. Star map: NASA/Goddard Space Flight Center Scientific Visualization Studio; Gaia DR2: ESA/Gaia/DPAC. https://svs.gsfc.nasa.gov/4851/ . '
          'Sound effects generated with ElevenLabs; original synthesized underscore. '
          'See accompanying credits and source manifests for detailed license information.')


def make_overlays(w=1920, h=1080):
    title = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    credits = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    serif = os.environ.get('OBS_SERIF_FONT') or next((f for f in ['/System/Library/Fonts/Supplemental/Baskerville.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'] if Path(f).exists()), 'DejaVuSerif.ttf')
    sans = os.environ.get('OBS_SANS_FONT') or next((f for f in ['/System/Library/Fonts/Supplemental/Arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if Path(f).exists()), 'DejaVuSans.ttf')

    def tracked(image, text, y, path, size, spacing, fill):
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(path, max(10, round(size)))
        lengths = [draw.textlength(c, font=font) for c in text]
        total = sum(lengths) + spacing * (len(text) - 1)
        if total > w * .9:
            raise ValueError('Title or attribution exceeds safe width')
        x = (w-total)/2
        for c, length in zip(text, lengths):
            draw.text((x, y), c, font=font, fill=fill)
            x += length+spacing

    tracked(title, 'THE LAST OBSERVATORY', h*.445, serif, w*.032, w*.0034, (226,219,195,255))
    tracked(title, 'THE STARS REMEMBER', h*.535, sans, w*.0105, w*.0027, (185,193,191,255))
    # Two readable lines in the bottom matte. The required character credit is intact.
    tracked(credits, 'Rain Rig (CC-BY) Blender Foundation | studio.blender.org',
            h*.896, sans, w*.0115, w*.00012, (188,194,194,255))
    tracked(credits, 'Sky: NASA/Goddard SVS • ESA/Gaia/DPAC   |   Scans: Poly Haven CC0   |   SFX: ElevenLabs',
            h*.928, sans, w*.0095, w*.00008, (160,169,170,255))
    folder = ROOT/'renders/v2'
    folder.mkdir(exist_ok=True)
    title_path, credits_path = folder/'title-overlay.png', folder/'credits-overlay.png'
    title.save(title_path)
    credits.save(credits_path)
    preview = Image.new('RGBA', (w,h), (0,0,0,255))
    preview.alpha_composite(title)
    preview.alpha_composite(credits)
    preview.convert('RGB').save(folder/'title-card-preview.png')
    return title_path, credits_path


def inspect_frames(folder, final):
    frames = sorted(p for p in folder.glob('*.png') if p.stem.isdigit())
    if not frames:
        raise SystemExit(f'No rendered frames in {folder}')
    numbers = [int(p.stem) for p in frames]
    expected = list(range(1,577)) if final else list(range(numbers[0],numbers[-1]+1))
    if numbers != expected:
        missing = sorted(set(expected)-set(numbers))
        extra = sorted(set(numbers)-set(expected))
        raise SystemExit(f'Incomplete frame sequence; missing {missing[:12]}, unexpected {extra[:12]}')
    with Image.open(frames[0]) as image:
        size = image.size
    if size[0]%2 or size[1]%2:
        raise SystemExit('H.264 yuv420p output requires even frame dimensions')
    for path in frames:
        if path.name != f'{int(path.stem):04d}.png':
            raise SystemExit(f'Frame filename must use four digits: {path.name}')
        with Image.open(path) as image:
            if image.size != size:
                raise SystemExit(f'Inconsistent frame dimensions: {path.name}')
            image.verify()
    return numbers[0], len(frames), size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('final','test'), nargs='?', default='final')
    parser.add_argument('--prepare-overlays', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.prepare_overlays:
        make_overlays()
        print(ROOT/'renders/v2/title-card-preview.png')
        return
    final = args.mode == 'final'
    folder = ROOT/'renders/v2'/('frames' if final else 'motion-test')
    first, count, (w,h) = inspect_frames(folder, final)
    title_path, credits_path = make_overlays(w,h)
    out = ROOT/('The Last Observatory - Arrival.mp4' if final else 'previews/v2/motion-test.mp4')
    out.parent.mkdir(exist_ok=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    bar = max(0, round((h-w/2.39)/2))
    filters = f'[0:v]drawbox=x=0:y=0:w=iw:h={bar}:color=black:t=fill,drawbox=x=0:y=ih-{bar}:w=iw:h={bar}:color=black:t=fill'
    cmd = [ff,'-y','-hide_banner','-framerate','24','-start_number',str(first),'-i',str(folder/'%04d.png')]
    if final:
        soundtrack = ROOT/'audio/v2/last_observatory_v2_mix.wav'
        with wave.open(str(soundtrack)) as audio:
            if audio.getnframes()/audio.getframerate() != 24 or audio.getnchannels()!=2:
                raise SystemExit('Final soundtrack must be 24-second stereo')
        cmd += ['-loop','1','-framerate','24','-i',str(title_path),
                '-loop','1','-framerate','24','-i',str(credits_path),'-i',str(soundtrack)]
        filters += (',fade=t=in:st=0:d=0.65,fade=t=out:st=21:d=2.0[base];'
                    '[1:v]format=rgba,fade=t=in:st=20.8:d=0.8:alpha=1[title];'
                    '[2:v]format=rgba,fade=t=in:st=20:d=0.5:alpha=1[credits];'
                    '[base][title]overlay=0:0:shortest=1:format=rgb[titled];'
                    '[titled][credits]overlay=0:0:shortest=1:format=rgb,'
                    'fade=t=out:st=23.4:d=0.6,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]')
        cmd += ['-filter_complex',filters,'-map','[v]','-map','3:a',
                '-t','24','-frames:v','576','-c:v','libx264','-preset','slow','-crf','16',
                '-c:a','aac','-b:a','320k']
    else:
        filters += ',scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709[v]'
        cmd += ['-filter_complex',filters,'-map','[v]','-frames:v',str(count),
                '-c:v','libx264','-preset','slow','-crf','18']
    cmd += ['-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709',
            '-color_trc','bt709','-color_range','tv','-metadata','title=The Last Observatory',
            '-metadata',f'comment={CREDIT}','-movflags','+faststart',str(out)]
    if args.dry_run:
        print(json.dumps({'validated_frames':count,'dimensions':[w,h],'first_frame':first,
                          'output':str(out),'command':cmd},indent=2))
        return
    subprocess.run(cmd,check=True)
    print(out)


if __name__ == '__main__':
    main()
