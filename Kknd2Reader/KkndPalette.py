from pathlib import Path

def rgb555_to_rgb24(value: int) -> int:
    r5 = (value >> 10) & 0x1F
    g5 = (value >> 5) & 0x1F
    b5 = value & 0x1F

    r8 = round(r5 * 255.0 / 31.0)
    g8 = round(g5 * 255.0 / 31.0)
    b8 = round(b5 * 255.0 / 31.0)

    return (r8 << 16) | (g8 << 8) | b8

def rgb24_to_bgr24(value: int) -> int:
    return ((value & 0xFF) << 16) | (value & 0xFF00) | ((value & 0xFF0000) >> 16)

def rgb_distance_squared(left: int, right: int) -> int:
    lr = (left >> 16) & 0xFF
    lg = (left >>  8) & 0xFF
    lb = (left >>  0) & 0xFF

    rr = (right >> 16) & 0xFF
    rg = (right >>  8) & 0xFF
    rb = (right >>  0) & 0xFF

    return (lr - rr) ** 2 + (lg - rg) ** 2 + (lb - rb) ** 2


def read_rgb555_words(path: str) -> list[int]:
    data = Path(path).read_bytes()
    return [
        int.from_bytes(data[i:i + 2], "little")
        for i in range(0, len(data), 2)
    ]


def read_spriteb_palette(levels_dir: str, faction_id: int, team_color_id: int) -> list[int]:
    """
    spriteb.pal:
        3 factions * 8 team colors * 256 RGB555 colors
    """
    if not 0 <= faction_id < 3:
        raise ValueError("faction_id must be 0..2")
    if not 0 <= team_color_id < 8:
        raise ValueError("team_color_id must be 0..7")

    words = read_rgb555_words(f"{levels_dir}/spriteb.pal")

    block_index = faction_id * 8 + team_color_id
    start = block_index * 256
    block = words[start:start + 256]

    if len(block) != 256:
        raise ValueError("invalid spriteb.pal size")

    return [rgb555_to_rgb24(color) for color in block]


def read_spritet_palette(levels_dir: str, faction_id: int, team_color_id: int) -> list[int]:
    """
    spritet.pal:
        3 factions * 8 team colors * 64 RGB555 colors
    """
    words = read_rgb555_words(f"{levels_dir}/spritet.pal")

    block_index = faction_id * 8 + team_color_id
    start = block_index * 64
    block = words[start:start + 64]

    if len(block) != 64:
        raise ValueError("invalid spritet.pal size")

    return [rgb555_to_rgb24(color) for color in block]

def read_blit_palette(levels_dir: str, faction_id: int, team_color_id: int, variant_id: int = 0) -> list[int]:
    """
    blit.pal:
        3 factions * 16 blocks * 16 RGB555 colors

    Kknd2.exe copies 16 colors from the selected block and another 16 colors
    from the block at +0x100 bytes. The variant_id selects between those two
    16-color ramps.
    """
    if not 0 <= faction_id < 3:
        raise ValueError("faction_id must be 0..2")
    if not 0 <= team_color_id < 8:
        raise ValueError("team_color_id must be 0..7")
    if not 0 <= variant_id < 2:
        raise ValueError("variant_id must be 0..1")

    words = read_rgb555_words(f"{levels_dir}/blit.pal")

    block_index = faction_id * 16 + team_color_id + variant_id * 8
    start = block_index * 16
    block = words[start:start + 16]

    if len(block) != 16:
        raise ValueError("invalid blit.pal size")

    return [rgb555_to_rgb24(color) for color in block]

class KkndPalette:
    def __init__(self, levels_dir: str, faction_id: int):
        
        self.spriteb_palettes = [read_spriteb_palette(levels_dir, faction_id, team_color_id) for team_color_id in range(8)]

        self.spritet_palettes = [read_spritet_palette(levels_dir, faction_id, team_color_id) for team_color_id in range(8)]

        self.blit_palettes = [
            [read_blit_palette(levels_dir, faction_id, team_color_id, variant_id) for team_color_id in range(8)]
            for variant_id in range(2)
        ]



palette_survivers : KkndPalette | None = None
palette_mutants : KkndPalette | None = None
palette_series9 : KkndPalette | None = None

def load_palettes(levels_dir: str):
    global palette_survivers, palette_mutants, palette_series9

    palette_survivers = KkndPalette(levels_dir, 0)
    palette_mutants = KkndPalette(levels_dir, 1)
    palette_series9 = KkndPalette(levels_dir, 2)

def get_team_palette_rgb(faction_id: int, team_color_id: int, palette_name: str | None) -> list[int]:
    if not 0 <= team_color_id < 8:
        raise ValueError("team_color_id must be 0..7")

    faction_palettes = {
        0: palette_survivers,
        1: palette_mutants,
        2: palette_series9,
    }

    if faction_id not in faction_palettes:
        raise ValueError("faction_id must be 0..2")

    palettes = faction_palettes[faction_id]
    if palettes is None:
        raise RuntimeError("team palettes are not loaded; call KkndPalette.load_palettes(levels_dir) first")
    
    if palette_name == "spritet.pal":
        return palettes.spritet_palettes[team_color_id]

    if palette_name == "blit.pal":
        return palettes.blit_palettes[0][team_color_id]
    
    return palettes.spriteb_palettes[team_color_id]

def get_team_palette_bgr(faction_id: int, team_color_id: int, palette_name: str | None) -> list[int]:
    return [rgb24_to_bgr24(color) for color in get_team_palette_rgb(faction_id, team_color_id, palette_name)]

def get_blit_palette_rgb(faction_id: int, team_color_id: int, variant_id: int = 0) -> list[int]:
    if not 0 <= team_color_id < 8:
        raise ValueError("team_color_id must be 0..7")
    if not 0 <= variant_id < 2:
        raise ValueError("variant_id must be 0..1")

    faction_palettes = {
        0: palette_survivers,
        1: palette_mutants,
        2: palette_series9,
    }

    if faction_id not in faction_palettes:
        raise ValueError("faction_id must be 0..2")

    palettes = faction_palettes[faction_id]
    if palettes is None:
        raise RuntimeError("team palettes are not loaded; call KkndPalette.load_palettes(levels_dir) first")

    return palettes.blit_palettes[variant_id][team_color_id]

def get_blit_palette_bgr(faction_id: int, team_color_id: int, variant_id: int = 0) -> list[int]:
    return [rgb24_to_bgr24(color) for color in get_blit_palette_rgb(faction_id, team_color_id, variant_id)]

def remap_team_colors_rgb(local_palette_rgb: list[int], faction_id: int, team_color_id: int) -> list[int]:
    if team_color_id == 0:
        return local_palette_rgb.copy()

    remapped_palette = local_palette_rgb.copy()
    source_palettes = [
        get_team_palette_rgb(faction_id, 0, "spritet.pal"),
    ]
    target_palettes = [
        get_team_palette_rgb(faction_id, team_color_id, "spritet.pal"),
    ]

    max_distance_squared = 2500

    for local_color_index, local_color in enumerate(local_palette_rgb):
        best_distance = max_distance_squared + 1
        best_target_color : int | None = None

        for palette_index in range(len(source_palettes)):
            source_palette = source_palettes[palette_index]
            target_palette = target_palettes[palette_index]

            for color_index in range(min(len(source_palette), len(target_palette))):
                if source_palette[color_index] == target_palette[color_index]:
                    continue

                distance = rgb_distance_squared(local_color, source_palette[color_index])
                if distance < best_distance:
                    best_distance = distance
                    best_target_color = target_palette[color_index]

        if best_target_color is not None:
            remapped_palette[local_color_index] = best_target_color

    return remapped_palette
    
