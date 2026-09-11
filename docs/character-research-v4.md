# Native character and facial performance research — V4

Research date: 2026-09-11. Goal: a young adult female cinematic character with an existing walk clip and editable facial controls. Search listings are treated as claims until the downloaded file can be inspected.

**Working V4 selection:** Microsoft Rocketbox Female Adult 04 is integrated from `assets/character/heroine_v4/`, with its matching start/walk/stop/idle motions and authored surprise/wonder performance. The acting proof is rendering for visual review. This is a practical animation replacement; it is not presented as the highest-quality model online. The more realistic Jungle Jim option remains pending authenticated Sketchfab download and inspection.

## Strongest candidate

[Realistic woman walking (animated), Jungle Jim](https://sketchfab.com/3d-models/realistic-woman-walking-animated-d1ce2b8009b8401481408aeecea903d0)

- Official Sketchfab API confirms **83,769 triangles, 50,181 vertices, one animation, and downloadable status**.
- **CC BY 4.0**, attribution to Jungle Jim. License URL: https://creativecommons.org/licenses/by/4.0/.
- Public listing tags include facial rig and facial expressions. The public portrait shows a realistic young adult face with modeled eyes and hair cards. The controls and the walk quality are **not yet verified in the source file**.
- Official download API requires authentication (HTTP 401). No viewer geometry was extracted. Browser access was unavailable because the Mac was locked.
- Saved public metadata and portrait: `assets/character/candidates_v4/jungle-jim-public-metadata.json` and `jungle-jim-preview.jpg`.

## Free native files acquired for inspection

### Microsoft Rocketbox Female Adult 04 — strongest acquired technical fallback

Source: [Microsoft's official Rocketbox repository](https://github.com/microsoft/Microsoft-Rocketbox), MIT license (license file retained locally). Acquired only the female facial FBX, its seven 2048×2048 texture maps, matching walk/start/stop/idle FBXs, and documentation. Exact pinned commit, upstream paths and SHA-256 checksums are in `assets/character/candidates_v4/rocketbox/acquisition-manifest.json`.

**Actual Blender inspection:** 5,170 vertices; 80 imported bones; 175 non-basis facial shape keys, including the 52 ARKit channels. Every character bone name occurs in each matching motion rig. Motion files include 41 additional terminal “Nub” bones. Native source timings are walk 1–37, start 1–29, stop 1–54 and breathing idle 1–81, all at 30 fps. These clips are supplied separately from the character FBX. The differing exported rest poses are converted by `scripts/heroine_motion_v4.py`; the assembled acting proof is under visual review.

Rendered neutral, surprise and wonder tests with repaired Cycles materials and one subdivision level: `rocketbox/portrait-neutral.png`, `portrait-surprise.png`, `portrait-wonder.png`; editable `rocketbox/portrait-proof.blend`. The eyes, jaw, lips and eyebrows respond to real morph controls. The brown leather jacket, cargo trousers and boots suit the observatory explorer. **The asset remains visibly older-generation game art:** hair cards, eye material, modest face geometry and skin textures limit portrait realism. It is a better animation foundation than a static generated mesh, not a contemporary AAA character scan.

### Nilda

[Nilda Female Character Walk Animation, ijiklvn / kelvin-carvalho](https://sketchfab.com/3d-models/nilda-female-character-walk-animation-d3f65ad04ec845b197a689db48ec4329)

- CC BY 4.0; listing credits the artist ijiklvn.
- Listed as a Blender Rigify character with a native walk. The artist notes it was their first rig and has some issues. Approximately 12.4k triangles.
- Downloaded the **author-linked** [MediaFire archive](https://www.mediafire.com/file/34gpm1ct966gkgy/nilda_female_character.rar/file), 14,677,319 bytes, with `female11111.blend`, `female_sketchfab.fbx`, and textures.
- Local archive: `assets/character/candidates_v4/nilda.rar`; extracted under `nilda/`.
- **Inspected in Blender 4.5.13 with embedded Python disabled:** native `rigAction` spans frames 0–84 at 30 fps; generated Rigify armature has 753 bones. Head, eyes, teeth and tongue have 63 non-basis facial shape keys, including jaw opening, brows, blinks, smile and eye widening. The accompanying FBX also preserves the walk and facial keys. Head texture is 2048×2048.
- The file emits warnings about four orphaned shape-key datablocks when migrating from Blender 3.01, but the active facial controls survive. Source scene also retains unused missing environment images; importing only the character avoids those dependencies.
- Public preview inspected: stylized face, long black coat, patterned leggings and high-heeled boots. **Technical requirements are met; visual direction and character quality are below the preferred Jungle Jim candidate.** Not selected merely because it downloads easily.

[Female Body Model, Fat cat / Graphic cat](https://graphic-cat.tistory.com/73)

- The artist's [corresponding Sketchfab listing](https://sketchfab.com/3d-models/free-lowpoly-female-7052ca1e09404ce39af47a964e08ee40) licenses the model CC BY and explicitly directs users to the blog's native Blender download to avoid a flawed FBX export.
- Downloaded that native archive: `assets/character/candidates_v4/graphic-cat-female.zip`, 685,272 bytes; contains `Character_002_Female.blend`.
- Official metadata confirms **zero animation clips**. This is an unfinished body base, not a ready cinematic actor. Not recommended for replacing the current clothed heroine.

## Other verified listings

| Candidate | Useful features | Current limitation |
|---|---|---|
| [Sara Character Animated, BlenderKit](https://www.blenderkit.com/asset-gallery-detail/7c2170d4-e9e7-4382-9e9d-0575d170a33a/) | Realistic female; native idle, walk, dance; 32,428 faces; 32.1 MiB | Current asset is Full Plan. No verified facial controls. Not purchased. |
| [Camilia, Superhive](https://superhivemarket.com/products/camilia-realistic-women-free) | 125+ facial morph controls; rigged; Blender/FBX | Despite the “Free” title, current page shows $1. Base mesh; no native walk verified. Not purchased. |
| [Riya, CGTrader](https://www.cgtrader.com/free-3d-models/character/woman/riya-realistic-girl) | Auto-Rig Pro; 52 ARKit shapes; 4K textures; Blender native file | Download requires account access. No native walk verified. Listed Royalty Free (no AI); source redistribution rights would need checking before public repository inclusion. |
| [Reallusion free CC base meshes](https://www.reallusion.com/character-creator/free-3d-character-base.html) | Five full-body rigs; 150+ facial morphs; eyes/teeth/tongue | Unfinished bases without wardrobe, hair or production skin; no native walk promised. Not equivalent to the finished Camila demo character. |

No paid model was purchased, and no protected viewer files or login bypasses were used.
