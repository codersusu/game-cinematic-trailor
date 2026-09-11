# Stellar centerpiece — v3

The centerpiece is original procedural 3D geometry inspired by the user's [supplied Astra visual reference](https://heise.cloudimg.io/v7/_www-heise-de_/imgs/18/5/1/5/8/7/6/4/Unbenannt-5a4f0e21050f208e.png?force_format=avif%2Cwebp%2Cjpeg&org_if_sml=1&q=70&width=1019). The reference was viewed for art direction; its pixels, text and logos are not used in the film.

`scripts/galaxy_v3.py` creates 5,456 individually modeled stars in eight efficient meshes, with a dominant winding arm, faint secondary arm, sparse outliers and a compact resolved stellar nucleus. Blue-white points are interspersed with warm stars. A tilted disk rotates 165 degrees over the 24-second timeline; eight radial layers add subtle differential rotation.

The old solid celestial globe, polar spindle and inner two gimbals are hidden. The two outer brass gimbals keep their engraved detail and original mechanical animation. A separate cool point light provides economical room illumination; tiny stars remain visible to camera/reflection rays without expensive individual light sampling.

`scripts/compositor_v3.py` adds a soft halo from the emission pass while preserving masonry contrast. The original camera travel is retained; the instrument detail shot now aims at the nucleus with a 48 mm lens instead of framing only the upper ring.

The distant sky remains the NASA/Goddard SVS 8K star map documented in `sky-v2.md`. It is independent of this animated, locally modeled galaxy.

The central northern pier is replaced by a broad archway, clearing the night-sky backdrop in the closing composition.
