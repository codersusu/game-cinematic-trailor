# V13 publication and local cleanup

Published to `codersusu/game-cinematic-trailor`, branch `main`. The content release commit is `0a081fb41cbe88ce4f1f81e91b16b429c556cc62`.

The latest film is `previews/v13/Forest-to-Astra-V13-1080p.mp4`: 1920×1080, 32.75 seconds, 12fps, with original music. Its SHA-256 is `53389d92f5c4258d50bf51bcf7fd6ce14e38de7653a2b21a91818c66b335ddca`.

All project code and audited redistributable assets were uploaded with Git LFS. The source inventory and [redistribution audit](redistribution-audit.md) describe the raw archer-pack/derived-scene exceptions, excluded signed responses, runtimes and regenerable caches. The editable public forest/bear scene and complete room scene are included. The full restricted production forest scene remains local.

Before cleanup, a fresh remote clone fetched all 44 video files independently. Every size and SHA-256 matched; Git LFS pointer validation passed. See [remote verification](videos-remote-verification.json).

Cleanup removed 44 production video exports (295,360,909 bytes), replaced 44 checkout video contents with their unchanged committed LFS pointers, and evicted their 44 local LFS cache objects. The temporary verification clone was removed as well. Source assets, code, music, editable scenes and individual render frames were preserved. See [cleanup result](video-cleanup-result.json).

## Restore a local video

From the Git checkout:

```sh
git lfs pull --include="previews/v13/Forest-to-Astra-V13-1080p.mp4" --exclude=""
```

Restore all archived videos with `git lfs pull --include="*.mp4" --exclude=""`. The small `.mp4` files left in the cleaned Git checkout are LFS pointers, not playable videos, until fetched.
