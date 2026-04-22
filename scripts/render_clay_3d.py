"""Render real-3D clay charts using pyrender + trimesh (headless EGL).

Generates three variants into examples/clay_preview/:
  * bar_vertical_3d.png          — capsule bars
  * bar_vertical_3d_box.png      — rounded-box bars
  * donut_3d.png                 — 3D donut with torus slices

Usage:
    PYTHONPATH=src python3.12 scripts/render_clay_3d.py
"""
from __future__ import annotations

import argparse
import math
import os
from pathlib import Path

os.environ.setdefault("PYOPENGL_PLATFORM", "egl")

import numpy as np
import trimesh
import pyrender
from PIL import Image
from shapely.geometry import Polygon


RECORDS = [
    {"label": "Organic", "value": 420},
    {"label": "Creators", "value": 310},
    {"label": "Email", "value": 260},
    {"label": "Paid", "value": 180},
    {"label": "Partners", "value": 135},
]

DONUT_RECORDS = [
    {"label": "Purple", "value": 42, "color": (0.545, 0.352, 0.623)},
    {"label": "Peach", "value": 26, "color": (0.902, 0.608, 0.502)},
    {"label": "Sage", "value": 18, "color": (0.482, 0.718, 0.647)},
    {"label": "Coral", "value": 14, "color": (0.847, 0.478, 0.478)},
]


WIDTH, HEIGHT = 1920, 1080


def srgb_to_linear(rgba: list[float]) -> list[float]:
    out = []
    for i, c in enumerate(rgba):
        if i == 3:
            out.append(c)
            continue
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
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
    mesh = trimesh.creation.capsule(height=height, radius=radius, count=[sections, sections // 2])
    mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    mesh.apply_translation([0.0, radius, 0.0])
    return mesh


def _rounded_rect_polygon(width: float, depth: float, corner_r: float, segments: int = 12) -> Polygon:
    hw, hd = width / 2.0, depth / 2.0
    r = max(0.0, min(corner_r, hw - 1e-6, hd - 1e-6))
    if r <= 0:
        return Polygon([(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)])
    points: list[tuple[float, float]] = []
    corners = [
        ((hw - r, hd - r), 0.0),
        ((-(hw - r), hd - r), 90.0),
        ((-(hw - r), -(hd - r)), 180.0),
        ((hw - r, -(hd - r)), 270.0),
    ]
    for (cx, cz), start_deg in corners:
        for i in range(segments + 1):
            angle = math.radians(start_deg + 90.0 * i / segments)
            points.append((cx + r * math.cos(angle), cz + r * math.sin(angle)))
    return Polygon(points)


def make_rounded_box_bar(
    height: float,
    width: float,
    depth: float,
    corner_r: float,
    top_bevel: float = 0.08,
) -> trimesh.Trimesh:
    """Rounded-rectangle extrusion with a subtle top bevel for soft upper edges."""
    bevel = min(top_bevel, height * 0.3, corner_r * 0.95)
    body_h = max(1e-3, height - bevel)
    body_poly = _rounded_rect_polygon(width, depth, corner_r)
    body = trimesh.creation.extrude_polygon(body_poly, height=body_h)
    body.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))

    cap_poly = _rounded_rect_polygon(
        width - 2 * bevel * 0.6,
        depth - 2 * bevel * 0.6,
        max(0.0, corner_r - bevel * 0.6),
    )
    cap = trimesh.creation.extrude_polygon(cap_poly, height=bevel)
    cap.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))
    cap.apply_translation([0.0, body_h, 0.0])

    combined = trimesh.util.concatenate([body, cap])
    combined.process(validate=False)
    return combined


def make_soft_shadow_disks(
    scene: pyrender.Scene,
    center_x: float,
    center_z: float,
    base_radius: float,
    *,
    layers: int = 14,
    max_scale: float = 1.95,
    depth_ratio: float = 0.48,
    peak_alpha: float = 0.34,
    y_base: float = 0.003,
) -> None:
    """Stack many translucent disks with exponential falloff to fake a blurred shadow."""
    for i in range(layers):
        t = i / max(1, layers - 1)
        scale = 1.0 + (max_scale - 1.0) * t
        radius = base_radius * scale
        alpha = peak_alpha * math.exp(-3.2 * t)
        if alpha < 0.012:
            continue
        disk = trimesh.creation.cylinder(radius=radius, height=0.008, sections=64)
        disk.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
        disk.apply_translation([center_x, y_base + i * 0.0008, center_z])
        disk.apply_scale([1.0, 1.0, depth_ratio])
        mat = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=[0.02, 0.018, 0.015, alpha],
            metallicFactor=0.0,
            roughnessFactor=1.0,
            alphaMode="BLEND",
        )
        scene.add(pyrender.Mesh.from_trimesh(disk, material=mat, smooth=False))


def make_torus_slice(
    major_radius: float,
    tube_radius: float,
    start_angle: float,
    end_angle: float,
    tube_sections: int = 48,
    arc_sections: int = 48,
) -> trimesh.Trimesh:
    """A torus arc spanning [start_angle, end_angle] (radians) around the Y axis."""
    span = end_angle - start_angle
    if span <= 0:
        raise ValueError("end_angle must exceed start_angle")
    phi = np.linspace(0.0, 2.0 * np.pi, tube_sections + 1)[:-1]
    theta = np.linspace(start_angle, end_angle, arc_sections + 1)
    vertices: list[np.ndarray] = []
    for t in theta:
        ct, st = math.cos(t), math.sin(t)
        for p in phi:
            cp, sp = math.cos(p), math.sin(p)
            x = (major_radius + tube_radius * cp) * ct
            z = (major_radius + tube_radius * cp) * st
            y = tube_radius * sp
            vertices.append([x, y, z])
    vertices_arr = np.asarray(vertices, dtype=float)

    faces: list[list[int]] = []
    for i in range(arc_sections):
        for j in range(tube_sections):
            a = i * tube_sections + j
            b = i * tube_sections + (j + 1) % tube_sections
            c = (i + 1) * tube_sections + (j + 1) % tube_sections
            d = (i + 1) * tube_sections + j
            faces.append([a, b, c])
            faces.append([a, c, d])

    start_ring_count = tube_sections
    end_ring_offset = arc_sections * tube_sections
    start_center_idx = len(vertices_arr)
    end_center_idx = start_center_idx + 1
    start_center = [major_radius * math.cos(start_angle), 0.0, major_radius * math.sin(start_angle)]
    end_center = [major_radius * math.cos(end_angle), 0.0, major_radius * math.sin(end_angle)]
    vertices_arr = np.vstack([vertices_arr, np.array([start_center, end_center])])
    for j in range(tube_sections):
        a = j
        b = (j + 1) % tube_sections
        faces.append([start_center_idx, b, a])
    for j in range(tube_sections):
        a = end_ring_offset + j
        b = end_ring_offset + (j + 1) % tube_sections
        faces.append([end_center_idx, a, b])

    mesh = trimesh.Trimesh(vertices=vertices_arr, faces=np.asarray(faces), process=False)
    return mesh


def _add_common_scene(scene: pyrender.Scene) -> None:
    floor = trimesh.creation.box(extents=[28.0, 0.12, 14.0])
    floor.apply_translation([0.0, -0.06, 0.0])
    floor_mat = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=FLOOR_COLOR,
        metallicFactor=0.0,
        roughnessFactor=0.95,
    )
    scene.add(pyrender.Mesh.from_trimesh(floor, material=floor_mat, smooth=True))

    key_light = pyrender.DirectionalLight(color=[1.0, 0.97, 0.92], intensity=3.4)
    key_pose = look_at(np.array([-4.5, 7.0, 4.5]), np.array([0.0, 1.0, 0.0]), np.array([0.0, 1.0, 0.0]))
    scene.add(key_light, pose=key_pose)

    fill_light = pyrender.DirectionalLight(color=[0.82, 0.90, 1.0], intensity=1.1)
    fill_pose = look_at(np.array([4.0, 3.5, 5.0]), np.array([0.0, 1.5, 0.0]), np.array([0.0, 1.0, 0.0]))
    scene.add(fill_light, pose=fill_pose)

    rim_light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=1.2)
    rim_pose = look_at(np.array([0.0, 5.0, -5.0]), np.array([0.0, 1.5, 0.0]), np.array([0.0, 1.0, 0.0]))
    scene.add(rim_light, pose=rim_pose)


def build_bar_scene(shape: str) -> pyrender.Scene:
    scene = pyrender.Scene(bg_color=BG_COLOR, ambient_light=[0.14, 0.14, 0.16])
    _add_common_scene(scene)

    max_value = max(rec["value"] for rec in RECORDS)
    bar_count = len(RECORDS)
    bar_radius = 0.42
    bar_width = bar_radius * 2.0
    bar_spacing = 1.35
    total_width = (bar_count - 1) * bar_spacing
    x_start = -total_width / 2.0

    bar_material = pyrender.MetallicRoughnessMaterial(
        baseColorFactor=BAR_COLOR,
        metallicFactor=0.0,
        roughnessFactor=0.42,
    )

    for index, rec in enumerate(RECORDS):
        body_height = (rec["value"] / max_value) * 3.8 + 0.4
        cx = x_start + index * bar_spacing
        make_soft_shadow_disks(scene, center_x=cx, center_z=0.0, base_radius=bar_radius)
        if shape == "capsule":
            bar = make_capsule_bar(height=body_height, radius=bar_radius)
        else:
            bar = make_rounded_box_bar(
                height=body_height,
                width=bar_width,
                depth=bar_width,
                corner_r=0.08,
                top_bevel=0.08,
            )
        bar.apply_translation([cx, 0.0, 0.0])
        scene.add(pyrender.Mesh.from_trimesh(bar, material=bar_material, smooth=True))

    camera = pyrender.PerspectiveCamera(yfov=np.radians(28.0), aspectRatio=WIDTH / HEIGHT)
    eye = np.array([0.0, 2.6, 10.0])
    target = np.array([0.0, 1.8, 0.0])
    scene.add(camera, pose=look_at(eye, target, np.array([0.0, 1.0, 0.0])))
    return scene


def build_donut_scene() -> pyrender.Scene:
    scene = pyrender.Scene(bg_color=BG_COLOR, ambient_light=[0.14, 0.14, 0.16])
    _add_common_scene(scene)

    major_r = 2.6
    tube_r = 0.72
    total = sum(rec["value"] for rec in DONUT_RECORDS)
    start = -math.pi / 2
    gap = math.radians(2.0)

    for rec in DONUT_RECORDS:
        sweep = rec["value"] / total * 2.0 * math.pi
        end = start + sweep
        slice_mesh = make_torus_slice(
            major_radius=major_r,
            tube_radius=tube_r,
            start_angle=start + gap / 2,
            end_angle=end - gap / 2,
            tube_sections=48,
            arc_sections=max(8, int(48 * sweep / (2.0 * math.pi))),
        )
        slice_mesh.apply_translation([0.0, tube_r + 0.02, 0.0])
        color_linear = srgb_to_linear([*rec["color"], 1.0])
        mat = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=color_linear,
            metallicFactor=0.0,
            roughnessFactor=0.40,
        )
        scene.add(pyrender.Mesh.from_trimesh(slice_mesh, material=mat, smooth=True))
        start = end

    shadow_layers = 16
    for i in range(shadow_layers):
        t = i / max(1, shadow_layers - 1)
        scale = 1.0 + 0.25 * t
        radius = (major_r + tube_r) * scale
        alpha = 0.30 * math.exp(-3.0 * t)
        if alpha < 0.012:
            continue
        disk = trimesh.creation.cylinder(radius=radius, height=0.008, sections=96)
        disk.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
        disk.apply_translation([0.0, 0.003 + i * 0.0009, 0.0])
        disk.apply_scale([1.0, 1.0, 0.42])
        mat = pyrender.MetallicRoughnessMaterial(
            baseColorFactor=[0.02, 0.018, 0.015, alpha],
            metallicFactor=0.0,
            roughnessFactor=1.0,
            alphaMode="BLEND",
        )
        scene.add(pyrender.Mesh.from_trimesh(disk, material=mat, smooth=False))

    camera = pyrender.PerspectiveCamera(yfov=np.radians(26.0), aspectRatio=WIDTH / HEIGHT)
    eye = np.array([0.0, 5.2, 8.4])
    target = np.array([0.0, 0.3, 0.0])
    scene.add(camera, pose=look_at(eye, target, np.array([0.0, 1.0, 0.0])))
    return scene


def render_scene(scene: pyrender.Scene, out_path: Path) -> None:
    renderer = pyrender.OffscreenRenderer(viewport_width=WIDTH, viewport_height=HEIGHT)
    try:
        color, _ = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)
    finally:
        renderer.delete()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(color[..., :3]).save(out_path)
    print(f"wrote {out_path} ({color.shape[1]}x{color.shape[0]})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render real-3D clay charts")
    parser.add_argument("--out-dir", default="examples/clay_preview", help="Output directory")
    parser.add_argument(
        "--only",
        choices=("capsule", "box", "donut", "all"),
        default="all",
        help="Which variant to render",
    )
    args = parser.parse_args()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if args.only in ("capsule", "all"):
        render_scene(build_bar_scene("capsule"), out_dir / "bar_vertical_3d.png")
    if args.only in ("box", "all"):
        render_scene(build_bar_scene("box"), out_dir / "bar_vertical_3d_box.png")
    if args.only in ("donut", "all"):
        render_scene(build_donut_scene(), out_dir / "donut_3d.png")


if __name__ == "__main__":
    main()
