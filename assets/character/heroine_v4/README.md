# V4 heroine — Microsoft Rocketbox Female Adult 04

This character is the working V4 replacement for the generated heroine. It provides an existing body rig, matching authored locomotion and editable facial expressions. Source: [Microsoft Rocketbox](https://github.com/microsoft/Microsoft-Rocketbox), released under the included [MIT license](LICENSE.md).

Verified in Blender 4.5.13:

- 5,170 source vertices and **80 imported bones**.
- **175 facial shape keys**, including 52 ARKit channels for eyes, brows, jaw, lips and cheeks.
- Matching native walk, walk start, walk stop and breathing idle clips, supplied as separate FBX files at 30 fps.
- Seven **2048 × 2048** texture maps for the body, head and transparent surfaces.

The production scripts in `scripts/heroine_motion_v4.py` and `scripts/heroine_look_v4.py` resolve this folder relative to the project. They convert the clips' exported rest poses, retain native articulation and root motion, rebuild Cycles materials, and animate the opening surprise and later wonder reaction. Scene integration is complete; the acting proof and final movie still require visual review before release.

The model remains older game artwork. Its modest face geometry, hair cards and 2K skin textures limit close-up realism. It was chosen as a usable animation foundation, not as the highest-quality character available online. The more realistic Jungle Jim candidate remains pending authenticated Sketchfab download and file inspection.

No API key, account or add-on is needed to use the included files. Preserve the repository's Git LFS assets when cloning. Source files are unchanged; checksums and the pinned upstream commit are in [acquisition-manifest.json](acquisition-manifest.json). Local changes are described in [ATTRIBUTION.md](ATTRIBUTION.md).
