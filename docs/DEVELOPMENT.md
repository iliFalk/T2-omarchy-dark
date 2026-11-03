# T2 Dark — development

The palette, the terminal slots, how the steps follow the light palette, the backgrounds and the credits.

The install and use steps sit in the [README](../README.md).

## Palette

The dark palette is the light T1 palette mirrored: the neutral ladder flips, and every semantic colour
keeps its hue with a lighter step, measured on the dark ground.

| Role | Hex | Contrast on `#1A1A18` |
|---|---|---|
| Background | `#1A1A18` | — |
| Surface | `#262624` | 1.15:1 |
| Elevated | `#333331` | 1.38:1 |
| Line / selection | `#41413E` | 1.70:1 |
| Scrim | `#0E0E0D` | 1.31:1 below the ground |
| Text | `#F0EDE5` | 14.90:1 |
| Muted | `#C5C3BE` | 9.90:1 |
| Helper | `#B4B3AE` | 8.30:1 |
| Placeholder | `#989894` | 6.02:1 |
| Disabled | `#8A8A87` | 5.03:1 |
| Accent (fill and text) | `#4694EA` | 5.55:1 |
| Accent press | `#5AA8FF` | 7.04:1 |
| Error | `#EF664D` | 5.54:1 |
| Error text | `#EE9E93` | 8.26:1 |
| Success | `#7EC59E` | 8.60:1 |
| Press | `#41413E` | 1.70:1 |

One accent step serves both roles: `#4694EA` measures 5.55:1 on the ground and the ground measures
5.55:1 on the accent. No white is needed on an accent fill.

A press moves the colour away from the ground, so the pressed accent is lighter, not darker.

### How the steps follow the light palette

Every semantic colour keeps the hue of its light step and rises in lightness until it reaches 5.5:1 on
`#1A1A18`. The bright slots aim at 8.6:1.

| Token | Light step | Dark step |
|---|---|---|
| accent / blue | `#0762B4` 5.26:1 | `#4694EA` 5.55:1 |
| red | `#BF3922` 4.69:1 | `#EF664D` 5.54:1 |
| green | `#237F52` 4.24:1 | `#4AA172` 5.50:1 |
| yellow | `#8A6100` 4.74:1 | `#B48A3C` 5.51:1 |
| magenta | `#6929C4` 6.61:1 | `#A775FF` 5.50:1 |
| cyan | `#005D5D` 6.59:1 | `#539D9C` 5.54:1 |
| orange | `#9C4A16` 5.27:1 | `#D27B4B` 5.54:1 |
| brown | `#70543E` 5.93:1 | `#A98B73` 5.50:1 |

## Terminal

| Slot | Hex | Contrast on `#1A1A18` |
|---|---|---|
| black | `#1A1A18` | — |
| red | `#EF664D` | 5.54:1 |
| green | `#4AA172` | 5.50:1 |
| yellow | `#B48A3C` | 5.51:1 |
| blue | `#4694EA` | 5.55:1 |
| magenta | `#A775FF` | 5.50:1 |
| cyan | `#539D9C` | 5.54:1 |
| white | `#F0EDE5` | 14.90:1 |
| bright black | `#B4B3AE` | 8.30:1 |
| bright red | `#FF9B9A` | 8.64:1 |
| bright green | `#7EC59E` | 8.60:1 |
| bright yellow | `#D5B26C` | 8.64:1 |
| bright blue | `#79BBFF` | 8.60:1 |
| bright magenta | `#D4A2FF` | 8.64:1 |
| bright cyan | `#77C1D6` | 8.62:1 |
| bright white | `#F0EDE5` | 14.90:1 |

The slotted colours are semantic: the red slot renders red. The previous build kept the Oxocarbon role
swap, where the red slot held a teal.

## What is themed

- Omarchy shell: bar, launcher, menus, notifications, tooltips, lock, image picker
- Hyprland borders, group bars and shadows
- Hyprlock
- Mako, Walker, SwayOSD, Waybar
- Terminals: Alacritty, Ghostty, Kitty, Foot (generated from `colors.toml`)
- btop, cava, fish, fzf, superfile
- GTK, Steam, Discord/Vencord, Zed, Chromium and Zen take the same palette: the base16 slots of those
  files carry the T2 ground, surface, text and eight semantic colours.

## Backgrounds

- `backgrounds/1-horisont.png` — horizon wallpaper, native 6016×3384
- `backgrounds/ascii-art.png` — coloured ASCII halftone flow
- `alt-backgrounds/` — the alternates that came with the theme

The horizon wallpaper is still graded to the older Oxocarbon steps: its ground reads `#0D0D0D` and its
glow `#3DB3F8`. The palette now sits on `#1A1A18` and `#4694EA`, so the picture is a few units off the
bar and the borders. A regrade is a separate change.

Cycle through the theme backgrounds with `omarchy-theme-bg-next`.

### Note on Omarchy's git-theme policy

Omarchy does not stage `alacritty.toml`, `ghostty.conf`, `kitty.conf`, `vscode.json` or `*.lua` from
themes installed from a git repository, because those files can execute code. The palette is therefore
defined in `colors.toml`; Omarchy generates the terminal configs from it. The explicit terminal files in
this repository are used when the theme is installed as a local (non-git) directory.

## Credits

- Original **Oxocarbon Dark** theme by
  [HANCORE-linux](https://github.com/HANCORE-linux/omarchy-oxocarbon-theme)
- The palette follows the **T1 design system**, published as
  [iliFalk/h1-design-system](https://github.com/iliFalk/h1-design-system)
- Theme structure generated with
  [Omarchist](https://github.com/tahayvr/omarchist) by
  [Taha](https://github.com/tahayvr)
- Oxocarbon colours by
  [nyoom-engineering](https://github.com/nyoom-engineering/oxocarbon.nvim)

## License

MIT — see [LICENSE](../LICENSE). The original Oxocarbon theme is MIT-licensed; this dark adaptation
keeps the same licence and attribution.
