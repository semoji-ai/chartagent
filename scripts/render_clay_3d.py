"""Render a real-3D clay bar chart using pyrender + trimesh (headless EGL).

Usage:
    PYTHONPATH=src python3.12 scripts/render_clay_3d.py [--out examples/clay_preview/bar_vertical_3d.png]
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

import numpy as np
import trimesh
import pyrender
from PIL import Image


RECORDS = [
    {"label": "Organic", "value": 420},
    {"label": "Creators", "value": 310},
    {"label": "Email", "value": 260},
    {"label": "Paid", "value": 180},
    {"label": "Partners", "value": 135},
]

WIDTH, HEIGHT = 1920, 1080

def srgb_to_linear(rgba: list[float]) -> list[float]:
    out = []
    for i, c in enumerate(rgba):
        if i == 3:
            out.append(c)
            continue
        if c <= 0.04045:
            out.append(c / 12.92)
        else:
            out.append(((c + 0.055) / 1.055) ** 2.4)
    return out


BG_COLOR = srgb_to_linear([0.738, 0.898, 0.812, 1.0])
FLOOR_COLOR = srgb_to_linear([0.820, 0.930, 0.855, 1.0])
BAR_COLOR = srgb_to_linear([0.545, 0.352, 0.623, 1.0])


def look_at(eye: np.ndarray, target: np.ndarray, up: np.ndarray) -> np.ndarray:
    eye = np.asarray(eye, dtype=float)
    target = np.asarray(target, dtype=float)
    up = np.asarray(up, dtype=float)
    forward = target - eye
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    camera_up = np.cross(right, forward)
    pose = np.eye(4)
    pose[:3, 0] = right
    pose[:3, 1] = camera_up
    pose[:3, 2] = -forward
    pose[:3, 3] = eye
    return pose


def make_capsule_bar(height: float, radius: float, sections: int = 64) -> trimesh.Trimesh:
    """Capsule-shaped bar: cylinder body with hemispherical caps.

    The result has its bottom cap sitting at y=0 and extends upward to y=(height+2*radius).
    Total visual height from floor: height + 2*radius.
    Axis aligned along +Y.
    """
    mesh = trimesh.creation.capsule(height=height, radius=radius, count=[sections, sections // 2])
    rotate_to_y = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
    mesh.apply_transform(rotate_to_y)
    mesh.apply_translation([0.0, radius, 0.0])
    return mesh


def build_scene() -> pyrender.Scene:
    scene = pyrender.Scene(
        bg_color=BG_COLOR,
        ambient_light=[0.14, 0.14, 0.16],
    )

    floor = trimesh.creation.box(extents=[24.0, 0.12, 10.0])
    floor.apply_translation([0.0, -0.06, 0.0])
    floor_mat = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=FLOOR_COLOR,
        metallicFactor=0.0,
        roughnessFactor=0.95,
    )
    scene.add(pyrender.Mesh.from_trimesh(floor, material=floor_mat, smooth=True))

    max_value = max(rec["value"] for rec in RECORDS)
    bar_count = len(RECORDS)
    bar_radius = 0.42
    bar_spacing = 1.35
    total_width = (bar_count - 1) * bar_spacing
    x_start = -total_width / 2.0

    bar_material = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=BAR_COLOR,
        metallicFactor=0.0,
        roughnessFactor=0.42,
    )

    shadow_layers = [
        (1.95, 0.18),
        (1.55, 0.26),
        (1.15, 0.34),
    ]

    for index, rec in enumerate(RECORDS):
        body_height = (rec["value"] / max_value) * 3.8 + 0.4
        cx = x_start + index * bar_spacing

        for layer_index, (scale_factor, alpha) in enumerate(shadow_layers):
            disk_y = 0.004 + layer_index * 0.0015
            shadow_disk = trimesh.creation.cylinder(
                radius=bar_radius * scale_factor, height=0.01, sections=64
            )
            shadow_disk.apply_transform(
                trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
            )
            shadow_disk.apply_translation([cx, disk_y, 0.0])
            shadow_disk.apply_scale([1.0, 1.0, 0.45])
            shadow_material = pyrender.MetallicRoughnessMaterial(
                baseColorFactor=[0.02, 0.018, 0.015, alpha],
                metallicFactor=0.0,
                roughnessFactor=1.0,
                alphaMode="BLEND",
            )
            scene.add(pyrender.Mesh.from_trimesh(shadow_disk, material=shadow_material, smooth=False))

        bar = make_capsule_bar(height=body_height, radius=bar_radius)
        bar.apply_translation([cx, 0.0, 0.0])
        scene.add(pyrender.Mesh.from_trimesh(bar, material=bar_material, smooth=True))

    camera = pyrender.PerspectiveCamera(
        yfov=np.radians(28.0),
        aspectRatio=WIDTH / HEIGHT,
    )
    eye = np.array([0.0, 2.6, 10.0])
    target = np.array([0.0, 1.8, 0.0])
    cam_pose = look_at(eye, target, np.array([0.0, 1.0, 0.0]))
    scene.add(camera, pose=cam_pose)

    key_light = pyrender.DirectionalLight(color=[1.0, 0.97, 0.92], intensity=3.4)
    key_pose = look_at(
        eye=np.array([-4.5, 7.0, 4.5]),
        target=np.array([0.0, 1.0, 0.0]),
        up=np.array([0.0, 1.0, 0.0]),
    )
    scene.add(key_light, pose=key_pose)

    fill_light = pyrender.DirectionalLight(color=[0.82, 0.90, 1.0], intensity=1.1)
    fill_pose = look_at(
        eye=np.array([4.0, 3.5, 5.0]),
        target=np.array([0.0, 1.5, 0.0]),
        up=np.array([0.0, 1.0, 0.0]),
    )
    scene.add(fill_light, pose=fill_pose)

    rim_light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=1.2)
    rim_pose = look_at(
        eye=np.array([0.0, 5.0, -5.0]),
        target=np.array([0.0, 1.5, 0.0]),
        up=np.array([0.0, 1.0, 0.0]),
    )
    scene.add(rim_light, pose=rim_pose)

    return scene


def render(out_path: Path) -> None:
    scene = build_scene()
    renderer = pyrender.OffscreenRenderer(viewport_width=WIDTH, viewport_height=HEIGHT)
    try:
        flags = pyrender.RenderFlags.RGBA
        color, _ = renderer.render(scene, flags=flags)
        color = color[..., :3]
    finally:
        renderer.delete()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(color).save(out_path)
    print(f"wrote {out_path} ({color.shape[1]}x{color.shape[0]})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render real-3D clay bar chart")
    parser.add_argument(
        "--out",
        default="examples/clay_preview/bar_vertical_3d.png",
        help="Output PNG path",
    )
    args = parser.parse_args()
    render(Path(args.out).expanduser().resolve())


if __name__ == "__main__":
    main()
