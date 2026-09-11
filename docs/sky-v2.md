# V2 sky — NASA catalog star panorama

## Download and provenance

- Source: [NASA SVS — Deep Star Maps 2020](https://svs.gsfc.nasa.gov/4851/), visualization by Ernie Wright. Published 9 September 2020; galactic maps corrected 4 January 2021.
- Original file: [starmap_2020_8k_gal.exr](https://svs.gsfc.nasa.gov/vis/a000000/a004800/a004851/starmap_2020_8k_gal.exr).
- Local file: `assets/hdri/stars/starmap_2020_8k_gal.exr`.
- Downloaded 11 September 2026. Size: **160,735,772 bytes**. Resolution verified in Blender: **8192 × 4096**.
- SHA-256: `d70924422d3e0159764b16a19658784befcf73b97e06e5c16614860c1514bb58`.

This is NASA's catalog-derived star visualization, based on Hipparcos-2, Tycho-2 and Gaia DR2, with supporting catalogs. It represents positions, brightness and colors of approximately 1.7 billion catalog stars. The Milky Way structure comes from that map, rather than procedural dots. Original EXR pixels are preserved. The map is linear half-float OpenEXR, interpreted as Linear Rec.709 in Blender.

Credit for the sky source: **NASA/Goddard Space Flight Center Scientific Visualization Studio. Gaia DR2: ESA/Gaia/DPAC.** Visualization: Ernie Wright. The constellation-line overlays are not used.

## Reproduction terms

The source page links to [NASA Images and Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/). This asset is recorded as NASA media under those guidelines, **not CC0**. NASA states that its media generally are not subject to US copyright; source acknowledgment and avoidance of implied endorsement apply. Third-party marked copyrighted material and NASA branding have separate restrictions. This panorama contains no people, logo, insignia or other NASA branding, and no separate copyright notice is displayed for the selected star map.

For this AI-assisted cinematic, credit identifies the unmodified underlying star-map source only. The scene, lighting, positioning, exposure and final trailer are our creative adaptation; they are not a NASA visualization or endorsement. No logo is included.

## Blender module and controls

`from star_sky_v2 import build_star_world`

`world = build_star_world()` returns the assigned Blender World. Default orientation places the galactic center **north (+Y), 25° above the horizon**, with the band rising approximately **35° to screen-right** when facing the center. An empty-scene CPU render verified this composition.

Parameters:

- `azimuth_deg=0`: north; 90 is east (+X).
- `elevation_deg=25`: center elevation.
- `band_tilt_deg=35`: center band roll.
- `rotation_deg=None`: optional direct XYZ Mapping rotation override in degrees.
- `star_strength=.85`: visible map exposure multiplier.
- `ambient_strength=.045`: separate diffuse illumination level.
- `base_color=(.00025,.0005,.0015)`: very dim blue addition to the visible sky.
- `ambient_color=(.16,.24,.40)`: diffuse ambient color.

The derived default Mapping rotation is approximately **(-25°, 35°, -90°)**. Camera, glossy and transmission rays see the stars; other paths use the separately controlled low-energy blue background. This preserves sky contrast without brightening the entire observatory. The function does not change scene lighting, film exposure, or texture-resolution limits.

Keep the Cycles final texture limit at **8192 or unlimited**. Globally limiting textures to 2K/4K will erase many stars. The panorama itself is never resized by this module. Linear interpolation avoids nearest-neighbor pixel steps; use the final render's antialiasing/sampling to assess star stability in motion.

## Validation

Blender 5.2.1 loaded the EXR at 8192 × 4096 and built all nodes successfully. The requested center direction transforms to texture direction (1, 0, 0), the center of an equirectangular environment. A 480 × 270 one-sample **CPU-only** proof render showed the galactic center and diagonal Milky Way band with distinct catalog stars. No GPU render was used for this subtask.
